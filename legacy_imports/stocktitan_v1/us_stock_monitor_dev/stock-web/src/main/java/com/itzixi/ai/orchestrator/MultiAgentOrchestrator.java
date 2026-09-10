package com.itzixi.ai.orchestrator;

import com.itzixi.ai.agent.AdvisorAgent;
import com.itzixi.ai.agent.AnalystAgent;
import com.itzixi.ai.agent.RiskManagerAgent;
import com.itzixi.ai.client.AIEngineClient;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * 多智能体协作编排器 (V4 - Python Microservice Delegator)
 * 协调分析师、风控师、投资顾问三个智能体协同工作
 *
 * @author 风间影月
 * @version 4.0 - Python LangGraph Native
 */
@Slf4j
@Service
public class MultiAgentOrchestrator {

    @Resource
    private AIEngineClient aiEngineClient;

    @Resource
    private RiskManagerAgent riskManagerAgent; // Keep localized for smartAlert quick checks

    private final ExecutorService executorService = Executors.newFixedThreadPool(10);

    /**
     * 完整的多智能体分析流程 (Delegated to Python)
     */
    @Monitor(value = "多智能体协作分析(LangGraph)", slowThreshold = 10000)
    public ComprehensiveReport analyze(USStockRss stock) {
        log.info("🤖 启动多智能体协作分析(Python Engine): {}", stock.getStockCode());

        ComprehensiveReport report = new ComprehensiveReport();
        report.setStockCode(stock.getStockCode());
        report.setAnalysisTime(LocalDateTime.now());

        try {
            // Build Payload for Python
            AIEngineClient.StockDataPayload payload = new AIEngineClient.StockDataPayload();
            payload.setStock_code(stock.getStockCode());
            payload.setPrice(stock.getCurrentPrice() != null ? stock.getCurrentPrice().doubleValue() : 0.0);
            
            List<String> news = new ArrayList<>();
            if (stock.getTitle() != null) news.add(stock.getTitle());
            if (stock.getDescription() != null) news.add(stock.getDescription());
            payload.setNews(news);

            // Synchronous call to Python Engine (which runs asynchronous LangGraph internally)
            AIEngineClient.ComprehensiveReport pythonReport = aiEngineClient.orchestrateAgents(payload);

            // Map back to legacy Java structure to prevent downstream controller breaking
            AnalystAgent.AnalysisReport analysis = new AnalystAgent.AnalysisReport();
            analysis.setExecutiveSummary(pythonReport.getExecutive_summary());
            analysis.setInvestmentThesis(pythonReport.getInvestment_thesis());
            analysis.setKeyCatalysts(pythonReport.getCatalysts());
            report.setAnalysisReport(analysis);

            RiskManagerAgent.RiskReport risk = new RiskManagerAgent.RiskReport();
            risk.setRiskFactors(pythonReport.getRisk_factors() != null ? String.join(", ", pythonReport.getRisk_factors()) : "None");
            report.setRiskReport(risk);

            AdvisorAgent.InvestmentAdvice advice = new AdvisorAgent.InvestmentAdvice();
            advice.setAction(pythonReport.getAdvice());
            advice.setReasoning(pythonReport.getConclusion());
            report.setInvestmentAdvice(advice);

            log.info("✅多智能体协作完成(Python Engine): {} - 建议: {}", stock.getStockCode(), advice.getAction());

        } catch (Exception e) {
            log.error("❌多智能体协作失败(Python Engine): {}", e.getMessage(), e);
            report.setError("分析失败: " + e.getMessage());
        }

        return report;
    }

    /**
     * 批量分析（并行处理）
     */
    @Monitor(value = "批量多智能体分析", slowThreshold = 30000)
    public List<ComprehensiveReport> analyzeBatch(List<USStockRss> stocks) {
        log.info("🤖 启动批量多智能体分析，股票数量: {}", stocks.size());

        List<CompletableFuture<ComprehensiveReport>> futures = stocks.stream()
                .map(stock -> CompletableFuture.supplyAsync(() -> analyze(stock), executorService))
                .toList();

        // 等待所有分析完成
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

        List<ComprehensiveReport> reports = new ArrayList<>();
        for (CompletableFuture<ComprehensiveReport> future : futures) {
            try {
                reports.add(future.get());
            } catch (Exception e) {
                log.error("获取分析结果失败: {}", e.getMessage());
            }
        }

        log.info("✅ 批量分析完成，成功: {}/{}", reports.size(), stocks.size());
        return reports;
    }

    /**
     * 智能预警（AI驱动） - kept local for high speed
     */
    @Monitor(value = "AI智能预警", slowThreshold = 10000)
    public AlertDecision smartAlert(USStockRss stock) {
        log.info("🚨 AI智能预警评估: {}", stock.getStockCode());

        // 快速风险评估
        RiskManagerAgent.RiskReport riskReport = riskManagerAgent.assessRisk(stock);

        AlertDecision decision = new AlertDecision();
        decision.setStockCode(stock.getStockCode());
        decision.setShouldAlert(shouldTriggerAlert(riskReport));
        decision.setAlertLevel(riskReport.getRiskLevel());
        decision.setReason(riskReport.getRiskFactors());

        if (decision.getShouldAlert()) {
            log.warn("⚠️ 触发AI预警: {} - 级别: {}",
                    stock.getStockCode(), decision.getAlertLevel());
        }

        return decision;
    }

    private Boolean shouldTriggerAlert(RiskManagerAgent.RiskReport riskReport) {
        String level = riskReport.getRiskLevel();
        return "高".equals(level) || "极高".equals(level);
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ComprehensiveReport {
        private String stockCode;
        private LocalDateTime analysisTime;
        private AnalystAgent.AnalysisReport analysisReport;
        private RiskManagerAgent.RiskReport riskReport;
        private AdvisorAgent.InvestmentAdvice investmentAdvice;
        private String error;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AlertDecision {
        private String stockCode;
        private Boolean shouldAlert;
        private String alertLevel;
        private String reason;
    }
}
