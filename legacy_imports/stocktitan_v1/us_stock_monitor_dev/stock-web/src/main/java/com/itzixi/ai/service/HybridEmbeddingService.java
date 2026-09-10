package com.itzixi.ai.service;

import com.itzixi.ai.entity.HistoricalCase;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.embedding.EmbeddingResponse;
import org.springframework.stereotype.Service;

import java.time.DayOfWeek;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.Arrays;
import java.util.List;

/**
 * 混合向量嵌入服务
 * 结合文本向量和股票特征向量，提升检索准确率
 *
 * @author 风间影月
 * @version 3.2 - Hybrid Embedding
 */
@Slf4j
@Service
public class HybridEmbeddingService {

    @Resource
    private EmbeddingModel embeddingModel;

    /**
     * 为股票新闻生成混合向量
     * 文本向量 + 特征向量
     */
    public float[] generateHybridEmbedding(USStockRss stock) {
        // 1. 生成文本向量
        String text = buildTextForEmbedding(stock);
        float[] textEmbedding = generateTextEmbedding(text);

        // 2. 生成特征向量
        float[] featureEmbedding = generateFeatureEmbedding(stock);

        // 3. 混合向量：80%文本 + 20%特征
        return combineEmbeddings(textEmbedding, featureEmbedding, 0.8, 0.2);
    }

    /**
     * 为历史案例生成混合向量
     */
    public float[] generateHybridEmbedding(HistoricalCase historicalCase) {
        // 1. 生成文本向量
        String text = buildTextForEmbedding(historicalCase);
        float[] textEmbedding = generateTextEmbedding(text);

        // 2. 生成特征向量（从历史案例中提取）
        float[] featureEmbedding = generateFeatureEmbedding(historicalCase);

        // 3. 混合向量：80%文本 + 20%特征
        return combineEmbeddings(textEmbedding, featureEmbedding, 0.8, 0.2);
    }

    /**
     * 生成文本向量
     */
    private float[] generateTextEmbedding(String text) {
        try {
            EmbeddingResponse response = embeddingModel.embedForResponse(List.of(text));
            float[] embedding = response.getResults().get(0).getOutput();
            return embedding != null ? embedding : new float[0];
        } catch (Exception e) {
            log.error("生成文本向量失败: {}", e.getMessage());
            return new float[0];
        }
    }

    /**
     * 为股票新闻生成特征向量
     * 特征包括：事件类型、情感倾向、时间特征等
     */
    private float[] generateFeatureEmbedding(USStockRss stock) {
        float[] features = new float[10];

        // 特征1-3: 事件类型编码（基于标签）
        String tags = stock.getTags() != null ? stock.getTags().toLowerCase() : "";
        features[0] = tags.contains("earnings") || tags.contains("财报") ? 1.0f : 0.0f;
        features[1] = tags.contains("merger") || tags.contains("acquisition") || tags.contains("并购") ? 1.0f : 0.0f;
        features[2] = tags.contains("fda") || tags.contains("approval") || tags.contains("监管") ? 1.0f : 0.0f;

        // 特征4-5: 情感倾向（基于标题关键词）
        String title = (stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle()).toLowerCase();
        features[3] = containsPositiveKeywords(title) ? 1.0f : 0.0f;
        features[4] = containsNegativeKeywords(title) ? 1.0f : 0.0f;

        // 特征6-7: 时间特征
        LocalDateTime pubDate = stock.getPubDateBj();
        if (pubDate != null) {
            features[5] = pubDate.getHour() / 24.0f; // 小时归一化
            features[6] = pubDate.getDayOfWeek().getValue() / 7.0f; // 星期归一化
        }

        // 特征8: 标题长度（归一化）
        features[7] = Math.min(title.length() / 200.0f, 1.0f);

        // 特征9-10: 保留用于未来扩展
        features[8] = 0.0f;
        features[9] = 0.0f;

        return features;
    }

    /**
     * 为历史案例生成特征向量
     */
    private float[] generateFeatureEmbedding(HistoricalCase historicalCase) {
        float[] features = new float[10];

        // 从历史案例中提取特征
        String title = historicalCase.getTitle() != null ? historicalCase.getTitle().toLowerCase() : "";

        // 特征1-3: 事件类型
        features[0] = title.contains("earnings") || title.contains("财报") ? 1.0f : 0.0f;
        features[1] = title.contains("merger") || title.contains("acquisition") || title.contains("并购") ? 1.0f : 0.0f;
        features[2] = title.contains("fda") || title.contains("approval") || title.contains("监管") ? 1.0f : 0.0f;

        // 特征4-5: 情感倾向
        features[3] = containsPositiveKeywords(title) ? 1.0f : 0.0f;
        features[4] = containsNegativeKeywords(title) ? 1.0f : 0.0f;

        // 特征6-10: 其他特征
        features[5] = 0.5f; // 默认中性时间
        features[6] = 0.5f;
        features[7] = Math.min(title.length() / 200.0f, 1.0f);
        features[8] = 0.0f;
        features[9] = 0.0f;

        return features;
    }

    /**
     * 合并文本向量和特征向量
     */
    private float[] combineEmbeddings(float[] textEmbedding, float[] featureEmbedding,
                                     double textWeight, double featureWeight) {
        if (textEmbedding.length == 0) {
            return new float[0];
        }

        // 创建混合向量：[加权文本向量, 特征向量]
        float[] combined = new float[textEmbedding.length + featureEmbedding.length];

        // 加权文本向量
        for (int i = 0; i < textEmbedding.length; i++) {
            combined[i] = (float) (textEmbedding[i] * textWeight);
        }

        // 加权特征向量
        for (int i = 0; i < featureEmbedding.length; i++) {
            combined[textEmbedding.length + i] = (float) (featureEmbedding[i] * featureWeight);
        }

        return combined;
    }

    /**
     * 构建用于嵌入的文本（股票新闻）
     */
    private String buildTextForEmbedding(USStockRss stock) {
        StringBuilder text = new StringBuilder();

        // 标题
        String title = stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle();
        text.append(title);

        // 标签
        if (stock.getTags() != null && !stock.getTags().isEmpty()) {
            text.append(" ").append(stock.getTags());
        }

        return text.toString();
    }

    /**
     * 构建用于嵌入的文本（历史案例）
     */
    private String buildTextForEmbedding(HistoricalCase historicalCase) {
        StringBuilder text = new StringBuilder();

        text.append(historicalCase.getTitle());

        if (historicalCase.getDescription() != null) {
            text.append(" ").append(historicalCase.getDescription());
        }

        return text.toString();
    }

    /**
     * 检查是否包含积极关键词
     */
    private boolean containsPositiveKeywords(String text) {
        String[] positiveKeywords = {
            "surge", "soar", "jump", "gain", "rise", "up", "beat", "exceed", "approval",
            "上涨", "飙升", "增长", "突破", "利好", "批准", "超预期"
        };

        for (String keyword : positiveKeywords) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 检查是否包含消极关键词
     */
    private boolean containsNegativeKeywords(String text) {
        String[] negativeKeywords = {
            "plunge", "drop", "fall", "decline", "down", "miss", "loss", "warning", "concern",
            "下跌", "暴跌", "下滑", "亏损", "警告", "担忧", "利空"
        };

        for (String keyword : negativeKeywords) {
            if (text.contains(keyword)) {
                return true;
            }
        }
        return false;
    }
}
