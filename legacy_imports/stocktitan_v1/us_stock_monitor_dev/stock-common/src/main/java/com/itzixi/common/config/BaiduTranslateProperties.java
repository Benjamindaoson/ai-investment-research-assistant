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
@ConfigurationProperties(prefix = "baidu.translate")
public class BaiduTranslateProperties {

    private String host;

    private String appid;

    private String securityKey;

    private Boolean enabled = true;

    private Long cacheExpireSeconds = 86400L;

    private Integer maxRetries = 3;

    private Long retryDelay = 1000L;

    @AssertTrue(message = "When baidu.translate.enabled=true, appid/securityKey must be configured with non-placeholder values")
    public boolean isConfigValidWhenEnabled() {
        if (!Boolean.TRUE.equals(enabled)) {
            return true;
        }
        return StringUtils.hasText(host) && isMeaningful(appid) && isMeaningful(securityKey);
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
