package com.itzixi.ai.controller.product;

import com.itzixi.ai.service.TradingProductService;
import com.itzixi.common.response.Result;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/ai/product")
public class TradingProductController {

    @Resource
    private TradingProductService tradingProductService;

    @GetMapping("/strategies/templates")
    public Result<List<TradingProductService.StrategyTemplate>> listStrategyTemplates() {
        return Result.success(tradingProductService.listStrategyTemplates());
    }

    @GetMapping("/watchlist")
    public Result<List<TradingProductService.WatchlistItem>> listWatchlist(@RequestParam String sessionId) {
        return Result.success(tradingProductService.listWatchlist(sessionId));
    }

    @PostMapping("/watchlist")
    public Result<List<TradingProductService.WatchlistItem>> addWatchlist(@RequestBody WatchlistRequest request) {
        return Result.success(tradingProductService.addWatchlist(
                request.getSessionId(),
                request.getSymbol(),
                request.getNote()
        ));
    }

    @DeleteMapping("/watchlist")
    public Result<List<TradingProductService.WatchlistItem>> removeWatchlist(@RequestParam String sessionId,
                                                                              @RequestParam String symbol) {
        return Result.success(tradingProductService.removeWatchlist(sessionId, symbol));
    }

    @GetMapping("/subscriptions")
    public Result<List<TradingProductService.AlertSubscription>> listSubscriptions(@RequestParam String sessionId) {
        return Result.success(tradingProductService.listSubscriptions(sessionId));
    }

    @PostMapping("/subscriptions")
    public Result<List<TradingProductService.AlertSubscription>> upsertSubscription(@RequestBody SubscriptionRequest request) {
        return Result.success(tradingProductService.upsertSubscription(
                request.getSessionId(),
                request.getSymbol(),
                request.getStrategyTemplateId(),
                request.getEnabled() == null || request.getEnabled(),
                request.getChannel()
        ));
    }

    @DeleteMapping("/subscriptions")
    public Result<List<TradingProductService.AlertSubscription>> removeSubscription(@RequestParam String sessionId,
                                                                                    @RequestParam String symbol,
                                                                                    @RequestParam String strategyTemplateId) {
        return Result.success(tradingProductService.removeSubscription(sessionId, symbol, strategyTemplateId));
    }

    @PostMapping("/subscriptions/scan")
    public Result<List<TradingProductService.AlertEvent>> scanSubscriptions(@RequestBody(required = false) ValidationRequest request) {
        String sessionId = request == null ? null : request.getSessionId();
        return Result.success(tradingProductService.scanSubscriptions(sessionId));
    }

    @PostMapping("/signals/generate")
    public Result<TradingProductService.SignalRecord> generateSignal(@RequestBody SignalGenerateRequest request) {
        return Result.success(tradingProductService.generateSignal(
                request.getSessionId(),
                request.getMessage(),
                request.getStrategyTemplateId(),
                request.getPreferredSymbol()
        ));
    }

    @PostMapping("/signals/generate/batch")
    public Result<List<TradingProductService.SignalRecord>> generateSignalsBatch(@RequestBody SignalGenerateBatchRequest request) {
        return Result.success(tradingProductService.generateSignalsBatch(
                request.getSessionId(),
                request.getMessage(),
                request.getStrategyTemplateId(),
                request.getSymbols(),
                request.getLimit()
        ));
    }

    @GetMapping("/signals")
    public Result<List<TradingProductService.SignalRecord>> listSignals(@RequestParam String sessionId) {
        return Result.success(tradingProductService.listSignals(sessionId));
    }

    @PostMapping("/signals/validate/run")
    public Result<TradingProductService.ValidationRunSummary> runValidation(@RequestBody(required = false) ValidationRequest request) {
        String sessionId = request == null ? null : request.getSessionId();
        return Result.success(tradingProductService.runValidation(sessionId));
    }

    @GetMapping("/signals/metrics")
    public Result<TradingProductService.SignalMetrics> metrics(@RequestParam(required = false) String sessionId) {
        return Result.success(tradingProductService.aggregateMetrics(sessionId));
    }

    @GetMapping("/signals/governance")
    public Result<List<TradingProductService.StrategyGovernance>> governance(@RequestParam(required = false) String sessionId) {
        return Result.success(tradingProductService.listStrategyGovernance(sessionId));
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class WatchlistRequest {
        private String sessionId;
        private String symbol;
        private String note;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SubscriptionRequest {
        private String sessionId;
        private String symbol;
        private String strategyTemplateId;
        private Boolean enabled;
        private String channel;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SignalGenerateRequest {
        private String sessionId;
        private String message;
        private String strategyTemplateId;
        private String preferredSymbol;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SignalGenerateBatchRequest {
        private String sessionId;
        private String message;
        private String strategyTemplateId;
        private List<String> symbols;
        private Integer limit;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ValidationRequest {
        private String sessionId;
    }
}
