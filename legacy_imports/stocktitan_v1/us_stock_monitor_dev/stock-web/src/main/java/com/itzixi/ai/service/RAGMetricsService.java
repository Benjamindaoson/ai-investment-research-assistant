package com.itzixi.ai.service;

import com.itzixi.ai.entity.HistoricalCase;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

/**
 * RAG监控指标服务
 * 记录和分析RAG系统的性能指标
 *
 * @author 风间影月
 * @version 3.7 - Metrics
 */
@Slf4j
@Service
public class RAGMetricsService {

    // 存储最近1000次检索记录
    private final List<SearchMetric> searchHistory = new ArrayList<>();
    private final int MAX_HISTORY_SIZE = 1000;

    /**
     * 记录一次检索
     */
    public void recordSearch(SearchMetric metric) {
        synchronized (searchHistory) {
            searchHistory.add(metric);
            // 保持最近1000条记录
            if (searchHistory.size() > MAX_HISTORY_SIZE) {
                searchHistory.remove(0);
            }
        }
        log.debug("记录检索指标: query={}, recallCount={}, latency={}ms",
                metric.getQuery(), metric.getRecallCount(), metric.getLatencyMs());
    }

    /**
     * 生成指标报告
     */
    public MetricsReport generateReport() {
        synchronized (searchHistory) {
            if (searchHistory.isEmpty()) {
                return new MetricsReport();
            }

            MetricsReport report = new MetricsReport();

            // 总检索次数
            report.setTotalSearches(searchHistory.size());

            // 平均召回数量
            double avgRecallCount = searchHistory.stream()
                    .mapToInt(SearchMetric::getRecallCount)
                    .average()
                    .orElse(0.0);
            report.setAvgRecallCount(avgRecallCount);

            // 平均质量分数
            double avgQualityScore = searchHistory.stream()
                    .filter(m -> m.getAvgQualityScore() > 0)
                    .mapToDouble(SearchMetric::getAvgQualityScore)
                    .average()
                    .orElse(0.0);
            report.setAvgQualityScore(avgQualityScore);

            // 平均响应时间
            double avgLatency = searchHistory.stream()
                    .mapToLong(SearchMetric::getLatencyMs)
                    .average()
                    .orElse(0.0);
            report.setAvgLatencyMs(avgLatency);

            // P95响应时间
            List<Long> sortedLatencies = searchHistory.stream()
                    .map(SearchMetric::getLatencyMs)
                    .sorted()
                    .collect(Collectors.toList());
            int p95Index = (int) (sortedLatencies.size() * 0.95);
            report.setP95LatencyMs(sortedLatencies.get(Math.min(p95Index, sortedLatencies.size() - 1)));

            // 用户满意度
            long satisfiedCount = searchHistory.stream()
                    .filter(m -> m.getUserFeedback() != null && m.getUserFeedback().equals("satisfied"))
                    .count();
            report.setUserSatisfactionRate(
                    searchHistory.size() > 0 ? (double) satisfiedCount / searchHistory.size() : 0.0
            );

            // 最近24小时检索量
            LocalDateTime oneDayAgo = LocalDateTime.now().minusDays(1);
            long recentSearches = searchHistory.stream()
                    .filter(m -> m.getTimestamp().isAfter(oneDayAgo))
                    .count();
            report.setRecentSearches24h(recentSearches);

            return report;
        }
    }

    /**
     * 获取最近的检索记录
     */
    public List<SearchMetric> getRecentSearches(int limit) {
        synchronized (searchHistory) {
            int size = searchHistory.size();
            int fromIndex = Math.max(0, size - limit);
            return new ArrayList<>(searchHistory.subList(fromIndex, size));
        }
    }

    /**
     * 清空历史记录
     */
    public void clearHistory() {
        synchronized (searchHistory) {
            searchHistory.clear();
        }
        log.info("已清空检索历史记录");
    }

    /**
     * 检索指标
     */
    @Data
    public static class SearchMetric {
        private String query;
        private String stockCode;
        private int recallCount;
        private double avgQualityScore;
        private long latencyMs;
        private String userFeedback;
        private LocalDateTime timestamp;
        private String searchType; // "vector", "multiPath", "timeDecay"

        public SearchMetric() {
            this.timestamp = LocalDateTime.now();
        }
    }

    /**
     * 指标报告
     */
    @Data
    public static class MetricsReport {
        private long totalSearches;
        private double avgRecallCount;
        private double avgQualityScore;
        private double avgLatencyMs;
        private long p95LatencyMs;
        private double userSatisfactionRate;
        private long recentSearches24h;
        private LocalDateTime generatedAt;

        public MetricsReport() {
            this.generatedAt = LocalDateTime.now();
        }

        @Override
        public String toString() {
            return String.format("""
                    RAG指标报告 (生成时间: %s)
                    ========================================
                    总检索次数: %d
                    平均召回数量: %.2f
                    平均质量分数: %.2f
                    平均响应时间: %.2f ms
                    P95响应时间: %d ms
                    用户满意度: %.2f%%
                    最近24小时检索: %d
                    """,
                    generatedAt,
                    totalSearches,
                    avgRecallCount,
                    avgQualityScore,
                    avgLatencyMs,
                    p95LatencyMs,
                    userSatisfactionRate * 100,
                    recentSearches24h
            );
        }
    }
}
