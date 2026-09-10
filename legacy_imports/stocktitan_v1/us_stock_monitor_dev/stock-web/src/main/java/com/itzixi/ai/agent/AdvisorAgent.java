package com.itzixi.ai.agent;

import com.itzixi.ai.AIService;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 投资顾问智能体
 * 负责生成投资建议
 *
 * @author 风间影月
 * @version 3.0 - Multi-Agent
 */
@Slf4j
@Component
public class AdvisorAgent {

    @Resource
    private AIService aiService;

    private static final String SYSTEM_PROMPT = """
            你是一位经验丰富的投资顾问，为客户提供专业的投资建议。
            你的职责是：
            1. 综合分析师和风控师的意见
            2. 给出明确的操作建议（买入/持有/卖出/观望）
            3. 提供具体的操作策略

            建议应该平衡收益和风险，符合稳健投资原则。
            """;

    /**
     * 生成投资建议
     */
    public InvestmentAdvice generateAdvice(
            USStockRss stock,
            AnalystAgent.AnalysisReport analysisReport,
            RiskManagerAgent.RiskReport riskReport) {

        log.info("投资顾问智能体开始生成建议: {}", stock.getStockCode());

        String userMessage = buildAdviceRequest(stock, analysisReport, riskReport);
        String response = aiService.chatWithSystem(SYSTEM_PROMPT, userMessage);

        InvestmentAdvice advice = new InvestmentAdvice();
        advice.setStockCode(stock.getStockCode());
        advice.setAction(extractAction(response));
        advice.setReason(response);
        advice.setConfidence(calculateConfidence(riskReport.getRiskLevel()));

        log.info("投资顾问智能体完成建议: {} - 操作: {}",
                stock.getStockCode(), advice.getAction());
        return advice;
    }

    private String buildAdviceRequest(
            USStockRss stock,
            AnalystAgent.AnalysisReport analysisReport,
            RiskManagerAgent.RiskReport riskReport) {

        return String.format("""
                请综合以下信息，给出投资建议：

                【股票信息】
                代码: %s
                异动: %s

                【分析师意见】
                %s

                【风控师评估】
                风险等级: %s
                %s

                【建议要求】
                1. 操作建议：买入/持有/卖出/观望
                2. 理由说明
                3. 具体策略（仓位、止损等）

                请给出明确的投资建议。
                """,
                stock.getStockCode(),
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle(),
                analysisReport.getAnalysis(),
                riskReport.getRiskLevel(),
                riskReport.getRiskFactors());
    }

    private String extractAction(String response) {
        if (response.contains("买入")) return "买入";
        if (response.contains("卖出")) return "卖出";
        if (response.contains("持有")) return "持有";
        return "观望";
    }

    private Integer calculateConfidence(String riskLevel) {
        return switch (riskLevel) {
            case "低" -> 85;
            case "中" -> 70;
            case "高" -> 50;
            case "极高" -> 30;
            default -> 60;
        };
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class InvestmentAdvice {
        private String stockCode;
        private String action;
        private String reason;
        private Integer confidence;
    }
}
