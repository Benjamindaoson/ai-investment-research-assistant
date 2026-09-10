package com.itzixi.ai.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.DailyReport;
import com.itzixi.ai.entity.MarketSentiment;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.RssService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * AI生成每日报告服务
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class DailyReportService {

    @Resource
    private AIService aiService;

    @Resource
    private RssService rssService;

    @Resource
    private SentimentAnalysisService sentimentAnalysisService;

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * 生成每日市场报告
     */
    @Monitor(value = "生成每日报告", slowThreshold = 15000)
    public DailyReport generateDailyReport(LocalDate date) {
        log.info("开始生成每日报告: {}", date);

        // 1. 检查缓存
        String cacheKey = "daily:report:" + date;
        DailyReport cached = (DailyReport) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {
            log.info("从缓存获取每日报告: {}", date);
            return cached;
        }

        // 2. 获取当日新闻
        List<USStockRss> todayNews = rssService.getStockRssByDate(date);
        if (todayNews.isEmpty()) {
            log.warn("当日无新闻数据: {}", date);
            return createEmptyReport(date);
        }

        // 3. 获取市场情绪
        MarketSentiment sentiment = sentimentAnalysisService.analyzeSentiment(todayNews);

        // 4. AI生成报告
        String prompt = buildReportPrompt(date, todayNews, sentiment);
        String jsonResponse = aiService.chat(prompt);

        // 5. 解析报告
        DailyReport report = parseReport(jsonResponse, date, sentiment);

        // 6. 缓存报告（24小时）
        redisTemplate.opsForValue().set(cacheKey, report, 24, TimeUnit.HOURS);

        log.info("每日报告生成完成: {}, 共{}条新闻", date, todayNews.size());
        return report;
    }

    /**
     * 构建报告提示词
     */
    private String buildReportPrompt(LocalDate date, List<USStockRss> news, MarketSentiment sentiment) {
        // 格式化新闻列表
        String newsList = news.stream()
                .limit(50) // 最多50条
                .map(n -> String.format("- [%s] %s",
                        n.getStockCode(),
                        n.getTitleZh() != null ? n.getTitleZh() : n.getTitle()))
                .collect(Collectors.joining("\n"));

        return String.format("""
                请基于以下信息生成美股市场日报，以JSON格式返回：

                【日期】%s
                【新闻数量】%d条
                【市场情绪】
                - 情绪指数: %d
                - 恐慌程度: %s
                - 主导情绪: %s

                【今日新闻】
                %s

                【报告要求】
                请生成JSON格式的报告：
                {
                  "marketOverview": "市场概览（3-5句话，总结今日市场整体表现）",
                  "topEvents": [
                    {
                      "stockCode": "股票代码",
                      "title": "事件标题",
                      "summary": "事件摘要",
                      "impactLevel": 影响程度1-10,
                      "sentiment": "正面/中性/负面"
                    }
                  ],
                  "sectorHotspots": [
                    {
                      "sector": "行业名称",
                      "description": "热点描述",
                      "relatedStocks": ["相关股票"],
                      "trend": "上涨/下跌/震荡"
                    }
                  ],
                  "riskAlerts": ["风险提示1", "风险提示2"],
                  "tomorrowFocus": ["明日关注点1", "明日关注点2"]
                }

                注意：
                1. 只返回JSON，不要其他文字
                2. topEvents选择5个最重要的事件
                3. sectorHotspots总结2-3个行业热点
                4. riskAlerts提示3-5个风险点
                5. tomorrowFocus给出3-5个明日关注点
                """,
                date,
                news.size(),
                sentiment.getSentimentIndex(),
                sentiment.getPanicLevel(),
                sentiment.getDominantEmotion(),
                newsList
        );
    }

    /**
     * 解析报告
     */
    private DailyReport parseReport(String jsonResponse, LocalDate date, MarketSentiment sentiment) {
        try {
            // 清理JSON
            String cleanJson = jsonResponse
                    .replaceAll("```json\\s*", "")
                    .replaceAll("```\\s*", "")
                    .trim();

            // 解析
            DailyReport report = objectMapper.readValue(cleanJson, DailyReport.class);
            report.setReportDate(date);
            report.setMarketSentiment(sentiment);
            report.setGeneratedAt(LocalDate.now().format(DateTimeFormatter.ISO_DATE_TIME));

            return report;
        } catch (Exception e) {
            log.error("解析报告失败: {}", e.getMessage(), e);
            return createEmptyReport(date);
        }
    }

    /**
     * 创建空报告
     */
    private DailyReport createEmptyReport(LocalDate date) {
        DailyReport report = new DailyReport();
        report.setReportDate(date);
        report.setMarketOverview("当日暂无数据");
        report.setGeneratedAt(LocalDate.now().format(DateTimeFormatter.ISO_DATE_TIME));
        return report;
    }

    /**
     * 获取最新报告
     */
    public DailyReport getLatestReport() {
        return generateDailyReport(LocalDate.now());
    }
}
