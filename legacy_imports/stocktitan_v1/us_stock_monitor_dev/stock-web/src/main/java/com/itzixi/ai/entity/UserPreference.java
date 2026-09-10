package com.itzixi.ai.entity;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 用户偏好设置
 *
 * @author 风间影月
 * @version 3.0 - AI Native
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserPreference {
    /**
     * 用户ID
     */
    private String userId;

    /**
     * 关注的股票代码列表
     */
    private List<String> focusStocks;

    /**
     * 风险偏好（保守/稳健/积极/激进）
     */
    private String riskTolerance;

    /**
     * 关注的行业
     */
    private List<String> interestedSectors;

    /**
     * 关注的事件类型
     */
    private List<String> interestedEventTypes;

    /**
     * 最小影响程度阈值（1-10）
     */
    private Integer minImpactLevel;

    /**
     * 是否接收负面新闻
     */
    private Boolean receiveNegativeNews;

    /**
     * 推送时间段（小时，0-23）
     */
    private List<Integer> pushHours;

    /**
     * 推送渠道偏好
     */
    private List<String> preferredChannels;
}
