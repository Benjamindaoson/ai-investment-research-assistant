package com.itzixi.service;

import com.itzixi.entity.USStockMsg;

import java.util.List;

/**
 * @ClassName WechatWorkBotService
 * @Author 风间影月
 * @Version 1.0
 * @Description 企业微信机器人推送服务
 **/
public interface WechatWorkBotService {

    void sendMessage(String text);

    void sendMessage(List<USStockMsg> msgList);

}
