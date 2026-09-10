package com.itzixi.ai.service;

import com.itzixi.ai.AIService;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * AI股票分析服务
 * 使用大模型进行智能分析，替代传统规则引擎
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class AIStockAnalysisService {

    @Resource
    private AIService aiService;

    /**
     * 分析股票异动原因
     */
    @Monitor(value = "AI分析异动原因", slowThreshold = 5000)
    public String analyzeMovementReason(USStockRss stock) {
        String prompt = buildAnalysisPrompt(stock);
        return aiService.chat(prompt);
    }

    /**
     * 评估风险等级
     */
    @Monitor(value = "AI评估风险", slowThreshold = 5000)
    public RiskAssessment assessRisk(USStockRss stock) {
        String systemPrompt = """
                你是一位专业的股票风险分析师。
                请根据股票异动信息，评估风险等级（低/中/高）。
                分析维度包括：异动频率、标签类型、市场环境等。
                请以JSON格式返回：{"riskLevel": "高", "reason": "原因说明", "suggestion": "建议"}
                """;

        String userMessage = String.format("""
                股票代码: %s
                标题: %s
                标签: %s
                24小时异动次数: 未知
                """,
                stock.getStockCode(),
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle(),
                stock.getTags());

        String response = aiService.chatWithSystem(systemPrompt, userMessage);
        return parseRiskAssessment(response);
    }

    /**
     * 生成投资建议
     */
    @Monitor(value = "AI生成投资建议", slowThreshold = 5000)
    public String generateInvestmentAdvice(USStockRss stock, List<USStockRss> historicalData) {
        String systemPrompt = """
                你是一位资深的投资顾问。
                请根据股票的历史异动数据，给出专业的投资建议。
                建议应包括：操作建议（买入/持有/卖出）、理由、风险提示。
                """;

        StringBuilder userMessage = new StringBuilder();
        userMessage.append("股票代码: ").append(stock.getStockCode()).append("\n");
        userMessage.append("最新异动: ").append(stock.getTitleZh()).append("\n");
        userMessage.append("历史异动记录:\n");

        for (int i = 0; i < Math.min(historicalData.size(), 5); i++) {
            USStockRss history = historicalData.get(i);
            userMessage.append(String.format("- %s: %s\n",
                    history.getPubDateBj(),
                    history.getTitleZh() != null ? history.getTitleZh() : history.getTitle()));
        }

        return aiService.chatWithSystem(systemPrompt, userMessage.toString());
    }

    /**
     * 预测趋势
     */
    @Monitor(value = "AI预测趋势", slowThreshold = 5000)
    public TrendPrediction predictTrend(String stockCode, List<USStockRss> historicalData) {
        String systemPrompt = """
                你是一位量化分析专家。
                请根据股票的历史异动数据，预测未来趋势。
                分析维度：异动频率变化、标签类型演变、市场情绪等。
                请以JSON格式返回：{"trend": "上涨/下跌/震荡", "confidence": "0-100", "reason": "原因"}
                """;

        StringBuilder userMessage = new StringBuilder();
        userMessage.append("股票代码: ").append(stockCode).append("\n");
        userMessage.append("历史异动数据:\n");

        for (USStockRss data : historicalData) {
            userMessage.append(String.format("- %s: %s (标签: %s)\n",
                    data.getPubDateBj(),
                    data.getTitleZh() != null ? data.getTitleZh() : data.getTitle(),
                    data.getTags()));
        }

        String response = aiService.chatWithSystem(systemPrompt, userMessage.toString());
        return parseTrendPrediction(response);
    }

    /**
     * 智能摘要（多条新闻）
     */
    @Monitor(value = "AI生成摘要", slowThreshold = 5000)
    public String generateSummary(List<USStockRss> stocks) {
        String systemPrompt = """
                你是一位财经新闻编辑。
                请将多条股票异动新闻整合成一份简洁的摘要报告。
                摘要应包括：主要事件、影响分析、关注重点。
                """;

        StringBuilder userMessage = new StringBuilder();
        userMessage.append("今日股票异动汇总:\n");

        for (USStockRss stock : stocks) {
            userMessage.append(String.format("- %s: %s\n",
                    stock.getStockCode(),
                    stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle()));
        }

        return aiService.chatWithSystem(systemPrompt, userMessage.toString());
    }

    /**
     * 构建分析提示词
     */
    private String buildAnalysisPrompt(USStockRss stock) {
        return String.format("""
                请分析以下股票异动的原因：

                股票代码: %s
                异动标题: %s
                相关标签: %s
                发布时间: %s

                请从以下角度分析：
                1. 异动的直接原因
                2. 可能的市场影响
                3. 投资者应关注的要点

                请用简洁专业的语言回答。
                """,
                stock.getStockCode(),
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle(),
                stock.getTags() != null ? stock.getTags() : "无",
                stock.getPubDateBj());
    }

    /**
     * 解析风险评估结果
     */
    private RiskAssessment parseRiskAssessment(String response) {
        // 简单解析，实际应使用JSON解析
        RiskAssessment assessment = new RiskAssessment();
        if (response.contains("高")) {
            assessment.setRiskLevel("高");
        } else if (response.contains("中")) {
            assessment.setRiskLevel("中");
        } else {
            assessment.setRiskLevel("低");
        }
        assessment.setReason(response);
        assessment.setSuggestion("请根据风险等级调整仓位");
        return assessment;
    }

    /**
     * 解析趋势预测结果
     */
    private TrendPrediction parseTrendPrediction(String response) {
        TrendPrediction prediction = new TrendPrediction();
        if (response.contains("上涨")) {
            prediction.setTrend("上涨");
        } else if (response.contains("下跌")) {
            prediction.setTrend("下跌");
        } else {
            prediction.setTrend("震荡");
        }
        prediction.setConfidence(75);
        prediction.setReason(response);
        return prediction;
    }

    /**
     * 风险评估结果
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class RiskAssessment {
        private String riskLevel;
        private String reason;
        private String suggestion;
    }

    /**
     * 趋势预测结果
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TrendPrediction {
        private String trend;
        private Integer confidence;
        private String reason;
    }
}
