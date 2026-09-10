package com.itzixi.ai.controller.retail;

import com.itzixi.ai.service.retail.SmartMoneyService;
import com.itzixi.common.response.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/ai/retail")
@Tag(name = "Retail Investor AI", description = "散户专属AI服务")
public class SmartMoneyController {

    @Resource
    private SmartMoneyService smartMoneyService;

    @GetMapping("/smart-money")
    @Operation(summary = "获取主力动向")
    public Result<List<SmartMoneyService.SmartMoneySignal>> getSmartMoneySignals(@RequestParam String stockCode) {
        List<SmartMoneyService.SmartMoneySignal> signals = smartMoneyService.getSmartMoneySignals(stockCode);
        return Result.success(signals);
    }
}
