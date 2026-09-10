package com.itzixi.service.impl;

import com.itzixi.entity.USStockMsg;
import com.itzixi.service.WechatBotService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @ClassName WechatBotServiceImpl
 * @Author 风间影月
 * @Version 1.0
 * @Description WechatBotServiceImpl
 **/
@Slf4j
@Service
public class WechatBotServiceImpl implements WechatBotService {

    @Value("${wechat.python-exe:python}")
    private String pythonExe;

    @Value("${wechat.script-path:}")
    private String scriptPath;

     /**
      * 注意事项：
      * 1. 安装Python3环境
      * 2. pip install wxauto
      * 3. 只能在Windows上运行
      * 4. 微信版本限制3.9.x或低版本的4.0.x
      * 5. 禁止使用微信进行违法行为，务必遵守微信使用守则
      *
      *【免责声明】：代码仅用于技术的交流学习使用，禁止用于实际生产项目，请勿用于非法用途和商业用途！
      *            如因此产生任何法律纠纷甚至造成微信封号或者其它损失等情况，本人及慕课网概不负责，由使用人承担所有责任。
      *
      */

    @Override
    public void sendMessage(String text) {

        callPythonScriptToSendToWeChat(text);

    }

    public void callPythonScriptToSendToWeChat(String text) {

        try {
            // 构造 ProcessBuilder，传入参数
            ProcessBuilder pb = new ProcessBuilder(pythonExe, scriptPath, text);
            pb.redirectErrorStream(true);

            // 关键：设置Python使用UTF-8编码（解决之前的编码问题）
            pb.environment().put("PYTHONIOENCODING", "utf-8");

            Process process = pb.start();

            // 读取 Python 输出
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream(), "UTF-8"));
            String line;
            while ((line = reader.readLine()) != null) {
                log.info("[Python输出] {}", line);
            }

            int exitCode = process.waitFor();
            log.info("Python 脚本执行结束，退出码: {}", exitCode);

        } catch (IOException | InterruptedException e) {
            log.error("微信脚本执行失败", e);
        }

    }

    @Override
    public void sendMessage(List<USStockMsg> msgList) throws Exception {

        List<List<USStockMsg>> result = splitList(msgList);

        for (List<USStockMsg> group : result) {

            String singleListStr = "";

            singleListStr = formatStockListHtml(group);

            sendMessage(singleListStr);
        }

    }

    public String formatStockListHtml(List<USStockMsg> stocks) {
        return stocks.stream()
                .map(stockMsg -> formatStockInfoHtml(stockMsg))
                .collect(Collectors.joining("\n\n------\n\n")); // 用分隔线分隔
    }

    public String formatStockInfoHtml(USStockMsg stock) {
        return "<b>📌 代码: " + stock.getStockCode() + "</b>\n" +
                "📅 时间: " + stock.getPubDateBj() + "\n" +
                "📰 标题: " + stock.getTitleZh() + "\n" +
                "🏷️ 标签: " + stock.getTags() + "\n" +
                "📊 统计: 24小时异动=" + stock.getCounts24Hour() + "次" +
                ", 3天内异动=" + stock.getCounts3Day() + "次" +
                ", 1周内异动=" + stock.getCounts1Week() + "次";
    }

    public static <T> List<List<T>> splitList(List<T> input) {
        List<List<T>> result = new ArrayList<>();
        int size = input.size();

        if (size <= 10) {
            // 直接整体放进去
            result.add(new ArrayList<>(input));
        } else {
            // 超过 10，就每 10 个拆分
            for (int i = 0; i < size; i += 10) {
                int end = Math.min(i + 10, size);
                result.add(new ArrayList<>(input.subList(i, end)));
            }
        }
        return result;
    }

}
