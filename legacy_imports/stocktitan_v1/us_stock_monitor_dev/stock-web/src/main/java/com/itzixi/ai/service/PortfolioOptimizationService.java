package com.itzixi.ai.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.PortfolioAdvice;
import com.itzixi.ai.entity.Position;
import com.itzixi.ai.entity.UserPreference;
import com.itzixi.common.annotation.Monitor;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 投资组合优化服务
 * AI驱动的组合管理和调仓建议
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class PortfolioOptimizationService {

    @Resource
    private AIService aiService;

    @Resource
    private SentimentAnalysisService sentimentAnalysisService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 优化投资组合
     */
    @Monitor(value = "投资组合优化", slowThreshold = 10000)
    public PortfolioAdvice optimizePortfolio(
            List<Position> currentPositions,
            UserPreference preference) {

        log.info("开始优化投资组合，持仓数量: {}", currentPositions.size());

        try {
            // 1. 获取市场情绪
            var sentiment = sentimentAnalysisService.getCurrentSentiment();

            // 2. 构建优化提示词
            String prompt = buildOptimizationPrompt(currentPositions, preference, sentiment);

            // 3. AI分析
            String jsonResponse = aiService.chat(prompt);

            // 4. 解析建议
            PortfolioAdvice advice = parseAdvice(jsonResponse);

            log.info("投资组合优化完成，需要调仓: {}", advice.getNeedRebalance());
            return advice;

        } catch (Exception e) {
            log.error("投资组合优化失败", e);
            return createDefaultAdvice();
        }
    }

    /**
     * 评估组合风险
     */
    public String assessPortfolioRisk(List<Position> positions) {
        log.info("评估组合风险，持仓数量: {}", positions.size());

        String prompt = buildRiskAssessmentPrompt(positions);
        return aiService.chat(prompt);
    }

    /**
     * 构建优化提示词
     */
    private String buildOptimizationPrompt(
            List<Position> positions,
            UserPreference preference,
            com.itzixi.ai.entity.MarketSentiment sentiment) {

        // 格式化持仓信息
        String positionsStr = positions.stream()
                .map(p -> String.format("- %s: 数量%d, 成本$%.2f, 当前$%.2f, 盈亏%.2f%%, 占比%.2f%%",
                        p.getStockCode(),
                        p.getQuantity(),
                        p.getCostPrice(),
                        p.getCurrentPrice(),
                        p.getProfitLossPercentage(),
                        p.getPositionPercentage()))
                .collect(Collectors.joining("\n"));

        return String.format("""
                请为以下投资组合提供优化建议，以JSON格式返回：

                【当前持仓】
                %s

                【用户偏好】
                - 风险偏好: %s
                - 关注行业: %s

                【市场环境】
                - 市场情绪指数: %d
                - 主导情绪: %s
                - 恐慌程度: %s

                【优化要求】
                请分析并以JSON格式返回：
                {
                  "needRebalance": true/false,
                  "buyRecommendations": [
                    {
                      "stockCode": "股票代码",
                      "action": "BUY",
                      "suggestedPrice": 建议价格,
                      "suggestedQuantity": 建议数量,
                      "reason": "理由",
                      "urgency": "低/中/高"
                    }
                  ],
                  "sellRecommendations": [
                    {
                      "stockCode": "股票代码",
                      "action": "SELL",
                      "suggestedPrice": 建议价格,
                      "suggestedQuantity": 建议数量,
                      "reason": "理由",
                      "urgency": "低/中/高"
                    }
                  ],
                  "positionAllocations": [
                    {
                      "stockCode": "股票代码",
                      "currentPercentage": 当前占比,
                      "targetPercentage": 目标占比,
                      "reason": "调整理由"
                    }
                  ],
                  "hedgingAdvice": ["对冲建议1", "对冲建议2"],
                  "overallRisk": "低/中/高",
                  "expectedReturn": 预期收益率,
                  "reasoning": "整体分析理由"
                }

                注意：
                1. 只返回JSON，不要其他文字
                2. 考虑用户风险偏好
                3. 结合市场情绪
                4. 给出具体可操作的建议
                """,
                positionsStr,
                preference.getRiskTolerance() != null ? preference.getRiskTolerance() : "稳健",
                preference.getInterestedSectors() != null ?
                        String.join(",", preference.getInterestedSectors()) : "无",
                sentiment.getSentimentIndex(),
                sentiment.getDominantEmotion(),
                sentiment.getPanicLevel()
        );
    }

    /**
     * 构建风险评估提示词
     */
    private String buildRiskAssessmentPrompt(List<Position> positions) {
        String positionsStr = positions.stream()
                .map(p -> String.format("- %s: 占比%.2f%%, 盈亏%.2f%%",
                        p.getStockCode(),
                        p.getPositionPercentage(),
                        p.getProfitLossPercentage()))
                .collect(Collectors.joining("\n"));

        return String.format("""
                请评估以下投资组合的风险：

                【持仓情况】
                %s

                【评估维度】
                1. 集中度风险（是否过于集中）
                2. 行业分散度
                3. 盈亏状况
                4. 整体风险等级（低/中/高）
                5. 主要风险点
                6. 风险控制建议

                请给出专业的风险评估报告。
                """, positionsStr);
    }

    /**
     * 解析建议
     */
    private PortfolioAdvice parseAdvice(String jsonResponse) {
        try {
            String cleanJson = jsonResponse
                    .replaceAll("```json\\s*", "")
                    .replaceAll("```\\s*", "")
                    .trim();

            return objectMapper.readValue(cleanJson, PortfolioAdvice.class);
        } catch (Exception e) {
            log.error("解析组合建议失败: {}", e.getMessage());
            return createDefaultAdvice();
        }
    }

    /**
     * 创建默认建议
     */
    private PortfolioAdvice createDefaultAdvice() {
        PortfolioAdvice advice = new PortfolioAdvice();
        advice.setNeedRebalance(false);
        advice.setOverallRisk("中");
        advice.setReasoning("分析失败，建议保持当前持仓");
        return advice;
    }
}
