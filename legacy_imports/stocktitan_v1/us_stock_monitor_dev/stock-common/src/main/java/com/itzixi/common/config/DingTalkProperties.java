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
@ConfigurationProperties(prefix = "dingding")
public class DingTalkProperties {

    private String token;

    private String secret;

    private String userid;

    private Boolean enabled = true;

    private Integer maxRetries = 3;

    private Long retryDelay = 1000L;

    @AssertTrue(message = "When dingding.enabled=true, token/secret/userid must be configured with non-placeholder values")
    public boolean isConfigValidWhenEnabled() {
        if (!Boolean.TRUE.equals(enabled)) {
            return true;
        }
        return isMeaningful(token) && isMeaningful(secret) && isMeaningful(userid);
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
