package com.itzixi.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.itzixi.entity.USStockRss;
import com.itzixi.mapper.USStockRssMapper;
import com.itzixi.service.StockService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

/**
 * @ClassName StockServiceImpl
 * @Author 风间影月
 * @Version 1.0
 * @Description StockServiceImpl
 **/
@Service
public class StockServiceImpl implements StockService {

    @Resource
    private USStockRssMapper usStockRssMapper;

    @Override
    public void saveStockNews(USStockRss stockNews) {
        usStockRssMapper.insert(stockNews);
    }

    @Override
    public Boolean isStockNewsExist(String stockCode, String link) {

        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("stock_code", stockCode);
        queryWrapper.eq("link", link);

        return usStockRssMapper.selectCount(queryWrapper) > 0;
    }

    @Override
    public Long getStockUnusualCounts(USStockRss stockNews, LocalDateTime startDate, LocalDateTime endDate) {

        String stockCode = stockNews.getStockCode();

        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("stock_code", stockCode);

//        数据库中的日期时间格式： yyyy-MM-dd HH:mm:ss
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String startDateStr = formatter.format(startDate);
        String endDateStr = formatter.format(endDate);

        queryWrapper.ge("pub_date_gmt", startDateStr);
        queryWrapper.le("pub_date_gmt", endDateStr);

        return usStockRssMapper.selectCount(queryWrapper);
    }

    @Override
    public List<USStockRss> getStockRssByDate(LocalDate date) {
        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();

        LocalDateTime startOfDay = date.atStartOfDay();
        LocalDateTime endOfDay = date.plusDays(1).atStartOfDay();

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        queryWrapper.ge("pub_date_gmt", formatter.format(startOfDay));
        queryWrapper.lt("pub_date_gmt", formatter.format(endOfDay));
        queryWrapper.orderByDesc("pub_date_gmt");

        return usStockRssMapper.selectList(queryWrapper);
    }

    @Override
    public List<USStockRss> getStockRssSince(LocalDateTime since) {
        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        queryWrapper.ge("pub_date_gmt", formatter.format(since));
        queryWrapper.orderByDesc("pub_date_gmt");

        return usStockRssMapper.selectList(queryWrapper);
    }

    @Override
    public List<USStockRss> getStockRssByCodeSince(String stockCode, LocalDateTime since) {
        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();

        queryWrapper.eq("stock_code", stockCode);

        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        queryWrapper.ge("pub_date_gmt", formatter.format(since));
        queryWrapper.orderByDesc("pub_date_gmt");

        return usStockRssMapper.selectList(queryWrapper);
    }

    @Override
    public List<USStockRss> queryStock(String stockCode) {
        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("stock_code", stockCode);
        queryWrapper.orderByDesc("pub_date_bj");
        return usStockRssMapper.selectList(queryWrapper);
    }

    @Override
    public List<USStockRss> searchByKeyword(String keyword, int limit) {
        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();

        queryWrapper.and(wrapper -> wrapper
                .like("title", keyword)
                .or()
                .like("title_zh", keyword)
                .or()
                .like("tags", keyword));

        queryWrapper.orderByDesc("pub_date_gmt");
        queryWrapper.last("LIMIT " + limit);

        return usStockRssMapper.selectList(queryWrapper);
    }

    @Override
    public List<String> getHotStocks(int limit) {
        // 获取最近7天的数据
        LocalDateTime since = LocalDateTime.now().minusDays(7);
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.ge("pub_date_gmt", formatter.format(since));
        queryWrapper.select("stock_code");

        List<USStockRss> allNews = usStockRssMapper.selectList(queryWrapper);

        // 统计每个股票代码出现的次数，返回TOP N
        return allNews.stream()
                .collect(Collectors.groupingBy(USStockRss::getStockCode, Collectors.counting()))
                .entrySet().stream()
                .sorted((e1, e2) -> e2.getValue().compareTo(e1.getValue()))
                .limit(limit)
                .map(e -> e.getKey())
                .collect(Collectors.toList());
    }
}
