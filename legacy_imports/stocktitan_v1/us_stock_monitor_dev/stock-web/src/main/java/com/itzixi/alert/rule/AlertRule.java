package com.itzixi.alert.rule;

import com.itzixi.entity.USStockRss;

/**
 * 预警规则接口
 *
 * @author 风间影月
 * @version 2.0
 */
public interface AlertRule {

    /**
     * 规则名称
     */
    String getName();

    /**
     * 规则描述
     */
    String getDescription();

    /**
     * 判断是否匹配规则
     */
    boolean match(USStockRss stock);

    /**
     * 获取预警消息
     */
    String getAlertMessage(USStockRss stock);

    /**
     * 预警级别
     */
    AlertLevel getLevel();
}
