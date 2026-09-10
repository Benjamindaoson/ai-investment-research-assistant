package com.itzixi.service.impl;

import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

/**
 * 多级缓存服务
 * L1: Caffeine本地缓存（热点数据）
 * L2: Redis分布式缓存（共享数据）
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@Service
public class MultiLevelCacheService {

    @Resource
    private RedisTemplate<String, Object> redisTemplate;

    /**
     * L1缓存：Caffeine本地缓存
     */
    private Cache<String, Object> localCache;

    @PostConstruct
    public void init() {
        localCache = Caffeine.newBuilder()
                .maximumSize(1000) // L1缓存较小，只存热点数据
                .expireAfterWrite(5, TimeUnit.MINUTES) // 5分钟过期
                .recordStats()
                .build();

        log.info("多级缓存服务初始化完成");
    }

    /**
     * 获取缓存数据（多级缓存）
     */
    public Object get(String key) {
        // 1. 先查L1缓存
        Object value = localCache.getIfPresent(key);
        if (value != null) {
            log.debug("L1缓存命中: {}", key);
            return value;
        }

        // 2. L1未命中，查L2缓存
        value = redisTemplate.opsForValue().get(key);
        if (value != null) {
            log.debug("L2缓存命中: {}", key);
            // 回写L1缓存
            localCache.put(key, value);
            return value;
        }

        log.debug("缓存未命中: {}", key);
        return null;
    }

    /**
     * 设置缓存（同时写入L1和L2）
     */
    public void set(String key, Object value, long timeout, TimeUnit unit) {
        // 写入L2缓存
        redisTemplate.opsForValue().set(key, value, timeout, unit);

        // 写入L1缓存
        localCache.put(key, value);

        log.debug("缓存已设置: key={}, timeout={}{}", key, timeout, unit);
    }

    /**
     * 删除缓存（同时删除L1和L2）
     */
    public void delete(String key) {
        // 删除L2缓存
        redisTemplate.delete(key);

        // 删除L1缓存
        localCache.invalidate(key);

        log.debug("缓存已删除: {}", key);
    }

    /**
     * 清空所有缓存
     */
    public void clear() {
        localCache.invalidateAll();
        log.info("L1缓存已清空");
    }

    /**
     * 获取缓存统计信息
     */
    public String getCacheStats() {
        var stats = localCache.stats();
        return String.format("L1缓存统计 - 命中率: %.2f%%, 命中: %d, 未命中: %d, 大小: %d",
                stats.hitRate() * 100,
                stats.hitCount(),
                stats.missCount(),
                localCache.estimatedSize());
    }
}
