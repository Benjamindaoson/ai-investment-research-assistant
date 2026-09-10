package com.itzixi.test;

import com.itzixi.ai.controller.product.TradingProductController;
import com.itzixi.ai.service.TradingProductService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyList;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class TradingProductControllerRegressionTest {

    private TradingProductService tradingProductService;
    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        tradingProductService = mock(TradingProductService.class);
        TradingProductController controller = new TradingProductController();
        ReflectionTestUtils.setField(controller, "tradingProductService", tradingProductService);
        mockMvc = MockMvcBuilders.standaloneSetup(controller).build();
    }

    @Test
    void shouldGenerateBatchSignalsWithDecisionFields() throws Exception {
        TradingProductService.SignalRecord signal = new TradingProductService.SignalRecord();
        signal.setSignalId("sig-1");
        signal.setSymbol("AAPL");
        signal.setDirection("BULLISH");
        signal.setSignalCreditScore(BigDecimal.valueOf(82.5));
        signal.setRiskBudgetPct(BigDecimal.valueOf(1.2));
        signal.setExpectedRMultiple(BigDecimal.valueOf(2.3));
        signal.setPositionSizing("30% starter");
        Map<String, BigDecimal> breakdown = new LinkedHashMap<>();
        breakdown.put("historicalHitRate", BigDecimal.valueOf(75));
        signal.setCreditBreakdown(breakdown);

        when(tradingProductService.generateSignalsBatch(anyString(), anyString(), anyString(), anyList(), anyInt()))
                .thenReturn(List.of(signal));

        String body = """
                {
                  "sessionId":"demo-user",
                  "message":"batch execute",
                  "strategyTemplateId":"volatility",
                  "symbols":["AAPL","MSFT"],
                  "limit":10
                }
                """;

        mockMvc.perform(post("/api/ai/product/signals/generate/batch")
                        .contentType("application/json")
                        .content(body))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].symbol").value("AAPL"))
                .andExpect(jsonPath("$.data[0].signalCreditScore").value(82.5))
                .andExpect(jsonPath("$.data[0].riskBudgetPct").value(1.2))
                .andExpect(jsonPath("$.data[0].expectedRMultiple").value(2.3))
                .andExpect(jsonPath("$.data[0].positionSizing").value("30% starter"));
    }

    @Test
    void shouldReturnMetricsAndGovernance() throws Exception {
        TradingProductService.SignalMetrics metrics = new TradingProductService.SignalMetrics();
        metrics.setTotalSignals(12);
        metrics.setWeeklyEffectiveSignals(5);
        metrics.setApproximateSharpe(BigDecimal.valueOf(1.42));
        metrics.setApproximateProfitFactor(BigDecimal.valueOf(1.85));
        metrics.setMaxDrawdownPct(BigDecimal.valueOf(6.3));

        TradingProductService.StrategyGovernance governance = new TradingProductService.StrategyGovernance();
        governance.setStrategyTemplateId("volatility");
        governance.setStatus("ACTIVE");
        governance.setWeight(BigDecimal.ONE);
        governance.setTotal(30);
        governance.setHitRatePct(BigDecimal.valueOf(63.5));
        governance.setReason("stable");

        when(tradingProductService.aggregateMetrics(any())).thenReturn(metrics);
        when(tradingProductService.listStrategyGovernance(any())).thenReturn(List.of(governance));

        mockMvc.perform(get("/api/ai/product/signals/metrics").param("sessionId", "demo-user"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data.totalSignals").value(12))
                .andExpect(jsonPath("$.data.weeklyEffectiveSignals").value(5))
                .andExpect(jsonPath("$.data.approximateSharpe").value(1.42));

        mockMvc.perform(get("/api/ai/product/signals/governance").param("sessionId", "demo-user"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.code").value(200))
                .andExpect(jsonPath("$.data[0].strategyTemplateId").value("volatility"))
                .andExpect(jsonPath("$.data[0].status").value("ACTIVE"))
                .andExpect(jsonPath("$.data[0].hitRatePct").value(63.5));
    }
}
