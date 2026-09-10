package com.itzixi.ai.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.StockEntity;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * AI实体提取服务
 * 自动从新闻中提取结构化信息
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class EntityExtractionService {

    @Resource
    private AIService aiService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 提取股票实体信息
     */
    @Monitor(value = "AI实体提取", slowThreshold = 5000)
    public StockEntity extractEntities(USStockRss stock) {
        log.info("开始提取实体信息: {}", stock.getStockCode());

        try {
            String prompt = buildExtractionPrompt(stock);
            String jsonResponse = aiService.chat(prompt);

            // 解析JSON响应
            StockEntity entity = parseEntityFromJson(jsonResponse, stock);

            log.info("实体提取完成: {} - 事件类型: {}, 情感: {}",
                    stock.getStockCode(), entity.getEventType(), entity.getSentiment());

            return entity;
        } catch (Exception e) {
            log.error("实体提取失败: {}", stock.getStockCode(), e);
            return createDefaultEntity(stock);
        }
    }

    /**
     * 构建提取提示词
     */
    private String buildExtractionPrompt(USStockRss stock) {
        String title = stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle();
        String description = stock.getTags() != null ? stock.getTags() : "";

        return String.format("""
                请从以下股票新闻中提取结构化信息，以JSON格式返回：

                【新闻信息】
                股票代码: %s
                标题: %s
                描述: %s

                【提取要求】
                请提取以下信息并以JSON格式返回：
                {
                  "companyName": "公司名称",
                  "eventType": "事件类型（财报/产品发布/并购/诉讼/人事变动/监管/其他）",
                  "keyMetrics": [
                    {"name": "指标名称", "value": "数值", "unit": "单位"}
                  ],
                  "sentiment": "情感倾向（正面/中性/负面）",
                  "sentimentScore": 情感分数（-1.0到1.0的小数）,
                  "impactLevel": 影响程度（1-10的整数）,
                  "keywords": ["关键词1", "关键词2", "关键词3"],
                  "tags": ["标签1", "标签2", "标签3"]
                }

                注意：
                1. 只返回JSON，不要其他文字
                2. 情感分数：正面0.5-1.0，中性-0.5-0.5，负面-1.0--0.5
                3. 影响程度：1-3轻微，4-6中等，7-8重大，9-10极重大
                4. 标签要简洁专业，如"业绩超预期"、"监管风险"等
                """,
                stock.getStockCode(),
                title,
                description
        );
    }

    /**
     * 从JSON解析实体
     */
    private StockEntity parseEntityFromJson(String jsonResponse, USStockRss stock) {
        try {
            // 清理可能的markdown代码块标记
            String cleanJson = jsonResponse
                    .replaceAll("```json\\s*", "")
                    .replaceAll("```\\s*", "")
                    .trim();

            // 解析JSON
            StockEntity entity = objectMapper.readValue(cleanJson, StockEntity.class);
            entity.setStockCode(stock.getStockCode());

            return entity;
        } catch (Exception e) {
            log.warn("JSON解析失败，尝试手动提取: {}", e.getMessage());
            return extractManually(jsonResponse, stock);
        }
    }

    /**
     * 手动提取（备用方案）
     */
    private StockEntity extractManually(String response, USStockRss stock) {
        StockEntity entity = new StockEntity();
        entity.setStockCode(stock.getStockCode());

        // 提取事件类型
        if (response.contains("财报")) entity.setEventType("财报");
        else if (response.contains("产品")) entity.setEventType("产品发布");
        else if (response.contains("并购")) entity.setEventType("并购");
        else if (response.contains("诉讼")) entity.setEventType("诉讼");
        else entity.setEventType("其他");

        // 提取情感
        if (response.contains("正面")) {
            entity.setSentiment("正面");
            entity.setSentimentScore(0.7);
        } else if (response.contains("负面")) {
            entity.setSentiment("负面");
            entity.setSentimentScore(-0.7);
        } else {
            entity.setSentiment("中性");
            entity.setSentimentScore(0.0);
        }

        // 默认影响程度
        entity.setImpactLevel(5);

        return entity;
    }

    /**
     * 创建默认实体
     */
    private StockEntity createDefaultEntity(USStockRss stock) {
        StockEntity entity = new StockEntity();
        entity.setStockCode(stock.getStockCode());
        entity.setEventType("其他");
        entity.setSentiment("中性");
        entity.setSentimentScore(0.0);
        entity.setImpactLevel(5);
        return entity;
    }

    /**
     * 批量提取
     */
    public void extractAndUpdateBatch(java.util.List<USStockRss> stocks) {
        for (USStockRss stock : stocks) {
            try {
                StockEntity entity = extractEntities(stock);
                // 更新stock的tags字段
                if (entity.getTags() != null && !entity.getTags().isEmpty()) {
                    stock.setTags(String.join(",", entity.getTags()));
                }
            } catch (Exception e) {
                log.error("批量提取失败: {}", stock.getStockCode(), e);
            }
        }
    }
}
