package com.itzixi.common.exception;

/**
 * RSS解析异常
 *
 * @author 风间影月
 * @version 2.0
 */
public class RssParseException extends StockMonitorException {

    public RssParseException(String message) {
        super("RSS_PARSE_ERROR", message);
    }

    public RssParseException(String message, Throwable cause) {
        super("RSS_PARSE_ERROR", message, cause);
    }
}
