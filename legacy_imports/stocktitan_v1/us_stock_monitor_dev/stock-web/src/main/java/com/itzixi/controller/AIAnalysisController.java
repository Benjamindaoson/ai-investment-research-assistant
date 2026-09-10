package com.itzixi.controller;

import com.itzixi.ai.orchestrator.MultiAgentOrchestrator;
import com.itzixi.ai.service.AIStockAnalysisService;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.common.response.Result;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.StockService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/ai")
public class AIAnalysisController {

    @Resource
    private AIStockAnalysisService aiStockAnalysisService;

    @Resource
    private MultiAgentOrchestrator multiAgentOrchestrator;

    @Resource
    private StockService stockService;

    @PostMapping("/analyze/reason")
    @Monitor(value = "AI analyze reason", slowThreshold = 5000)
    public Result<String> analyzeReason(@RequestBody USStockRss stock) {
        String analysis = aiStockAnalysisService.analyzeMovementReason(stock);
        return Result.success(analysis);
    }

    @PostMapping("/analyze/risk")
    @Monitor(value = "AI assess risk", slowThreshold = 5000)
    public Result<AIStockAnalysisService.RiskAssessment> assessRisk(@RequestBody USStockRss stock) {
        AIStockAnalysisService.RiskAssessment assessment = aiStockAnalysisService.assessRisk(stock);
        return Result.success(assessment);
    }

    @GetMapping("/analyze/advice/{stockCode}")
    @Monitor(value = "AI generate advice", slowThreshold = 5000)
    public Result<String> generateAdvice(@PathVariable String stockCode) {
        List<USStockRss> stocks = stockService.queryStock(stockCode);
        if (stocks == null || stocks.isEmpty()) {
            return Result.error("no stock data");
        }
        String advice = aiStockAnalysisService.generateInvestmentAdvice(stocks.get(0), stocks);
        return Result.success(advice);
    }

    @GetMapping("/analyze/trend/{stockCode}")
    @Monitor(value = "AI predict trend", slowThreshold = 5000)
    public Result<AIStockAnalysisService.TrendPrediction> predictTrend(@PathVariable String stockCode) {
        List<USStockRss> stocks = stockService.queryStock(stockCode);
        if (stocks == null || stocks.isEmpty()) {
            return Result.error("no stock data");
        }
        AIStockAnalysisService.TrendPrediction prediction = aiStockAnalysisService.predictTrend(stockCode, stocks);
        return Result.success(prediction);
    }

    @PostMapping("/multi-agent/analyze")
    @Monitor(value = "multi-agent analyze", slowThreshold = 10000)
    public Result<MultiAgentOrchestrator.ComprehensiveReport> multiAgentAnalyze(@RequestBody USStockRss stock) {
        MultiAgentOrchestrator.ComprehensiveReport report = multiAgentOrchestrator.analyze(stock);
        return Result.success(report);
    }

    @PostMapping("/multi-agent/batch-analyze")
    @Monitor(value = "multi-agent batch", slowThreshold = 30000)
    public Result<List<MultiAgentOrchestrator.ComprehensiveReport>> batchAnalyze(@RequestBody List<USStockRss> stocks) {
        List<MultiAgentOrchestrator.ComprehensiveReport> reports = multiAgentOrchestrator.analyzeBatch(stocks);
        return Result.success(reports);
    }

    @PostMapping("/smart-alert")
    @Monitor(value = "AI smart alert", slowThreshold = 10000)
    public Result<MultiAgentOrchestrator.AlertDecision> smartAlert(@RequestBody USStockRss stock) {
        MultiAgentOrchestrator.AlertDecision decision = multiAgentOrchestrator.smartAlert(stock);
        return Result.success(decision);
    }

    @GetMapping("/summary/daily")
    @Monitor(value = "AI daily summary", slowThreshold = 10000)
    public Result<String> generateDailySummary(@RequestParam(defaultValue = "10") Integer limit) {
        int safeLimit = Math.max(1, Math.min(50, limit == null ? 10 : limit));
        List<String> hotSymbols = stockService.getHotStocks(safeLimit);

        List<USStockRss> samples = new ArrayList<>();
        if (hotSymbols != null) {
            for (String symbol : hotSymbols) {
                List<USStockRss> rows = stockService.queryStock(symbol);
                if (rows != null && !rows.isEmpty()) {
                    samples.add(rows.get(0));
                }
                if (samples.size() >= safeLimit) {
                    break;
                }
            }
        }

        if (samples.isEmpty()) {
            return Result.error("no data");
        }

        String summary = aiStockAnalysisService.generateSummary(samples);
        return Result.success(summary);
    }
}