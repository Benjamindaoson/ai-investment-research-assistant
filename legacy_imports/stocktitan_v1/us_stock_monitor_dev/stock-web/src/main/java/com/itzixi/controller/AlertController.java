package com.itzixi.controller;

import com.itzixi.alert.AlertRuleEngine;
import com.itzixi.alert.rule.AlertRule;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.common.response.Result;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.StockService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 预警控制器
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@RestController
@RequestMapping("/api/alert")
public class AlertController {

    @Resource
    private AlertRuleEngine alertRuleEngine;

    @Resource
    private StockService stockService;

    /**
     * 获取所有预警规则
     */
    @GetMapping("/rules")
    public Result<List<AlertRule>> getAllRules() {
        log.info("查询所有预警规则");
        List<AlertRule> rules = alertRuleEngine.getAllRules();
        return Result.success(rules);
    }

    /**
     * 评估单个股票
     */
    @PostMapping("/evaluate")
    @Monitor(value = "评估股票预警", slowThreshold = 2000)
    public Result<List<AlertRuleEngine.AlertResult>> evaluateStock(@RequestBody USStockRss stock) {
        log.info("评估股票预警: {}", stock.getStockCode());
        List<AlertRuleEngine.AlertResult> results = alertRuleEngine.evaluate(stock);
        return Result.success(results);
    }

    /**
     * 评估指定股票代码
     */
    @GetMapping("/evaluate/{stockCode}")
    @Monitor(value = "评估股票代码预警", slowThreshold = 2000)
    public Result<List<AlertRuleEngine.AlertResult>> evaluateByCode(@PathVariable String stockCode) {
        log.info("评估股票代码预警: {}", stockCode);

        // 查询最近的股票数据
        List<USStockRss> stocks = stockService.queryStock(stockCode);
        if (stocks.isEmpty()) {
            return Result.error("未找到股票数据");
        }

        List<AlertRuleEngine.AlertResult> results = alertRuleEngine.evaluateBatch(stocks);
        return Result.success(results);
    }
}
