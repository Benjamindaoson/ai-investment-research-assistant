package com.itzixi.common.handler;

import com.itzixi.common.exception.StockMonitorException;
import com.itzixi.common.response.Result;
import org.junit.jupiter.api.Test;
import org.springframework.http.converter.HttpMessageNotReadableException;

import static org.junit.jupiter.api.Assertions.assertEquals;

class GlobalExceptionHandlerTest {

    private final GlobalExceptionHandler handler = new GlobalExceptionHandler();

    @Test
    void shouldReturn400ForUnreadableRequestBody() {
        Result<Void> result = handler.handleHttpMessageNotReadableException(
                new HttpMessageNotReadableException("bad json")
        );
        assertEquals(400, result.getCode());
    }

    @Test
    void shouldReturn500ForStockMonitorException() {
        Result<Void> result = handler.handleStockMonitorException(
                new StockMonitorException("E001", "boom")
        );
        assertEquals(500, result.getCode());
        assertEquals("boom", result.getMessage());
    }
}

