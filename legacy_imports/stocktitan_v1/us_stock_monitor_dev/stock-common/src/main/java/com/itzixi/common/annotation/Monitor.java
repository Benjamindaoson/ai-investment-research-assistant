package com.itzixi.common.annotation;

import java.lang.annotation.*;

/**
 * 性能监控注解
 * 用于标记需要监控性能的方法
 *
 * @author 风间影月
 * @version 2.0
 */
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@Documented
public @interface Monitor {

    /**
     * 操作描述
     */
    String value() default "";

    /**
     * 慢方法阈值（毫秒）
     */
    long slowThreshold() default 3000;
}
