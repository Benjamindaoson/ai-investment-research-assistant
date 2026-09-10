package com.itzixi.service;

import com.itzixi.entity.USStockMsg;

import java.util.List;

/**
 * @ClassName TelegramBotService
 * @Author 风间影月
 * @Version 1.0
 * @Description TelegramBotService
 **/
public interface TelegramBotService {

    /**
     * @Description: 用于发送单个消息（测试）
     * @Author 风间影月
     * @param text
     */
    public void sendMessage(String text);

    /**
     * @Description: 发送消息
     * @Author 风间影月
     * @param msgList
     */
    public void sendMessage(List<USStockMsg> msgList) throws Exception;

}
