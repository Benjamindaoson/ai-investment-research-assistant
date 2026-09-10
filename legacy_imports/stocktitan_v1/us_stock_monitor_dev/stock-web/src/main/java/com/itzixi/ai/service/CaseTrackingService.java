package com.itzixi.ai.service;

import com.itzixi.ai.entity.HistoricalCase;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 实时案例追踪服务
 * 追踪历史案例的实际影响，自动更新案例，验证预测准确性
 *
 * @author 风间影月
 * @version 3.6 - Real-time Tracking
 */
@Slf4j
@Service
public class CaseTrackingService {

    @Resource
    private VectorStoreService vectorStoreService;

    @Resource
    private com.itzixi.service.StockService stockService;

    // 追踪中的案例：caseId -> 创建时间
    private final Map<String, LocalDateTime> trackingCases = new ConcurrentHashMap<>();

    /**
     * 开始追踪案例
     * 案例创建后，自动追踪7天
     */
    public void startTracking(HistoricalCase historicalCase) {
        trackingCases.put(historicalCase.getId(), LocalDateTime.now());
        log.info("开始追踪案例: id={}, stockCode={}",
                historicalCase.getId(), historicalCase.getStockCode());
    }

    /**
     * 定期更新追踪中的案例（每小时执行一次）
     */
    @Scheduled(cron = "0 0 * * * ?")
    public void scheduledUpdate() {
        log.info("开始定期更新追踪案例，当前追踪{}个案例", trackingCases.size());
        updateTrackingCases();
    }

    /**
     * 更新所有追踪中的案例
     */
    public void updateTrackingCases() {
        List<String> completedCases = new java.util.ArrayList<>();

        for (Map.Entry<String, LocalDateTime> entry : trackingCases.entrySet()) {
            String caseId = entry.getKey();
            LocalDateTime startTime = entry.getValue();

            // 追踪7天后停止
            long daysSinceStart = ChronoUnit.DAYS.between(startTime, LocalDateTime.now());
            if (daysSinceStart > 7) {
                completedCases.add(caseId);
                log.info("案例追踪完成: id={}", caseId);
                continue;
            }

            // 更新案例
            try {
                updateCase(caseId);
            } catch (Exception e) {
                log.error("更新案例失败: id={}", caseId, e);
            }
        }

        // 移除已完成的案例
        completedCases.forEach(trackingCases::remove);
    }

    /**
     * 更新单个案例
     */
    private void updateCase(String caseId) {
        // 获取案例
        List<HistoricalCase> cases = vectorStoreService.similaritySearch(caseId, 1);
        if (cases.isEmpty()) {
            log.warn("案例不存在: id={}", caseId);
            return;
        }

        HistoricalCase historicalCase = cases.get(0);

        // 获取该股票的最新新闻
        String stockCode = historicalCase.getStockCode();
        LocalDateTime occurredAt = parseDateTime(historicalCase.getOccurredAt());
        List<USStockRss> recentNews = stockService.getStockRssByCodeSince(
                stockCode,
                occurredAt
        );

        // 分析实际影响
        String actualImpact = analyzeActualImpact(historicalCase, recentNews);

        // 如果有新的实际影响，更新案例
        if (actualImpact != null && !actualImpact.isEmpty()) {
            historicalCase.setActualImpact(actualImpact);
            vectorStoreService.addCase(historicalCase);
            log.info("案例已更新: id={}, actualImpact={}", caseId, actualImpact);
        }
    }

    /**
     * 分析实际影响
     */
    private String analyzeActualImpact(HistoricalCase historicalCase, List<USStockRss> recentNews) {
        if (recentNews.isEmpty()) {
            return null;
        }

        StringBuilder impact = new StringBuilder();
        impact.append("后续影响：\n");

        // 统计积极和消极新闻
        long positiveCount = recentNews.stream()
                .filter(news -> containsPositiveKeywords(news))
                .count();

        long negativeCount = recentNews.stream()
                .filter(news -> containsNegativeKeywords(news))
                .count();

        // 判断整体影响
        if (positiveCount > negativeCount) {
            impact.append("- 整体影响偏积极，后续出现").append(positiveCount).append("条利好新闻\n");
        } else if (negativeCount > positiveCount) {
            impact.append("- 整体影响偏消极，后续出现").append(negativeCount).append("条利空新闻\n");
        } else {
            impact.append("- 整体影响中性，市场反应平稳\n");
        }

        // 添加关键后续事件
        List<USStockRss> keyEvents = recentNews.stream()
                .filter(this::isKeyEvent)
                .limit(3)
                .toList();

        if (!keyEvents.isEmpty()) {
            impact.append("- 关键后续事件：\n");
            for (USStockRss event : keyEvents) {
                String title = event.getTitleZh() != null ? event.getTitleZh() : event.getTitle();
                impact.append("  * ").append(title).append("\n");
            }
        }

        return impact.toString();
    }

    /**
     * 检查是否包含积极关键词
     */
    private boolean containsPositiveKeywords(USStockRss news) {
        String text = (news.getTitleZh() != null ? news.getTitleZh() : news.getTitle()).toLowerCase();
        String[] keywords = {
            "surge", "soar", "jump", "gain", "rise", "up", "beat", "exceed", "approval",
            "上涨", "飙升", "增长", "突破", "利好", "批准", "超预期"
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
    private boolean containsNegativeKeywords(USStockRss news) {
        String text = (news.getTitleZh() != null ? news.getTitleZh() : news.getTitle()).toLowerCase();
        String[] keywords = {
            "plunge", "drop", "fall", "decline", "down", "miss", "loss", "warning", "concern",
            "下跌", "暴跌", "下滑", "亏损", "警告", "担忧", "利空"
        };

        for (String keyword : keywords) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 判断是否为关键事件
     */
    private boolean isKeyEvent(USStockRss news) {
        String text = (news.getTitleZh() != null ? news.getTitleZh() : news.getTitle()).toLowerCase();
        String[] keyEventKeywords = {
            "earnings", "财报", "merger", "acquisition", "并购",
            "fda", "approval", "批准", "lawsuit", "诉讼",
            "bankruptcy", "破产", "dividend", "分红"
        };

        for (String keyword : keyEventKeywords) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 解析日期时间
     */
    private LocalDateTime parseDateTime(String dateTimeStr) {
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
            return LocalDateTime.parse(dateTimeStr, formatter);
        } catch (Exception e) {
            return LocalDateTime.now().minusDays(7);
        }
    }

    /**
     * 验证预测准确性
     * 比较AI分析和实际影响的一致性
     */
    public double validatePrediction(HistoricalCase historicalCase) {
        if (historicalCase.getActualImpact() == null || historicalCase.getActualImpact().isEmpty()) {
            return 0.5; // 无实际影响数据，返回中性分数
        }

        String analysis = historicalCase.getAnalysis() != null ?
                historicalCase.getAnalysis().toLowerCase() : "";
        String actualImpact = historicalCase.getActualImpact().toLowerCase();

        // 检查预测和实际的一致性
        boolean predictedPositive = analysis.contains("利好") || analysis.contains("上涨") ||
                analysis.contains("positive") || analysis.contains("rise");
        boolean actualPositive = actualImpact.contains("利好") || actualImpact.contains("上涨") ||
                actualImpact.contains("积极") || actualImpact.contains("positive");

        boolean predictedNegative = analysis.contains("利空") || analysis.contains("下跌") ||
                analysis.contains("negative") || analysis.contains("fall");
        boolean actualNegative = actualImpact.contains("利空") || actualImpact.contains("下跌") ||
                actualImpact.contains("消极") || actualImpact.contains("negative");

        // 计算准确性分数
        if ((predictedPositive && actualPositive) || (predictedNegative && actualNegative)) {
            return 1.0; // 预测准确
        } else if ((predictedPositive && actualNegative) || (predictedNegative && actualPositive)) {
            return 0.0; // 预测错误
        } else {
            return 0.5; // 中性或不确定
        }
    }

    /**
     * 获取追踪统计信息
     */
    public Map<String, Object> getTrackingStats() {
        return Map.of(
                "trackingCases", trackingCases.size(),
                "trackingCaseIds", trackingCases.keySet()
        );
    }
}
