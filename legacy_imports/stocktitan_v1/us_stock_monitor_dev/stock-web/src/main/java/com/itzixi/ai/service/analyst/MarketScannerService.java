package com.itzixi.ai.service.analyst;

import com.itzixi.ai.marketdata.MarketDataClient;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.service.RssService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

@Slf4j
@Service
public class MarketScannerService {

    @Resource
    private MarketDataClient marketDataClient;

    @Resource
    private RssService rssService;

    @Value("${ai.scanner.universe:AAPL,MSFT,NVDA,AMZN,GOOGL,META,TSLA,AMD,NFLX,AVGO,ORCL,CRM,ADBE,INTC,PLTR,SMCI,TSM,BABA,JPM,BAC}")
    private String scannerUniverse;

    @Value("${ai.scanner.max-symbols:30}")
    private int maxScanSymbols;

    @Monitor(value = "Market Scanner", slowThreshold = 5000)
    public List<ScanResult> scanMarket(String query) {
        ScanCriteria criteria = parseCriteria(query);
        List<String> symbols = buildUniverse(criteria.maxSymbols());

        List<ScoredStock> scored = new ArrayList<>();
        for (String symbol : symbols) {
            MarketDataClient.QuoteSnapshot quote = marketDataClient.getQuote(symbol);
            if (!quote.isAvailable() || quote.getPrice() == null) {
                continue;
            }

            BigDecimal changePct = nvl(quote.getChangePercent());
            long volume = quote.getVolume() == null ? 0L : quote.getVolume();
            long avgVolume = quote.getAvgVolume() == null ? 1L : Math.max(1L, quote.getAvgVolume());
            BigDecimal volumeRatio = BigDecimal.valueOf(volume)
                    .divide(BigDecimal.valueOf(avgVolume), 4, RoundingMode.HALF_UP);

            boolean directionPass = switch (criteria.direction()) {
                case BULLISH -> changePct.compareTo(BigDecimal.ZERO) > 0;
                case BEARISH -> changePct.compareTo(BigDecimal.ZERO) < 0;
                default -> true;
            };
            boolean changePass = changePct.abs().compareTo(criteria.minAbsChangePct()) >= 0;
            boolean volumePass = volumeRatio.compareTo(criteria.minVolumeRatio()) >= 0;

            if (!(directionPass && changePass && volumePass)) {
                continue;
            }

            MarketDataClient.OptionsSnapshot options = criteria.requireUnusualOptions()
                    ? marketDataClient.getOptionsSnapshot(symbol)
                    : null;
            long maxOptionAnomalyBps = maxOptionAnomaly(options);
            if (criteria.requireUnusualOptions() && maxOptionAnomalyBps < 2500) {
                continue;
            }

            double score = score(changePct, volumeRatio, maxOptionAnomalyBps);
            String reason = buildReason(quote, changePct, volumeRatio, maxOptionAnomalyBps);
            scored.add(new ScoredStock(symbol, quote.getName(), reason, score));
        }

        scored.sort((a, b) -> Double.compare(b.score(), a.score()));
        return scored.stream()
                .limit(criteria.topK())
                .map(s -> new ScanResult(s.symbol(), s.name(), s.reason()))
                .toList();
    }

    private ScanCriteria parseCriteria(String query) {
        String q = query == null ? "" : query.toLowerCase();

        Direction direction = Direction.NEUTRAL;
        if (containsAny(q, "bull", "看涨", "上涨", "breakout", "strong")) {
            direction = Direction.BULLISH;
        } else if (containsAny(q, "bear", "看跌", "下跌", "weak", "breakdown")) {
            direction = Direction.BEARISH;
        }

        BigDecimal minAbsChange = containsAny(q, "异常", "异动", "volatility", "剧烈")
                ? new BigDecimal("2.0") : new BigDecimal("1.0");

        BigDecimal minVolumeRatio = containsAny(q, "放量", "volume", "大单", "active")
                ? new BigDecimal("1.8") : new BigDecimal("1.2");

        boolean unusualOptions = containsAny(q, "期权", "option", "smart money", "主力");

        int topK = containsAny(q, "top 20", "20") ? 20 : 10;
        int maxSymbols = Math.max(10, Math.min(maxScanSymbols, containsAny(q, "全市场", "all") ? maxScanSymbols : 25));

        return new ScanCriteria(direction, minAbsChange, minVolumeRatio, unusualOptions, topK, maxSymbols);
    }

    private List<String> buildUniverse(int limit) {
        Set<String> merged = new LinkedHashSet<>();
        List<String> hot = rssService.getHotStocks(Math.min(30, Math.max(10, limit)));
        if (hot != null) {
            hot.stream().map(this::normalize).filter(s -> !s.isBlank()).forEach(merged::add);
        }
        Arrays.stream(scannerUniverse.split(","))
                .map(this::normalize)
                .filter(s -> !s.isBlank())
                .forEach(merged::add);

        return merged.stream().limit(Math.max(10, limit)).toList();
    }

    private long maxOptionAnomaly(MarketDataClient.OptionsSnapshot options) {
        if (options == null || !options.isAvailable()) {
            return 0L;
        }
        long maxCall = options.getCalls() == null ? 0L
                : options.getCalls().stream().mapToLong(MarketDataClient.OptionContract::getVolumeToOiBps).max().orElse(0L);
        long maxPut = options.getPuts() == null ? 0L
                : options.getPuts().stream().mapToLong(MarketDataClient.OptionContract::getVolumeToOiBps).max().orElse(0L);
        return Math.max(maxCall, maxPut);
    }

    private String buildReason(MarketDataClient.QuoteSnapshot quote,
                               BigDecimal changePct,
                               BigDecimal volumeRatio,
                               long maxOptionAnomalyBps) {
        StringBuilder sb = new StringBuilder();
        sb.append("price=").append(format2(quote.getPrice()))
                .append(", change=").append(format2(changePct)).append("%")
                .append(", volRatio=").append(format2(volumeRatio));
        if (maxOptionAnomalyBps > 0) {
            sb.append(", optionAnomaly=").append(maxOptionAnomalyBps / 100.0).append("x");
        }
        return sb.toString();
    }

    private double score(BigDecimal changePct, BigDecimal volumeRatio, long optionAnomalyBps) {
        double move = Math.min(8.0, changePct.abs().doubleValue());
        double vol = Math.min(8.0, volumeRatio.doubleValue() * 2.0);
        double opt = Math.min(8.0, optionAnomalyBps / 800.0);
        return move + vol + opt;
    }

    private String normalize(String symbol) {
        return symbol == null ? "" : symbol.trim().toUpperCase();
    }

    private boolean containsAny(String text, String... words) {
        for (String w : words) {
            if (text.contains(w.toLowerCase())) {
                return true;
            }
        }
        return false;
    }

    private BigDecimal nvl(BigDecimal value) {
        return value == null ? BigDecimal.ZERO : value;
    }

    private String format2(BigDecimal value) {
        return nvl(value).setScale(2, RoundingMode.HALF_UP).toPlainString();
    }

    public record ScanResult(String symbol, String name, String reason) {}

    private record ScoredStock(String symbol, String name, String reason, double score) {}

    private record ScanCriteria(Direction direction,
                                BigDecimal minAbsChangePct,
                                BigDecimal minVolumeRatio,
                                boolean requireUnusualOptions,
                                int topK,
                                int maxSymbols) {}

    private enum Direction {
        BULLISH,
        BEARISH,
        NEUTRAL
    }
}