package com.itzixi.service.impl;

import com.itzixi.entity.USStockMsg;
import com.itzixi.entity.USStockRss;
import com.itzixi.enums.StockTag;
import com.itzixi.service.RssService;
import com.itzixi.service.StockService;
import com.itzixi.service.TranslationService;
import com.itzixi.utils.DingTalkApi;
import com.itzixi.utils.GMTDateConverter;
import com.itzixi.utils.StockTitanCrawler;
import com.rometools.rome.feed.synd.SyndEntry;
import com.rometools.rome.feed.synd.SyndFeed;
import com.rometools.rome.io.SyndFeedInput;
import com.rometools.rome.io.XmlReader;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.stereotype.Service;

import java.net.URL;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * RSS service implementation.
 */
@Slf4j
@Service
public class RssServiceImpl implements RssService {

    @Resource
    private StockService stockService;

    @Resource
    private TranslationService translationService;

    @Resource
    private DingTalkApi dingTalkApi;

    public static final String RSS_URL = "https://www.stocktitan.net/rss";

    @Override
    public void displayRss() throws Exception {
        List<USStockMsg> stockMsgList = new ArrayList<>();
        List<SyndEntry> rssList = this.fetchRssReed(RSS_URL);

        if (rssList == null || rssList.isEmpty()) {
            log.warn("RSS list is empty");
            return;
        }

        log.info("Start processing RSS data, total {} entries", rssList.size());

        for (SyndEntry entry : rssList) {
            try {
                USStockRss stockNews = processRssEntry(entry);
                if (stockNews != null) {
                    USStockMsg stockMsg = buildStockMsg(stockNews, entry.getPublishedDate());
                    stockMsgList.add(stockMsg);
                }
            } catch (Exception e) {
                log.error("Failed to process RSS entry: {}", e.getMessage(), e);
            }
        }

        if (!stockMsgList.isEmpty()) {
            dingTalkApi.sendTextMessage(dingTalkApi.formatStockInfoFromList(stockMsgList));
            log.info("Pushed {} stock movement messages", stockMsgList.size());
        }
    }

    private USStockRss processRssEntry(SyndEntry entry) {
        USStockRss stockNews = new USStockRss();

        String title = entry.getTitle();
        String titleEn = getStockTitle(title);
        stockNews.setTitle(titleEn);
        stockNews.setLink(entry.getLink());

        Date publishedDate = entry.getPublishedDate();
        LocalDateTime gmtDate = GMTDateConverter.convertGmt(publishedDate);
        stockNews.setPubDateGmt(gmtDate);
        stockNews.setPubDateBj(GMTDateConverter.convertGmtToBeijing(publishedDate));

        String stockCode = getStockCode(title);
        stockNews.setStockCode(stockCode);

        if (stockService.isStockNewsExist(stockCode, stockNews.getLink())) {
            log.debug("Stock {} already exists, skip", stockCode);
            return null;
        }

        String finalTitleZh = translationService.translate(titleEn, "en", "zh");
        stockNews.setTitleZh(finalTitleZh);

        try {
            List<String> tagsList = StockTitanCrawler.getTags(titleEn);
            stockNews.setTags(getTagsZh(tagsList));
        } catch (Exception e) {
            log.warn("Failed to fetch tags: {}", e.getMessage());
            stockNews.setTags("");
        }

        stockService.saveStockNews(stockNews);
        return stockNews;
    }

    private USStockMsg buildStockMsg(USStockRss stockNews, Date publishedDate) {
        USStockMsg stockMsg = new USStockMsg();
        BeanUtils.copyProperties(stockNews, stockMsg);

        stockMsg.setPubDateBj(GMTDateConverter.getBeijingTime(publishedDate));

        LocalDateTime gmtDate = stockNews.getPubDateGmt();
        Long counts24Hour = stockService.getStockUnusualCounts(
                stockNews,
                GMTDateConverter.minus24Hour(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );
        Long counts3Day = stockService.getStockUnusualCounts(
                stockNews,
                GMTDateConverter.minus3Day(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );
        Long counts1Week = stockService.getStockUnusualCounts(
                stockNews,
                GMTDateConverter.minus1Week(gmtDate),
                GMTDateConverter.plus1Minute(gmtDate)
        );

        stockMsg.setCounts24Hour(counts24Hour.intValue());
        stockMsg.setCounts3Day(counts3Day.intValue());
        stockMsg.setCounts1Week(counts1Week.intValue());

        return stockMsg;
    }

    @Override
    public List<SyndEntry> fetchRssReed(String rssUrl) throws Exception {
        URL url = new URL(rssUrl);
        SyndFeedInput input = new SyndFeedInput();
        SyndFeed feed = input.build(new XmlReader(url));
        return feed.getEntries();
    }

    private String getStockTitle(String title) {
        String[] titleArr = title.split("\\|");
        return titleArr[0].trim();
    }

    private String getStockCode(String title) {
        String[] titleArr = title.split("\\|");
        String stockStr = titleArr[titleArr.length - 1];
        String[] stockCodeArr = stockStr.split("Stock News");
        return stockCodeArr[0].trim();
    }

    private String getTagsZh(List<String> list) {
        if (list == null || list.isEmpty()) {
            return "";
        }

        StringBuilder tagBuilder = new StringBuilder();
        for (int i = 0; i < list.size(); i++) {
            String tag = list.get(i);
            tagBuilder.append(StockTag.getTagValue(tag));
            if (i < list.size() - 1) {
                tagBuilder.append(", ");
            }
        }

        return tagBuilder.toString();
    }

    @Override
    public List<USStockRss> getStockRssByDate(LocalDate date) {
        return stockService.getStockRssByDate(date);
    }

    @Override
    public List<USStockRss> getRecentNews(int hours) {
        LocalDateTime since = LocalDateTime.now().minusHours(hours);
        return stockService.getStockRssSince(since);
    }

    @Override
    public List<USStockRss> getRecentByStockCode(String stockCode, int days) {
        LocalDateTime since = LocalDateTime.now().minusDays(days);
        return stockService.getStockRssByCodeSince(stockCode, since);
    }

    @Override
    public List<USStockRss> searchByKeyword(String keyword, int limit) {
        return stockService.searchByKeyword(keyword, limit);
    }

    @Override
    public List<String> getHotStocks(int limit) {
        return stockService.getHotStocks(limit);
    }
}