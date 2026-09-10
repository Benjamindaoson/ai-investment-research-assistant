package com.itzixi.ai.controller.analyst;

import com.itzixi.ai.service.analyst.ResearchAgentService;
import com.itzixi.common.response.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/ai/analyst")
@Tag(name = "Analyst Workbench", description = "分析师工作台")
public class ResearchAgentController {

    @Resource
    private ResearchAgentService researchAgentService;

    @PostMapping("/research/generate")
    @Operation(summary = "生成研报初稿")
    public Result<String> generateReport(@RequestBody Map<String, String> payload) {
        String stockCode = payload.get("stockCode");
        String focusArea = payload.getOrDefault("focusArea", "General Update");

        if (stockCode == null || stockCode.trim().isEmpty()) {
            return Result.error("股票代码不能为空");
        }

        String report = researchAgentService.generateReport(stockCode, focusArea);
        return Result.success(report);
    }
}
