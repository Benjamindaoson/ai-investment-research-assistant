package com.itzixi.ai.marketdata;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.List;

@Slf4j
@Component
public class MarketDataClient {

    private static final String UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";
    private static final Duration CONNECT_TIMEOUT = Duration.ofSeconds(2);
    private static final Duration REQUEST_TIMEOUT = Duration.ofSeconds(5);

    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(CONNECT_TIMEOUT)
            .build();

    private final ObjectMapper objectMapper;

    private final Cache<String, QuoteSnapshot> quoteCache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofSeconds(15))
            .maximumSize(2000)
            .build();

    private final Cache<String, OptionsSnapshot> optionsCache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofSeconds(30))
            .maximumSize(1000)
            .build();

    private final Cache<String, PriceHistory> historyCache = Caffeine.newBuilder()
            .expireAfterWrite(Duration.ofMinutes(10))
            .maximumSize(1000)
            .build();

    public MarketDataClient(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public QuoteSnapshot getQuote(String symbol) {
        String key = normalizeSymbol(symbol);
        QuoteSnapshot cached = quoteCache.getIfPresent(key);
        if (cached != null) {
            return cached;
        }

        try {
            String url = "https://query1.finance.yahoo.com/v7/finance/quote?symbols=" + encode(key);
            JsonNode root = getJson(url);
            JsonNode result = root.path("quoteResponse").path("result");
            if (!result.isArray() || result.isEmpty()) {
                return QuoteSnapshot.unavailable(key);
            }

            JsonNode n = result.get(0);
            QuoteSnapshot snapshot = new QuoteSnapshot();
            snapshot.setSymbol(key);
            snapshot.setName(text(n, "longName", text(n, "shortName", key)));
            snapshot.setCurrency(text(n, "currency", "USD"));
            snapshot.setMarketState(text(n, "marketState", "UNKNOWN"));
            snapshot.setPrice(decimal(n, "regularMarketPrice"));
            snapshot.setPreviousClose(decimal(n, "regularMarketPreviousClose"));
            snapshot.setChange(decimal(n, "regularMarketChange"));
            snapshot.setChangePercent(decimal(n, "regularMarketChangePercent"));
            snapshot.setVolume(longValue(n, "regularMarketVolume"));
            snapshot.setAvgVolume(longValue(n, "averageDailyVolume3Month"));
            snapshot.setMarketCap(decimal(n, "marketCap"));
            snapshot.setPeRatio(decimal(n, "trailingPE"));
            snapshot.setEps(decimal(n, "epsTrailingTwelveMonths"));
            snapshot.setFiftyTwoWeekHigh(decimal(n, "fiftyTwoWeekHigh"));
            snapshot.setFiftyTwoWeekLow(decimal(n, "fiftyTwoWeekLow"));
            snapshot.setTimestamp(Instant.now());
            snapshot.setAvailable(snapshot.getPrice() != null);

            quoteCache.put(key, snapshot);
            return snapshot;
        } catch (Exception e) {
            log.warn("quote fetch failed for {}: {}", key, e.getMessage());
            return QuoteSnapshot.unavailable(key);
        }
    }

    public OptionsSnapshot getOptionsSnapshot(String symbol) {
        String key = normalizeSymbol(symbol);
        OptionsSnapshot cached = optionsCache.getIfPresent(key);
        if (cached != null) {
            return cached;
        }

        try {
            String url = "https://query2.finance.yahoo.com/v7/finance/options/" + encode(key);
            JsonNode root = getJson(url);
            JsonNode result = root.path("optionChain").path("result");
            if (!result.isArray() || result.isEmpty()) {
                return OptionsSnapshot.unavailable(key);
            }

            JsonNode first = result.get(0);
            JsonNode options = first.path("options");
            if (!options.isArray() || options.isEmpty()) {
                return OptionsSnapshot.unavailable(key);
            }

            JsonNode optionSet = options.get(0);
            List<OptionContract> calls = parseContracts(optionSet.path("calls"), "CALL");
            List<OptionContract> puts = parseContracts(optionSet.path("puts"), "PUT");
            calls.sort((a, b) -> Long.compare(b.getVolumeToOiBps(), a.getVolumeToOiBps()));
            puts.sort((a, b) -> Long.compare(b.getVolumeToOiBps(), a.getVolumeToOiBps()));

            OptionsSnapshot snapshot = new OptionsSnapshot();
            snapshot.setSymbol(key);
            snapshot.setExpiryEpoch(optionSet.path("expirationDate").asLong(0));
            snapshot.setCalls(calls.stream().limit(20).toList());
            snapshot.setPuts(puts.stream().limit(20).toList());
            snapshot.setTimestamp(Instant.now());
            snapshot.setAvailable(!snapshot.getCalls().isEmpty() || !snapshot.getPuts().isEmpty());

            optionsCache.put(key, snapshot);
            return snapshot;
        } catch (Exception e) {
            log.warn("options fetch failed for {}: {}", key, e.getMessage());
            return OptionsSnapshot.unavailable(key);
        }
    }

    public PriceHistory getHistory(String symbol, int days) {
        String key = normalizeSymbol(symbol) + ":" + days;
        PriceHistory cached = historyCache.getIfPresent(key);
        if (cached != null) {
            return cached;
        }

        try {
            int clampedDays = Math.max(2, Math.min(days, 365));
            String range = clampedDays <= 7 ? "7d" : (clampedDays <= 30 ? "1mo" : (clampedDays <= 90 ? "3mo" : "1y"));
            String url = "https://query1.finance.yahoo.com/v8/finance/chart/" + encode(normalizeSymbol(symbol))
                    + "?interval=1d&range=" + range;

            JsonNode root = getJson(url);
            JsonNode result = root.path("chart").path("result");
            if (!result.isArray() || result.isEmpty()) {
                return PriceHistory.unavailable(symbol);
            }

            JsonNode first = result.get(0);
            JsonNode timestamps = first.path("timestamp");
            JsonNode closes = first.path("indicators").path("quote");
            if (!closes.isArray() || closes.isEmpty()) {
                return PriceHistory.unavailable(symbol);
            }
            JsonNode closeArr = closes.get(0).path("close");
            if (!timestamps.isArray() || !closeArr.isArray()) {
                return PriceHistory.unavailable(symbol);
            }

            List<PricePoint> points = new ArrayList<>();
            int size = Math.min(timestamps.size(), closeArr.size());
            for (int i = 0; i < size; i++) {
                JsonNode close = closeArr.get(i);
                if (close == null || close.isNull()) {
                    continue;
                }
                long ts = timestamps.get(i).asLong(0);
                LocalDate day = Instant.ofEpochSecond(ts).atZone(ZoneOffset.UTC).toLocalDate();
                points.add(new PricePoint(day, close.decimalValue()));
            }

            PriceHistory history = new PriceHistory();
            history.setSymbol(normalizeSymbol(symbol));
            history.setPoints(points);
            history.setAvailable(!points.isEmpty());
            history.setTimestamp(Instant.now());
            historyCache.put(key, history);
            return history;
        } catch (Exception e) {
            log.warn("history fetch failed for {}: {}", symbol, e.getMessage());
            return PriceHistory.unavailable(symbol);
        }
    }

    private List<OptionContract> parseContracts(JsonNode arr, String type) {
        List<OptionContract> out = new ArrayList<>();
        if (!arr.isArray()) {
            return out;
        }
        for (JsonNode n : arr) {
            OptionContract c = new OptionContract();
            c.setType(type);
            c.setContractSymbol(text(n, "contractSymbol", ""));
            c.setStrike(decimal(n, "strike"));
            c.setLastPrice(decimal(n, "lastPrice"));
            c.setBid(decimal(n, "bid"));
            c.setAsk(decimal(n, "ask"));
            c.setOpenInterest(longValue(n, "openInterest"));
            c.setVolume(longValue(n, "volume"));
            c.setImpliedVolatility(decimal(n, "impliedVolatility"));
            c.setInTheMoney(n.path("inTheMoney").asBoolean(false));
            long oi = c.getOpenInterest() == null ? 0 : c.getOpenInterest();
            long vol = c.getVolume() == null ? 0 : c.getVolume();
            c.setVolumeToOiBps((vol * 10000L) / Math.max(1L, oi));
            out.add(c);
        }
        return out;
    }

    private JsonNode getJson(String url) throws Exception {
        HttpRequest req = HttpRequest.newBuilder(URI.create(url))
                .timeout(REQUEST_TIMEOUT)
                .header("User-Agent", UA)
                .GET()
                .build();
        HttpResponse<String> resp = httpClient.send(req, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
        if (resp.statusCode() >= 400) {
            throw new IllegalStateException("HTTP " + resp.statusCode());
        }
        return objectMapper.readTree(resp.body());
    }

    private String normalizeSymbol(String symbol) {
        return symbol == null ? "" : symbol.trim().toUpperCase();
    }

    private String encode(String value) {
        return URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    private String text(JsonNode n, String field, String defaultValue) {
        JsonNode x = n.path(field);
        return x.isMissingNode() || x.isNull() ? defaultValue : x.asText(defaultValue);
    }

    private BigDecimal decimal(JsonNode n, String field) {
        JsonNode x = n.path(field);
        if (x.isMissingNode() || x.isNull()) {
            return null;
        }
        return x.decimalValue();
    }

    private Long longValue(JsonNode n, String field) {
        JsonNode x = n.path(field);
        if (x.isMissingNode() || x.isNull()) {
            return null;
        }
        return x.asLong();
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class QuoteSnapshot {
        private String symbol;
        private String name;
        private String currency;
        private String marketState;
        private BigDecimal price;
        private BigDecimal previousClose;
        private BigDecimal change;
        private BigDecimal changePercent;
        private Long volume;
        private Long avgVolume;
        private BigDecimal marketCap;
        private BigDecimal peRatio;
        private BigDecimal eps;
        private BigDecimal fiftyTwoWeekHigh;
        private BigDecimal fiftyTwoWeekLow;
        private Instant timestamp;
        private boolean available;

        public static QuoteSnapshot unavailable(String symbol) {
            QuoteSnapshot s = new QuoteSnapshot();
            s.setSymbol(symbol);
            s.setName(symbol);
            s.setAvailable(false);
            s.setTimestamp(Instant.now());
            return s;
        }
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OptionsSnapshot {
        private String symbol;
        private long expiryEpoch;
        private List<OptionContract> calls = new ArrayList<>();
        private List<OptionContract> puts = new ArrayList<>();
        private Instant timestamp;
        private boolean available;

        public static OptionsSnapshot unavailable(String symbol) {
            OptionsSnapshot s = new OptionsSnapshot();
            s.setSymbol(symbol);
            s.setAvailable(false);
            s.setTimestamp(Instant.now());
            return s;
        }
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OptionContract {
        private String type;
        private String contractSymbol;
        private BigDecimal strike;
        private BigDecimal lastPrice;
        private BigDecimal bid;
        private BigDecimal ask;
        private Long openInterest;
        private Long volume;
        private BigDecimal impliedVolatility;
        private boolean inTheMoney;
        private long volumeToOiBps;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PriceHistory {
        private String symbol;
        private List<PricePoint> points = new ArrayList<>();
        private Instant timestamp;
        private boolean available;

        public static PriceHistory unavailable(String symbol) {
            PriceHistory s = new PriceHistory();
            s.setSymbol(symbol == null ? "" : symbol.toUpperCase());
            s.setTimestamp(Instant.now());
            s.setAvailable(false);
            return s;
        }
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class PricePoint {
        private LocalDate date;
        private BigDecimal close;
    }
}
