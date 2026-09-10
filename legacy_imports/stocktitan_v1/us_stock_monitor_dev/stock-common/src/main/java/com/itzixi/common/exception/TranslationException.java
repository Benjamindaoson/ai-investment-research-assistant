package com.itzixi.common.exception;

/**
 * 翻译服务异常
 *
 * @author 风间影月
 * @version 2.0
 */
public class TranslationException extends StockMonitorException {

    public TranslationException(String message) {
        super("TRANSLATION_ERROR", message);
    }

    public TranslationException(String message, Throwable cause) {
        super("TRANSLATION_ERROR", message, cause);
    }
}
