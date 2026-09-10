package com.itzixi.config;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpStatus;
import org.springframework.mock.http.server.reactive.MockServerHttpRequest;
import org.springframework.mock.web.server.MockServerWebExchange;
import org.springframework.web.server.WebFilterChain;
import reactor.core.publisher.Mono;

import java.util.concurrent.atomic.AtomicBoolean;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class ApiKeyAuthWebFilterTest {

    private AppSecurityProperties properties;
    private ApiKeyAuthWebFilter filter;

    @BeforeEach
    void setUp() {
        properties = new AppSecurityProperties();
        properties.setEnabled(true);
        properties.setApiKey("test-key");
        filter = new ApiKeyAuthWebFilter(properties);
    }

    @Test
    void shouldAllowPermitAllPath() {
        MockServerWebExchange exchange = MockServerWebExchange.from(
                MockServerHttpRequest.get("/actuator/health").build()
        );
        AtomicBoolean called = new AtomicBoolean(false);
        WebFilterChain chain = ex -> {
            called.set(true);
            return Mono.empty();
        };

        filter.filter(exchange, chain).block();

        assertTrue(called.get());
    }

    @Test
    void shouldRejectMissingApiKey() {
        MockServerWebExchange exchange = MockServerWebExchange.from(
                MockServerHttpRequest.get("/sse").build()
        );
        AtomicBoolean called = new AtomicBoolean(false);
        WebFilterChain chain = ex -> {
            called.set(true);
            return Mono.empty();
        };

        filter.filter(exchange, chain).block();

        assertEquals(HttpStatus.UNAUTHORIZED, exchange.getResponse().getStatusCode());
        assertTrue(!called.get());
    }

    @Test
    void shouldAllowValidHeaderApiKey() {
        MockServerWebExchange exchange = MockServerWebExchange.from(
                MockServerHttpRequest.get("/sse").header("X-API-KEY", "test-key").build()
        );
        AtomicBoolean called = new AtomicBoolean(false);
        WebFilterChain chain = ex -> {
            called.set(true);
            return Mono.empty();
        };

        filter.filter(exchange, chain).block();

        assertTrue(called.get());
        assertNull(exchange.getResponse().getStatusCode());
    }
}

