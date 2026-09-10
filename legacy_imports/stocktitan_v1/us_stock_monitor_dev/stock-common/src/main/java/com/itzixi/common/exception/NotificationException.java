package com.itzixi.common.exception;

/**
 * 通知服务异常
 *
 * @author 风间影月
 * @version 2.0
 */
public class NotificationException extends StockMonitorException {

    public NotificationException(String message) {
        super("NOTIFICATION_ERROR", message);
    }

    public NotificationException(String message, Throwable cause) {
        super("NOTIFICATION_ERROR", message, cause);
    }
}
