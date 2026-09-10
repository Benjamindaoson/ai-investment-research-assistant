package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

/**
 * 聊天消息
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ChatMessage {
    /**
     * 角色（user/assistant/system）
     */
    private String role;

    /**
     * 消息内容
     */
    private String content;

    /**
     * 时间戳
     */
    private Long timestamp;

    public static ChatMessage user(String content) {
        return new ChatMessage("user", content, System.currentTimeMillis());
    }

    public static ChatMessage assistant(String content) {
        return new ChatMessage("assistant", content, System.currentTimeMillis());
    }

    public static ChatMessage system(String content) {
        return new ChatMessage("system", content, System.currentTimeMillis());
    }
}
