package com.itzixi.alert.rule.impl;

import com.itzixi.alert.rule.AlertLevel;
import com.itzixi.alert.rule.AlertRule;
import com.itzixi.entity.USStockRss;
import com.itzixi.service.StockService;
import com.itzixi.utils.GMTDateConverter;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

/**
 * 频繁异动预警规则
 * 24小时内异动超过指定次数
 *
 * @author 风间影月
 * @version 2.0
 */
@Component
public class FrequentAlertRule implements AlertRule {

    @Resource
    private StockService stockService;

    private final int threshold = 5; // 阈值：5次

    @Override
    public String getName() {
        return "频繁异动预警";
    }

    @Override
    public String getDescription() {
        return "24小时内异动超过" + threshold + "次";
    }

    @Override
    public boolean match(USStockRss stock) {
        LocalDateTime gmtDate = stock.getPubDateGmt();
        Long counts = stockService.getStockUnusualCounts(
                stock,
                GMTDateConverter.minus24Hour(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );
        return counts > threshold;
    }

    @Override
    public String getAlertMessage(USStockRss stock) {
        LocalDateTime gmtDate = stock.getPubDateGmt();
        Long counts = stockService.getStockUnusualCounts(
                stock,
                GMTDateConverter.minus24Hour(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );
        return String.format("🔥 【频繁异动】股票 %s 在24小时内异动 %d 次，超过阈值 %d 次！",
                stock.getStockCode(), counts, threshold);
    }

    @Override
    public AlertLevel getLevel() {
        return AlertLevel.IMPORTANT;
    }
}
