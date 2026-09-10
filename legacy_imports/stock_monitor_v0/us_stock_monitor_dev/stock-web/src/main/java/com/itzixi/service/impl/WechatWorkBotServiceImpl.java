package com.itzixi.service.impl;

import com.itzixi.entity.USStockMsg;
import com.itzixi.service.WechatWorkBotService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import jakarta.annotation.Resource;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * @ClassName WechatWorkBotServiceImpl
 * @Author 风间影月
 * @Version 1.0
 * @Description 企业微信群机器人 Webhook 推送实现
 **/
@Slf4j
@Service
public class WechatWorkBotServiceImpl implements WechatWorkBotService {

    @Value("${wecom.webhook-url:}")
    private String webhookUrl;

    @Resource
    private RestTemplate restTemplate;

    @Override
    public void sendMessage(String text) {
        if (webhookUrl == null || webhookUrl.isBlank()) {
            log.warn("企业微信 webhook-url 未配置，跳过推送");
            return;
        }
        Map<String, Object> body = new HashMap<>();
        body.put("msgtype", "text");
        Map<String, String> textContent = new HashMap<>();
        textContent.put("content", text);
        body.put("text", textContent);
        try {
            restTemplate.postForObject(webhookUrl, body, String.class);
        } catch (Exception e) {
            log.error("企业微信推送失败", e);
        }
    }

    @Override
    public void sendMessage(List<USStockMsg> msgList) {
        String text = msgList.stream()
                .map(this::formatStockInfo)
                .collect(Collectors.joining("\n\n------\n\n"));
        sendMessage(text);
    }

    private String formatStockInfo(USStockMsg stock) {
        return "代码: " + stock.getStockCode() + "\n" +
                "时间: " + stock.getPubDateBj() + "\n" +
                "标题: " + stock.getTitleZh() + "\n" +
                "标签: " + stock.getTags() + "\n" +
                "统计: 24小时异动=" + stock.getCounts24Hour() + "次" +
                ", 3天内异动=" + stock.getCounts3Day() + "次" +
                ", 1周内异动=" + stock.getCounts1Week() + "次";
    }

}
