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
 * 持续异动预警规则
 * 3天内异动超过10次
 *
 * @author 风间影月
 * @version 2.0
 */
@Component
public class ContinuousAlertRule implements AlertRule {

    @Resource
    private StockService stockService;

    private final int threshold = 10;

    @Override
    public String getName() {
        return "持续异动预警";
    }

    @Override
    public String getDescription() {
        return "3天内异动超过" + threshold + "次";
    }

    @Override
    public boolean match(USStockRss stock) {
        LocalDateTime gmtDate = stock.getPubDateGmt();
        Long counts = stockService.getStockUnusualCounts(
                stock,
                GMTDateConverter.minus3Day(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );
        return counts > threshold;
    }

    @Override
    public String getAlertMessage(USStockRss stock) {
        LocalDateTime gmtDate = stock.getPubDateGmt();
        Long counts = stockService.getStockUnusualCounts(
                stock,
                GMTDateConverter.minus3Day(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );
        return String.format("📈 【持续异动】股票 %s 在3天内异动 %d 次，持续活跃！",
                stock.getStockCode(), counts);
    }

    @Override
    public AlertLevel getLevel() {
        return AlertLevel.NORMAL;
    }
}
