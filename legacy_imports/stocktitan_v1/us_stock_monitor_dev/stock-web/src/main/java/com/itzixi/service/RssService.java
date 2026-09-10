package com.itzixi.service;

import com.itzixi.entity.USStockRss;
import com.rometools.rome.feed.synd.SyndEntry;

import java.time.LocalDate;
import java.util.List;

/**
 * @ClassName RssService
 * @Author 风间影月
 * @Version 2.0
 * @Description RssService
 **/
public interface RssService {

    public void displayRss() throws Exception;

    public List<SyndEntry> fetchRssReed(String rssUrl) throws Exception;

    /**
     * 获取指定日期的股票新闻
     */
    public List<USStockRss> getStockRssByDate(LocalDate date);

    /**
     * 获取最近N小时的新闻
     */
    public List<USStockRss> getRecentNews(int hours);

    /**
     * 获取指定股票最近N天的新闻
     */
    public List<USStockRss> getRecentByStockCode(String stockCode, int days);

    /**
     * 搜索包含关键词的新闻
     */
    public List<USStockRss> searchByKeyword(String keyword, int limit);

    /**
     * 获取热门股票列表
     */
    public List<String> getHotStocks(int limit);

}
