package com.itzixi.utils;

import com.itzixi.entity.USStockMsg;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class TelegramMessageSplitter {

    public static <T> List<List<T>> splitList(List<T> input) {
        List<List<T>> result = new ArrayList<>();
        int size = input.size();

        if (size <= 8) {
            // 直接整体放进去
            result.add(new ArrayList<>(input));
        } else {
            // 超过 8，就每 8 个拆分
            for (int i = 0; i < size; i += 8) {
                int end = Math.min(i + 8, size);
                result.add(new ArrayList<>(input.subList(i, end)));
            }
        }
        return result;
    }

    /**
     * 把对象 List 拆分，每 8 个一组，返回拼接好的消息
     */
    public static List<String> splitMessages(List<USStockMsg> items) {
        List<String> messages = new ArrayList<>();
        int size = items.size();

        if (size <= 3) {
            // ≤3 个，直接合并
//            messages.add(formatGroup(items));
        } else {
            List<USStockMsg> subList = null;

            // >3 个，每 3 个拆分一次
            for (int i = 0; i < size; i += 3) {
                int end = Math.min(i + 3, size);
                subList = items.subList(i, end);
//                messages.add(formatGroup(subList));
            }

            System.out.println(subList);
        }

        return messages;
    }

    // 拼接一个 group 内的对象
    private static String formatGroup(List<USStockMsg> group) {
        return group.stream()
                .map(USStockMsg::toString)
                .collect(Collectors.joining("\n------\n"));
    }

//    public static void main(String[] args) {
//        List<USStockMsg> stocks = List.of(
//                new USStockMsg("title-1", new Date(), "SMX", "⚖️ 低浮动", 3, 2, 3),
//                new USStockMsg("title-1", new Date(), "GCI", "🤖 AI人工智能", 1, 3, 4),
//                new USStockMsg("title-1", new Date(), "SEQP", "💵 低价股", 2, 3, 6),
//                new USStockMsg("title-1", new Date(), "OPEN", "📈 房地产", 5, 6 ,6),
//                new USStockMsg("title-1", new Date(), "OPAD", "📉 短期下跌", 2, 8, 2)
//        );
//
////        List<String> msgs = splitMessages(stocks);
//
//        // 模拟发送
////        for (String msg : msgs) {
////            System.out.println("发送消息:\n" + msg);
////            System.out.println("======================");
////        }
//
//        List<List<USStockMsg>> result = splitList(stocks);
//
//        // 打印结果
//        for (List<USStockMsg> group : result) {
//            System.out.println(group);
//        }
//    }
}
