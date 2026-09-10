package com.itzixi.config;

import jakarta.validation.constraints.AssertTrue;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;
import org.springframework.validation.annotation.Validated;

import java.util.ArrayList;
import java.util.List;

@Data
@Component
@Validated
@ConfigurationProperties(prefix = "app.security")
public class AppSecurityProperties {

    private Boolean enabled = false;

    private String apiKeyHeader = "X-API-KEY";

    private String apiKey;

    private List<String> permitAllPaths = new ArrayList<>(List.of(
            "/hello/**",
            "/actuator/health",
            "/actuator/health/**",
            "/error"
    ));

    @AssertTrue(message = "When app.security.enabled=true, app.security.api-key must be configured with a non-placeholder value")
    public boolean isApiKeyValidWhenEnabled() {
        if (!Boolean.TRUE.equals(enabled)) {
            return true;
        }
        return isMeaningful(apiKey);
    }

    public boolean isMeaningful(String value) {
        if (!StringUtils.hasText(value)) {
            return false;
        }
        String normalized = value.trim().toLowerCase();
        return !normalized.contains("placeholder")
                && !normalized.contains("local-dev")
                && !normalized.equals("changeme");
    }
}
