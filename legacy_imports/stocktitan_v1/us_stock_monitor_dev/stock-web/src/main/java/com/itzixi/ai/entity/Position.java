package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * 持仓信息
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Position {
    /**
     * 股票代码
     */
    private String stockCode;

    /**
     * 持仓数量
     */
    private Integer quantity;

    /**
     * 成本价
     */
    private BigDecimal costPrice;

    /**
     * 当前价格
     */
    private BigDecimal currentPrice;

    /**
     * 盈亏金额
     */
    private BigDecimal profitLoss;

    /**
     * 盈亏比例
     */
    private BigDecimal profitLossPercentage;

    /**
     * 持仓占比
     */
    private BigDecimal positionPercentage;
}
