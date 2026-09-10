package com.itzixi.ai.service.analyst;

import com.itzixi.ai.AIService;
import com.itzixi.ai.service.RAGService;
import com.itzixi.ai.tools.StockDataTools;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

/**
 * AI研报生成代理 (Research Agent)
 * 自动化生成美股研报初稿
 *
 * @author 风间影月
 * @version 1.0 - Analyst Workbench
 */
@Slf4j
@Service
public class ResearchAgentService {

    @Resource
    private AIService aiService;

    @Resource
    private StockDataTools stockDataTools;

    @Resource
    private RAGService ragService;

    /**
     * 生成研报
     *
     * @param stockCode 股票代码
     * @param focusArea 关注领域 (e.g., Earnings, M&A, General)
     * @return Markdown格式的研报
     */
    @Monitor(value = "Generative Research Report", slowThreshold = 15000)
    public String generateReport(String stockCode, String focusArea) {
        log.info("开始生成研报: {}, focus={}", stockCode, focusArea);

        // 1. 获取实时数据 (Price, News)
        var price = stockDataTools.getRealTimePrice(stockCode);
        List<USStockRss> recentNews = stockDataTools.getRecentNews(stockCode, 14); // 过去2周新闻

        // 2. 构建上下文数据
        String marketContext = buildMarketContext(stockCode, price, recentNews);

        // 3. 构建 Prompt
        String prompt = buildReportPrompt(stockCode, focusArea, marketContext);

        // 4. AI 生成
        return aiService.chat(prompt);
    }

    private String buildMarketContext(String stockCode, StockDataTools.StockPrice price, List<USStockRss> news) {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("当前价格: $%.2f (涨跌: %.2f%%)\n", price.getCurrentPrice(), price.getChangePercent()));
        sb.append("【近期重要新闻及信源】\n");
        for (int i = 0; i < news.size(); i++) {
            USStockRss item = news.get(i);
            sb.append(String.format("[%d] %s (日期: %s, 信源: %s)\n",
                    i + 1,
                    item.getTitleZh() != null ? item.getTitleZh() : item.getTitle(),
                    item.getPubDateBj().toLocalDate(),
                    item.getLink()));
        }
        return sb.toString();
    }

    private String buildReportPrompt(String stockCode, String focusArea, String context) {
        return String.format("""
                你是一位顶级投行（如高盛、摩根大通）的资深权益分析师。请为 %s 撰写一份专业的研报初稿。

                【关注焦点】
                %s

                【市场数据与新闻上下文】
                %s

                【写作要求】
                1. 格式：使用标准 Markdown 格式。
                2. 结构：
                   - **Executive Summary**: 投资逻辑核心（Buy/Sell/Hold）。
                   - **Investment Thesis**: 为什么现在关注？
                   - **Key Catalysts**: 驱动股价的因素。
                   - **Risk Factors**: 潜在风险。
                   - **Conclusion**: 总结。
                3. 风格：专业、客观、数据驱动。不要使用虚浮的形容词。
                4. 引用规范 (Crucial)：
                   - 每一个关键论断必须标注信源编号，格式为 [1], [2]。
                   - 例如："公司净利润增长20% [1]，主要得益于云服务扩张 [3]。"
                   - 在研报末尾列出 "Reference" 章节，罗列所有引用的新闻链接。

                请直接输出研报内容。
                """, stockCode, focusArea, context);
    }
}
