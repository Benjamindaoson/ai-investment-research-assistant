package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 市场情绪分析
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MarketSentiment {
    /**
     * 情绪指数（-100到+100）
     */
    private Integer sentimentIndex;

    /**
     * 恐慌程度（低/中/高）
     */
    private String panicLevel;

    /**
     * 主导情绪（贪婪/恐惧/观望）
     */
    private String dominantEmotion;

    /**
     * 情绪变化趋势（上升/下降/稳定）
     */
    private String trend;

    /**
     * 关键驱动因素
     */
    private List<String> keyDrivers;

    /**
     * 正面新闻数量
     */
    private Integer positiveCount;

    /**
     * 负面新闻数量
     */
    private Integer negativeCount;

    /**
     * 中性新闻数量
     */
    private Integer neutralCount;

    /**
     * 分析时间范围（小时）
     */
    private Integer timeRangeHours;

    /**
     * AI分析摘要
     */
    private String summary;
}
