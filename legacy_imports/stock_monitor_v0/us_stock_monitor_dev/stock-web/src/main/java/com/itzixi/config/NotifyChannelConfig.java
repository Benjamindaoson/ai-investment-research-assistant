package com.itzixi.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * @ClassName NotifyChannelConfig
 * @Author 风间影月
 * @Version 1.0
 * @Description 推送渠道开关配置
 **/
@Data
@Component
@ConfigurationProperties(prefix = "notify.channels")
public class NotifyChannelConfig {

    private boolean dingtalk = true;
    private boolean wechat = false;
    private boolean wecom = false;

}
