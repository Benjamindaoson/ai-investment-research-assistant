package com.itzixi.ai.service;

import com.itzixi.ai.entity.HistoricalCase;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 动态案例库管理服务
 * 自动清理低质量案例、归档旧案例、合并相似案例
 *
 * @author 风间影月
 * @version 3.5 - Dynamic Management
 */
@Slf4j
@Service
public class CaseLibraryManager {

    @Resource
    private VectorStoreService vectorStoreService;

    @Resource
    private CaseQualityService caseQualityService;

    /**
     * 定期清理案例库（每天凌晨3点执行）
     */
    @Scheduled(cron = "0 0 3 * * ?")
    public void scheduledCleanup() {
        log.info("开始定期清理案例库");
        cleanupCaseLibrary();
        log.info("案例库清理完成");
    }

    /**
     * 清理案例库
     * 1. 删除低质量案例
     * 2. 归档过期案例
     * 3. 合并重复案例
     */
    public void cleanupCaseLibrary() {
        try {
            // 获取所有案例
            List<HistoricalCase> allCases = getAllCases();
            log.info("案例库清理前: 共{}个案例", allCases.size());

            // 1. 删除低质量案例（质量分<30）
            List<HistoricalCase> qualityCases = removeLowQualityCases(allCases, 30.0);
            log.info("删除低质量案例后: 剩余{}个案例", qualityCases.size());

            // 2. 归档过期案例（3年以上）
            List<HistoricalCase> activeCases = archiveOldCases(qualityCases, 3 * 365);
            log.info("归档过期案例后: 剩余{}个案例", activeCases.size());

            // 3. 合并相似案例
            List<HistoricalCase> mergedCases = mergeSimilarCases(activeCases, 0.95);
            log.info("合并相似案例后: 剩余{}个案例", mergedCases.size());

            // 重建向量库
            rebuildVectorStore(mergedCases);

            log.info("案例库清理完成: 从{}个减少到{}个案例",
                    allCases.size(), mergedCases.size());

        } catch (Exception e) {
            log.error("案例库清理失败", e);
        }
    }

    /**
     * 删除低质量案例
     */
    private List<HistoricalCase> removeLowQualityCases(List<HistoricalCase> cases, double minScore) {
        return cases.stream()
                .filter(c -> {
                    double score = caseQualityService.calculateQualityScore(c);
                    if (score < minScore) {
                        log.debug("删除低质量案例: id={}, score={}", c.getId(), score);
                        return false;
                    }
                    return true;
                })
                .collect(Collectors.toList());
    }

    /**
     * 归档过期案例
     */
    private List<HistoricalCase> archiveOldCases(List<HistoricalCase> cases, int maxAgeDays) {
        LocalDateTime cutoffDate = LocalDateTime.now().minusDays(maxAgeDays);

        return cases.stream()
                .filter(c -> {
                    try {
                        LocalDateTime occurredAt = parseDateTime(c.getOccurredAt());
                        if (occurredAt.isBefore(cutoffDate)) {
                            log.debug("归档过期案例: id={}, occurredAt={}", c.getId(), c.getOccurredAt());
                            return false;
                        }
                        return true;
                    } catch (Exception e) {
                        return true; // 解析失败的保留
                    }
                })
                .collect(Collectors.toList());
    }

    /**
     * 合并相似案例
     * 如果两个案例的相似度超过阈值，保留质量更高的
     */
    private List<HistoricalCase> mergeSimilarCases(List<HistoricalCase> cases, double similarityThreshold) {
        List<HistoricalCase> result = new ArrayList<>();
        List<String> processedIds = new ArrayList<>();

        for (HistoricalCase c1 : cases) {
            if (processedIds.contains(c1.getId())) {
                continue;
            }

            // 查找相似案例
            List<HistoricalCase> similarCases = new ArrayList<>();
            similarCases.add(c1);

            for (HistoricalCase c2 : cases) {
                if (c1.getId().equals(c2.getId()) || processedIds.contains(c2.getId())) {
                    continue;
                }

                // 检查相似度
                if (isSimilar(c1, c2, similarityThreshold)) {
                    similarCases.add(c2);
                    processedIds.add(c2.getId());
                }
            }

            // 如果有相似案例，选择质量最高的
            if (similarCases.size() > 1) {
                HistoricalCase best = similarCases.stream()
                        .max((a, b) -> Double.compare(
                                caseQualityService.calculateQualityScore(a),
                                caseQualityService.calculateQualityScore(b)
                        ))
                        .orElse(c1);

                result.add(best);
                processedIds.add(c1.getId());

                log.debug("合并{}个相似案例，保留: {}", similarCases.size(), best.getId());
            } else {
                result.add(c1);
                processedIds.add(c1.getId());
            }
        }

        return result;
    }

    /**
     * 判断两个案例是否相似
     */
    private boolean isSimilar(HistoricalCase c1, HistoricalCase c2, double threshold) {
        // 1. 股票代码必须相同
        if (!c1.getStockCode().equals(c2.getStockCode())) {
            return false;
        }

        // 2. 标题相似度
        double titleSimilarity = calculateTextSimilarity(c1.getTitle(), c2.getTitle());
        if (titleSimilarity < threshold) {
            return false;
        }

        // 3. 时间接近（7天内）
        try {
            LocalDateTime time1 = parseDateTime(c1.getOccurredAt());
            LocalDateTime time2 = parseDateTime(c2.getOccurredAt());
            long daysDiff = Math.abs(ChronoUnit.DAYS.between(time1, time2));

            return daysDiff <= 7;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 计算文本相似度（简单的Jaccard相似度）
     */
    private double calculateTextSimilarity(String text1, String text2) {
        if (text1 == null || text2 == null) {
            return 0.0;
        }

        String[] words1 = text1.toLowerCase().split("\\s+");
        String[] words2 = text2.toLowerCase().split("\\s+");

        java.util.Set<String> set1 = new java.util.HashSet<>(java.util.Arrays.asList(words1));
        java.util.Set<String> set2 = new java.util.HashSet<>(java.util.Arrays.asList(words2));

        // 交集
        java.util.Set<String> intersection = new java.util.HashSet<>(set1);
        intersection.retainAll(set2);

        // 并集
        java.util.Set<String> union = new java.util.HashSet<>(set1);
        union.addAll(set2);

        if (union.isEmpty()) {
            return 0.0;
        }

        return (double) intersection.size() / union.size();
    }

    /**
     * 重建向量库
     */
    private void rebuildVectorStore(List<HistoricalCase> cases) {
        // 清空现有向量库并重新添加
        vectorStoreService.addCases(cases);
        vectorStoreService.saveVectorStore();
    }

    /**
     * 获取所有案例（从向量库）
     */
    private List<HistoricalCase> getAllCases() {
        // 使用一个通用查询获取所有案例
        return vectorStoreService.similaritySearch("", 10000);
    }

    /**
     * 解析日期时间
     */
    private LocalDateTime parseDateTime(String dateTimeStr) {
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            return LocalDateTime.parse(dateTimeStr, formatter);
        } catch (Exception e) {
            return LocalDateTime.now();
        }
    }

    /**
     * 获取案例库统计信息
     */
    public Map<String, Object> getLibraryStats() {
        List<HistoricalCase> allCases = getAllCases();

        long totalCases = allCases.size();
        double avgQuality = allCases.stream()
                .mapToDouble(c -> caseQualityService.calculateQualityScore(c))
                .average()
                .orElse(0.0);

        long highQualityCases = allCases.stream()
                .filter(c -> caseQualityService.calculateQualityScore(c) >= 70)
                .count();

        return Map.of(
                "totalCases", totalCases,
                "avgQuality", avgQuality,
                "highQualityCases", highQualityCases,
                "highQualityRate", totalCases > 0 ? (double) highQualityCases / totalCases : 0.0
        );
    }
}
