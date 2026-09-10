package com.itzixi.ai.controller.retail;

import com.itzixi.ai.service.retail.SimplificationService;
import com.itzixi.common.response.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/ai/retail")
@Tag(name = "Retail Investor AI", description = "散户专属AI服务")
public class SimplificationController {

    @Resource
    private SimplificationService simplificationService;

    @PostMapping("/simplify")
    @Operation(summary = "简化金融文本")
    public Result<String> simplify(@RequestBody Map<String, String> payload,
                                   @RequestParam(defaultValue = "beginner") String level) {
        String text = payload.get("text");
        if (text == null || text.trim().isEmpty()) {
            return Result.error("文本不能为空");
        }

        String simplified = simplificationService.simplify(text, level);
        return Result.success(simplified);
    }
}
