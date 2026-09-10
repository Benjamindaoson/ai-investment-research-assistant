package com.itzixi.ai.service.retail;

import com.itzixi.ai.marketdata.MarketDataClient;
import com.itzixi.common.annotation.Monitor;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Service
public class SmartMoneyService {

    @Resource
    private MarketDataClient marketDataClient;

    @Monitor(value = "SmartMoney", slowThreshold = 2000)
    public List<SmartMoneySignal> getSmartMoneySignals(String stockCode) {
        String symbol = normalize(stockCode);
        List<SmartMoneySignal> signals = new ArrayList<>();

        MarketDataClient.QuoteSnapshot quote = marketDataClient.getQuote(symbol);
        if (quote.isAvailable()) {
            long volume = quote.getVolume() == null ? 0L : quote.getVolume();
            long avgVolume = quote.getAvgVolume() == null ? 1L : Math.max(1L, quote.getAvgVolume());
            BigDecimal volumeRatio = BigDecimal.valueOf(volume)
                    .divide(BigDecimal.valueOf(avgVolume), 4, RoundingMode.HALF_UP);

            if (volumeRatio.compareTo(new BigDecimal("2.50")) >= 0) {
                String sentiment = nvl(quote.getChangePercent()).compareTo(BigDecimal.ZERO) >= 0 ? "Bullish" : "Bearish";
                String title = sentiment.equals("Bullish") ? "High-volume accumulation" : "High-volume distribution";
                signals.add(new SmartMoneySignal(
                        "Block Trade Proxy",
                        title,
                        "Volume ratio=" + format2(volumeRatio) + "x, change=" + format2(quote.getChangePercent()) + "%",
                        sentiment,
                        "High"
                ));
            }
        }

        MarketDataClient.OptionsSnapshot options = marketDataClient.getOptionsSnapshot(symbol);
        if (options.isAvailable()) {
            long callVol = options.getCalls() == null ? 0L
                    : options.getCalls().stream().mapToLong(c -> c.getVolume() == null ? 0L : c.getVolume()).sum();
            long putVol = options.getPuts() == null ? 0L
                    : options.getPuts().stream().mapToLong(c -> c.getVolume() == null ? 0L : c.getVolume()).sum();

            long topCallBps = options.getCalls() == null ? 0L
                    : options.getCalls().stream().mapToLong(MarketDataClient.OptionContract::getVolumeToOiBps).max().orElse(0L);
            long topPutBps = options.getPuts() == null ? 0L
                    : options.getPuts().stream().mapToLong(MarketDataClient.OptionContract::getVolumeToOiBps).max().orElse(0L);

            if (Math.max(topCallBps, topPutBps) >= 3000) {
                boolean callDominant = topCallBps >= topPutBps;
                signals.add(new SmartMoneySignal(
                        "Option Alert",
                        callDominant ? "Unusual call activity" : "Unusual put activity",
                        "max(volume/OI)=" + (Math.max(topCallBps, topPutBps) / 100.0) + "x",
                        callDominant ? "Bullish" : "Bearish",
                        "Very High"
                ));
            }

            if (callVol + putVol > 0) {
                double putCallRatio = (double) putVol / Math.max(1L, callVol);
                if (putCallRatio > 1.3 || putCallRatio < 0.7) {
                    String sentiment = putCallRatio < 0.7 ? "Bullish" : "Bearish";
                    signals.add(new SmartMoneySignal(
                            "Option Flow",
                            "Put/Call imbalance",
                            "putVol=" + putVol + ", callVol=" + callVol + ", ratio=" + String.format("%.2f", putCallRatio),
                            sentiment,
                            "Medium"
                    ));
                }
            }
        }

        if (signals.isEmpty()) {
            signals.add(new SmartMoneySignal(
                    "Neutral",
                    "No strong smart-money anomaly",
                    "No significant volume or options anomaly detected from public feed",
                    "Neutral",
                    "Low"
            ));
        }

        return signals;
    }

    private String normalize(String stockCode) {
        return stockCode == null ? "" : stockCode.trim().toUpperCase();
    }

    private BigDecimal nvl(BigDecimal v) {
        return v == null ? BigDecimal.ZERO : v;
    }

    private String format2(BigDecimal value) {
        return nvl(value).setScale(2, RoundingMode.HALF_UP).toPlainString();
    }

    @Data
    @AllArgsConstructor
    @NoArgsConstructor
    public static class SmartMoneySignal {
        private String type;
        private String title;
        private String description;
        private String sentiment;
        private String urgency;
    }
}