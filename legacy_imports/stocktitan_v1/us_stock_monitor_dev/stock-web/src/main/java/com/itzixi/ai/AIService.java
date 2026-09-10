package com.itzixi.ai;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.messages.Message;
import org.springframework.ai.chat.messages.UserMessage;
import org.springframework.ai.chat.prompt.Prompt;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * AI服务基类
 * 封装与大模型的交互逻辑
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Slf4j
@Service
public class AIService {

    private final ChatClient chatClient;

    @Value("${spring.ai.openai.api-key:}")
    private String apiKey;

    @Value("${spring.ai.openai.model:gpt-4}")
    private String model;

    public AIService(ChatClient.Builder chatClientBuilder) {
        this.chatClient = chatClientBuilder.build();
    }

    /**
     * 调用大模型（简单对话）
     */
    public String chat(String userMessage) {
        if (!isOpenAiConfigured()) {
            return "AI服务未配置可用的OpenAI Key，已降级为本地模式。";
        }
        try {
            log.debug("AI请求: {}", userMessage);
            String response = chatClient.prompt()
                    .user(userMessage)
                    .call()
                    .content();
            log.debug("AI响应: {}", response);
            return response;
        } catch (Exception e) {
            log.error("AI调用失败: {}", e.getMessage(), e);
            return "AI服务暂时不可用，请稍后重试";
        }
    }

    /**
     * 调用大模型（带系统提示词）
     */
    public String chatWithSystem(String systemPrompt, String userMessage) {
        if (!isOpenAiConfigured()) {
            return "AI服务未配置可用的OpenAI Key，已降级为本地模式。";
        }
        try {
            log.debug("AI请求 [系统提示: {}] [用户: {}]", systemPrompt, userMessage);
            String response = chatClient.prompt()
                    .system(systemPrompt)
                    .user(userMessage)
                    .call()
                    .content();
            log.debug("AI响应: {}", response);
            return response;
        } catch (Exception e) {
            log.error("AI调用失败: {}", e.getMessage(), e);
            return "AI服务暂时不可用，请稍后重试";
        }
    }

    /**
     * 流式调用（适合长文本生成）
     */
    public void chatStream(String userMessage, java.util.function.Consumer<String> callback) {
        if (!isOpenAiConfigured()) {
            callback.accept("AI服务未配置可用的OpenAI Key，已降级为本地模式。");
            return;
        }
        try {
            chatClient.prompt()
                    .user(userMessage)
                    .stream()
                    .content()
                    .subscribe(callback);
        } catch (Exception e) {
            log.error("AI流式调用失败: {}", e.getMessage(), e);
            callback.accept("AI服务暂时不可用");
        }
    }

    /**
     * 结构化输出（返回JSON）
     */
    public <T> T chatWithStructuredOutput(String userMessage, Class<T> responseType) {
        if (!isOpenAiConfigured()) {
            return null;
        }
        try {
            return chatClient.prompt()
                    .user(userMessage)
                    .call()
                    .entity(responseType);
        } catch (Exception e) {
            log.error("AI结构化输出失败: {}", e.getMessage(), e);
            return null;
        }
    }

    private boolean isOpenAiConfigured() {
        if (apiKey == null) {
            return false;
        }
        String key = apiKey.trim().toLowerCase();
        if (key.isEmpty()) {
            return false;
        }
        return !(key.contains("placeholder") || key.contains("local-dev"));
    }
}
