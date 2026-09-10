package com.itzixi.ai.service;

import com.itzixi.ai.AIService;
import com.itzixi.ai.entity.HistoricalCase;
import com.itzixi.common.annotation.Monitor;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

/**
 * RAG增强的分析服务
 * 结合历史案例提供更准确的分析
 * 支持时间衰减、多路召回、实时追踪
 *
 * @author 风间影月
 * @version 3.6 - Real-time Tracking
 */
@Slf4j
@Service
public class RAGService {

    @Resource
    private AIService aiService;

    @Resource
    private VectorStoreService vectorStoreService;

    @Resource
    private CaseTrackingService caseTrackingService;

    /**
     * RAG增强的异动分析（使用多路召回）
     */
    @Monitor(value = "RAG增强分析", slowThreshold = 8000)
    public String analyzeWithHistory(USStockRss stock) {
        log.info("开始RAG增强分析（多路召回）: {}", stock.getStockCode());

        // 1. 使用多路召回检索相似历史案例
        String query = buildQuery(stock);
        List<HistoricalCase> similarCases = vectorStoreService.multiPathRecall(
                stock.getStockCode(),
                query,
                5  // Top-5
        );

        // 2. 构建包含历史案例的提示词
        String prompt = buildRAGPrompt(stock, similarCases);

        // 3. AI分析
        String analysis = aiService.chat(prompt);

        log.info("RAG增强分析完成: {}", stock.getStockCode());
        return analysis;
    }

    /**
     * 保存分析结果为历史案例
     */
    public void saveAsHistoricalCase(USStockRss stock, String analysis, String actualImpact) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        HistoricalCase historicalCase = new HistoricalCase();
        historicalCase.setId(generateCaseId(stock));
        historicalCase.setStockCode(stock.getStockCode());
        historicalCase.setTitle(stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle());
        historicalCase.setDescription(stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle());
        historicalCase.setAnalysis(analysis);
        historicalCase.setActualImpact(actualImpact);
        historicalCase.setOccurredAt(
                stock.getPubDateBj() != null
                        ? stock.getPubDateBj().format(formatter)
                        : LocalDateTime.now().format(formatter)
        );

        vectorStoreService.addCase(historicalCase);
        log.info("分析结果已保存为历史案例: {}", historicalCase.getId());

        // 开始追踪案例
        caseTrackingService.startTracking(historicalCase);
    }

    /**
     * 构建查询
     */
    private String buildQuery(USStockRss stock) {
        String title = stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle();
        String tags = stock.getTags() != null ? stock.getTags() : "";
        return title + " " + tags;
    }

    /**
     * 构建RAG提示词（优化版 - 针对股票分析）
     */
    private String buildRAGPrompt(USStockRss stock, List<HistoricalCase> similarCases) {
        StringBuilder prompt = new StringBuilder();

        prompt.append("你是一位资深的美股分析师，擅长基于历史案例预测股票走势。\n\n");

        // 当前异动信息
        prompt.append("【当前异动】\n");
        prompt.append("股票代码: ").append(stock.getStockCode()).append("\n");
        prompt.append("异动标题: ").append(
                stock.getTitleZh() != null ? stock.getTitleZh() : stock.getTitle()
        ).append("\n");
        prompt.append("相关标签: ").append(
                stock.getTags() != null ? stock.getTags() : "无"
        ).append("\n");
        prompt.append("发生时间: ").append(stock.getPubDateBj()).append("\n\n");

        // 历史相似案例
        if (!similarCases.isEmpty()) {
            prompt.append("【历史相似案例】（按相关性排序）\n");
            for (int i = 0; i < similarCases.size(); i++) {
                HistoricalCase c = similarCases.get(i);
                prompt.append(String.format("""
                        案例%d:
                        - 股票: %s
                        - 事件: %s
                        - 当时分析: %s
                        - 实际影响: %s
                        - 发生时间: %s

                        """,
                        i + 1,
                        c.getStockCode(),
                        c.getTitle(),
                        c.getAnalysis() != null ? c.getAnalysis() : "暂无",
                        c.getActualImpact() != null ? c.getActualImpact() : "待观察",
                        c.getOccurredAt()
                ));
            }
        } else {
            prompt.append("【历史相似案例】\n暂无相似历史案例\n\n");
        }

        // 分析要求（优化版）
        prompt.append("""
                【分析要求】
                请提供结构化的专业分析，包含以下内容：

                1. 事件分类
                   - 识别事件类型（财报/并购/监管/诉讼/产品/其他）
                   - 评估事件的重要性级别（高/中/低）

                2. 历史对比
                   - 与历史案例的相似点
                   - 与历史案例的差异点
                   - 历史案例的经验教训

                3. 影响评估
                   - 短期影响（1-3天）：预期涨跌幅范围
                   - 中期影响（1-4周）：趋势判断
                   - 关键影响因素

                4. 价格预测
                   - 目标价格区间（如果可预测）
                   - 支撑位和阻力位
                   - 置信度（高/中/低）

                5. 风险提示
                   - 主要风险因素
                   - 需要关注的后续事件

                6. 操作建议
                   - 建议操作（买入/持有/观望/卖出）
                   - 建议仓位
                   - 止损止盈建议

                请给出专业、客观、可操作的分析。
                """);

        return prompt.toString();
    }

    /**
     * 生成案例ID
     */
    private String generateCaseId(USStockRss stock) {
        return stock.getStockCode() + "_" + System.currentTimeMillis();
    }
}
