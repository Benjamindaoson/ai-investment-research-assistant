package com.itzixi.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

@Data
@Component
@ConfigurationProperties(prefix = "app.security")
public class AppSecurityProperties {

    private Boolean enabled = false;

    private String apiKeyHeader = "X-API-KEY";

    private String apiKey;

    private List<String> permitAllPaths = new ArrayList<>(List.of(
            "/actuator/health",
            "/actuator/health/**",
            "/error"
    ));

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
