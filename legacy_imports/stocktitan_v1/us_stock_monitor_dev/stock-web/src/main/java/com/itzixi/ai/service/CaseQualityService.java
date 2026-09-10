package com.itzixi.ai.service;

import com.itzixi.ai.entity.HistoricalCase;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

/**
 * 案例质量评分服务
 * 评估历史案例的完整性、准确性和影响程度
 *
 * @author 风间影月
 * @version 3.4 - Quality Scoring
 */
@Slf4j
@Service
public class CaseQualityService {

    /**
     * 计算案例的综合质量分数（0-100）
     */
    public double calculateQualityScore(HistoricalCase historicalCase) {
        try {
            // 1. 完整性评分（40%）
            double completenessScore = calculateCompletenessScore(historicalCase);

            // 2. 准确性评分（30%）
            double accuracyScore = calculateAccuracyScore(historicalCase);

            // 3. 影响程度评分（30%）
            double impactScore = calculateImpactScore(historicalCase);

            // 综合分数
            double totalScore = completenessScore * 0.4 + accuracyScore * 0.3 + impactScore * 0.3;

            log.debug("案例质量评分: id={}, 完整性={}, 准确性={}, 影响={}, 总分={}",
                    historicalCase.getId(), completenessScore, accuracyScore, impactScore, totalScore);

            return totalScore;
        } catch (Exception e) {
            log.error("计算质量分数失败: {}", historicalCase.getId(), e);
            return 50.0; // 默认中等分数
        }
    }

    /**
     * 完整性评分（0-100）
     * 评估案例信息的完整程度
     */
    private double calculateCompletenessScore(HistoricalCase c) {
        double score = 0.0;

        // 必填字段（60分）
        if (c.getStockCode() != null && !c.getStockCode().isEmpty()) score += 10;
        if (c.getTitle() != null && !c.getTitle().isEmpty()) score += 15;
        if (c.getAnalysis() != null && !c.getAnalysis().isEmpty()) score += 20;
        if (c.getOccurredAt() != null && !c.getOccurredAt().isEmpty()) score += 15;

        // 可选但重要的字段（40分）
        if (c.getDescription() != null && !c.getDescription().isEmpty()) score += 20;
        if (c.getActualImpact() != null && !c.getActualImpact().isEmpty()) score += 20;

        return score;
    }

    /**
     * 准确性评分（0-100）
     * 评估分析的准确性和实际影响的一致性
     */
    private double calculateAccuracyScore(HistoricalCase c) {
        double score = 50.0; // 基础分

        // 如果有实际影响记录，说明案例经过验证
        if (c.getActualImpact() != null && !c.getActualImpact().isEmpty()) {
            score += 30;

            // 检查分析和实际影响的一致性
            String analysis = c.getAnalysis() != null ? c.getAnalysis().toLowerCase() : "";
            String actualImpact = c.getActualImpact().toLowerCase();

            // 积极预测 vs 实际结果
            boolean predictedPositive = containsPositiveKeywords(analysis);
            boolean actualPositive = containsPositiveKeywords(actualImpact);

            // 消极预测 vs 实际结果
            boolean predictedNegative = containsNegativeKeywords(analysis);
            boolean actualNegative = containsNegativeKeywords(actualImpact);

            // 预测准确加分
            if ((predictedPositive && actualPositive) || (predictedNegative && actualNegative)) {
                score += 20;
            }
        }

        return Math.min(score, 100.0);
    }

    /**
     * 影响程度评分（0-100）
     * 评估事件的重要性和影响力
     */
    private double calculateImpactScore(HistoricalCase c) {
        double score = 50.0; // 基础分

        String title = c.getTitle() != null ? c.getTitle().toLowerCase() : "";
        String analysis = c.getAnalysis() != null ? c.getAnalysis().toLowerCase() : "";
        String actualImpact = c.getActualImpact() != null ? c.getActualImpact().toLowerCase() : "";

        // 高影响事件类型（+20分）
        if (title.contains("earnings") || title.contains("财报")) score += 10;
        if (title.contains("merger") || title.contains("acquisition") || title.contains("并购")) score += 15;
        if (title.contains("fda") || title.contains("approval") || title.contains("批准")) score += 15;
        if (title.contains("bankruptcy") || title.contains("破产")) score += 20;

        // 影响程度关键词（+20分）
        if (actualImpact.contains("surge") || actualImpact.contains("暴涨") || actualImpact.contains("飙升")) score += 15;
        if (actualImpact.contains("plunge") || actualImpact.contains("暴跌") || actualImpact.contains("崩盘")) score += 15;
        if (actualImpact.contains("significant") || actualImpact.contains("重大") || actualImpact.contains("显著")) score += 10;

        // 分析深度（+10分）
        if (analysis.length() > 200) score += 5;
        if (analysis.length() > 500) score += 5;

        return Math.min(score, 100.0);
    }

    /**
     * 检查是否包含积极关键词
     */
    private boolean containsPositiveKeywords(String text) {
        String[] keywords = {
            "surge", "soar", "jump", "gain", "rise", "up", "beat", "exceed", "approval", "success",
            "上涨", "飙升", "增长", "突破", "利好", "批准", "超预期", "成功"
        };

        for (String keyword : keywords) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 检查是否包含消极关键词
     */
    private boolean containsNegativeKeywords(String text) {
        String[] keywords = {
            "plunge", "drop", "fall", "decline", "down", "miss", "loss", "warning", "concern", "fail",
            "下跌", "暴跌", "下滑", "亏损", "警告", "担忧", "利空", "失败"
        };

        for (String keyword : keywords) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 根据质量分数过滤案例
     * @param cases 案例列表
     * @param minScore 最低质量分数（0-100）
     * @return 过滤后的案例列表
     */
    public java.util.List<HistoricalCase> filterByQuality(
            java.util.List<HistoricalCase> cases, double minScore) {

        return cases.stream()
                .filter(c -> calculateQualityScore(c) >= minScore)
                .collect(java.util.stream.Collectors.toList());
    }

    /**
     * 为案例列表添加质量分数并排序
     */
    public java.util.List<HistoricalCase> sortByQuality(java.util.List<HistoricalCase> cases) {
        return cases.stream()
                .sorted((a, b) -> {
                    double scoreA = calculateQualityScore(a);
                    double scoreB = calculateQualityScore(b);
                    return Double.compare(scoreB, scoreA);
                })
                .collect(java.util.stream.Collectors.toList());
    }
}
