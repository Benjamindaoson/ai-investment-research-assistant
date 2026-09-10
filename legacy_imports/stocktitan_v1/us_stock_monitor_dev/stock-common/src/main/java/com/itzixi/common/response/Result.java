package com.itzixi.common.response;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * 统一响应结果
 *
 * @author 风间影月
 * @version 2.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Result<T> {

    private Integer code;
    private String message;
    private T data;
    private LocalDateTime timestamp;

    public static <T> Result<T> success() {
        return new Result<>(200, "操作成功", null, LocalDateTime.now());
    }

    public static <T> Result<T> success(T data) {
        return new Result<>(200, "操作成功", data, LocalDateTime.now());
    }

    public static <T> Result<T> success(String message, T data) {
        return new Result<>(200, message, data, LocalDateTime.now());
    }

    public static <T> Result<T> error(String message) {
        return new Result<>(500, message, null, LocalDateTime.now());
    }

    public static <T> Result<T> error(Integer code, String message) {
        return new Result<>(code, message, null, LocalDateTime.now());
    }

    public static <T> Result<T> error(Integer code, String message, T data) {
        return new Result<>(code, message, data, LocalDateTime.now());
    }
}
