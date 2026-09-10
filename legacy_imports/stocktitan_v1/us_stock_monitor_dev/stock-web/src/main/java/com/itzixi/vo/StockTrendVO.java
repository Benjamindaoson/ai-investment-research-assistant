package com.itzixi.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 股票趋势VO
 *
 * @author 风间影月
 * @version 2.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class StockTrendVO {
    private String stockCode;
    private List<String> dates;
    private List<Integer> counts;
    private Integer totalCounts;
    private Double avgCounts;
}
