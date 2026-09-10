package com.itzixi.ai.service;

import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.MarketSentiment;
import com.itzixi.ai.entity.StockEntity;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * 情感分析和市场情绪追踪服务
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class SentimentAnalysisService {

    @Resource
    private AIService aiService;

    @Resource
    private EntityExtractionService entityExtractionService;

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    private static final String SENTIMENT_CACHE_KEY = "market:sentiment:current";

    /**
     * 分析市场整体情绪
     */
    @Monitor(value = "市场情绪分析", slowThreshold = 10000)
    public MarketSentiment analyzeSentiment(List<USStockRss> recentNews) {
        log.info("开始分析市场情绪，新闻数量: {}", recentNews.size());

        if (recentNews.isEmpty()) {
            return createNeutralSentiment();
        }

        // 1. 统计情感分布
        int positiveCount = 0;
        int negativeCount = 0;
        int neutralCount = 0;

        for (USStockRss news : recentNews) {
            try {
                StockEntity entity = entityExtractionService.extractEntities(news);
                String sentiment = entity.getSentiment();

                if ("正面".equals(sentiment)) positiveCount++;
                else if ("负面".equals(sentiment)) negativeCount++;
                else neutralCount++;
            } catch (Exception e) {
                log.warn("提取情感失败: {}", news.getStockCode());
                neutralCount++;
            }
        }

        // 2. AI综合分析
        String prompt = buildSentimentPrompt(recentNews, positiveCount, negativeCount, neutralCount);
        String response = aiService.chat(prompt);

        // 3. 解析情绪
        MarketSentiment sentiment = parseSentiment(response, positiveCount, negativeCount, neutralCount);
        sentiment.setTimeRangeHours(24);

        // 4. 缓存（1小时）
        redisTemplate.opsForValue().set(SENTIMENT_CACHE_KEY, sentiment, 1, TimeUnit.HOURS);

        log.info("市场情绪分析完成: 指数={}, 主导情绪={}",
                sentiment.getSentimentIndex(), sentiment.getDominantEmotion());

        return sentiment;
    }

    /**
     * 获取当前市场情绪（从缓存）
     */
    public MarketSentiment getCurrentSentiment() {
        MarketSentiment cached = (MarketSentiment) redisTemplate.opsForValue().get(SENTIMENT_CACHE_KEY);
        if (cached != null) {
            return cached;
        }
        return createNeutralSentiment();
    }

    /**
     * 构建情绪分析提示词
     */
    private String buildSentimentPrompt(List<USStockRss> news, int positive, int negative, int neutral) {
        // 提取关键新闻标题
        String headlines = news.stream()
                .limit(20)
                .map(n -> n.getTitleZh() != null ? n.getTitleZh() : n.getTitle())
                .reduce((a, b) -> a + "\n- " + b)
                .orElse("");

        return String.format("""
                请分析当前美股市场的整体情绪：

                【统计数据】
                - 总新闻数: %d条
                - 正面新闻: %d条
                - 负面新闻: %d条
                - 中性新闻: %d条

                【关键新闻标题】
                - %s

                【分析要求】
                请评估市场情绪并回答：
                1. 情绪指数（-100到+100，负数表示悲观，正数表示乐观）
                2. 恐慌程度（低/中/高）
                3. 主导情绪（贪婪/恐惧/观望）
                4. 情绪变化趋势（上升/下降/稳定）
                5. 关键驱动因素（列出3-5个）
                6. 简短摘要（2-3句话）

                格式：情绪指数|恐慌程度|主导情绪|趋势|驱动因素1,驱动因素2|摘要
                例如：-30|中|恐惧|下降|通胀担忧,加息预期,财报不及预期|市场情绪偏悲观，投资者担忧经济前景
                """,
                news.size(),
                positive,
                negative,
                neutral,
                headlines
        );
    }

    /**
     * 解析情绪
     */
    private MarketSentiment parseSentiment(String response, int positive, int negative, int neutral) {
        MarketSentiment sentiment = new MarketSentiment();
        sentiment.setPositiveCount(positive);
        sentiment.setNegativeCount(negative);
        sentiment.setNeutralCount(neutral);

        try {
            String[] parts = response.split("\\|");
            if (parts.length >= 6) {
                sentiment.setSentimentIndex(Integer.parseInt(parts[0].trim()));
                sentiment.setPanicLevel(parts[1].trim());
                sentiment.setDominantEmotion(parts[2].trim());
                sentiment.setTrend(parts[3].trim());

                String[] drivers = parts[4].split(",");
                sentiment.setKeyDrivers(List.of(drivers));

                sentiment.setSummary(parts[5].trim());
            } else {
                // 简单解析
                parseSimple(response, sentiment);
            }
        } catch (Exception e) {
            log.warn("解析情绪失败，使用默认值: {}", e.getMessage());
            parseSimple(response, sentiment);
        }

        return sentiment;
    }

    /**
     * 简单解析
     */
    private void parseSimple(String response, MarketSentiment sentiment) {
        // 计算情绪指数
        int total = sentiment.getPositiveCount() + sentiment.getNegativeCount() + sentiment.getNeutralCount();
        if (total > 0) {
            int index = (sentiment.getPositiveCount() - sentiment.getNegativeCount()) * 100 / total;
            sentiment.setSentimentIndex(index);
        } else {
            sentiment.setSentimentIndex(0);
        }

        // 判断恐慌程度
        if (sentiment.getNegativeCount() > sentiment.getPositiveCount() * 2) {
            sentiment.setPanicLevel("高");
        } else if (sentiment.getNegativeCount() > sentiment.getPositiveCount()) {
            sentiment.setPanicLevel("中");
        } else {
            sentiment.setPanicLevel("低");
        }

        // 主导情绪
        if (sentiment.getSentimentIndex() > 30) {
            sentiment.setDominantEmotion("贪婪");
        } else if (sentiment.getSentimentIndex() < -30) {
            sentiment.setDominantEmotion("恐惧");
        } else {
            sentiment.setDominantEmotion("观望");
        }

        sentiment.setTrend("稳定");
        sentiment.setSummary(response);
    }

    /**
     * 创建中性情绪
     */
    private MarketSentiment createNeutralSentiment() {
        MarketSentiment sentiment = new MarketSentiment();
        sentiment.setSentimentIndex(0);
        sentiment.setPanicLevel("低");
        sentiment.setDominantEmotion("观望");
        sentiment.setTrend("稳定");
        sentiment.setPositiveCount(0);
        sentiment.setNegativeCount(0);
        sentiment.setNeutralCount(0);
        sentiment.setSummary("暂无数据");
        return sentiment;
    }
}
