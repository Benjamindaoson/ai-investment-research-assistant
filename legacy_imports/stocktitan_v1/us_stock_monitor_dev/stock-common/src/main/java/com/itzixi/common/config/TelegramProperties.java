package com.itzixi.common.config;

import jakarta.validation.constraints.AssertTrue;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.validation.annotation.Validated;

@Data
@Component
@Validated
@ConfigurationProperties(prefix = "telegram")
public class TelegramProperties {

    private String token;

    private String chatId;

    private Boolean enabled = true;

    private String apiUrl;

    private Integer maxRetries = 3;

    private Long retryDelay = 1000L;

    public String getApiUrl() {
        if (!StringUtils.hasText(apiUrl)) {
            return "https://api.telegram.org/bot" + token + "/sendMessage";
        }
        return apiUrl;
    }

    @AssertTrue(message = "When telegram.enabled=true, token/chatId must be configured with non-placeholder values")
    public boolean isConfigValidWhenEnabled() {
        if (!Boolean.TRUE.equals(enabled)) {
            return true;
        }
        return isMeaningful(token) && isMeaningful(chatId);
    }

    private boolean isMeaningful(String value) {
        if (!StringUtils.hasText(value)) {
            return false;
        }
        String normalized = value.trim().toLowerCase();
        return !normalized.contains("placeholder")
                && !normalized.contains("local-dev")
                && !normalized.equals("changeme");
    }
}
