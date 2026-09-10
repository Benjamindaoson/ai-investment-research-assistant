package com.itzixi.ai.client;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Arrays;
import java.util.ArrayList;
import java.util.List;

/**
 * Client for delegating advanced AI tasks to the Python Engine.
 * Supports calling LangGraph Agents and Pandas Backtesting engine.
 */
@Slf4j
@Service
public class AIEngineClient {

    private final RestTemplate restTemplate;
    
    @Value("${spring.ai.engine.base-url}")
    private String engineBaseUrl;

    public AIEngineClient(RestTemplateBuilder builder) {
        this.restTemplate = builder.build();
    }

    public ComprehensiveReport orchestrateAgents(StockDataPayload payload) {
        String url = engineBaseUrl + "/api/v1/orchestrate";
        try {
            log.info("Sending payload to Python AI Engine at {}", url);
            return restTemplate.postForObject(url, payload, ComprehensiveReport.class);
        } catch (Exception e) {
            log.error("Failed to call Python Orchestrator", e);
            throw new RuntimeException("Python AI Engine Error", e);
        }
    }

    public BacktestResult runBacktest(List<SignalRecordDto> signals) {
        String url = engineBaseUrl + "/api/v1/backtest";
        try {
            log.info("Sending {} signals to Python Backtest Engine at {}", signals.size(), url);
            return restTemplate.postForObject(url, signals, BacktestResult.class);
        } catch (Exception e) {
            log.error("Failed to call Python Backtester", e);
            throw new RuntimeException("Python AI Engine Error", e);
        }
    }

    public List<HistoricalCaseDto> rerankCandidates(RerankRequest request) {
        String url = engineBaseUrl + "/api/v1/rerank";
        try {
            log.info("Sending {} candidates to Python Reranker at {}", request.getCandidates().size(), url);
            HistoricalCaseDto[] result = restTemplate.postForObject(url, request, HistoricalCaseDto[].class);
            return result != null ? Arrays.asList(result) : new ArrayList<>();
        } catch (Exception e) {
            log.error("Failed to call Python Reranker", e);
            throw new RuntimeException("Python AI Engine Error", e);
        }
    }

    // DTO Definitions
    @Data
    public static class StockDataPayload {
        private String stock_code;
        private double price;
        private List<String> news;
    }

    @Data
    public static class ComprehensiveReport {
        private String stock_code;
        private String executive_summary;
        private String investment_thesis;
        private List<String> catalysts;
        private List<String> risk_factors;
        private String conclusion;
        private String advice;
        private int confidence;
    }

    @Data
    public static class SignalRecordDto {
        private String id;
        private String symbol;
        private String direction;
        private double entry_price;
        private int confidence;
        private String created_at;
    }

    @Data
    public static class BacktestResult {
        private int total_signals;
        private double hit_rate_pct;
        private double avg_return_pct;
        private String status;
        private double weight;
    }

    @Data
    public static class HistoricalCaseDto {
        private String id;
        private String stock_code;
        private String title;
        private String description;
        private String analysis;
        private String actual_impact;
        private String occurred_at;
    }

    @Data
    @lombok.AllArgsConstructor
    @lombok.NoArgsConstructor
    public static class RerankRequest {
        private String query;
        private List<HistoricalCaseDto> candidates;
        private int top_k;
    }
}
