package com.itzixi.controller;

import com.itzixi.common.annotation.Monitor;
import com.itzixi.common.response.Result;
import com.itzixi.entity.StockCounts;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.StatisticsService;
import com.itzixi.vo.HotStockVO;
import com.itzixi.vo.StockTrendVO;
import com.itzixi.vo.TagDistributionVO;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 数据统计分析控制器
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@RestController
@RequestMapping("/api/statistics")
public class StatisticsController {

    @Resource
    private StatisticsService statisticsService;

    /**
     * 获取热门股票TOP10
     */
    @GetMapping("/hot-stocks")
    @Monitor(value = "查询热门股票", slowThreshold = 2000)
    public Result<List<HotStockVO>> getHotStocks(
            @RequestParam(defaultValue = "7") Integer days,
            @RequestParam(defaultValue = "10") Integer limit) {
        log.info("查询热门股票: days={}, limit={}", days, limit);
        List<HotStockVO> hotStocks = statisticsService.getHotStocks(days, limit);
        return Result.success(hotStocks);
    }

    /**
     * 获取股票异动趋势
     */
    @GetMapping("/stock-trend/{stockCode}")
    @Monitor(value = "查询股票趋势", slowThreshold = 2000)
    public Result<StockTrendVO> getStockTrend(
            @PathVariable String stockCode,
            @RequestParam(defaultValue = "30") Integer days) {
        log.info("查询股票趋势: stockCode={}, days={}", stockCode, days);
        StockTrendVO trend = statisticsService.getStockTrend(stockCode, days);
        return Result.success(trend);
    }

    /**
     * 获取标签分布统计
     */
    @GetMapping("/tag-distribution")
    @Monitor(value = "查询标签分布", slowThreshold = 2000)
    public Result<List<TagDistributionVO>> getTagDistribution(
            @RequestParam(defaultValue = "7") Integer days) {
        log.info("查询标签分布: days={}", days);
        List<TagDistributionVO> distribution = statisticsService.getTagDistribution(days);
        return Result.success(distribution);
    }

    /**
     * 获取时段分析（按小时统计）
     */
    @GetMapping("/hourly-analysis")
    @Monitor(value = "查询时段分析", slowThreshold = 2000)
    public Result<List<Integer>> getHourlyAnalysis(
            @RequestParam(defaultValue = "7") Integer days) {
        log.info("查询时段分析: days={}", days);
        List<Integer> hourlyData = statisticsService.getHourlyAnalysis(days);
        return Result.success(hourlyData);
    }

    /**
     * 获取异动频繁的股票
     */
    @GetMapping("/frequent-stocks")
    @Monitor(value = "查询异动频繁股票", slowThreshold = 2000)
    public Result<List<StockCounts>> getFrequentStocks(
            @RequestParam Integer targetCounts,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime startDate,
            @RequestParam @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss") LocalDateTime endDate) {
        log.info("查询异动频繁股票: targetCounts={}, startDate={}, endDate={}", targetCounts, startDate, endDate);
        List<StockCounts> stocks = statisticsService.getFrequentStocks(targetCounts, startDate, endDate);
        return Result.success(stocks);
    }

    /**
     * 获取系统统计概览
     */
    @GetMapping("/overview")
    @Monitor(value = "查询系统概览", slowThreshold = 1000)
    public Result<java.util.Map<String, Object>> getOverview() {
        log.info("查询系统统计概览");
        java.util.Map<String, Object> overview = statisticsService.getSystemOverview();
        return Result.success(overview);
    }
}
