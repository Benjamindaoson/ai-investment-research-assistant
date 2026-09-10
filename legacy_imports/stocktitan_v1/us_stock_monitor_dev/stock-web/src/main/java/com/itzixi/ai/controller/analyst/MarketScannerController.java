package com.itzixi.ai.controller.analyst;

import com.itzixi.ai.service.analyst.MarketScannerService;
import com.itzixi.common.response.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/ai/analyst")
@Tag(name = "Analyst Workbench", description = "分析师工作台")
public class MarketScannerController {

    @Resource
    private MarketScannerService marketScannerService;

    @PostMapping("/scanner/scan")
    @Operation(summary = "自然语言选股")
    public Result<List<MarketScannerService.ScanResult>> scanMarket(@RequestBody Map<String, String> payload) {
        String query = payload.get("query");
        if (query == null || query.trim().isEmpty()) {
            return Result.error("查询条件不能为空");
        }

        List<MarketScannerService.ScanResult> results = marketScannerService.scanMarket(query);
        return Result.success(results);
    }
}
