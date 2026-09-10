package com.itzixi.controller;

import com.itzixi.ai.service.TradingProductService;
import com.itzixi.common.response.Result;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/demo")
public class DemoShowcaseController {

    @Resource
    private TradingProductService tradingProductService;

    @GetMapping("/health")
    public Result<Map<String, Object>> health() {
        return Result.success(Map.of(
                "product", "US Stock AI Monitor",
                "mode", "demo",
                "nowEpochSec", Instant.now().getEpochSecond(),
                "features", List.of(
                        "watchlist",
                        "subscription",
                        "strategy_templates",
                        "signal_generation",
                        "T+1/T+5/T+20_validation"
                )
        ));
    }

    @PostMapping("/one-click")
    public Result<DemoResult> oneClick(@RequestBody DemoRequest req) {
        String sessionId = req.getSessionId() == null || req.getSessionId().isBlank() ? "demo-user" : req.getSessionId();
        String symbol = req.getSymbol() == null || req.getSymbol().isBlank() ? "AAPL" : req.getSymbol().toUpperCase();
        String strategy = req.getStrategyTemplateId() == null || req.getStrategyTemplateId().isBlank()
                ? "volatility" : req.getStrategyTemplateId();

        List<TradingProductService.WatchlistItem> watchlist = tradingProductService.addWatchlist(
                sessionId, symbol, "demo watch");
        List<TradingProductService.AlertSubscription> subscriptions = tradingProductService.upsertSubscription(
                sessionId, symbol, strategy, true, "in_app");

        TradingProductService.SignalRecord signal = tradingProductService.generateSignal(
                sessionId,
                "Generate executable signal for " + symbol + " with strategy " + strategy,
                strategy,
                symbol
        );

        TradingProductService.ValidationRunSummary validation = tradingProductService.runValidation(sessionId);
        TradingProductService.SignalMetrics metrics = tradingProductService.aggregateMetrics();
        List<TradingProductService.AlertEvent> alerts = tradingProductService.scanSubscriptions(sessionId);

        DemoResult result = new DemoResult();
        result.setSessionId(sessionId);
        result.setSymbol(symbol);
        result.setStrategyTemplateId(strategy);
        result.setWatchlistSize(watchlist.size());
        result.setSubscriptionSize(subscriptions.size());
        result.setSignal(signal);
        result.setValidation(validation);
        result.setMetrics(metrics);
        result.setAlerts(alerts);
        return Result.success(result);
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DemoRequest {
        private String sessionId;
        private String symbol;
        private String strategyTemplateId;
    }

    @Data
    @NoArgsConstructor
    public static class DemoResult {
        private String sessionId;
        private String symbol;
        private String strategyTemplateId;
        private Integer watchlistSize;
        private Integer subscriptionSize;
        private TradingProductService.SignalRecord signal;
        private TradingProductService.ValidationRunSummary validation;
        private TradingProductService.SignalMetrics metrics;
        private List<TradingProductService.AlertEvent> alerts;
    }
}
