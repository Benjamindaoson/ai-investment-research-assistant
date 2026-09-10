package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 历史案例
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class HistoricalCase {
    /**
     * 案例ID
     */
    private String id;

    /**
     * 股票代码
     */
    private String stockCode;

    /**
     * 事件标题
     */
    private String title;

    /**
     * 事件描述
     */
    private String description;

    /**
     * AI分析结果
     */
    private String analysis;

    /**
     * 实际影响
     */
    private String actualImpact;

    /**
     * 发生时间
     */
    private String occurredAt;

    /**
     * 相似度分数
     */
    private Double similarityScore;
}
