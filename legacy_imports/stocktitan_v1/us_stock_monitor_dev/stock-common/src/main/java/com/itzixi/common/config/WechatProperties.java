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
@ConfigurationProperties(prefix = "wechat")
public class WechatProperties {

    private Boolean enabled = false;

    private String pythonPath = "python";

    private String scriptPath;

    private Integer maxRetries = 3;

    private Long retryDelay = 1000L;

    @AssertTrue(message = "When wechat.enabled=true, scriptPath must be configured")
    public boolean isConfigValidWhenEnabled() {
        if (!Boolean.TRUE.equals(enabled)) {
            return true;
        }
        return StringUtils.hasText(scriptPath);
    }
}
