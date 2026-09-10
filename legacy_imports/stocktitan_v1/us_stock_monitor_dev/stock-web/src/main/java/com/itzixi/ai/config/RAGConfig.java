package com.itzixi.ai.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

/**
 * RAG系统配置
 * 支持动态调整各项参数
 *
 * @author 风间影月
 * @version 3.7 - Configuration
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "rag")
public class RAGConfig {

    /**
     * 多路召回权重配置
     */
    private RecallWeights recallWeights = new RecallWeights();

    /**
     * 质量评分配置
     */
    private QualityConfig quality = new QualityConfig();

    /**
     * 时间衰减配置
     */
    private TimeDecayConfig timeDecay = new TimeDecayConfig();

    /**
     * 案例库管理配置
     */
    private LibraryConfig library = new LibraryConfig();

    /**
     * 追踪配置
     */
    private TrackingConfig tracking = new TrackingConfig();

    /**
     * 多路召回权重
     */
    @Data
    public static class RecallWeights {
        /**
         * 向量召回权重（默认0.5）
         */
        private double vector = 0.5;

        /**
         * 同股票召回权重（默认0.3）
         */
        private double sameStock = 0.3;

        /**
         * 同事件召回权重（默认0.2）
         */
        private double sameEvent = 0.2;
    }

    /**
     * 质量评分配置
     */
    @Data
    public static class QualityConfig {
        /**
         * 最低质量分数（默认60）
         */
        private double minScore = 60.0;

        /**
         * 降级质量分数（默认40）
         */
        private double fallbackScore = 40.0;

        /**
         * 完整性权重（默认0.4）
         */
        private double completenessWeight = 0.4;

        /**
         * 准确性权重（默认0.3）
         */
        private double accuracyWeight = 0.3;

        /**
         * 影响程度权重（默认0.3）
         */
        private double impactWeight = 0.3;
    }

    /**
     * 时间衰减配置
     */
    @Data
    public static class TimeDecayConfig {
        /**
         * 衰减因子（默认0.5，范围0.1-1.0）
         */
        private double factor = 0.5;

        /**
         * 相似度权重（默认0.7）
         */
        private double similarityWeight = 0.7;

        /**
         * 时间权重（默认0.3）
         */
        private double timeWeight = 0.3;
    }

    /**
     * 案例库管理配置
     */
    @Data
    public static class LibraryConfig {
        /**
         * 低质量案例删除阈值（默认30）
         */
        private double lowQualityThreshold = 30.0;

        /**
         * 案例归档天数（默认3年）
         */
        private int archiveDays = 3 * 365;

        /**
         * 相似案例合并阈值（默认0.95）
         */
        private double mergeSimilarityThreshold = 0.95;

        /**
         * 定时清理cron表达式（默认每天凌晨3点）
         */
        private String cleanupCron = "0 0 3 * * ?";
    }

    /**
     * 追踪配置
     */
    @Data
    public static class TrackingConfig {
        /**
         * 追踪天数（默认7天）
         */
        private int trackingDays = 7;

        /**
         * 更新频率cron表达式（默认每小时）
         */
        private String updateCron = "0 0 * * * ?";
    }
}
