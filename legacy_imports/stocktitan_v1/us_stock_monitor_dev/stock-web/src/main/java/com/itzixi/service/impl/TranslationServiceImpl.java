package com.itzixi.service.impl;

import cn.hutool.json.JSONUtil;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import com.itzixi.common.config.BaiduTranslateProperties;
import com.itzixi.common.exception.TranslationException;
import com.itzixi.common.retry.RetryUtil;
import com.itzixi.entity.BaiduTransEntity;
import com.itzixi.service.TranslationService;
import com.itzixi.utils.TransApi;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * 翻译服务实现（带缓存和降级）
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@Service
public class TranslationServiceImpl implements TranslationService {

    @Resource
    private TransApi transApi;

    @Resource
    private BaiduTranslateProperties translateProperties;

    /**
     * 本地缓存（Caffeine）
     */
    private Cache<String, String> translationCache;

    @PostConstruct
    public void init() {
        // 初始化本地缓存
        translationCache = Caffeine.newBuilder()
                .maximumSize(10000) // 最多缓存10000条
                .expireAfterWrite(translateProperties.getCacheExpireSeconds(), TimeUnit.SECONDS)
                .recordStats() // 记录统计信息
                .build();

        log.info("翻译服务初始化完成，缓存过期时间: {}秒", translateProperties.getCacheExpireSeconds());
    }

    @Override
    public String translate(String text, String from, String to) {
        if (!translateProperties.getEnabled()) {
            log.debug("翻译功能已禁用，返回原文");
            return text;
        }

        if (text == null || text.trim().isEmpty()) {
            return text;
        }

        // 生成缓存key
        String cacheKey = generateCacheKey(text, from, to);

        // 先查缓存
        String cached = translationCache.getIfPresent(cacheKey);
        if (cached != null) {
            log.debug("翻译缓存命中: {}", text.substring(0, Math.min(50, text.length())));
            return cached;
        }

        // 缓存未命中，调用翻译API
        try {
            String result = RetryUtil.executeWithRetry(
                    () -> translateInternal(text, from, to),
                    translateProperties.getMaxRetries(),
                    translateProperties.getRetryDelay(),
                    "百度翻译"
            );

            // 存入缓存
            translationCache.put(cacheKey, result);
            log.info("翻译成功并缓存: {} -> {}",
                    text.substring(0, Math.min(30, text.length())),
                    result.substring(0, Math.min(30, result.length())));

            return result;
        } catch (Exception e) {
            log.error("翻译失败，返回原文: {}", e.getMessage());
            // 降级策略：返回原文
            return text;
        }
    }

    @Override
    public List<String> batchTranslate(List<String> texts, String from, String to) {
        List<String> results = new ArrayList<>();
        for (String text : texts) {
            results.add(translate(text, from, to));
        }
        return results;
    }

    @Override
    public void clearCache() {
        translationCache.invalidateAll();
        log.info("翻译缓存已清空");
    }

    /**
     * 内部翻译方法
     */
    private String translateInternal(String text, String from, String to) {
        try {
            String result = transApi.getTransResult(text, from, to);

            if (result == null || result.isEmpty()) {
                throw new TranslationException("翻译API返回空结果");
            }

            BaiduTransEntity transEntity = JSONUtil.toBean(result, BaiduTransEntity.class);

            if (transEntity == null || transEntity.getTrans_result() == null ||
                transEntity.getTrans_result().isEmpty()) {
                throw new TranslationException("翻译结果解析失败");
            }

            return transEntity.getTrans_result().get(0).getDst();
        } catch (Exception e) {
            throw new TranslationException("翻译失败: " + e.getMessage(), e);
        }
    }

    /**
     * 生成缓存key
     */
    private String generateCacheKey(String text, String from, String to) {
        return from + "_" + to + "_" + text.hashCode();
    }

    /**
     * 获取缓存统计信息
     */
    public String getCacheStats() {
        var stats = translationCache.stats();
        return String.format("缓存统计 - 命中率: %.2f%%, 命中次数: %d, 未命中次数: %d, 缓存大小: %d",
                stats.hitRate() * 100,
                stats.hitCount(),
                stats.missCount(),
                translationCache.estimatedSize());
    }
}
