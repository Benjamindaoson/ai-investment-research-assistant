package com.itzixi.ai.service;

import com.itzixi.ai.marketdata.MarketDataClient;
import com.itzixi.ai.tools.StockDataTools;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
public class TradingProductService {

    private static final String SESSION_SET_KEY = "ai:product:sessions";
    private static final String WATCHLIST_KEY_PREFIX = "ai:product:watchlist:";
    private static final String SUBSCRIPTION_KEY_PREFIX = "ai:product:subs:";
    private static final String SIGNAL_KEY_PREFIX = "ai:product:signals:";

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    @Resource
    private AIChatService aiChatService;

    @Resource
    private StockDataTools stockDataTools;

    @Resource
    private MarketDataClient marketDataClient;

    @Resource
    private com.itzixi.ai.client.AIEngineClient aiEngineClient;

    private final Map<String, List<WatchlistItem>> watchlistFallback = new ConcurrentHashMap<>();
    private final Map<String, List<AlertSubscription>> subscriptionFallback = new ConcurrentHashMap<>();
    private final Map<String, List<SignalRecord>> signalFallback = new ConcurrentHashMap<>();
    private final Set<String> sessionFallback = ConcurrentHashMap.newKeySet();

    public List<StrategyTemplate> listStrategyTemplates() {
        return List.of(
                new StrategyTemplate("earnings", "Earnings Breakout", "财报驱动：业绩超预期+放量突破", "post-earnings breakout"),
                new StrategyTemplate("regulatory", "Regulatory Catalyst", "监管审批/处罚驱动：事件窗口交易", "regulatory catalyst"),
                new StrategyTemplate("ma", "M&A Event", "并购传闻/落地：事件波动跟踪", "merger or acquisition"),
                new StrategyTemplate("volatility", "Abnormal Volatility", "异常波动：量价和期权异动结合", "abnormal volatility")
        );
    }

    public List<WatchlistItem> listWatchlist(String sessionId) {
        return readList(watchlistKey(sessionId), watchlistFallback, sessionId, WatchlistItem.class);
    }

    public List<WatchlistItem> addWatchlist(String sessionId, String symbol, String note) {
        String normalized = normalizeSymbol(symbol);
        if (normalized.isBlank()) {
            return listWatchlist(sessionId);
        }

        List<WatchlistItem> current = new ArrayList<>(listWatchlist(sessionId));
        boolean exists = current.stream().anyMatch(x -> normalized.equalsIgnoreCase(x.getSymbol()));
        if (!exists) {
            current.add(new WatchlistItem(normalized, note == null ? "" : note.trim(), Instant.now().getEpochSecond()));
            current.sort(Comparator.comparing(WatchlistItem::getCreatedAtEpochSec).reversed());
            writeList(watchlistKey(sessionId), watchlistFallback, sessionId, current);
            markSession(sessionId);
        }
        return current;
    }

    public List<WatchlistItem> removeWatchlist(String sessionId, String symbol) {
        String normalized = normalizeSymbol(symbol);
        List<WatchlistItem> current = new ArrayList<>(listWatchlist(sessionId));
        current.removeIf(x -> normalized.equalsIgnoreCase(x.getSymbol()));
        writeList(watchlistKey(sessionId), watchlistFallback, sessionId, current);
        markSession(sessionId);
        return current;
    }

    public List<AlertSubscription> listSubscriptions(String sessionId) {
        return readList(subscriptionKey(sessionId), subscriptionFallback, sessionId, AlertSubscription.class);
    }

    public List<AlertSubscription> upsertSubscription(String sessionId,
                                                      String symbol,
                                                      String strategyTemplateId,
                                                      boolean enabled,
                                                      String channel) {
        String normalized = normalizeSymbol(symbol);
        String templateId = strategyTemplateId == null || strategyTemplateId.isBlank() ? "volatility" : strategyTemplateId;
        String normalizedChannel = channel == null || channel.isBlank() ? "in_app" : channel.trim().toLowerCase();

        List<AlertSubscription> current = new ArrayList<>(listSubscriptions(sessionId));
        AlertSubscription target = current.stream()
                .filter(x -> normalized.equalsIgnoreCase(x.getSymbol()) && templateId.equalsIgnoreCase(x.getStrategyTemplateId()))
                .findFirst()
                .orElse(null);

        if (target == null) {
            target = new AlertSubscription(normalized, templateId, normalizedChannel, enabled, Instant.now().getEpochSecond());
            current.add(target);
        } else {
            target.setEnabled(enabled);
            target.setChannel(normalizedChannel);
        }

        current.sort(Comparator.comparing(AlertSubscription::getCreatedAtEpochSec).reversed());
        writeList(subscriptionKey(sessionId), subscriptionFallback, sessionId, current);
        markSession(sessionId);
        return current;
    }

    public List<AlertSubscription> removeSubscription(String sessionId, String symbol, String strategyTemplateId) {
        String normalized = normalizeSymbol(symbol);
        String templateId = strategyTemplateId == null ? "" : strategyTemplateId.trim();

        List<AlertSubscription> current = new ArrayList<>(listSubscriptions(sessionId));
        current.removeIf(x -> normalized.equalsIgnoreCase(x.getSymbol())
                && templateId.equalsIgnoreCase(x.getStrategyTemplateId()));
        writeList(subscriptionKey(sessionId), subscriptionFallback, sessionId, current);
        markSession(sessionId);
        return current;
    }

    public List<AlertEvent> scanSubscriptions(String sessionId) {
        List<String> sessions = new ArrayList<>();
        if (sessionId == null || sessionId.isBlank()) {
            sessions.addAll(listAllSessions());
        } else {
            sessions.add(sessionId);
        }

        List<AlertEvent> events = new ArrayList<>();
        for (String sid : sessions) {
            List<AlertSubscription> subs = listSubscriptions(sid);
            for (AlertSubscription sub : subs) {
                if (!Boolean.TRUE.equals(sub.getEnabled())) {
                    continue;
                }
                String symbol = normalizeSymbol(sub.getSymbol());
                if (symbol.isBlank()) {
                    continue;
                }

                MarketDataClient.QuoteSnapshot quote = marketDataClient.getQuote(symbol);
                if (!quote.isAvailable() || quote.getPrice() == null) {
                    continue;
                }
                BigDecimal move = nvl(quote.getChangePercent());
                long vol = quote.getVolume() == null ? 0L : quote.getVolume();
                long avgVol = quote.getAvgVolume() == null ? 1L : Math.max(1L, quote.getAvgVolume());
                BigDecimal volRatio = BigDecimal.valueOf(vol)
                        .divide(BigDecimal.valueOf(avgVol), 4, RoundingMode.HALF_UP);

                boolean triggered = move.abs().compareTo(BigDecimal.valueOf(2.0)) >= 0
                        || volRatio.compareTo(BigDecimal.valueOf(2.0)) >= 0;
                if (!triggered) {
                    continue;
                }

                AlertEvent event = new AlertEvent();
                event.setSessionId(sid);
                event.setSymbol(symbol);
                event.setStrategyTemplateId(sub.getStrategyTemplateId());
                event.setChannel(sub.getChannel());
                event.setTriggeredAtEpochSec(Instant.now().getEpochSecond());
                event.setTitle("Subscription Triggered");
                event.setMessage("changePct=" + format2(move) + "%, volRatio=" + format2(volRatio));
                event.setSeverity(move.abs().compareTo(BigDecimal.valueOf(5.0)) >= 0 ? "HIGH" : "MEDIUM");
                events.add(event);
            }
        }
        return events;
    }

    public SignalRecord generateSignal(String sessionId,
                                       String userMessage,
                                       String strategyTemplateId,
                                       String preferredSymbol) {
        String message = buildSignalMessage(userMessage, strategyTemplateId, preferredSymbol);
        AIChatService.TradeSignal signal = aiChatService.chatSignal(sessionId, message);

        String symbol = normalizeSymbol(signal.getSymbol());
        if (symbol.isBlank() && preferredSymbol != null) {
            symbol = normalizeSymbol(preferredSymbol);
        }

        BigDecimal entryPrice = BigDecimal.ZERO;
        if (!symbol.isBlank()) {
            StockDataTools.StockPrice price = stockDataTools.getRealTimePrice(symbol);
            if (price != null && price.getCurrentPrice() != null) {
                entryPrice = price.getCurrentPrice();
            }
        }

        SignalRecord record = new SignalRecord();
        record.setSignalId(UUID.randomUUID().toString());
        record.setSessionId(sessionId);
        record.setSymbol(symbol);
        record.setDirection(signal.getDirection());
        record.setConfidence(signal.getConfidence() == null ? 50 : signal.getConfidence());
        record.setStrategyTemplateId(strategyTemplateId == null || strategyTemplateId.isBlank() ? "volatility" : strategyTemplateId);
        record.setTriggerCondition(signal.getTriggerCondition());
        record.setInvalidationCondition(signal.getInvalidationCondition());
        record.setStopLossSuggestion(signal.getStopLossSuggestion());
        record.setTakeProfitSuggestion(signal.getTakeProfitSuggestion());
        record.setPositionSizing(signal.getPositionSizing());
        record.setRiskBudgetPct(signal.getRiskBudgetPct());
        record.setExpectedRMultiple(signal.getExpectedRMultiple());
        record.setRationale(signal.getRationale());
        record.setToolContext(signal.getToolContext());
        record.setEntryPrice(entryPrice);
        record.setMarketRegime(inferMarketRegime(symbol));
        record.setDataFreshnessSec(15L);
        record.setCreatedAtEpochSec(Instant.now().getEpochSecond());
        record.setValidationByHorizon(new HashMap<>());

        List<SignalRecord> current = new ArrayList<>(listSignals(sessionId));
        SignalCreditScore score = computeSignalCreditScore(record, current);
        record.setSignalCreditScore(score.getScore());
        record.setCreditBreakdown(score.getBreakdown());
        current.add(0, record);
        writeList(signalKey(sessionId), signalFallback, sessionId, current);
        markSession(sessionId);
        return record;
    }

    public List<SignalRecord> generateSignalsBatch(String sessionId,
                                                   String userMessage,
                                                   String strategyTemplateId,
                                                   List<String> symbols,
                                                   Integer limit) {
        int max = limit == null ? 10 : Math.max(1, Math.min(50, limit));
        List<String> target = new ArrayList<>();
        if (symbols != null) {
            for (String s : symbols) {
                String normalized = normalizeSymbol(s);
                if (!normalized.isBlank() && !target.contains(normalized)) {
                    target.add(normalized);
                }
                if (target.size() >= max) {
                    break;
                }
            }
        }
        if (target.isEmpty()) {
            List<WatchlistItem> watchlist = listWatchlist(sessionId);
            for (WatchlistItem item : watchlist) {
                if (item != null && item.getSymbol() != null) {
                    target.add(normalizeSymbol(item.getSymbol()));
                }
                if (target.size() >= max) {
                    break;
                }
            }
        }

        List<SignalRecord> out = new ArrayList<>();
        for (String symbol : target) {
            out.add(generateSignal(sessionId, userMessage, strategyTemplateId, symbol));
        }
        return out;
    }

    public List<SignalRecord> listSignals(String sessionId) {
        List<SignalRecord> current = readList(signalKey(sessionId), signalFallback, sessionId, SignalRecord.class);
        current.sort(Comparator.comparing(SignalRecord::getCreatedAtEpochSec).reversed());
        return current;
    }

    @com.itzixi.common.annotation.Monitor(value = "Python引擎回测", slowThreshold = 20000)
    public ValidationRunSummary runValidation(String sessionId) {
        log.info("Delegating Backtest Validation to Python AI Engine...");
        List<String> sessions = new ArrayList<>();
        if (sessionId != null && !sessionId.isBlank()) {
            sessions.add(sessionId);
        } else {
            sessions.addAll(listAllSessions());
        }

        int evaluated = 0;
        int skipped = 0;
        
        for (String sid : sessions) {
            List<SignalRecord> signals = new ArrayList<>(listSignals(sid));
            if (signals.isEmpty()) continue;

            // Map to Python DTO
            List<com.itzixi.ai.client.AIEngineClient.SignalRecordDto> dtos = new ArrayList<>();
            for (SignalRecord s : signals) {
                com.itzixi.ai.client.AIEngineClient.SignalRecordDto dto = new com.itzixi.ai.client.AIEngineClient.SignalRecordDto();
                dto.setId(s.getSignalId());
                dto.setSymbol(s.getSymbol());
                dto.setDirection(s.getDirection());
                dto.setEntry_price(s.getEntryPrice() != null ? s.getEntryPrice().doubleValue() : 0.0);
                dto.setConfidence(s.getConfidence() != null ? s.getConfidence() : 50);
                dto.setCreated_at(String.valueOf(s.getCreatedAtEpochSec()));
                dtos.add(dto);
            }

            try {
                // Call Python
                com.itzixi.ai.client.AIEngineClient.BacktestResult pythonResult = aiEngineClient.runBacktest(dtos);
                
                if (pythonResult != null) {
                    evaluated += pythonResult.getTotal_signals();
                    log.info("Python Backtester Summary for session {}: HitRate={}%, Returns={}%, Governance Status: {}", 
                        sid, pythonResult.getHit_rate_pct(), pythonResult.getAvg_return_pct(), pythonResult.getStatus());
                }
            } catch (Exception e) {
                log.error("Failed to run backtest via Python Engine for session {}", sid, e);
                skipped += dtos.size();
            }
        }

        SignalMetrics metrics = aggregateMetrics();
        return new ValidationRunSummary(evaluated, skipped, sessions.size(), metrics);
    }

    public SignalMetrics aggregateMetrics() {
        return aggregateMetrics(null);
    }

    public SignalMetrics aggregateMetrics(String sessionId) {
        List<SignalRecord> all = new ArrayList<>();
        if (sessionId != null && !sessionId.isBlank()) {
            all.addAll(listSignals(sessionId));
        } else {
            for (String sid : listAllSessions()) {
                all.addAll(listSignals(sid));
            }
        }

        Map<String, HorizonMetric> byHorizon = new LinkedHashMap<>();
        byHorizon.put("T+1", new HorizonMetric("T+1", 1, 0, 0, BigDecimal.ZERO));
        byHorizon.put("T+5", new HorizonMetric("T+5", 5, 0, 0, BigDecimal.ZERO));
        byHorizon.put("T+20", new HorizonMetric("T+20", 20, 0, 0, BigDecimal.ZERO));

        Map<String, StrategyMetric> strategyMetricMap = new LinkedHashMap<>();
        Map<String, RegimeMetric> regimeMetricMap = new LinkedHashMap<>();
        List<BigDecimal> returns = new ArrayList<>();

        for (SignalRecord signal : all) {
            Map<Integer, ValidationResult> val = signal.getValidationByHorizon();
            if (val == null) {
                continue;
            }
            String strategyId = signal.getStrategyTemplateId() == null ? "unknown" : signal.getStrategyTemplateId();
            String regime = signal.getMarketRegime() == null || signal.getMarketRegime().isBlank()
                    ? "UNKNOWN" : signal.getMarketRegime();
            StrategyMetric sm = strategyMetricMap.computeIfAbsent(strategyId,
                    k -> new StrategyMetric(k, 0, 0, BigDecimal.ZERO));
            RegimeMetric rm = regimeMetricMap.computeIfAbsent(regime,
                    k -> new RegimeMetric(k, 0, 0, BigDecimal.ZERO, BigDecimal.ZERO));

            for (Map.Entry<Integer, ValidationResult> e : val.entrySet()) {
                int horizon = e.getKey();
                ValidationResult vr = e.getValue();
                String horizonKey = horizon == 1 ? "T+1" : horizon == 5 ? "T+5" : horizon == 20 ? "T+20" : null;
                if (horizonKey == null) {
                    continue;
                }

                HorizonMetric hm = byHorizon.get(horizonKey);
                hm.setTotal(hm.getTotal() + 1);
                if (Boolean.TRUE.equals(vr.getHit())) {
                    hm.setHits(hm.getHits() + 1);
                }
                hm.setAvgReturnPct(hm.getAvgReturnPct().add(nvl(vr.getReturnPct())));

                sm.setTotal(sm.getTotal() + 1);
                if (Boolean.TRUE.equals(vr.getHit())) {
                    sm.setHits(sm.getHits() + 1);
                }
                sm.setAvgReturnPct(sm.getAvgReturnPct().add(nvl(vr.getReturnPct())));

                rm.setTotal(rm.getTotal() + 1);
                if (Boolean.TRUE.equals(vr.getHit())) {
                    rm.setHits(rm.getHits() + 1);
                }
                rm.setAvgReturnPct(rm.getAvgReturnPct().add(nvl(vr.getReturnPct())));

                returns.add(nvl(vr.getReturnPct()));
            }
        }

        for (HorizonMetric hm : byHorizon.values()) {
            if (hm.getTotal() > 0) {
                hm.setHitRatePct(BigDecimal.valueOf(hm.getHits() * 100.0 / hm.getTotal()).setScale(2, RoundingMode.HALF_UP));
                hm.setAvgReturnPct(hm.getAvgReturnPct().divide(BigDecimal.valueOf(hm.getTotal()), 4, RoundingMode.HALF_UP));
            } else {
                hm.setHitRatePct(BigDecimal.ZERO);
                hm.setAvgReturnPct(BigDecimal.ZERO);
            }
        }

        List<StrategyMetric> strategyRanking = new ArrayList<>(strategyMetricMap.values());
        for (StrategyMetric sm : strategyRanking) {
            if (sm.getTotal() > 0) {
                sm.setHitRatePct(BigDecimal.valueOf(sm.getHits() * 100.0 / sm.getTotal()).setScale(2, RoundingMode.HALF_UP));
                sm.setAvgReturnPct(sm.getAvgReturnPct().divide(BigDecimal.valueOf(sm.getTotal()), 4, RoundingMode.HALF_UP));
            } else {
                sm.setHitRatePct(BigDecimal.ZERO);
                sm.setAvgReturnPct(BigDecimal.ZERO);
            }
        }
        strategyRanking.sort((a, b) -> b.getHitRatePct().compareTo(a.getHitRatePct()));

        List<RegimeMetric> regimeMetrics = new ArrayList<>(regimeMetricMap.values());
        for (RegimeMetric rm : regimeMetrics) {
            if (rm.getTotal() > 0) {
                rm.setHitRatePct(BigDecimal.valueOf(rm.getHits() * 100.0 / rm.getTotal()).setScale(2, RoundingMode.HALF_UP));
                rm.setAvgReturnPct(rm.getAvgReturnPct().divide(BigDecimal.valueOf(rm.getTotal()), 4, RoundingMode.HALF_UP));
            } else {
                rm.setHitRatePct(BigDecimal.ZERO);
                rm.setAvgReturnPct(BigDecimal.ZERO);
            }
        }
        regimeMetrics.sort((a, b) -> b.getHitRatePct().compareTo(a.getHitRatePct()));

        List<StrategyGovernance> governance = computeStrategyGovernance(strategyRanking);

        SignalMetrics metrics = new SignalMetrics();
        metrics.setTotalSignals(all.size());
        metrics.setHorizonMetrics(new ArrayList<>(byHorizon.values()));
        metrics.setStrategyRanking(strategyRanking);
        metrics.setRegimeMetrics(regimeMetrics);
        metrics.setStrategyGovernance(governance);
        metrics.setApproximateSharpe(approximateSharpe(returns));
        metrics.setApproximateProfitFactor(approximateProfitFactor(returns));
        metrics.setMaxDrawdownPct(maxDrawdownPct(returns));
        metrics.setWeeklyEffectiveSignals(weeklyEffectiveSignals(all));
        metrics.setGeneratedAtEpochSec(Instant.now().getEpochSecond());
        return metrics;
    }

    private int evaluateOneSignal(SignalRecord signal) {
        int[] horizons = new int[]{1, 5, 20};
        int evaluated = 0;
        LocalDate createdDate = Instant.ofEpochSecond(signal.getCreatedAtEpochSec()).atZone(ZoneOffset.UTC).toLocalDate();
        MarketDataClient.PriceHistory history = marketDataClient.getHistory(signal.getSymbol(), 365);
        if (!history.isAvailable() || history.getPoints() == null || history.getPoints().isEmpty()) {
            return 0;
        }

        for (int horizon : horizons) {
            if (signal.getValidationByHorizon().containsKey(horizon)) {
                continue;
            }
            LocalDate targetDate = createdDate.plusDays(horizon);
            if (LocalDate.now(ZoneOffset.UTC).isBefore(targetDate)) {
                continue;
            }

            BigDecimal targetPrice = findTargetPrice(history.getPoints(), targetDate);
            if (targetPrice == null || signal.getEntryPrice().compareTo(BigDecimal.ZERO) <= 0) {
                continue;
            }

            BigDecimal retPct = targetPrice.subtract(signal.getEntryPrice())
                    .multiply(BigDecimal.valueOf(100))
                    .divide(signal.getEntryPrice(), 4, RoundingMode.HALF_UP);
            boolean hit = computeHit(signal.getDirection(), retPct);

            ValidationResult vr = new ValidationResult();
            vr.setHorizonDays(horizon);
            vr.setHit(hit);
            vr.setReturnPct(retPct);
            vr.setTargetPrice(targetPrice);
            vr.setEvaluatedAtEpochSec(Instant.now().getEpochSecond());

            signal.getValidationByHorizon().put(horizon, vr);
            evaluated++;
        }
        return evaluated;
    }

    private BigDecimal findTargetPrice(List<MarketDataClient.PricePoint> points, LocalDate targetDate) {
        return points.stream()
                .filter(p -> p.getDate() != null && (p.getDate().isEqual(targetDate) || p.getDate().isAfter(targetDate)))
                .map(MarketDataClient.PricePoint::getClose)
                .filter(x -> x != null)
                .findFirst()
                .orElseGet(() -> points.get(points.size() - 1).getClose());
    }

    private boolean computeHit(String direction, BigDecimal retPct) {
        String d = direction == null ? "NEUTRAL" : direction.toUpperCase();
        if ("BULLISH".equals(d)) {
            return retPct.compareTo(BigDecimal.ZERO) > 0;
        }
        if ("BEARISH".equals(d)) {
            return retPct.compareTo(BigDecimal.ZERO) < 0;
        }
        return retPct.abs().compareTo(BigDecimal.valueOf(2)) <= 0;
    }

    private String buildSignalMessage(String userMessage, String strategyTemplateId, String preferredSymbol) {
        String base = userMessage == null ? "" : userMessage.trim();
        String strategy = strategyTemplateId == null ? "volatility" : strategyTemplateId.trim();
        String symbol = preferredSymbol == null ? "" : preferredSymbol.trim().toUpperCase();
        return String.format("strategy=%s symbol=%s question=%s", strategy, symbol, base);
    }

    public List<StrategyGovernance> listStrategyGovernance(String sessionId) {
        return aggregateMetrics(sessionId).getStrategyGovernance();
    }

    private SignalCreditScore computeSignalCreditScore(SignalRecord record, List<SignalRecord> history) {
        BigDecimal historicalHit = historicalHitRate(record, history);
        BigDecimal regimeFit = strategyRegimeFit(record.getStrategyTemplateId(), record.getMarketRegime());
        BigDecimal freshness = freshnessScore(record.getDataFreshnessSec());
        BigDecimal consistency = multiSourceConsistency(record.getToolContext());
        BigDecimal modelConfidence = BigDecimal.valueOf(record.getConfidence() == null ? 50 : record.getConfidence());

        BigDecimal score = historicalHit.multiply(BigDecimal.valueOf(0.35))
                .add(regimeFit.multiply(BigDecimal.valueOf(0.20)))
                .add(freshness.multiply(BigDecimal.valueOf(0.15)))
                .add(consistency.multiply(BigDecimal.valueOf(0.15)))
                .add(modelConfidence.multiply(BigDecimal.valueOf(0.15)))
                .setScale(2, RoundingMode.HALF_UP);

        Map<String, BigDecimal> breakdown = new LinkedHashMap<>();
        breakdown.put("historicalHitRate", historicalHit);
        breakdown.put("regimeFit", regimeFit);
        breakdown.put("dataFreshness", freshness);
        breakdown.put("sourceConsistency", consistency);
        breakdown.put("modelConfidence", modelConfidence);
        return new SignalCreditScore(score, breakdown);
    }

    private BigDecimal historicalHitRate(SignalRecord record, List<SignalRecord> history) {
        int total = 0;
        int hits = 0;
        String strategy = record.getStrategyTemplateId() == null ? "" : record.getStrategyTemplateId();
        for (SignalRecord x : history) {
            if (x == null || x.getValidationByHorizon() == null) {
                continue;
            }
            if (!strategy.equalsIgnoreCase(x.getStrategyTemplateId())) {
                continue;
            }
            ValidationResult vr = x.getValidationByHorizon().get(5);
            if (vr == null) {
                continue;
            }
            total++;
            if (Boolean.TRUE.equals(vr.getHit())) {
                hits++;
            }
        }
        if (total == 0) {
            return BigDecimal.valueOf(55.0);
        }
        return BigDecimal.valueOf(hits * 100.0 / total).setScale(2, RoundingMode.HALF_UP);
    }

    private BigDecimal strategyRegimeFit(String strategyTemplateId, String regime) {
        String s = strategyTemplateId == null ? "volatility" : strategyTemplateId.toLowerCase();
        String r = regime == null ? "UNKNOWN" : regime.toUpperCase();
        if ("volatility".equals(s) && ("HIGH_VOL_UP".equals(r) || "HIGH_VOL_DOWN".equals(r))) {
            return BigDecimal.valueOf(85);
        }
        if ("earnings".equals(s) && ("TREND_UP".equals(r) || "HIGH_VOL_UP".equals(r))) {
            return BigDecimal.valueOf(80);
        }
        if ("regulatory".equals(s)) {
            return BigDecimal.valueOf(72);
        }
        if ("ma".equals(s) && ("RANGE".equals(r) || "TREND_UP".equals(r))) {
            return BigDecimal.valueOf(78);
        }
        return BigDecimal.valueOf(60);
    }

    private BigDecimal freshnessScore(Long dataFreshnessSec) {
        long sec = dataFreshnessSec == null ? 120L : Math.max(0L, dataFreshnessSec);
        if (sec <= 15) {
            return BigDecimal.valueOf(95);
        }
        if (sec <= 30) {
            return BigDecimal.valueOf(90);
        }
        if (sec <= 60) {
            return BigDecimal.valueOf(80);
        }
        if (sec <= 180) {
            return BigDecimal.valueOf(68);
        }
        return BigDecimal.valueOf(50);
    }

    private BigDecimal multiSourceConsistency(String toolContext) {
        if (toolContext == null || toolContext.isBlank()) {
            return BigDecimal.valueOf(45);
        }
        int score = 45;
        if (toolContext.contains("newsCount=")) {
            score += 15;
        }
        if (toolContext.contains("price=")) {
            score += 20;
        }
        if (toolContext.contains("pe=") || toolContext.contains("eps=")) {
            score += 10;
        }
        if (toolContext.contains("vol=")) {
            score += 10;
        }
        return BigDecimal.valueOf(Math.min(95, score));
    }

    private String inferMarketRegime(String symbol) {
        if (symbol == null || symbol.isBlank()) {
            return "UNKNOWN";
        }
        MarketDataClient.QuoteSnapshot quote = marketDataClient.getQuote(symbol);
        if (!quote.isAvailable() || quote.getChangePercent() == null) {
            return "UNKNOWN";
        }
        BigDecimal changePct = quote.getChangePercent();
        BigDecimal volRatio = BigDecimal.valueOf(quote.getVolume() == null ? 0 : quote.getVolume())
                .divide(BigDecimal.valueOf(Math.max(1L, quote.getAvgVolume() == null ? 1L : quote.getAvgVolume())), 4, RoundingMode.HALF_UP);
        if (changePct.compareTo(BigDecimal.valueOf(2.0)) >= 0 && volRatio.compareTo(BigDecimal.valueOf(1.5)) >= 0) {
            return "HIGH_VOL_UP";
        }
        if (changePct.compareTo(BigDecimal.valueOf(-2.0)) <= 0 && volRatio.compareTo(BigDecimal.valueOf(1.5)) >= 0) {
            return "HIGH_VOL_DOWN";
        }
        if (changePct.compareTo(BigDecimal.valueOf(0.8)) >= 0) {
            return "TREND_UP";
        }
        if (changePct.compareTo(BigDecimal.valueOf(-0.8)) <= 0) {
            return "TREND_DOWN";
        }
        return "RANGE";
    }

    private List<StrategyGovernance> computeStrategyGovernance(List<StrategyMetric> strategyRanking) {
        List<StrategyGovernance> out = new ArrayList<>();
        for (StrategyMetric sm : strategyRanking) {
            String status = "ACTIVE";
            BigDecimal weight = BigDecimal.ONE;
            String reason = "stable";
            if (sm.getTotal() >= 20 && sm.getHitRatePct().compareTo(BigDecimal.valueOf(45)) < 0) {
                status = "RETIRED";
                weight = BigDecimal.ZERO;
                reason = "low hit rate over enough samples";
            } else if (sm.getTotal() >= 10 && sm.getHitRatePct().compareTo(BigDecimal.valueOf(52)) < 0) {
                status = "DOWNWEIGHT";
                weight = BigDecimal.valueOf(0.5);
                reason = "subpar hit rate in recent window";
            }
            StrategyGovernance governance = new StrategyGovernance();
            governance.setStrategyTemplateId(sm.getStrategyTemplateId());
            governance.setStatus(status);
            governance.setWeight(weight);
            governance.setReason(reason);
            governance.setTotal(sm.getTotal());
            governance.setHitRatePct(sm.getHitRatePct());
            governance.setAvgReturnPct(sm.getAvgReturnPct());
            governance.setUpdatedAtEpochSec(Instant.now().getEpochSecond());
            out.add(governance);
        }
        return out;
    }

    private BigDecimal approximateSharpe(List<BigDecimal> returns) {
        if (returns == null || returns.size() < 2) {
            return BigDecimal.ZERO;
        }
        double mean = returns.stream().mapToDouble(BigDecimal::doubleValue).average().orElse(0.0);
        double variance = 0.0;
        for (BigDecimal r : returns) {
            double d = r.doubleValue() - mean;
            variance += d * d;
        }
        variance = variance / (returns.size() - 1);
        double std = Math.sqrt(Math.max(variance, 1e-9));
        double sharpe = mean / std;
        return BigDecimal.valueOf(sharpe).setScale(4, RoundingMode.HALF_UP);
    }

    private BigDecimal approximateProfitFactor(List<BigDecimal> returns) {
        if (returns == null || returns.isEmpty()) {
            return BigDecimal.ZERO;
        }
        BigDecimal gain = BigDecimal.ZERO;
        BigDecimal loss = BigDecimal.ZERO;
        for (BigDecimal r : returns) {
            if (r.compareTo(BigDecimal.ZERO) >= 0) {
                gain = gain.add(r);
            } else {
                loss = loss.add(r.abs());
            }
        }
        if (loss.compareTo(BigDecimal.ZERO) == 0) {
            return gain.compareTo(BigDecimal.ZERO) > 0 ? BigDecimal.valueOf(9.99) : BigDecimal.ZERO;
        }
        return gain.divide(loss, 4, RoundingMode.HALF_UP);
    }

    private BigDecimal maxDrawdownPct(List<BigDecimal> returns) {
        if (returns == null || returns.isEmpty()) {
            return BigDecimal.ZERO;
        }
        BigDecimal equity = BigDecimal.valueOf(100.0);
        BigDecimal peak = equity;
        BigDecimal maxDrawdown = BigDecimal.ZERO;
        for (BigDecimal ret : returns) {
            BigDecimal factor = BigDecimal.ONE.add(ret.divide(BigDecimal.valueOf(100.0), 6, RoundingMode.HALF_UP));
            equity = equity.multiply(factor).setScale(6, RoundingMode.HALF_UP);
            if (equity.compareTo(peak) > 0) {
                peak = equity;
            }
            BigDecimal dd = peak.subtract(equity).multiply(BigDecimal.valueOf(100.0))
                    .divide(peak, 4, RoundingMode.HALF_UP);
            if (dd.compareTo(maxDrawdown) > 0) {
                maxDrawdown = dd;
            }
        }
        return maxDrawdown;
    }

    private Integer weeklyEffectiveSignals(List<SignalRecord> all) {
        long now = Instant.now().getEpochSecond();
        long minTs = now - 7 * 24 * 3600;
        int count = 0;
        for (SignalRecord r : all) {
            if (r.getCreatedAtEpochSec() == null || r.getCreatedAtEpochSec() < minTs) {
                continue;
            }
            if (r.getSignalCreditScore() == null || r.getSignalCreditScore().compareTo(BigDecimal.valueOf(70)) < 0) {
                continue;
            }
            if (r.getExpectedRMultiple() == null || r.getExpectedRMultiple().compareTo(BigDecimal.valueOf(1.5)) < 0) {
                continue;
            }
            count++;
        }
        return count;
    }

    private String normalizeSymbol(String symbol) {
        return symbol == null ? "" : symbol.trim().toUpperCase();
    }

    private void markSession(String sessionId) {
        if (sessionId == null || sessionId.isBlank()) {
            return;
        }
        try {
            redisTemplate.opsForSet().add(SESSION_SET_KEY, sessionId);
        } catch (Exception e) {
            sessionFallback.add(sessionId);
        }
    }

    private List<String> listAllSessions() {
        Set<String> sessions = new LinkedHashSet<>();
        try {
            Set<Object> raw = redisTemplate.opsForSet().members(SESSION_SET_KEY);
            if (raw != null) {
                for (Object x : raw) {
                    if (x != null) {
                        sessions.add(String.valueOf(x));
                    }
                }
            }
        } catch (Exception e) {
            log.debug("read session set from redis failed: {}", e.getMessage());
        }
        sessions.addAll(sessionFallback);
        return new ArrayList<>(sessions);
    }

    @SuppressWarnings("unchecked")
    private <T> List<T> readList(String key,
                                 Map<String, List<T>> fallback,
                                 String sessionId,
                                 Class<T> type) {
        try {
            Object value = redisTemplate.opsForValue().get(key);
            if (value instanceof List<?>) {
                return (List<T>) value;
            }
        } catch (Exception e) {
            log.debug("read list from redis failed: key={}, err={}", key, e.getMessage());
        }
        return new ArrayList<>(fallback.getOrDefault(sessionId, new ArrayList<>()));
    }

    private <T> void writeList(String key,
                               Map<String, List<T>> fallback,
                               String sessionId,
                               List<T> value) {
        try {
            redisTemplate.opsForValue().set(key, value);
        } catch (Exception e) {
            log.debug("write list to redis failed: key={}, err={}", key, e.getMessage());
            fallback.put(sessionId, value);
        }
    }

    private String watchlistKey(String sessionId) {
        return WATCHLIST_KEY_PREFIX + sessionId;
    }

    private String subscriptionKey(String sessionId) {
        return SUBSCRIPTION_KEY_PREFIX + sessionId;
    }

    private String signalKey(String sessionId) {
        return SIGNAL_KEY_PREFIX + sessionId;
    }

    private BigDecimal nvl(BigDecimal v) {
        return v == null ? BigDecimal.ZERO : v;
    }

    private String format2(BigDecimal v) {
        return nvl(v).setScale(2, RoundingMode.HALF_UP).toPlainString();
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class WatchlistItem {
        private String symbol;
        private String note;
        private Long createdAtEpochSec;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AlertSubscription {
        private String symbol;
        private String strategyTemplateId;
        private String channel;
        private Boolean enabled;
        private Long createdAtEpochSec;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StrategyTemplate {
        private String templateId;
        private String name;
        private String description;
        private String scenario;
    }

    @Data
    @NoArgsConstructor
    public static class SignalRecord {
        private String signalId;
        private String sessionId;
        private String symbol;
        private String direction;
        private Integer confidence;
        private String strategyTemplateId;
        private String triggerCondition;
        private String invalidationCondition;
        private String stopLossSuggestion;
        private String takeProfitSuggestion;
        private String positionSizing;
        private BigDecimal riskBudgetPct;
        private BigDecimal expectedRMultiple;
        private BigDecimal signalCreditScore;
        private Map<String, BigDecimal> creditBreakdown;
        private String marketRegime;
        private Long dataFreshnessSec;
        private String rationale;
        private String toolContext;
        private BigDecimal entryPrice;
        private Long createdAtEpochSec;
        private Map<Integer, ValidationResult> validationByHorizon;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ValidationResult {
        private Integer horizonDays;
        private Boolean hit;
        private BigDecimal returnPct;
        private BigDecimal targetPrice;
        private Long evaluatedAtEpochSec;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ValidationRunSummary {
        private Integer evaluatedSignals;
        private Integer skippedSignals;
        private Integer scannedSessions;
        private SignalMetrics metricsSnapshot;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AlertEvent {
        private String sessionId;
        private String symbol;
        private String strategyTemplateId;
        private String channel;
        private String title;
        private String message;
        private String severity;
        private Long triggeredAtEpochSec;
    }

    @Data
    @NoArgsConstructor
    public static class SignalMetrics {
        private Integer totalSignals;
        private List<HorizonMetric> horizonMetrics;
        private List<StrategyMetric> strategyRanking;
        private List<RegimeMetric> regimeMetrics;
        private List<StrategyGovernance> strategyGovernance;
        private BigDecimal approximateSharpe;
        private BigDecimal approximateProfitFactor;
        private BigDecimal maxDrawdownPct;
        private Integer weeklyEffectiveSignals;
        private Long generatedAtEpochSec;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class HorizonMetric {
        private String horizon;
        private Integer horizonDays;
        private Integer total;
        private Integer hits;
        private BigDecimal avgReturnPct;
        private BigDecimal hitRatePct;

        public HorizonMetric(String horizon, Integer horizonDays, Integer total, Integer hits, BigDecimal avgReturnPct) {
            this.horizon = horizon;
            this.horizonDays = horizonDays;
            this.total = total;
            this.hits = hits;
            this.avgReturnPct = avgReturnPct;
            this.hitRatePct = BigDecimal.ZERO;
        }
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StrategyMetric {
        private String strategyTemplateId;
        private Integer total;
        private Integer hits;
        private BigDecimal avgReturnPct;
        private BigDecimal hitRatePct;

        public StrategyMetric(String strategyTemplateId, Integer total, Integer hits, BigDecimal avgReturnPct) {
            this.strategyTemplateId = strategyTemplateId;
            this.total = total;
            this.hits = hits;
            this.avgReturnPct = avgReturnPct;
            this.hitRatePct = BigDecimal.ZERO;
        }
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RegimeMetric {
        private String regime;
        private Integer total;
        private Integer hits;
        private BigDecimal avgReturnPct;
        private BigDecimal hitRatePct;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StrategyGovernance {
        private String strategyTemplateId;
        private String status;
        private BigDecimal weight;
        private String reason;
        private Integer total;
        private BigDecimal hitRatePct;
        private BigDecimal avgReturnPct;
        private Long updatedAtEpochSec;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SignalCreditScore {
        private BigDecimal score;
        private Map<String, BigDecimal> breakdown;
    }
}
