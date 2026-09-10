package com.itzixi.aspect;

import com.itzixi.common.annotation.Monitor;
import lombok.extern.slf4j.Slf4j;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.reflect.MethodSignature;
import org.springframework.stereotype.Component;
import org.springframework.util.StopWatch;

import java.lang.reflect.Method;

/**
 * 性能监控切面
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@Aspect
@Component
public class PerformanceMonitorAspect {

    @Around("@annotation(com.itzixi.common.annotation.Monitor)")
    public Object monitor(ProceedingJoinPoint pjp) throws Throwable {
        MethodSignature signature = (MethodSignature) pjp.getSignature();
        Method method = signature.getMethod();
        Monitor monitor = method.getAnnotation(Monitor.class);

        String methodName = pjp.getTarget().getClass().getSimpleName() + "." + method.getName();
        String description = monitor.value().isEmpty() ? methodName : monitor.value();

        StopWatch stopWatch = new StopWatch();
        stopWatch.start();

        Object result = null;
        try {
            result = pjp.proceed();
            stopWatch.stop();

            long takeTime = stopWatch.getTotalTimeMillis();

            if (takeTime > monitor.slowThreshold()) {
                log.warn("🐌 慢方法告警 [{}] 耗时: {}ms (阈值: {}ms)", description, takeTime, monitor.slowThreshold());
            } else {
                log.info("⚡ 方法执行 [{}] 耗时: {}ms", description, takeTime);
            }

            return result;
        } catch (Exception e) {
            stopWatch.stop();
            log.error("💥 方法异常 [{}] 耗时: {}ms, 异常: {}", description, stopWatch.getTotalTimeMillis(), e.getMessage());
            throw e;
        }
    }
}
