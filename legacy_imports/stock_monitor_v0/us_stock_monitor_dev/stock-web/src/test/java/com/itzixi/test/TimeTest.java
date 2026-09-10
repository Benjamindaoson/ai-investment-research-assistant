package com.itzixi.test;








import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.util.StopWatch;

@SpringBootTest
public class TimeTest {

    @Test
    public void testTime() throws Exception {

        StopWatch stopWatch = new StopWatch();
        stopWatch.start("前100行代码");
        Thread.sleep(1001);
        stopWatch.stop();

        stopWatch.start("中间150行代码");
        Thread.sleep(860);
        stopWatch.stop();

        stopWatch.start("最后200行代码");
        Thread.sleep(1280);
        stopWatch.stop();

        // 打印上方3个任务的耗时统计
        System.out.println(stopWatch.prettyPrint());
        System.out.println(stopWatch.shortSummary());

        // 任务总览
        System.out.println(stopWatch.getTotalTimeMillis());
        System.out.println(stopWatch.getTaskCount());

    }

}
