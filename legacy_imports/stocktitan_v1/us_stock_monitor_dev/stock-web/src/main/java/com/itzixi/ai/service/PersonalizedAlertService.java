package com.itzixi.ai.service;

import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.StockEntity;
import com.itzixi.ai.entity.UserPreference;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 个性化AI推送服务
 * 根据用户偏好智能决定是否推送
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class PersonalizedAlertService {

    @Resource
    private AIService aiService;

    @Resource
    private EntityExtractionService entityExtractionService;

    /**
     * 判断是否应该推送给用户
     */
    @Monitor(value = "个性化推送判断", slowThreshold = 3000)
    public AlertDecision shouldAlert(USStockRss stock, UserPreference preference) {
        log.info("开始个性化推送判断: {} for user {}", stock.getStockCode(), preference.getUserId());

        try {
            // 1. 提取实体信息
            StockEntity entity = entityExtractionService.extractEntities(stock);

            // 2. 快速规则过滤
            if (!passQuickFilter(stock, entity, preference)) {
                return AlertDecision.reject("不符合用户偏好的快速过滤条件");
            }

            // 3. AI深度判断
            String prompt = buildAlertPrompt(stock, entity, preference);
            String response = aiService.chat(prompt);

            // 4. 解析AI决策
            return parseAlertDecision(response);

        } catch (Exception e) {
            log.error("个性化推送判断失败: {}", stock.getStockCode(), e);
            // 失败时默认推送
            return AlertDecision.approve("判断失败，默认推送", 5);
        }
    }

    /**
     * 批量过滤
     */
    public List<USStockRss> filterForUser(List<USStockRss> stocks, UserPreference preference) {
        return stocks.stream()
                .filter(stock -> {
                    AlertDecision decision = shouldAlert(stock, preference);
                    return decision.isApproved();
                })
                .collect(Collectors.toList());
    }

    /**
     * 快速规则过滤
     */
    private boolean passQuickFilter(USStockRss stock, StockEntity entity, UserPreference preference) {
        // 1. 检查推送时间
        if (preference.getPushHours() != null && !preference.getPushHours().isEmpty()) {
            int currentHour = LocalDateTime.now().getHour();
            if (!preference.getPushHours().contains(currentHour)) {
                log.debug("不在推送时间段: {}", currentHour);
                return false;
            }
        }

        // 2. 检查关注股票
        if (preference.getFocusStocks() != null && !preference.getFocusStocks().isEmpty()) {
            if (!preference.getFocusStocks().contains(stock.getStockCode())) {
                log.debug("不在关注股票列表: {}", stock.getStockCode());
                return false;
            }
        }

        // 3. 检查影响程度
        if (preference.getMinImpactLevel() != null && entity.getImpactLevel() != null) {
            if (entity.getImpactLevel() < preference.getMinImpactLevel()) {
                log.debug("影响程度不足: {} < {}", entity.getImpactLevel(), preference.getMinImpactLevel());
                return false;
            }
        }

        // 4. 检查负面新闻偏好
        if (Boolean.FALSE.equals(preference.getReceiveNegativeNews())) {
            if ("负面".equals(entity.getSentiment())) {
                log.debug("用户不接收负面新闻");
                return false;
            }
        }

        return true;
    }

    /**
     * 构建AI判断提示词
     */
    private String buildAlertPrompt(USStockRss stock, StockEntity entity, UserPreference preference) {
        return String.format("""
                请判断是否应该将以下股票异动推送给用户：

                【用户偏好】
                - 关注股票: %s
                - 风险偏好: %s
                - 关注行业: %s
                - 关注事件: %s

                【当前异动】
                - 股票代码: %s
                - 事件类型: %s
                - 情感倾向: %s (分数: %.2f)
                - 影响程度: %d/10
                - 标题: %s

                【判断要求】
                1. 考虑用户的风险偏好和关注点
                2. 评估异动的重要性和相关性
                3. 判断是否值得打扰用户

                请回答：
                - 决策: 推送/不推送
                - 优先级: 1-10（1最低，10最高）
                - 理由: 简短说明

                格式：决策|优先级|理由
                例如：推送|8|该股票是用户重点关注，且事件影响重大
                """,
                preference.getFocusStocks() != null ? String.join(",", preference.getFocusStocks()) : "无",
                preference.getRiskTolerance() != null ? preference.getRiskTolerance() : "稳健",
                preference.getInterestedSectors() != null ? String.join(",", preference.getInterestedSectors()) : "无",
                preference.getInterestedEventTypes() != null ? String.join(",", preference.getInterestedEventTypes()) : "无",
                stock.getStockCode(),
                entity.getEventType(),
                entity.getSentiment(),
                entity.getSentimentScore(),
                entity.getImpactLevel(),
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle()
        );
    }

    /**
     * 解析AI决策
     */
    private AlertDecision parseAlertDecision(String response) {
        try {
            // 解析格式：决策|优先级|理由
            String[] parts = response.split("\\|");
            if (parts.length >= 3) {
                String decision = parts[0].trim();
                int priority = Integer.parseInt(parts[1].trim());
                String reason = parts[2].trim();

                boolean approved = decision.contains("推送") && !decision.contains("不推送");
                return new AlertDecision(approved, reason, priority);
            }
        } catch (Exception e) {
            log.warn("解析AI决策失败，尝试简单判断: {}", e.getMessage());
        }

        // 简单判断
        boolean approved = response.contains("推送") && !response.contains("不推送");
        return new AlertDecision(approved, response, 5);
    }

    /**
     * 推送决策
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AlertDecision {
        private boolean approved;
        private String reason;
        private int priority;

        public static AlertDecision approve(String reason, int priority) {
            return new AlertDecision(true, reason, priority);
        }

        public static AlertDecision reject(String reason) {
            return new AlertDecision(false, reason, 0);
        }
    }
}
