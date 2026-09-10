package com.itzixi.ai.service;

import com.itzixi.ai.AIService;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.StockService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 案例库冷启动服务
 * 从历史新闻批量生成初始案例
 *
 * @author 风间影月
 * @version 3.8 - Bootstrap
 */
@Slf4j
@Service
public class CaseBootstrapService {

    @Resource
    private StockService stockService;

    @Resource
    private AIService aiService;

    @Resource
    private RAGService ragService;

    /**
     * 从历史新闻批量生成案例
     * @param months 回溯月数（建议3-6个月）
     * @param limit 最大案例数（建议100-500）
     */
    public void bootstrapFromHistoricalNews(int months, int limit) {
        log.info("开始案例库冷启动: 回溯{}个月, 最多{}个案例", months, limit);

        try {
            // 1. 获取历史新闻
            LocalDateTime since = LocalDateTime.now().minusMonths(months);
            List<USStockRss> historicalNews = stockService.getStockRssSince(since);

            log.info("找到{}条历史新闻", historicalNews.size());

            // 2. 限制数量
            List<USStockRss> selectedNews = historicalNews.stream()
                    .limit(limit)
                    .toList();

            // 3. 批量生成案例
            int successCount = 0;
            int failCount = 0;

            for (int i = 0; i < selectedNews.size(); i++) {
                USStockRss news = selectedNews.get(i);

                try {
                    // 生成分析
                    String analysis = generateAnalysis(news);

                    // 生成实际影响（简化版，实际应该基于股价数据）
                    String actualImpact = "待验证";

                    // 保存为历史案例
                    ragService.saveAsHistoricalCase(news, analysis, actualImpact);

                    successCount++;

                    if ((i + 1) % 10 == 0) {
                        log.info("进度: {}/{}, 成功: {}, 失败: {}",
                                i + 1, selectedNews.size(), successCount, failCount);
                    }

                } catch (Exception e) {
                    failCount++;
                    log.warn("生成案例失败: {} - {}", news.getStockCode(), e.getMessage());
                }

                // 避免API限流
                if (i < selectedNews.size() - 1) {
                    Thread.sleep(1000);  // 每个案例间隔1秒
                }
            }

            log.info("案例库冷启动完成: 成功{}个, 失败{}个", successCount, failCount);

        } catch (Exception e) {
            log.error("案例库冷启动失败", e);
        }
    }

    /**
     * 生成简化的分析（用于冷启动）
     */
    private String generateAnalysis(USStockRss news) {
        String prompt = String.format("""
                请简要分析以下股票异动：

                股票代码: %s
                异动标题: %s
                相关标签: %s

                请给出简短分析（100字以内），包括：
                1. 事件类型
                2. 可能的影响
                3. 风险提示
                """,
                news.getStockCode(),
                news.getTitleZh() != null ? news.getTitleZh() : news.getTitle(),
                news.getTags() != null ? news.getTags() : "无"
        );

        return aiService.chat(prompt);
    }

    /**
     * 快速冷启动（使用默认参数）
     */
    public void quickBootstrap() {
        bootstrapFromHistoricalNews(3, 100);  // 3个月，100个案例
    }
}
