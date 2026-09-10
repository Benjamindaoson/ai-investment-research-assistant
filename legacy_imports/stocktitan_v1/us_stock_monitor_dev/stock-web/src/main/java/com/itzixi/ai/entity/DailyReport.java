package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;
import java.util.List;

/**
 * AI生成的每日市场报告
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DailyReport {
    /**
     * 报告日期
     */
    private LocalDate reportDate;

    /**
     * 市场概览
     */
    private String marketOverview;

    /**
     * 重大事件TOP5
     */
    private List<TopEvent> topEvents;

    /**
     * 行业热点
     */
    private List<SectorHotspot> sectorHotspots;

    /**
     * 风险提示
     */
    private List<String> riskAlerts;

    /**
     * 明日关注
     */
    private List<String> tomorrowFocus;

    /**
     * 市场情绪指数
     */
    private MarketSentiment marketSentiment;

    /**
     * 生成时间
     */
    private String generatedAt;

    /**
     * 重大事件
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TopEvent {
        private String stockCode;
        private String title;
        private String summary;
        private Integer impactLevel;
        private String sentiment;
    }

    /**
     * 行业热点
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SectorHotspot {
        private String sector;
        private String description;
        private List<String> relatedStocks;
        private String trend;
    }
}
