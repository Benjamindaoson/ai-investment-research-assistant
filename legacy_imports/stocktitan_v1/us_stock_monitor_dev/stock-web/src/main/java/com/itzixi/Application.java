package com.itzixi;

import io.github.cdimascio.dotenv.Dotenv;
import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {

        // 加载.env文件
        Dotenv dotenv = Dotenv.configure().ignoreIfMissing().load();
        // 把.env文件中的变量参数设置到当前项目中
        dotenv.entries().forEach(entry -> {
            String value = entry.getValue();
            if (value != null && !value.trim().isEmpty()) {
                System.setProperty(entry.getKey(), value);
            }
        });

        SpringApplication.run(Application.class, args);
    }
}
