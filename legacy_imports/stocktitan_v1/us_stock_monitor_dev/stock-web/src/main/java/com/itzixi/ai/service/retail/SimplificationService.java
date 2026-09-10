package com.itzixi.ai.service.retail;

import com.itzixi.ai.AIService;
import com.itzixi.common.annotation.Monitor;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

/**
 * 散户友好化服务 ("说人话"服务)
 * 将复杂的金融文本转化为简单易懂的语言
 *
 * @author 风间影月
 * @version 1.0 - Retail First
 */
@Slf4j
@Service
public class SimplificationService {

    @Resource
    private AIService aiService;

    /**
     * 简化金融文本
     *
     * @param text  原始文本
     * @param level 简化等级 (beginner/intermediate)
     * @return 简化后的文本
     */
    @Monitor(value = "文本简化", slowThreshold = 3000)
    public String simplify(String text, String level) {
        log.info("开始简化文本, level={}", level);

        try {
            String prompt = buildSimplificationPrompt(text, level);
            return aiService.chat(prompt);
        } catch (Exception e) {
            log.error("文本简化失败", e);
            return "抱歉，AI暂时无法简化此内容，请参考原文。";
        }
    }

    /**
     * 构建简化提示词
     */
    private String buildSimplificationPrompt(String text, String level) {
        String levelInstruction = "beginner".equalsIgnoreCase(level) ?
                "目标受众是没有任何金融背景的散户小白。请使用大白话、简单的比喻。" :
                "目标受众是有一定经验的散户。保留关键数据，但解释复杂的术语。";

        return String.format("""
                请作为一位资深的投资顾问，将以下金融文本翻译成"人话"：

                【原始文本】
                %s

                【翻译要求】
                1. %s
                2. 核心解释：这件事对股价是利好还是利空？为什么？
                3. 风险提示：有什么需要小心的陷阱？
                4. 篇幅限制：100字以内。
                5. 语气：亲切、客观、像朋友一样聊天。
                6. 禁止使用复杂的金融黑话（如"同比环比"、"EBITDA"），必须解释清楚。

                请直接输出翻译后的内容，不要包含"翻译如下"等废话。
                """, text, levelInstruction);
    }
}
