package com.itzixi.test;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

/**
 * @ClassName TestPython
 * @Author 风间影月
 * @Version 1.0
 * @Description TestPython
 **/
public class TestPython {

    public static void main(String[] args) {

        String text = "[hello world]";

        try {
            String pythonExe = "python"; // 或 "python3"
            String scriptPath = "/Users/lee/Desktop/test/send_wx_v3.py";

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
//                System.out.println("[Python输出] " + line);
                System.out.println(line);
            }

            int exitCode = process.waitFor();
            System.out.println("Python 脚本执行结束，退出码: " + exitCode);

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
        }

    }

}
