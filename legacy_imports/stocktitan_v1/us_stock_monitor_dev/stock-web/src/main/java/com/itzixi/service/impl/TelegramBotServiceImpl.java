package com.itzixi.service.impl;

import com.itzixi.common.config.TelegramProperties;
import com.itzixi.common.exception.NotificationException;
import com.itzixi.common.retry.RetryUtil;
import com.itzixi.entity.USStockMsg;
import com.itzixi.service.TelegramBotService;
import com.itzixi.utils.TelegramMessageSplitter;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Telegram机器人服务实现
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@Service
public class TelegramBotServiceImpl implements TelegramBotService {

    /**
     * 声明：禁止使用Telegram进行违反国家法律法规的活动
     */

    @Resource
    private RestTemplate restTemplate;

    @Resource
    private TelegramProperties telegramProperties;

    public String formatStockInfoHtml(USStockMsg stock) {
        return "<b>📌 代码: " + stock.getStockCode() + "</b>\n" +
                "📅 时间: " + stock.getPubDateBj() + "\n" +
                "📰 标题: " + stock.getTitleZh() + "\n" +
                "🏷️ 标签: " + stock.getTags() + "\n" +
                "📊 统计: 24小时异动=" + stock.getCounts24Hour() + "次" +
                ", 3天内异动=" + stock.getCounts3Day() + "次" +
                ", 1周内异动=" + stock.getCounts1Week() + "次";
    }

    public String formatStockListHtml(List<USStockMsg> stocks) {
        return stocks.stream()
                .map(this::formatStockInfoHtml)
                .collect(Collectors.joining("\n\n------\n\n"));
    }

    @Override
    public void sendMessage(List<USStockMsg> msgList) throws Exception {
        if (!telegramProperties.getEnabled()) {
            log.info("Telegram推送已禁用，跳过发送");
            return;
        }

        List<List<USStockMsg>> result = TelegramMessageSplitter.splitList(msgList);
        for (List<USStockMsg> group : result) {
            String singleListStr = formatStockListHtml(group);
            sendMessage(singleListStr);
        }
    }

    @Override
    public void sendMessage(String text) {
        if (!telegramProperties.getEnabled()) {
            log.info("Telegram推送已禁用，跳过发送");
            return;
        }

        try {
            RetryUtil.executeWithRetry(
                    () -> sendMessageInternal(text),
                    telegramProperties.getMaxRetries(),
                    telegramProperties.getRetryDelay(),
                    "Telegram消息发送"
            );
            log.info("Telegram消息发送成功");
        } catch (Exception e) {
            log.error("Telegram消息发送失败: {}", e.getMessage(), e);
            throw new NotificationException("Telegram消息发送失败", e);
        }
    }

    private String sendMessageInternal(String text) {
        Map<String, String> request = new HashMap<>();
        request.put("chat_id", telegramProperties.getChatId());
        request.put("text", text);
        request.put("parse_mode", "HTML");

        String response = restTemplate.postForObject(
                telegramProperties.getApiUrl(),
                request,
                String.class
        );
        log.debug("Telegram API 响应: {}", response);
        return response;
    }
}
