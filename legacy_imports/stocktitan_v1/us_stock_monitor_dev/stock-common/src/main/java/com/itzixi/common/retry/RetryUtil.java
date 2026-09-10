package com.itzixi.common.retry;

import lombok.extern.slf4j.Slf4j;

import java.util.function.Supplier;

/**
 * 重试工具类
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
public class RetryUtil {

    /**
     * 执行带重试的操作
     *
     * @param supplier 要执行的操作
     * @param maxRetries 最大重试次数
     * @param retryDelay 重试延迟（毫秒）
     * @param operationName 操作名称（用于日志）
     * @return 操作结果
     */
    public static <T> T executeWithRetry(Supplier<T> supplier, int maxRetries, long retryDelay, String operationName) {
        int attempt = 0;
        Exception lastException = null;

        while (attempt < maxRetries) {
            try {
                return supplier.get();
            } catch (Exception e) {
                lastException = e;
                attempt++;
                if (attempt < maxRetries) {
                    log.warn("{}执行失败，第{}次重试，错误: {}", operationName, attempt, e.getMessage());
                    try {
                        Thread.sleep(retryDelay);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        throw new RuntimeException(operationName + "重试被中断", ie);
                    }
                }
            }
        }

        log.error("{}执行失败，已达到最大重试次数{}", operationName, maxRetries);
        throw new RuntimeException(operationName + "执行失败", lastException);
    }

    /**
     * 执行带重试的操作（使用默认参数）
     */
    public static <T> T executeWithRetry(Supplier<T> supplier, String operationName) {
        return executeWithRetry(supplier, 3, 1000, operationName);
    }
}
