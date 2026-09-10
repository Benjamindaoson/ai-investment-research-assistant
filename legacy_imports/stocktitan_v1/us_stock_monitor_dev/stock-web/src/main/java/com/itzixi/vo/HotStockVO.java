package com.itzixi.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 热门股票VO
 *
 * @author 风间影月
 * @version 2.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class HotStockVO {
    private String stockCode;
    private String stockName;
    private Integer occurCounts;
    private String latestTitle;
    private String latestTitleZh;
    private String latestTime;
}
