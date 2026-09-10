package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * AI提取的股票实体信息
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class StockEntity {
    /**
     * 股票代码
     */
    private String stockCode;

    /**
     * 公司名称
     */
    private String companyName;

    /**
     * 事件类型（财报/产品发布/并购/诉讼/人事变动等）
     */
    private String eventType;

    /**
     * 关键数字（涨跌幅/金额等）
     */
    private List<KeyMetric> keyMetrics;

    /**
     * 情感倾向（正面/中性/负面）
     */
    private String sentiment;

    /**
     * 情感分数（-1.0到1.0）
     */
    private Double sentimentScore;

    /**
     * 影响程度（1-10分）
     */
    private Integer impactLevel;

    /**
     * 提取的关键词
     */
    private List<String> keywords;

    /**
     * AI生成的标签
     */
    private List<String> tags;

    /**
     * 关键数字
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class KeyMetric {
        private String name;
        private String value;
        private String unit;
    }
}
