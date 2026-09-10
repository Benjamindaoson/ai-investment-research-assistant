package com.itzixi.service;

import com.itzixi.entity.USStockRss;
import com.rometools.rome.feed.synd.SyndEntry;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/**
 * @ClassName StockService
 * @Author 风间影月
 * @Version 2.0
 * @Description StockService
 **/
public interface StockService {

    public void saveStockNews(USStockRss stockNews);

    public Boolean isStockNewsExist(String stockCode, String link);

    public Long getStockUnusualCounts(USStockRss stockNews, LocalDateTime startDate, LocalDateTime endDate);

    /**
     * 获取指定日期的股票新闻
     */
    public List<USStockRss> getStockRssByDate(LocalDate date);

    /**
     * 获取指定时间之后的股票新闻
     */
    public List<USStockRss> getStockRssSince(LocalDateTime since);

    /**
     * 获取指定股票代码在指定时间之后的新闻
     */
    public List<USStockRss> getStockRssByCodeSince(String stockCode, LocalDateTime since);

    public List<USStockRss> queryStock(String stockCode);

    /**
     * 搜索包含关键词的新闻
     */
    public List<USStockRss> searchByKeyword(String keyword, int limit);

    /**
     * 获取热门股票列表
     */
    public List<String> getHotStocks(int limit);

}
