package com.itzixi.ai.tools;

import com.itzixi.ai.marketdata.MarketDataClient;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.RssService;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;

/**
 * Stock data tools for AI services.
 *
 * Replaces legacy mock price/financial outputs with real market snapshots.
 */
@Slf4j
@Service
public class StockDataTools {

    @Resource
    private MarketDataClient marketDataClient;

    @Resource
    private RssService rssService;

    public List<USStockRss> getRecentNews(String stockCode, int days) {
        return rssService.getRecentByStockCode(normalize(stockCode), Math.max(1, days));
    }

    public List<USStockRss> searchNews(String keyword, int limit) {
        return rssService.searchByKeyword(keyword == null ? "" : keyword.trim(), Math.max(1, limit));
    }

    public StockPrice getRealTimePrice(String stockCode) {
        String symbol = normalize(stockCode);
        MarketDataClient.QuoteSnapshot quote = marketDataClient.getQuote(symbol);

        StockPrice out = new StockPrice();
        out.setStockCode(symbol);
        out.setName(quote.getName());
        out.setCurrency(quote.getCurrency() == null ? "USD" : quote.getCurrency());
        out.setSource("yahoo.quote");
        out.setTimestamp(Instant.now());
        out.setAvailable(quote.isAvailable());

        BigDecimal current = nvl(quote.getPrice());
        BigDecimal prev = nvl(quote.getPreviousClose());
        BigDecimal change = quote.getChange() != null ? quote.getChange() : current.subtract(prev);
        BigDecimal pct = quote.getChangePercent();
        if (pct == null && prev.compareTo(BigDecimal.ZERO) > 0) {
            pct = change
                    .multiply(BigDecimal.valueOf(100))
                    .divide(prev, 4, RoundingMode.HALF_UP);
        }

        out.setCurrentPrice(current);
        out.setPreviousClose(prev);
        out.setChangeAmount(change);
        out.setChangePercent(pct == null ? BigDecimal.ZERO : pct);
        out.setVolume(quote.getVolume() == null ? 0L : quote.getVolume());
        out.setAvgVolume(quote.getAvgVolume() == null ? 0L : quote.getAvgVolume());

        return out;
    }

    public FinancialData getFinancials(String stockCode) {
        String symbol = normalize(stockCode);
        MarketDataClient.QuoteSnapshot quote = marketDataClient.getQuote(symbol);

        FinancialData out = new FinancialData();
        out.setStockCode(symbol);
        out.setName(quote.getName());
        out.setPeRatio(quote.getPeRatio());
        out.setEps(quote.getEps());
        out.setMarketCap(quote.getMarketCap());
        out.setFiftyTwoWeekHigh(quote.getFiftyTwoWeekHigh());
        out.setFiftyTwoWeekLow(quote.getFiftyTwoWeekLow());
        out.setSource("yahoo.quote");
        out.setTimestamp(Instant.now());
        out.setAvailable(quote.isAvailable());
        return out;
    }

    public List<String> getHotStocks(int limit) {
        int safeLimit = Math.max(1, Math.min(100, limit));
        List<String> hot = rssService.getHotStocks(safeLimit);
        if (hot == null) {
            return new ArrayList<>();
        }
        return hot;
    }

    private String normalize(String stockCode) {
        return stockCode == null ? "" : stockCode.trim().toUpperCase();
    }

    private BigDecimal nvl(BigDecimal value) {
        return value == null ? BigDecimal.ZERO : value;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class StockPrice {
        private String stockCode;
        private String name;
        private String currency;
        private BigDecimal currentPrice;
        private BigDecimal previousClose;
        private BigDecimal changeAmount;
        private BigDecimal changePercent;
        private Long volume;
        private Long avgVolume;
        private String source;
        private Instant timestamp;
        private boolean available;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FinancialData {
        private String stockCode;
        private String name;
        private BigDecimal peRatio;
        private BigDecimal eps;
        private BigDecimal marketCap;
        private BigDecimal fiftyTwoWeekHigh;
        private BigDecimal fiftyTwoWeekLow;
        private String source;
        private Instant timestamp;
        private boolean available;
    }
}
