package com.itzixi.common.exception;

/**
 * 数据访问异常
 *
 * @author 风间影月
 * @version 2.0
 */
public class DataAccessException extends StockMonitorException {

    public DataAccessException(String message) {
        super("DATA_ACCESS_ERROR", message);
    }

    public DataAccessException(String message, Throwable cause) {
        super("DATA_ACCESS_ERROR", message, cause);
    }
}
