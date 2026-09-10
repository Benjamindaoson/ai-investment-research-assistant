package com.itzixi.config;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.util.StringUtils;
import org.springframework.web.servlet.HandlerInterceptor;

import java.io.IOException;

@Slf4j
@Component
@RequiredArgsConstructor
public class ApiKeyAuthInterceptor implements HandlerInterceptor {

    private static final String DEFAULT_API_KEY_HEADER = "X-API-KEY";
    private final AntPathMatcher pathMatcher = new AntPathMatcher();
    private final AppSecurityProperties securityProperties;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        if (!Boolean.TRUE.equals(securityProperties.getEnabled())) {
            return true;
        }

        String requestPath = request.getRequestURI();
        if (isPermitAllPath(requestPath)) {
            return true;
        }

        String expectedApiKey = securityProperties.getApiKey();
        if (!securityProperties.isMeaningful(expectedApiKey)) {
            writeError(response, HttpServletResponse.SC_SERVICE_UNAVAILABLE,
                    "{\"code\":503,\"msg\":\"API key auth enabled but key is not configured\"}");
            return false;
        }

        String headerName = StringUtils.hasText(securityProperties.getApiKeyHeader())
                ? securityProperties.getApiKeyHeader()
                : DEFAULT_API_KEY_HEADER;
        String providedApiKey = request.getHeader(headerName);
        if (!StringUtils.hasText(providedApiKey)) {
            providedApiKey = request.getParameter("apiKey");
        }

        if (expectedApiKey.equals(providedApiKey)) {
            return true;
        }

        log.warn("Rejected unauthorized request: method={}, path={}, remote={}",
                request.getMethod(), requestPath, request.getRemoteAddr());
        writeError(response, HttpServletResponse.SC_UNAUTHORIZED,
                "{\"code\":401,\"msg\":\"Unauthorized: invalid API key\"}");
        return false;
    }

    private boolean isPermitAllPath(String requestPath) {
        for (String pattern : securityProperties.getPermitAllPaths()) {
            if (pathMatcher.match(pattern, requestPath)) {
                return true;
            }
        }
        return false;
    }

    private void writeError(HttpServletResponse response, int statusCode, String body) throws IOException {
        response.setStatus(statusCode);
        response.setCharacterEncoding("UTF-8");
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write(body);
    }
}
