package com.itzixi.alert.rule;

/**
 * 预警级别
 *
 * @author 风间影月
 * @version 2.0
 */
public enum AlertLevel {
    /**
     * 普通
     */
    NORMAL("普通", 1),

    /**
     * 重要
     */
    IMPORTANT("重要", 2),

    /**
     * 紧急
     */
    URGENT("紧急", 3);

    private final String name;
    private final int priority;

    AlertLevel(String name, int priority) {
        this.name = name;
        this.priority = priority;
    }

    public String getName() {
        return name;
    }

    public int getPriority() {
        return priority;
    }
}
