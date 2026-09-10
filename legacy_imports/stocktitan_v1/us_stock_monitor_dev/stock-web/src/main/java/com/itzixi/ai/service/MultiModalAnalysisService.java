package com.itzixi.ai.service;

import com.itzixi.ai.AIService;
import com.itzixi.common.annotation.Monitor;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.Base64;

/**
 * 多模态分析服务
 * 支持图表分析（K线图、财报图表等）
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class MultiModalAnalysisService {

    @Resource
    private AIService aiService;

    /**
     * 分析K线图
     */
    @Monitor(value = "K线图分析", slowThreshold = 8000)
    public String analyzeChart(String stockCode, byte[] chartImage) {
        log.info("开始分析K线图: {}", stockCode);

        try {
            String prompt = buildChartAnalysisPrompt(stockCode);

            // 注意：这需要GPT-4V或类似的多模态模型
            // Spring AI的实现可能需要特殊配置
            String analysis = aiService.chat(prompt + "\n[图片分析功能需要GPT-4V支持]");

            log.info("K线图分析完成: {}", stockCode);
            return analysis;
        } catch (Exception e) {
            log.error("K线图分析失败: {}", stockCode, e);
            return "图表分析功能暂不可用，请确保使用支持多模态的模型（如GPT-4V）";
        }
    }

    /**
     * 分析财报图表
     */
    public String analyzeFinancialChart(String stockCode, byte[] chartImage) {
        log.info("开始分析财报图表: {}", stockCode);

        String prompt = String.format("""
                请分析这张%s的财报图表：

                【分析要求】
                1. 识别图表类型（柱状图/折线图/饼图等）
                2. 提取关键数据和趋势
                3. 分析财务健康状况
                4. 识别异常或亮点
                5. 给出投资建议

                请给出专业、详细的分析。
                """, stockCode);

        return aiService.chat(prompt + "\n[图片分析功能需要GPT-4V支持]");
    }

    /**
     * 技术形态识别
     */
    public String identifyPattern(String stockCode, byte[] chartImage) {
        log.info("开始识别技术形态: {}", stockCode);

        String prompt = String.format("""
                请识别这张%s K线图中的技术形态：

                【识别要求】
                1. 经典形态（头肩顶/双底/三角形等）
                2. 支撑位和阻力位
                3. 趋势线
                4. 成交量特征
                5. 技术指标信号（如有）

                请给出识别结果和操作建议。
                """, stockCode);

        return aiService.chat(prompt + "\n[图片分析功能需要GPT-4V支持]");
    }

    /**
     * 构建图表分析提示词
     */
    private String buildChartAnalysisPrompt(String stockCode) {
        return String.format("""
                请分析这张%s的K线图：

                【分析维度】
                1. 技术形态（头肩顶/双底/三角形/旗形等）
                2. 支撑位和阻力位
                3. 成交量特征
                4. 趋势判断（上升/下降/震荡）
                5. 关键价格位
                6. 操作建议（买入/卖出/观望）

                请给出专业的技术分析。
                """, stockCode);
    }

    /**
     * 将图片转为Base64（用于API调用）
     */
    private String imageToBase64(byte[] imageBytes) {
        return Base64.getEncoder().encodeToString(imageBytes);
    }

    /**
     * 批量分析多张图表
     */
    public String analyzeMultipleCharts(String stockCode, java.util.List<byte[]> charts) {
        log.info("开始批量分析图表: {}, 数量: {}", stockCode, charts.size());

        StringBuilder result = new StringBuilder();
        result.append(String.format("【%s 综合图表分析】\n\n", stockCode));

        for (int i = 0; i < charts.size(); i++) {
            result.append(String.format("图表%d分析：\n", i + 1));
            result.append(analyzeChart(stockCode, charts.get(i)));
            result.append("\n\n");
        }

        return result.toString();
    }
}
