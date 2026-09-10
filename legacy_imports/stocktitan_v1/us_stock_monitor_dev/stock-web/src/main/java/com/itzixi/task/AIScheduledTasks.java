package com.itzixi.task;

import com.itzixi.ai.entity.MarketSentiment;
import com.itzixi.ai.service.DailyReportService;
import com.itzixi.ai.service.SentimentAnalysisService;
import com.itzixi.ai.service.TradingProductService;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.RssService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * AI定时任务
 * 自动更新市场情绪和生成报告
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Component
public class AIScheduledTasks {

    @Resource
    private SentimentAnalysisService sentimentAnalysisService;

    @Resource
    private DailyReportService dailyReportService;

    @Resource
    private RssService rssService;

    @Resource
    private TradingProductService tradingProductService;

    /**
     * 每小时更新市场情绪
     * 每小时的第5分钟执行
     */
    @Scheduled(cron = "0 5 * * * ?")
    public void updateMarketSentiment() {
        log.info("开始定时更新市场情绪: {}", LocalDateTime.now());

        try {
            // 获取最近24小时的新闻
            List<USStockRss> recentNews = rssService.getRecentNews(24);

            if (recentNews.isEmpty()) {
                log.warn("最近24小时无新闻数据，跳过情绪分析");
                return;
            }

            // 分析市场情绪
            MarketSentiment sentiment = sentimentAnalysisService.analyzeSentiment(recentNews);

            log.info("市场情绪更新完成: 指数={}, 主导情绪={}, 恐慌程度={}",
                    sentiment.getSentimentIndex(),
                    sentiment.getDominantEmotion(),
                    sentiment.getPanicLevel());

        } catch (Exception e) {
            log.error("更新市场情绪失败", e);
        }
    }

    /**
     * 每天早上8点生成每日报告
     */
    @Scheduled(cron = "0 0 8 * * ?")
    public void generateDailyReport() {
        log.info("开始生成每日报告: {}", LocalDate.now());

        try {
            // 生成昨天的报告
            LocalDate yesterday = LocalDate.now().minusDays(1);
            dailyReportService.generateDailyReport(yesterday);

            log.info("每日报告生成完成: {}", yesterday);

        } catch (Exception e) {
            log.error("生成每日报告失败", e);
        }
    }

    /**
     * 每天晚上10点生成当天报告
     */
    @Scheduled(cron = "0 0 22 * * ?")
    public void generateTodayReport() {
        log.info("开始生成今日报告: {}", LocalDate.now());

        try {
            dailyReportService.generateDailyReport(LocalDate.now());
            log.info("今日报告生成完成");

        } catch (Exception e) {
            log.error("生成今日报告失败", e);
        }
    }

    /**
     * 每30分钟更新一次情绪（交易时段）
     * 工作日 9:30-16:00 (美股交易时间)
     */
    @Scheduled(cron = "0 */30 9-16 * * MON-FRI")
    public void updateSentimentDuringTradingHours() {
        log.info("交易时段情绪更新: {}", LocalDateTime.now());

        try {
            List<USStockRss> recentNews = rssService.getRecentNews(2);
            if (!recentNews.isEmpty()) {
                sentimentAnalysisService.analyzeSentiment(recentNews);
                log.info("交易时段情绪更新完成");
            }
        } catch (Exception e) {
            log.error("交易时段情绪更新失败", e);
        }
    }

    /**
     * 每小时执行一次信号回看与订阅扫描，形成策略闭环。
     */
    @Scheduled(cron = "0 10 * * * ?")
    public void runSignalValidationAndSubscriptionScan() {
        try {
            TradingProductService.ValidationRunSummary summary = tradingProductService.runValidation(null);
            int alerts = tradingProductService.scanSubscriptions(null).size();
            log.info("signal validation done: evaluated={}, skipped={}, sessions={}, alerts={}",
                    summary.getEvaluatedSignals(),
                    summary.getSkippedSignals(),
                    summary.getScannedSessions(),
                    alerts);
        } catch (Exception e) {
            log.error("signal validation/subscription scan failed", e);
        }
    }
}
