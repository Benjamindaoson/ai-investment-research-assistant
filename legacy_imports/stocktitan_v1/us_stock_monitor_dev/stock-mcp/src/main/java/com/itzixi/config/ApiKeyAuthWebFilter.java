package com.itzixi.config;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.util.StringUtils;
import org.springframework.web.server.ServerWebExchange;
import org.springframework.web.server.WebFilter;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.nio.charset.StandardCharsets;

@Slf4j
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 10)
@RequiredArgsConstructor
public class ApiKeyAuthWebFilter implements WebFilter {

    private static final String DEFAULT_API_KEY_HEADER = "X-API-KEY";
    private final AppSecurityProperties securityProperties;
    private final AntPathMatcher antPathMatcher = new AntPathMatcher();

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, WebFilterChain chain) {
        if (!Boolean.TRUE.equals(securityProperties.getEnabled())) {
            return chain.filter(exchange);
        }

        String requestPath = exchange.getRequest().getPath().value();
        if (isPermitAllPath(requestPath)) {
            return chain.filter(exchange);
        }

        String expectedApiKey = securityProperties.getApiKey();
        if (!securityProperties.isMeaningful(expectedApiKey)) {
            return writeError(exchange, HttpStatus.SERVICE_UNAVAILABLE,
                    "{\"code\":503,\"msg\":\"API key auth enabled but key is not configured\"}");
        }

        String headerName = StringUtils.hasText(securityProperties.getApiKeyHeader())
                ? securityProperties.getApiKeyHeader()
                : DEFAULT_API_KEY_HEADER;
        String providedApiKey = exchange.getRequest().getHeaders().getFirst(headerName);
        if (!StringUtils.hasText(providedApiKey)) {
            providedApiKey = exchange.getRequest().getQueryParams().getFirst("apiKey");
        }

        if (expectedApiKey.equals(providedApiKey)) {
            return chain.filter(exchange);
        }

        log.warn("Rejected unauthorized MCP request: method={}, path={}, remote={}",
                exchange.getRequest().getMethod(), requestPath, exchange.getRequest().getRemoteAddress());
        return writeError(exchange, HttpStatus.UNAUTHORIZED,
                "{\"code\":401,\"msg\":\"Unauthorized: invalid API key\"}");
    }

    private boolean isPermitAllPath(String requestPath) {
        for (String pattern : securityProperties.getPermitAllPaths()) {
            if (antPathMatcher.match(pattern, requestPath)) {
                return true;
            }
        }
        return false;
    }

    private Mono<Void> writeError(ServerWebExchange exchange, HttpStatus status, String body) {
        var response = exchange.getResponse();
        response.setStatusCode(status);
        response.getHeaders().setContentType(MediaType.APPLICATION_JSON);
        byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
        return response.writeWith(Mono.just(response.bufferFactory().wrap(bytes)));
    }
}
