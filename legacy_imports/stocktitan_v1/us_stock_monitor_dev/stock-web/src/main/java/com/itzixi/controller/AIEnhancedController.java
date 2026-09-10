package com.itzixi.controller;

import com.itzixi.ai.entity.*;
import com.itzixi.ai.service.*;
import com.itzixi.common.response.Result;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDate;
import java.util.List;

@Slf4j
@RestController
@RequestMapping("/api/ai/enhanced")
public class AIEnhancedController {

    @Resource
    private RAGService ragService;

    @Resource
    private EntityExtractionService entityExtractionService;

    @Resource
    private PersonalizedAlertService personalizedAlertService;

    @Resource
    private DailyReportService dailyReportService;

    @Resource
    private SentimentAnalysisService sentimentAnalysisService;

    @Resource
    private AIChatService aiChatService;

    @Resource
    private MultiModalAnalysisService multiModalAnalysisService;

    @Resource
    private PortfolioOptimizationService portfolioOptimizationService;

    @PostMapping("/rag/analyze")
    public Result<String> ragAnalyze(@RequestBody USStockRss stock) {
        try {
            return Result.success(ragService.analyzeWithHistory(stock));
        } catch (Exception e) {
            log.error("RAG analyze failed", e);
            return Result.error("RAG analyze failed: " + e.getMessage());
        }
    }

    @PostMapping("/rag/save-case")
    public Result<String> saveHistoricalCase(@RequestBody SaveCaseRequest request) {
        try {
            ragService.saveAsHistoricalCase(
                    request.getStock(),
                    request.getAnalysis(),
                    request.getActualImpact()
            );
            return Result.success("saved");
        } catch (Exception e) {
            log.error("save historical case failed", e);
            return Result.error("save failed: " + e.getMessage());
        }
    }

    @PostMapping("/entity/extract")
    public Result<StockEntity> extractEntity(@RequestBody USStockRss stock) {
        try {
            return Result.success(entityExtractionService.extractEntities(stock));
        } catch (Exception e) {
            log.error("entity extract failed", e);
            return Result.error("entity extract failed: " + e.getMessage());
        }
    }

    @PostMapping("/personalized/should-alert")
    public Result<PersonalizedAlertService.AlertDecision> shouldAlert(
            @RequestBody PersonalizedAlertRequest request) {
        try {
            PersonalizedAlertService.AlertDecision decision = personalizedAlertService.shouldAlert(
                    request.getStock(), request.getPreference());
            return Result.success(decision);
        } catch (Exception e) {
            log.error("should-alert failed", e);
            return Result.error("should-alert failed: " + e.getMessage());
        }
    }

    @PostMapping("/personalized/filter")
    public Result<List<USStockRss>> filterForUser(@RequestBody FilterRequest request) {
        try {
            return Result.success(personalizedAlertService.filterForUser(
                    request.getStocks(), request.getPreference()));
        } catch (Exception e) {
            log.error("personalized filter failed", e);
            return Result.error("filter failed: " + e.getMessage());
        }
    }

    @GetMapping("/report/daily")
    public Result<DailyReport> getDailyReport(@RequestParam(required = false) String date) {
        try {
            LocalDate reportDate = date != null ? LocalDate.parse(date) : LocalDate.now();
            return Result.success(dailyReportService.generateDailyReport(reportDate));
        } catch (Exception e) {
            log.error("daily report failed", e);
            return Result.error("report failed: " + e.getMessage());
        }
    }

    @GetMapping("/report/latest")
    public Result<DailyReport> getLatestReport() {
        try {
            return Result.success(dailyReportService.getLatestReport());
        } catch (Exception e) {
            log.error("latest report failed", e);
            return Result.error("latest report failed: " + e.getMessage());
        }
    }

    @GetMapping("/sentiment/current")
    public Result<MarketSentiment> getCurrentSentiment() {
        try {
            return Result.success(sentimentAnalysisService.getCurrentSentiment());
        } catch (Exception e) {
            log.error("current sentiment failed", e);
            return Result.error("sentiment failed: " + e.getMessage());
        }
    }

    @PostMapping("/chat")
    public Result<String> chat(@RequestBody ChatRequest request) {
        try {
            return Result.success(aiChatService.chat(request.getSessionId(), request.getMessage()));
        } catch (Exception e) {
            log.error("chat failed", e);
            return Result.error("chat failed: " + e.getMessage());
        }
    }

    @PostMapping("/chat/with-tools")
    public Result<String> chatWithTools(@RequestBody ChatRequest request) {
        try {
            return Result.success(aiChatService.chatWithTools(request.getSessionId(), request.getMessage()));
        } catch (Exception e) {
            log.error("chat-with-tools failed", e);
            return Result.error("chat-with-tools failed: " + e.getMessage());
        }
    }

    @PostMapping("/chat/signal")
    public Result<AIChatService.TradeSignal> chatSignal(@RequestBody ChatRequest request) {
        try {
            return Result.success(aiChatService.chatSignal(request.getSessionId(), request.getMessage()));
        } catch (Exception e) {
            log.error("chat signal failed", e);
            return Result.error("chat signal failed: " + e.getMessage());
        }
    }

    @DeleteMapping("/chat/history/{sessionId}")
    public Result<String> clearHistory(@PathVariable String sessionId) {
        try {
            aiChatService.clearHistory(sessionId);
            return Result.success("cleared");
        } catch (Exception e) {
            log.error("clear history failed", e);
            return Result.error("clear history failed: " + e.getMessage());
        }
    }

    @PostMapping("/chart/analyze")
    public Result<String> analyzeChart(@RequestParam String stockCode,
                                       @RequestParam MultipartFile chartImage) {
        try {
            byte[] imageBytes = chartImage.getBytes();
            return Result.success(multiModalAnalysisService.analyzeChart(stockCode, imageBytes));
        } catch (Exception e) {
            log.error("chart analyze failed", e);
            return Result.error("chart analyze failed: " + e.getMessage());
        }
    }

    @PostMapping("/portfolio/optimize")
    public Result<PortfolioAdvice> optimizePortfolio(@RequestBody PortfolioRequest request) {
        try {
            PortfolioAdvice advice = portfolioOptimizationService.optimizePortfolio(
                    request.getPositions(), request.getPreference());
            return Result.success(advice);
        } catch (Exception e) {
            log.error("portfolio optimize failed", e);
            return Result.error("portfolio optimize failed: " + e.getMessage());
        }
    }

    @PostMapping("/portfolio/assess-risk")
    public Result<String> assessRisk(@RequestBody List<Position> positions) {
        try {
            return Result.success(portfolioOptimizationService.assessPortfolioRisk(positions));
        } catch (Exception e) {
            log.error("assess risk failed", e);
            return Result.error("assess risk failed: " + e.getMessage());
        }
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SaveCaseRequest {
        private USStockRss stock;
        private String analysis;
        private String actualImpact;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PersonalizedAlertRequest {
        private USStockRss stock;
        private UserPreference preference;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FilterRequest {
        private List<USStockRss> stocks;
        private UserPreference preference;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ChatRequest {
        private String sessionId;
        private String message;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PortfolioRequest {
        private List<Position> positions;
        private UserPreference preference;
    }
}