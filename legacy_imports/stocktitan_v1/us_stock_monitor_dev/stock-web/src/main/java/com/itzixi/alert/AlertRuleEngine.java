package com.itzixi.alert;

import com.itzixi.alert.rule.AlertLevel;
import com.itzixi.alert.rule.AlertRule;
import com.itzixi.entity.USStockRss;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * 预警规则引擎
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@Service
public class AlertRuleEngine {

    @Resource
    private List<AlertRule> alertRules;

    @PostConstruct
    public void init() {
        log.info("预警规则引擎初始化完成，加载规则数量: {}", alertRules.size());
        alertRules.forEach(rule -> log.info("  - {}: {}", rule.getName(), rule.getDescription()));
    }

    /**
     * 评估股票是否触发预警
     */
    public List<AlertResult> evaluate(USStockRss stock) {
        List<AlertResult> results = new ArrayList<>();

        for (AlertRule rule : alertRules) {
            try {
                if (rule.match(stock)) {
                    AlertResult result = new AlertResult();
                    result.setStockCode(stock.getStockCode());
                    result.setRuleName(rule.getName());
                    result.setLevel(rule.getLevel());
                    result.setMessage(rule.getAlertMessage(stock));
                    result.setAlertTime(LocalDateTime.now());

                    results.add(result);
                    log.info("触发预警: {}", result.getMessage());
                }
            } catch (Exception e) {
                log.error("规则执行失败: rule={}, error={}", rule.getName(), e.getMessage());
            }
        }

        return results;
    }

    /**
     * 批量评估
     */
    public List<AlertResult> evaluateBatch(List<USStockRss> stocks) {
        return stocks.stream()
                .flatMap(stock -> evaluate(stock).stream())
                .collect(Collectors.toList());
    }

    /**
     * 获取所有规则
     */
    public List<AlertRule> getAllRules() {
        return new ArrayList<>(alertRules);
    }

    /**
     * 预警结果
     */
    @lombok.Data
    public static class AlertResult {
        private String stockCode;
        private String ruleName;
        private AlertLevel level;
        private String message;
        private LocalDateTime alertTime;
    }
}
