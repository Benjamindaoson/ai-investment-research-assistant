package com.itzixi.ai.agent;

import com.itzixi.ai.AIService;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * 风控师智能体
 * 负责风险评估和预警
 *
 * @author 风间影月
 * @version 3.0 - Multi-Agent
 */
@Slf4j
@Component
public class RiskManagerAgent {

    @Resource
    private AIService aiService;

    private static final String SYSTEM_PROMPT = """
            你是一位严谨的风险控制专家，专注于识别和评估投资风险。
            你的职责是：
            1. 评估股票异动的风险等级（低/中/高/极高）
            2. 识别潜在的风险因素
            3. 提供风险控制建议

            评估时请保持谨慎，宁可高估风险也不要低估。
            """;

    /**
     * 评估风险
     */
    public RiskReport assessRisk(USStockRss stock) {
        log.info("风控师智能体开始评估: {}", stock.getStockCode());

        String userMessage = buildRiskRequest(stock);
        String response = aiService.chatWithSystem(SYSTEM_PROMPT, userMessage);

        RiskReport report = new RiskReport();
        report.setStockCode(stock.getStockCode());
        report.setRiskLevel(extractRiskLevel(response));
        report.setRiskFactors(response);
        report.setSuggestion(extractSuggestion(response));

        log.info("风控师智能体完成评估: {} - 风险等级: {}",
                stock.getStockCode(), report.getRiskLevel());
        return report;
    }

    private String buildRiskRequest(USStockRss stock) {
        return String.format("""
                请评估以下股票异动的风险：

                【股票信息】
                代码: %s
                异动: %s
                标签: %s

                【评估要求】
                1. 风险等级：低/中/高/极高
                2. 主要风险因素
                3. 风险控制建议

                请给出明确的风险评级和建议。
                """,
                stock.getStockCode(),
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle(),
                stock.getTags() != null ? stock.getTags() : "无");
    }

    private String extractRiskLevel(String response) {
        if (response.contains("极高")) return "极高";
        if (response.contains("高")) return "高";
        if (response.contains("中")) return "中";
        return "低";
    }

    private String extractSuggestion(String response) {
        // 简单提取建议部分
        if (response.contains("建议")) {
            int index = response.indexOf("建议");
            return response.substring(index);
        }
        return "请谨慎操作，控制仓位";
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RiskReport {
        private String stockCode;
        private String riskLevel;
        private String riskFactors;
        private String suggestion;
    }
}
