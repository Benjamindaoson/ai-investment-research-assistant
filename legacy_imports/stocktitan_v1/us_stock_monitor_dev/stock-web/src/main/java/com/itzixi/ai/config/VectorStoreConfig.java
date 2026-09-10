package com.itzixi.ai.config;

import lombok.extern.slf4j.Slf4j;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.io.File;

/**
 * 向量存储配置
 * 支持持久化到文件
 *
 * @author 风间影月
 * @version 3.1 - Enhanced RAG
 */
@Slf4j
@Configuration
public class VectorStoreConfig {

    @Value("${spring.ai.vectorstore.file-path:./data/vector-store.json}")
    private String vectorStoreFilePath;

    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        SimpleVectorStore vectorStore = SimpleVectorStore.builder(embeddingModel).build();

        // 尝试从文件加载
        File vectorStoreFile = new File(vectorStoreFilePath);
        if (vectorStoreFile.exists()) {
            try {
                vectorStore.load(vectorStoreFile);
                log.info("向量存储已从文件加载: {}", vectorStoreFilePath);
            } catch (Exception e) {
                log.warn("加载向量存储失败，将创建新的: {}", e.getMessage());
            }
        } else {
            log.info("向量存储文件不存在，将创建新的: {}", vectorStoreFilePath);
            // 确保目录存在
            vectorStoreFile.getParentFile().mkdirs();
        }

        return vectorStore;
    }
}
