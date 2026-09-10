package com.itzixi.service;

import com.itzixi.entity.StockCounts;
import com.itzixi.vo.HotStockVO;
import com.itzixi.vo.StockTrendVO;
import com.itzixi.vo.TagDistributionVO;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

/**
 * 统计服务接口
 *
 * @author 风间影月
 * @version 2.0
 */
public interface StatisticsService {

    /**
     * 获取热门股票
     */
    List<HotStockVO> getHotStocks(Integer days, Integer limit);

    /**
     * 获取股票趋势
     */
    StockTrendVO getStockTrend(String stockCode, Integer days);

    /**
     * 获取标签分布
     */
    List<TagDistributionVO> getTagDistribution(Integer days);

    /**
     * 获取时段分析
     */
    List<Integer> getHourlyAnalysis(Integer days);

    /**
     * 获取异动频繁的股票
     */
    List<StockCounts> getFrequentStocks(Integer targetCounts, LocalDateTime startDate, LocalDateTime endDate);

    /**
     * 获取系统概览
     */
    Map<String, Object> getSystemOverview();
}
