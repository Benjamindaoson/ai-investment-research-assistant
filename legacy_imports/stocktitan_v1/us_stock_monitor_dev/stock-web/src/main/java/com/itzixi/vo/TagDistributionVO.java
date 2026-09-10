package com.itzixi.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * 标签分布VO
 *
 * @author 风间影月
 * @version 2.0
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TagDistributionVO {
    private String tag;
    private String tagZh;
    private Integer count;
    private Double percentage;
}
