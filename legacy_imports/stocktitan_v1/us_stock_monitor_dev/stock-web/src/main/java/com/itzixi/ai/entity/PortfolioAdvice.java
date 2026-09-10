package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

/**
 * 投资组合优化建议
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PortfolioAdvice {
    /**
     * 是否需要调仓
     */
    private Boolean needRebalance;

    /**
     * 建议买入
     */
    private List<TradeRecommendation> buyRecommendations;

    /**
     * 建议卖出
     */
    private List<TradeRecommendation> sellRecommendations;

    /**
     * 仓位配置建议
     */
    private List<PositionAllocation> positionAllocations;

    /**
     * 风险对冲建议
     */
    private List<String> hedgingAdvice;

    /**
     * 整体风险评估
     */
    private String overallRisk;

    /**
     * 预期收益率
     */
    private BigDecimal expectedReturn;

    /**
     * AI分析理由
     */
    private String reasoning;

    /**
     * 交易建议
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TradeRecommendation {
        private String stockCode;
        private String action; // BUY/SELL
        private BigDecimal suggestedPrice;
        private Integer suggestedQuantity;
        private String reason;
        private String urgency; // 低/中/高
    }

    /**
     * 仓位配置
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PositionAllocation {
        private String stockCode;
        private BigDecimal currentPercentage;
        private BigDecimal targetPercentage;
        private String reason;
    }
}
