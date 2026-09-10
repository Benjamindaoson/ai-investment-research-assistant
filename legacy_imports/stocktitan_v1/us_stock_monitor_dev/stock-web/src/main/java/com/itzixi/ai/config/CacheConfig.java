package com.itzixi.ai.config;

import org.springframework.cache.CacheManager;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.cache.concurrent.ConcurrentMapCacheManager;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 缓存配置
 * 用于优化RAG检索性能
 *
 * @author 风间影月
 * @version 3.7 - Cache
 */
@Configuration
@EnableCaching
public class CacheConfig {

    @Bean("aiCacheManager")
    public CacheManager cacheManager() {
        return new ConcurrentMapCacheManager(
            "stockCases",      // 同股票案例缓存
            "eventCases",      // 同事件案例缓存
            "qualityScores"    // 质量分数缓存
        );
    }
}
