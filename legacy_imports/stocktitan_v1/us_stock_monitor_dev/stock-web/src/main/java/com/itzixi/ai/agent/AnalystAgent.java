package com.itzixi.ai.agent;

import com.itzixi.ai.AIService;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;

/**
 * 分析师智能体
 * 负责深度分析股票异动
 *
 * @author 风间影月
 * @version 3.0 - Multi-Agent
 */
@Slf4j
@Component
public class AnalystAgent {

    @Resource
    private AIService aiService;

    private static final String SYSTEM_PROMPT = """
            你是一位资深的股票分析师，拥有20年的市场分析经验。
            你的职责是：
            1. 深度分析股票异动的根本原因
            2. 评估异动对股价的潜在影响
            3. 识别市场情绪和趋势信号

            分析时请保持客观、专业，基于事实和数据。
            """;

    /**
     * 分析股票异动
     */
    public AnalysisReport analyze(USStockRss stock) {
        log.info("分析师智能体开始分析: {}", stock.getStockCode());

        String userMessage = buildAnalysisRequest(stock);
        String response = aiService.chatWithSystem(SYSTEM_PROMPT, userMessage);

        AnalysisReport report = new AnalysisReport();
        report.setStockCode(stock.getStockCode());
        report.setAnalysis(response);
        report.setAnalyst("AI分析师");

        log.info("分析师智能体完成分析: {}", stock.getStockCode());
        return report;
    }

    /**
     * 批量分析
     */
    public List<AnalysisReport> analyzeBatch(List<USStockRss> stocks) {
        return stocks.stream()
                .map(this::analyze)
                .toList();
    }

    private String buildAnalysisRequest(USStockRss stock) {
        return String.format("""
                请分析以下股票异动：

                【基本信息】
                股票代码: %s
                异动标题: %s
                相关标签: %s
                发布时间: %s

                【分析要求】
                1. 异动的核心原因是什么？
                2. 这个异动对股价有何影响？（短期/长期）
                3. 当前市场情绪如何？
                4. 是否存在风险信号？

                请给出专业、简洁的分析。
                """,
                stock.getStockCode(),
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle(),
                stock.getTags() != null ? stock.getTags() : "无",
                stock.getPubDateBj());
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AnalysisReport {
        private String stockCode;
        private String analysis;
        private String analyst;
    }
}
