package com.itzixi.common.exception;

import lombok.Getter;

/**
 * 股票监控系统基础异常类
 *
 * @author 风间影月
 * @version 2.0
 */
@Getter
public class StockMonitorException extends RuntimeException {

    private final String errorCode;
    private final Object[] args;

    public StockMonitorException(String message) {
        super(message);
        this.errorCode = "UNKNOWN_ERROR";
        this.args = null;
    }

    public StockMonitorException(String errorCode, String message) {
        super(message);
        this.errorCode = errorCode;
        this.args = null;
    }

    public StockMonitorException(String errorCode, String message, Throwable cause) {
        super(message, cause);
        this.errorCode = errorCode;
        this.args = null;
    }

    public StockMonitorException(String errorCode, String message, Object[] args) {
        super(message);
        this.errorCode = errorCode;
        this.args = args;
    }

    public StockMonitorException(String errorCode, String message, Throwable cause, Object[] args) {
        super(message, cause);
        this.errorCode = errorCode;
        this.args = args;
    }
}
