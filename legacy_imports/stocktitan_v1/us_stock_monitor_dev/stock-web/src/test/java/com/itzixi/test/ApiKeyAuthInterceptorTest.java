package com.itzixi.test;

import com.itzixi.config.ApiKeyAuthInterceptor;
import com.itzixi.config.AppSecurityProperties;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ApiKeyAuthInterceptorTest {

    private AppSecurityProperties properties;
    private ApiKeyAuthInterceptor interceptor;

    @BeforeEach
    void setUp() {
        properties = new AppSecurityProperties();
        properties.setEnabled(true);
        properties.setApiKey("test-key");
        interceptor = new ApiKeyAuthInterceptor(properties);
    }

    @Test
    void shouldAllowPermitAllPath() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/hello/world");
        MockHttpServletResponse response = new MockHttpServletResponse();

        assertTrue(interceptor.preHandle(request, response, new Object()));
    }

    @Test
    void shouldRejectMissingApiKey() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/statistics/overview");
        MockHttpServletResponse response = new MockHttpServletResponse();

        assertFalse(interceptor.preHandle(request, response, new Object()));
        assertTrue(response.getStatus() == 401);
    }

    @Test
    void shouldAllowValidHeaderApiKey() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/statistics/overview");
        request.addHeader("X-API-KEY", "test-key");
        MockHttpServletResponse response = new MockHttpServletResponse();

        assertTrue(interceptor.preHandle(request, response, new Object()));
    }

    @Test
    void shouldAllowValidQueryApiKey() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest("GET", "/api/statistics/overview");
        request.setParameter("apiKey", "test-key");
        MockHttpServletResponse response = new MockHttpServletResponse();

        assertTrue(interceptor.preHandle(request, response, new Object()));
    }
}

