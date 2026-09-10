package com.itzixi.ai.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.ChatMessage;
import com.itzixi.ai.tools.StockDataTools;
import com.itzixi.common.annotation.Monitor;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
public class AIChatService {

    @Resource
    private AIService aiService;

    @Resource
    private StockDataTools stockDataTools;

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    @Resource
    private ObjectMapper objectMapper;

    private final Map<String, List<ChatMessage>> historyFallback = new ConcurrentHashMap<>();

    private static final long LIGHT_BUDGET_MS = 3000;
    private static final long HEAVY_BUDGET_MS = 8000;

    private static final String SYSTEM_PROMPT = """
            你是专业美股投资助手。回答要求：
            1) 先给结论，再给依据；
            2) 严格基于用户问题和工具数据；
            3) 不确定时明确说不确定。
            """;

    private static final String COACH_SYSTEM_PROMPT = """
            你是严格、理性的交易教练。
            你要帮助用户建立计划、止损和风险收益比，不要鼓励冲动交易。
            """;

    @Monitor(value = "AIChat", slowThreshold = 5000)
    public String chat(String sessionId, String userMessage) {
        List<ChatMessage> history = getHistory(sessionId);
        history.add(ChatMessage.user(userMessage));

        String prompt = buildChatPrompt(history);
        long budget = inferBudget(userMessage);
        String response = callModelWithBudget(SYSTEM_PROMPT, prompt, budget,
                "请求超时，已降级为简短建议，请稍后重试。");

        history.add(ChatMessage.assistant(response));
        saveHistory(sessionId, history);
        return response;
    }

    @Monitor(value = "AITradingCoach", slowThreshold = 5000)
    public String chatWithCoach(String sessionId, String userMessage) {
        List<ChatMessage> history = getHistory(sessionId);
        history.add(ChatMessage.user(userMessage));

        String prompt = buildChatPrompt(history);
        String response = callModelWithBudget(COACH_SYSTEM_PROMPT, prompt, HEAVY_BUDGET_MS,
                "交易教练响应超时，请先写下入场、止损、止盈三要素后再提交。");

        history.add(ChatMessage.assistant(response));
        saveHistory(sessionId, history);
        return response;
    }

    public String chatWithTools(String sessionId, String userMessage) {
        String toolResult = tryCallTool(userMessage);
        String enhancedMessage = toolResult == null ? userMessage
                : userMessage + "\n\n[Tool Context]\n" + toolResult;
        return chat(sessionId, enhancedMessage);
    }

    public TradeSignal chatSignal(String sessionId, String userMessage) {
        String stockCode = extractStockCode(userMessage);
        String toolResult = tryCallTool(userMessage);

        String prompt = """
                输出严格 JSON，不要任何额外文本。
                字段: symbol,direction,confidence,triggerCondition,invalidationCondition,stopLossSuggestion,takeProfitSuggestion,positionSizing,riskBudgetPct,expectedRMultiple,rationale
                direction 枚举: BULLISH,BEARISH,NEUTRAL
                confidence 0-100 整数
                riskBudgetPct: 单笔风险预算(%)，例如 0.8
                expectedRMultiple: 预期R倍数，例如 2.1
                positionSizing: 仓位建议，例如 0.5R 先建仓 / 30% starter
                结合下面信息给出可执行信号：
                userMessage: %s
                toolContext: %s
                """.formatted(userMessage, toolResult == null ? "N/A" : toolResult);

        String raw = callModelWithBudget(SYSTEM_PROMPT, prompt, HEAVY_BUDGET_MS, "");
        TradeSignal signal = parseSignal(raw, stockCode, toolResult);

        List<ChatMessage> history = getHistory(sessionId);
        history.add(ChatMessage.user(userMessage));
        history.add(ChatMessage.assistant("[SIGNAL] " + toCompactSignal(signal)));
        saveHistory(sessionId, history);

        return signal;
    }

    public void clearHistory(String sessionId) {
        try {
            redisTemplate.delete(historyKey(sessionId));
        } catch (Exception e) {
            log.debug("clear redis history failed: {}", e.getMessage());
        }
        historyFallback.remove(sessionId);
    }

    @SuppressWarnings("unchecked")
    private List<ChatMessage> getHistory(String sessionId) {
        try {
            List<ChatMessage> history = (List<ChatMessage>) redisTemplate.opsForValue().get(historyKey(sessionId));
            if (history != null) {
                historyFallback.put(sessionId, history);
                return history;
            }
        } catch (Exception e) {
            log.debug("read redis history failed: {}", e.getMessage());
        }
        return new ArrayList<>(historyFallback.getOrDefault(sessionId, new ArrayList<>()));
    }

    private void saveHistory(String sessionId, List<ChatMessage> history) {
        List<ChatMessage> toSave = history;
        if (history.size() > 20) {
            toSave = history.subList(history.size() - 20, history.size());
        }
        historyFallback.put(sessionId, new ArrayList<>(toSave));
        try {
            redisTemplate.opsForValue().set(historyKey(sessionId), toSave, 30, TimeUnit.MINUTES);
        } catch (Exception e) {
            log.debug("save redis history failed: {}", e.getMessage());
        }
    }

    private String historyKey(String sessionId) {
        return "chat:history:" + sessionId;
    }

    private String buildChatPrompt(List<ChatMessage> history) {
        StringBuilder prompt = new StringBuilder();
        for (ChatMessage msg : history) {
            if ("user".equals(msg.getRole())) {
                prompt.append("User: ").append(msg.getContent()).append("\n\n");
            } else if ("assistant".equals(msg.getRole())) {
                prompt.append("Assistant: ").append(msg.getContent()).append("\n\n");
            }
        }
        return prompt.toString();
    }

    private String callModelWithBudget(String systemPrompt,
                                       String prompt,
                                       long budgetMs,
                                       String timeoutFallback) {
        long start = System.currentTimeMillis();
        try {
            String response = CompletableFuture
                    .supplyAsync(() -> aiService.chatWithSystem(systemPrompt, prompt))
                    .orTimeout(Math.max(500, budgetMs), TimeUnit.MILLISECONDS)
                    .exceptionally(ex -> timeoutFallback)
                    .join();

            long elapsed = System.currentTimeMillis() - start;
            if (elapsed > budgetMs) {
                log.warn("ai response exceeded budget: elapsed={}ms budget={}ms", elapsed, budgetMs);
            }
            return response == null || response.isBlank() ? timeoutFallback : response;
        } catch (Exception e) {
            log.warn("ai call with budget failed: {}", e.getMessage());
            return timeoutFallback;
        }
    }

    private long inferBudget(String userMessage) {
        String msg = userMessage == null ? "" : userMessage.toLowerCase(Locale.ROOT);
        boolean heavy = containsAny(msg, "rag", "report", "研报", "多因子", "策略", "回测", "portfolio");
        return heavy ? HEAVY_BUDGET_MS : LIGHT_BUDGET_MS;
    }

    private String tryCallTool(String message) {
        try {
            if (message == null) {
                return null;
            }
            String msg = message.toLowerCase(Locale.ROOT);
            String stockCode = extractStockCode(message);

            if (stockCode != null && containsAny(msg, "news", "新闻")) {
                var news = stockDataTools.getRecentNews(stockCode, 7);
                return formatNews(news);
            }
            if (stockCode != null && containsAny(msg, "price", "股价", "行情")) {
                var price = stockDataTools.getRealTimePrice(stockCode);
                return formatPrice(price);
            }
            if (stockCode != null && containsAny(msg, "financial", "估值", "pe", "财务")) {
                var fin = stockDataTools.getFinancials(stockCode);
                return formatFinancials(fin);
            }
            if (containsAny(msg, "hot", "热门")) {
                var hotStocks = stockDataTools.getHotStocks(10);
                return "hotStocks=" + String.join(",", hotStocks);
            }
        } catch (Exception e) {
            log.warn("tool call failed: {}", e.getMessage());
        }
        return null;
    }

    private TradeSignal parseSignal(String raw, String symbol, String toolContext) {
        try {
            if (raw != null && raw.contains("{")) {
                TradeSignal parsed = objectMapper.readValue(raw, TradeSignal.class);
                normalizeSignal(parsed, symbol, toolContext);
                return parsed;
            }
        } catch (Exception ignored) {
        }

        TradeSignal fallback = new TradeSignal();
        fallback.setSymbol(symbol == null ? "N/A" : symbol);
        fallback.setDirection("NEUTRAL");
        fallback.setConfidence(45);
        fallback.setTriggerCondition("price breaks recent high with volume > 1.8x avg");
        fallback.setInvalidationCondition("price closes below support and volume expands");
        fallback.setStopLossSuggestion("1.5%-3% below entry by volatility");
        fallback.setTakeProfitSuggestion("first target at 1.5R, trail after 2R");
        fallback.setPositionSizing("30%-40% starter size, add on confirmation");
        fallback.setRiskBudgetPct(BigDecimal.valueOf(1.0));
        fallback.setExpectedRMultiple(BigDecimal.valueOf(1.8));
        fallback.setRationale("LLM did not return valid JSON; fallback signal generated from risk template.");
        fallback.setToolContext(toolContext);
        return fallback;
    }

    private void normalizeSignal(TradeSignal signal, String symbol, String toolContext) {
        if (signal.getSymbol() == null || signal.getSymbol().isBlank()) {
            signal.setSymbol(symbol == null ? "N/A" : symbol);
        }
        if (signal.getDirection() == null || signal.getDirection().isBlank()) {
            signal.setDirection("NEUTRAL");
        }
        if (signal.getConfidence() == null) {
            signal.setConfidence(50);
        }
        signal.setConfidence(Math.max(0, Math.min(100, signal.getConfidence())));
        if (signal.getTriggerCondition() == null || signal.getTriggerCondition().isBlank()) {
            signal.setTriggerCondition("wait for confirmation with volume expansion");
        }
        if (signal.getInvalidationCondition() == null || signal.getInvalidationCondition().isBlank()) {
            signal.setInvalidationCondition("thesis breaks with adverse price action");
        }
        if (signal.getStopLossSuggestion() == null || signal.getStopLossSuggestion().isBlank()) {
            signal.setStopLossSuggestion("define stop before entry");
        }
        if (signal.getTakeProfitSuggestion() == null || signal.getTakeProfitSuggestion().isBlank()) {
            signal.setTakeProfitSuggestion("scale out by predefined R targets");
        }
        if (signal.getPositionSizing() == null || signal.getPositionSizing().isBlank()) {
            signal.setPositionSizing("30% starter size, add only after trigger confirms");
        }
        if (signal.getRiskBudgetPct() == null) {
            signal.setRiskBudgetPct(BigDecimal.valueOf(1.0));
        }
        if (signal.getExpectedRMultiple() == null) {
            signal.setExpectedRMultiple(BigDecimal.valueOf(1.8));
        }
        signal.setRiskBudgetPct(signal.getRiskBudgetPct()
                .max(BigDecimal.valueOf(0.1))
                .min(BigDecimal.valueOf(5.0))
                .setScale(2, RoundingMode.HALF_UP));
        signal.setExpectedRMultiple(signal.getExpectedRMultiple()
                .max(BigDecimal.valueOf(0.5))
                .min(BigDecimal.valueOf(10.0))
                .setScale(2, RoundingMode.HALF_UP));
        signal.setToolContext(toolContext);
    }

    private boolean containsAny(String text, String... words) {
        for (String w : words) {
            if (text.contains(w.toLowerCase(Locale.ROOT))) {
                return true;
            }
        }
        return false;
    }

    private String extractStockCode(String message) {
        if (message == null) {
            return null;
        }
        String[] words = message.split("\\s+");
        for (String word : words) {
            if (word.matches("[A-Z]{1,5}")) {
                return word;
            }
        }
        return null;
    }

    private String formatNews(List<?> news) {
        if (news == null || news.isEmpty()) {
            return "news=none";
        }
        return "newsCount=" + news.size();
    }

    private String formatPrice(StockDataTools.StockPrice price) {
        if (price == null) {
            return "price=na";
        }
        return "price=" + format2(price.getCurrentPrice())
                + ",change=" + format2(price.getChangeAmount())
                + ",changePct=" + format2(price.getChangePercent())
                + ",vol=" + (price.getVolume() == null ? 0 : price.getVolume())
                + ",avgVol=" + (price.getAvgVolume() == null ? 0 : price.getAvgVolume());
    }

    private String formatFinancials(StockDataTools.FinancialData fin) {
        if (fin == null) {
            return "financials=na";
        }
        return "pe=" + format2(fin.getPeRatio())
                + ",eps=" + format2(fin.getEps())
                + ",mktCap=" + format2(fin.getMarketCap())
                + ",52wHigh=" + format2(fin.getFiftyTwoWeekHigh())
                + ",52wLow=" + format2(fin.getFiftyTwoWeekLow());
    }

    private String toCompactSignal(TradeSignal signal) {
        return signal.getSymbol() + ":" + signal.getDirection() + "@" + signal.getConfidence();
    }

    private String format2(BigDecimal value) {
        if (value == null) {
            return "0.00";
        }
        return value.setScale(2, RoundingMode.HALF_UP).toPlainString();
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TradeSignal {
        private String symbol;
        private String direction;
        private Integer confidence;
        private String triggerCondition;
        private String invalidationCondition;
        private String stopLossSuggestion;
        private String takeProfitSuggestion;
        private String positionSizing;
        private BigDecimal riskBudgetPct;
        private BigDecimal expectedRMultiple;
        private String rationale;
        private String toolContext;
    }
}
