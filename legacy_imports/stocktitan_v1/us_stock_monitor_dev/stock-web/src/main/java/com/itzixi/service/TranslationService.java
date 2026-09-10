package com.itzixi.service;

/**
 * 翻译服务接口
 *
 * @author 风间影月
 * @version 2.0
 */
public interface TranslationService {

    /**
     * 翻译文本（带缓存）
     *
     * @param text 原文
     * @param from 源语言
     * @param to 目标语言
     * @return 翻译结果
     */
    String translate(String text, String from, String to);

    /**
     * 批量翻译
     *
     * @param texts 原文列表
     * @param from 源语言
     * @param to 目标语言
     * @return 翻译结果列表
     */
    java.util.List<String> batchTranslate(java.util.List<String> texts, String from, String to);

    /**
     * 清除缓存
     */
    void clearCache();
}
