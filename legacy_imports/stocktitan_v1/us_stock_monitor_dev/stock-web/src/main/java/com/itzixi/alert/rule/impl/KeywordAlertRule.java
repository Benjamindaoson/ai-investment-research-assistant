package com.itzixi.alert.rule.impl;

import com.itzixi.alert.rule.AlertLevel;
import com.itzixi.alert.rule.AlertRule;
import com.itzixi.entity.USStockRss;
import org.springframework.stereotype.Component;

/**
 * 关键标签预警规则
 * 包含特定关键标签时触发
 *
 * @author 风间影月
 * @version 2.0
 */
@Component
public class KeywordAlertRule implements AlertRule {

    private static final String[] KEYWORDS = {
            "破产", "诉讼", "FDA", "临床试验", "收购", "合并"
    };

    @Override
    public String getName() {
        return "关键标签预警";
    }

    @Override
    public String getDescription() {
        return "包含关键标签：破产、诉讼、FDA等";
    }

    @Override
    public boolean match(USStockRss stock) {
        String tags = stock.getTags();
        if (tags == null || tags.isEmpty()) {
            return false;
        }

        for (String keyword : KEYWORDS) {
            if (tags.contains(keyword)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public String getAlertMessage(USStockRss stock) {
        return String.format("⚠️ 【关键事件】股票 %s 出现关键标签：%s",
                stock.getStockCode(), stock.getTags());
    }

    @Override
    public AlertLevel getLevel() {
        return AlertLevel.URGENT;
    }
}
