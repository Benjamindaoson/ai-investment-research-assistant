package com.itzixi.ai.service;

import com.itzixi.ai.config.RAGConfig;
import com.itzixi.ai.entity.HistoricalCase;
import jakarta.annotation.PreDestroy;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.io.File;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
public class VectorStoreService {

    @Resource
    private VectorStore vectorStore;

    @Resource
    private CaseQualityService caseQualityService;

    @Resource
    private RAGConfig ragConfig;

    @Resource
    private RAGMetricsService metricsService;

    @Resource
    private HybridEmbeddingService hybridEmbeddingService;

    @Resource
    private com.itzixi.ai.client.AIEngineClient aiEngineClient;

    @Value("${spring.ai.vectorstore.file-path:./data/vector-store.json}")
    private String vectorStoreFilePath;

    @PreDestroy
    public void shutdown() {
        saveVectorStore();
    }

    public void saveVectorStore() {
        try {
            if (vectorStore instanceof SimpleVectorStore simpleVectorStore) {
                File file = new File(vectorStoreFilePath);
                if (file.getParentFile() != null) {
                    file.getParentFile().mkdirs();
                }
                simpleVectorStore.save(file);
                log.info("vector store saved to {}", vectorStoreFilePath);
            }
        } catch (Exception e) {
            log.error("save vector store failed", e);
        }
    }

    public void addCase(HistoricalCase historicalCase) {
        try {
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("stockCode", historicalCase.getStockCode());
            metadata.put("title", historicalCase.getTitle());
            metadata.put("occurredAt", historicalCase.getOccurredAt());

            try {
                float[] features = hybridEmbeddingService.generateHybridEmbedding(historicalCase);
                metadata.put("featureVector", arrayToString(features));
                metadata.put("hasHybridFeatures", true);
            } catch (Exception ignored) {
                metadata.put("hasHybridFeatures", false);
            }

            Document document = new Document(
                    historicalCase.getId(),
                    buildCaseContent(historicalCase),
                    metadata
            );
            vectorStore.add(List.of(document));
        } catch (Exception e) {
            log.error("add case failed: {}", historicalCase.getId(), e);
        }
    }

    public void addCases(List<HistoricalCase> cases) {
        List<Document> documents = new ArrayList<>();
        for (HistoricalCase c : cases) {
            Map<String, Object> metadata = new HashMap<>();
            metadata.put("stockCode", c.getStockCode());
            metadata.put("title", c.getTitle());
            metadata.put("occurredAt", c.getOccurredAt());
            try {
                float[] features = hybridEmbeddingService.generateHybridEmbedding(c);
                metadata.put("featureVector", arrayToString(features));
                metadata.put("hasHybridFeatures", true);
            } catch (Exception ignored) {
                metadata.put("hasHybridFeatures", false);
            }
            documents.add(new Document(c.getId(), buildCaseContent(c), metadata));
        }
        if (!documents.isEmpty()) {
            vectorStore.add(documents);
        }
    }

    public List<HistoricalCase> similaritySearch(String query, int topK) {
        try {
            int safeTopK = Math.max(1, Math.min(topK, 10000));
            List<Document> results = vectorStore.similaritySearch(
                    SearchRequest.builder().query(query == null ? "" : query).topK(safeTopK).build()
            );
            if (results == null) {
                return new ArrayList<>();
            }
            return results.stream().map(this::documentToCase).collect(Collectors.toList());
        } catch (Exception e) {
            log.error("similarity search failed: {}", query, e);
            return new ArrayList<>();
        }
    }

    public List<HistoricalCase> timeDecaySearch(String query, int topK, double decayFactor) {
        try {
            int safeTopK = Math.max(1, topK);
            double actualDecayFactor = decayFactor > 0 ? decayFactor : ragConfig.getTimeDecay().getFactor();

            List<Document> candidates = vectorStore.similaritySearch(
                    SearchRequest.builder().query(query == null ? "" : query).topK(Math.max(20, safeTopK * 3)).build()
            );
            if (candidates == null || candidates.isEmpty()) {
                return new ArrayList<>();
            }

            LocalDateTime now = LocalDateTime.now();
            int candidateSize = candidates.size();
            List<ScoredCase> scoredCases = new ArrayList<>();

            for (int i = 0; i < candidates.size(); i++) {
                HistoricalCase c = documentToCase(candidates.get(i));
                double rankScore = 1.0 - (i / (double) candidateSize);
                rankScore = Math.max(0.05, rankScore);

                double finalScore;
                try {
                    LocalDateTime occurredAt = parseDateTime(c.getOccurredAt());
                    long daysDiff = Math.max(0, ChronoUnit.DAYS.between(occurredAt, now));
                    double timeDecay = Math.exp(-actualDecayFactor * daysDiff / 365.0);
                    finalScore = rankScore * (
                            ragConfig.getTimeDecay().getSimilarityWeight()
                                    + ragConfig.getTimeDecay().getTimeWeight() * timeDecay
                    );
                } catch (Exception e) {
                    finalScore = rankScore * ragConfig.getTimeDecay().getSimilarityWeight();
                }
                scoredCases.add(new ScoredCase(c, finalScore));
            }

            return scoredCases.stream()
                    .sorted((a, b) -> Double.compare(b.score, a.score))
                    .limit(safeTopK)
                    .map(sc -> sc.historicalCase)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            log.error("time decay search failed: {}", query, e);
            return similaritySearch(query, topK);
        }
    }

    public List<HistoricalCase> searchByStock(String stockCode, String query, int topK) {
        String enhancedQuery = String.format("stockCode: %s, %s", stockCode, query);
        return similaritySearch(enhancedQuery, topK);
    }

    public List<HistoricalCase> multiPathRecall(String stockCode, String query, int topK) {
        long startTime = System.currentTimeMillis();
        try {
            int safeTopK = Math.max(1, topK);
            RAGConfig.RecallWeights weights = ragConfig.getRecallWeights();

            List<HistoricalCase> vectorResults = timeDecaySearch(query, safeTopK * 2, 0);
            List<HistoricalCase> sameStockResults = searchByStockCode(stockCode, safeTopK);
            List<HistoricalCase> sameEventResults = searchByEventType(query, safeTopK);

            List<HistoricalCase> fusedResults = fuseResults(
                    vectorResults,
                    sameStockResults,
                    sameEventResults,
                    weights.getVector(),
                    weights.getSameStock(),
                    weights.getSameEvent(),
                    Math.max(20, safeTopK * 6) // Fetch more candidates for CrossEncoder
            );

            RAGConfig.QualityConfig qualityConfig = ragConfig.getQuality();
            List<HistoricalCase> qualityFiltered = caseQualityService.filterByQuality(
                    fusedResults, qualityConfig.getMinScore());

            if (qualityFiltered.size() < safeTopK) {
                qualityFiltered = caseQualityService.filterByQuality(
                        fusedResults, qualityConfig.getFallbackScore());
            }

            // --- Deep Learning Cross-Encoder Reranking (Python Native) ---
            List<HistoricalCase> finalResults = qualityFiltered;
            if (!qualityFiltered.isEmpty()) {
                try {
                    List<com.itzixi.ai.client.AIEngineClient.HistoricalCaseDto> dtos = new ArrayList<>();
                    for (HistoricalCase c : qualityFiltered) {
                        com.itzixi.ai.client.AIEngineClient.HistoricalCaseDto dto = new com.itzixi.ai.client.AIEngineClient.HistoricalCaseDto();
                        dto.setId(c.getId());
                        dto.setStock_code(c.getStockCode());
                        dto.setTitle(c.getTitle());
                        dto.setDescription(c.getDescription());
                        dto.setAnalysis(c.getAnalysis());
                        dto.setActual_impact(c.getActualImpact());
                        dto.setOccurred_at(c.getOccurredAt());
                        dtos.add(dto);
                    }
                    com.itzixi.ai.client.AIEngineClient.RerankRequest req = 
                        new com.itzixi.ai.client.AIEngineClient.RerankRequest(query, dtos, safeTopK);
                    
                    List<com.itzixi.ai.client.AIEngineClient.HistoricalCaseDto> rerankedDtos = aiEngineClient.rerankCandidates(req);
                    
                    if (rerankedDtos != null && !rerankedDtos.isEmpty()) {
                        List<HistoricalCase> rerankedCases = new ArrayList<>();
                        for (com.itzixi.ai.client.AIEngineClient.HistoricalCaseDto d : rerankedDtos) {
                            qualityFiltered.stream().filter(x -> x.getId().equals(d.getId())).findFirst().ifPresent(rerankedCases::add);
                        }
                        finalResults = rerankedCases;
                    } else {
                        finalResults = qualityFiltered.stream().limit(safeTopK).collect(Collectors.toList());
                    }
                } catch (Exception e) {
                    log.error("Failed to call Python Reranker, falling back to Java heuristics", e);
                    finalResults = qualityFiltered.stream().limit(safeTopK).collect(Collectors.toList());
                }
            }

            recordMetrics(query, stockCode, finalResults, startTime, "multiPath+CrossEncoder");
            return finalResults;
        } catch (Exception e) {
            log.error("multi-path recall failed", e);
            return timeDecaySearch(query, topK, 0);
        }
    }

    private void recordMetrics(String query,
                               String stockCode,
                               List<HistoricalCase> results,
                               long startTime,
                               String searchType) {
        try {
            long latency = System.currentTimeMillis() - startTime;
            double avgQuality = results.stream()
                    .mapToDouble(caseQualityService::calculateQualityScore)
                    .average()
                    .orElse(0.0);

            RAGMetricsService.SearchMetric metric = new RAGMetricsService.SearchMetric();
            metric.setQuery(query);
            metric.setStockCode(stockCode);
            metric.setRecallCount(results.size());
            metric.setAvgQualityScore(avgQuality);
            metric.setLatencyMs(latency);
            metric.setSearchType(searchType);
            metricsService.recordSearch(metric);
        } catch (Exception e) {
            log.warn("record rag metric failed", e);
        }
    }

    @Cacheable(value = "stockCases", key = "#stockCode + '_' + #limit")
    private List<HistoricalCase> searchByStockCode(String stockCode, int limit) {
        try {
            String normalizedCode = stockCode == null ? "" : stockCode.trim().toUpperCase();
            if (normalizedCode.isEmpty()) {
                return new ArrayList<>();
            }

            int candidateTopK = Math.max(40, Math.min(300, Math.max(1, limit) * 10));
            List<Document> focusedDocs = vectorStore.similaritySearch(
                    SearchRequest.builder().query(normalizedCode).topK(candidateTopK).build()
            );
            List<HistoricalCase> focused = toStockSortedList(focusedDocs, normalizedCode, limit);
            if (focused.size() >= limit || candidateTopK >= 300) {
                return focused;
            }

            List<Document> fallbackDocs = vectorStore.similaritySearch(
                    SearchRequest.builder().query("stock " + normalizedCode).topK(300).build()
            );
            return toStockSortedList(fallbackDocs, normalizedCode, limit);
        } catch (Exception e) {
            log.warn("search by stock failed: {}", stockCode, e);
            return new ArrayList<>();
        }
    }

    private List<HistoricalCase> toStockSortedList(List<Document> docs, String stockCode, int limit) {
        if (docs == null) {
            return new ArrayList<>();
        }
        return docs.stream()
                .map(this::documentToCase)
                .filter(c -> stockCode.equalsIgnoreCase(c.getStockCode()))
                .sorted((a, b) -> {
                    try {
                        return parseDateTime(b.getOccurredAt()).compareTo(parseDateTime(a.getOccurredAt()));
                    } catch (Exception e) {
                        return 0;
                    }
                })
                .limit(Math.max(1, limit))
                .collect(Collectors.toList());
    }

    private List<HistoricalCase> searchByEventType(String query, int limit) {
        try {
            String eventType = extractEventType(query == null ? "" : query.toLowerCase());
            if (eventType.isEmpty()) {
                return new ArrayList<>();
            }
            return similaritySearch(eventType, limit);
        } catch (Exception e) {
            log.warn("search by event failed: {}", query, e);
            return new ArrayList<>();
        }
    }

    private String extractEventType(String query) {
        if (query.contains("earnings") || query.contains("财报")) {
            return "财报";
        }
        if (query.contains("merger") || query.contains("acquisition") || query.contains("并购")) {
            return "并购";
        }
        if (query.contains("fda") || query.contains("approval") || query.contains("监管")) {
            return "监管批准";
        }
        if (query.contains("lawsuit") || query.contains("诉讼")) {
            return "法律诉讼";
        }
        if (query.contains("dividend") || query.contains("分红")) {
            return "分红";
        }
        return "";
    }

    private List<HistoricalCase> fuseResults(
            List<HistoricalCase> path1,
            List<HistoricalCase> path2,
            List<HistoricalCase> path3,
            double weight1,
            double weight2,
            double weight3,
            int topK) {

        Map<String, ScoredCase> scoreMap = new HashMap<>();

        for (int i = 0; i < path1.size(); i++) {
            HistoricalCase c = path1.get(i);
            double score = weight1 * (1.0 - i / (double) Math.max(1, path1.size()));
            scoreMap.put(c.getId(), new ScoredCase(c, score));
        }

        for (int i = 0; i < path2.size(); i++) {
            HistoricalCase c = path2.get(i);
            double score = weight2 * (1.0 - i / (double) Math.max(1, path2.size()));
            mergeScore(scoreMap, c, score);
        }

        for (int i = 0; i < path3.size(); i++) {
            HistoricalCase c = path3.get(i);
            double score = weight3 * (1.0 - i / (double) Math.max(1, path3.size()));
            mergeScore(scoreMap, c, score);
        }

        return scoreMap.values().stream()
                .sorted((a, b) -> Double.compare(b.score, a.score))
                .limit(Math.max(1, topK))
                .map(sc -> sc.historicalCase)
                .collect(Collectors.toList());
    }

    private void mergeScore(Map<String, ScoredCase> scoreMap, HistoricalCase c, double score) {
        ScoredCase existing = scoreMap.get(c.getId());
        if (existing == null) {
            scoreMap.put(c.getId(), new ScoredCase(c, score));
        } else {
            existing.score += score;
        }
    }

    private String buildCaseContent(HistoricalCase c) {
        return String.format("""
                stockCode: %s
                title: %s
                description: %s
                analysis: %s
                actualImpact: %s
                occurredAt: %s
                """,
                safe(c.getStockCode()),
                safe(c.getTitle()),
                safe(c.getDescription()),
                safe(c.getAnalysis()),
                safe(c.getActualImpact()),
                safe(c.getOccurredAt()));
    }

    private HistoricalCase documentToCase(Document doc) {
        HistoricalCase c = new HistoricalCase();
        c.setId(doc.getId());
        Object stock = doc.getMetadata().get("stockCode");
        Object title = doc.getMetadata().get("title");
        Object occurredAt = doc.getMetadata().get("occurredAt");

        c.setStockCode(stock == null ? "" : String.valueOf(stock));
        c.setTitle(title == null ? "" : String.valueOf(title));
        c.setOccurredAt(occurredAt == null ? "" : String.valueOf(occurredAt));

        String text = doc.getText() == null ? "" : doc.getText();
        c.setDescription(extractField(text, "description"));
        c.setAnalysis(extractField(text, "analysis"));
        c.setActualImpact(extractField(text, "actualImpact"));
        return c;
    }

    private String extractField(String content, String fieldName) {
        String marker = fieldName + ": ";
        int start = content.indexOf(marker);
        if (start < 0) {
            return "";
        }
        start += marker.length();
        int end = content.indexOf("\n", start);
        if (end < 0) {
            end = content.length();
        }
        return content.substring(start, end).trim();
    }

    private LocalDateTime parseDateTime(String dateTimeStr) {
        if (dateTimeStr == null || dateTimeStr.isBlank()) {
            return LocalDateTime.now().minusDays(30);
        }

        try {
            return LocalDateTime.parse(dateTimeStr, DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        } catch (Exception ignored) {
        }
        try {
            return LocalDateTime.parse(dateTimeStr, DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        } catch (Exception ignored) {
        }
        try {
            return LocalDateTime.parse(dateTimeStr + " 00:00:00", DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        } catch (Exception ignored) {
        }
        return LocalDateTime.now().minusDays(30);
    }

    private String safe(String value) {
        return value == null ? "" : value;
    }

    private String arrayToString(float[] array) {
        if (array == null || array.length == 0) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        int n = Math.min(array.length, 20);
        for (int i = 0; i < n; i++) {
            if (i > 0) {
                sb.append(',');
            }
            sb.append(String.format("%.4f", array[i]));
        }
        return sb.toString();
    }

    private static class ScoredCase {
        HistoricalCase historicalCase;
        double score;

        ScoredCase(HistoricalCase historicalCase, double score) {
            this.historicalCase = historicalCase;
            this.score = score;
        }
    }
}
