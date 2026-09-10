package com.itzixi.ai.controller.retail;

import com.itzixi.ai.service.AIChatService;
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
@RequestMapping("/api/ai/retail/coach")
@Tag(name = "Retail Investor AI", description = "散户专属AI服务")
public class TradingCoachController {

    @Resource
    private AIChatService aiChatService;

    @PostMapping("/chat")
    @Operation(summary = "与交易教练聊天")
    public Result<String> chatWithCoach(@RequestBody Map<String, String> payload,
                                        @RequestParam String sessionId) {
        String message = payload.get("message");
        if (message == null || message.trim().isEmpty()) {
            return Result.error("消息不能为空");
        }

        String response = aiChatService.chatWithCoach(sessionId, message);
        return Result.success(response);
    }
}
