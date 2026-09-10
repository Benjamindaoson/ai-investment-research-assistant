package com.itzixi.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.itzixi.entity.StockCounts;
import com.itzixi.entity.USStockRss;
import com.itzixi.mapper.USStockRssMapper;
import com.itzixi.service.StatisticsService;
import com.itzixi.vo.HotStockVO;
import com.itzixi.vo.StockTrendVO;
import com.itzixi.vo.TagDistributionVO;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

/**
 * 统计服务实现
 *
 * @author 风间影月
 * @version 2.0
 */
@Slf4j
@Service
public class StatisticsServiceImpl implements StatisticsService {

    @Resource
    private USStockRssMapper usStockRssMapper;

    @Override
    public List<HotStockVO> getHotStocks(Integer days, Integer limit) {
        LocalDateTime endDate = LocalDateTime.now();
        LocalDateTime startDate = endDate.minusDays(days);

        // 查询指定时间段内的所有股票
        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.ge("pub_date_bj", startDate);
        queryWrapper.le("pub_date_bj", endDate);
        queryWrapper.orderByDesc("pub_date_bj");

        List<USStockRss> allStocks = usStockRssMapper.selectList(queryWrapper);

        // 按股票代码分组统计
        Map<String, List<USStockRss>> groupedStocks = allStocks.stream()
                .collect(Collectors.groupingBy(USStockRss::getStockCode));

        // 转换为HotStockVO并排序
        List<HotStockVO> hotStocks = groupedStocks.entrySet().stream()
                .map(entry -> {
                    String stockCode = entry.getKey();
                    List<USStockRss> stocks = entry.getValue();
                    USStockRss latest = stocks.get(0);

                    HotStockVO vo = new HotStockVO();
                    vo.setStockCode(stockCode);
                    vo.setStockName(stockCode); // 可以后续扩展获取股票名称
                    vo.setOccurCounts(stocks.size());
                    vo.setLatestTitle(latest.getTitle());
                    vo.setLatestTitleZh(latest.getTitleZh());
                    vo.setLatestTime(latest.getPubDateBj().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
                    return vo;
                })
                .sorted(Comparator.comparing(HotStockVO::getOccurCounts).reversed())
                .limit(limit)
                .collect(Collectors.toList());

        log.info("查询到{}天内热门股票{}只", days, hotStocks.size());
        return hotStocks;
    }

    @Override
    public StockTrendVO getStockTrend(String stockCode, Integer days) {
        LocalDateTime endDate = LocalDateTime.now();
        LocalDateTime startDate = endDate.minusDays(days);

        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.eq("stock_code", stockCode);
        queryWrapper.ge("pub_date_bj", startDate);
        queryWrapper.le("pub_date_bj", endDate);
        queryWrapper.orderByAsc("pub_date_bj");

        List<USStockRss> stocks = usStockRssMapper.selectList(queryWrapper);

        // 按日期分组统计
        Map<String, Long> dailyCounts = stocks.stream()
                .collect(Collectors.groupingBy(
                        stock -> stock.getPubDateBj().toLocalDate().toString(),
                        Collectors.counting()
                ));

        StockTrendVO vo = new StockTrendVO();
        vo.setStockCode(stockCode);
        vo.setDates(new ArrayList<>(dailyCounts.keySet()));
        vo.setCounts(dailyCounts.values().stream().map(Long::intValue).collect(Collectors.toList()));
        vo.setTotalCounts(stocks.size());
        vo.setAvgCounts(stocks.isEmpty() ? 0.0 : (double) stocks.size() / days);

        return vo;
    }

    @Override
    public List<TagDistributionVO> getTagDistribution(Integer days) {
        LocalDateTime endDate = LocalDateTime.now();
        LocalDateTime startDate = endDate.minusDays(days);

        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.ge("pub_date_bj", startDate);
        queryWrapper.le("pub_date_bj", endDate);
        queryWrapper.isNotNull("tags");
        queryWrapper.ne("tags", "");

        List<USStockRss> stocks = usStockRssMapper.selectList(queryWrapper);

        // 统计标签出现次数
        Map<String, Integer> tagCounts = new HashMap<>();
        for (USStockRss stock : stocks) {
            String tags = stock.getTags();
            if (tags != null && !tags.isEmpty()) {
                String[] tagArray = tags.split(",");
                for (String tag : tagArray) {
                    String trimmedTag = tag.trim();
                    tagCounts.put(trimmedTag, tagCounts.getOrDefault(trimmedTag, 0) + 1);
                }
            }
        }

        int total = tagCounts.values().stream().mapToInt(Integer::intValue).sum();

        // 转换为VO
        List<TagDistributionVO> distribution = tagCounts.entrySet().stream()
                .map(entry -> {
                    TagDistributionVO vo = new TagDistributionVO();
                    vo.setTag(entry.getKey());
                    vo.setTagZh(entry.getKey()); // 已经是中文标签
                    vo.setCount(entry.getValue());
                    vo.setPercentage(total == 0 ? 0.0 : (double) entry.getValue() / total * 100);
                    return vo;
                })
                .sorted(Comparator.comparing(TagDistributionVO::getCount).reversed())
                .collect(Collectors.toList());

        log.info("查询到{}天内标签分布{}个", days, distribution.size());
        return distribution;
    }

    @Override
    public List<Integer> getHourlyAnalysis(Integer days) {
        LocalDateTime endDate = LocalDateTime.now();
        LocalDateTime startDate = endDate.minusDays(days);

        QueryWrapper<USStockRss> queryWrapper = new QueryWrapper<>();
        queryWrapper.ge("pub_date_bj", startDate);
        queryWrapper.le("pub_date_bj", endDate);

        List<USStockRss> stocks = usStockRssMapper.selectList(queryWrapper);

        // 按小时统计
        int[] hourlyCounts = new int[24];
        for (USStockRss stock : stocks) {
            int hour = stock.getPubDateBj().getHour();
            hourlyCounts[hour]++;
        }

        return Arrays.stream(hourlyCounts).boxed().collect(Collectors.toList());
    }

    @Override
    public List<StockCounts> getFrequentStocks(Integer targetCounts, LocalDateTime startDate, LocalDateTime endDate) {
        Map<String, Object> map = new HashMap<>();
        map.put("targetCounts", targetCounts);
        map.put("startDate", startDate.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        map.put("endDate", endDate.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));

        return usStockRssMapper.queryStockCountsBetweenDate(map);
    }

    @Override
    public Map<String, Object> getSystemOverview() {
        Map<String, Object> overview = new HashMap<>();

        // 总股票数
        QueryWrapper<USStockRss> totalWrapper = new QueryWrapper<>();
        totalWrapper.select("DISTINCT stock_code");
        long totalStocks = usStockRssMapper.selectCount(totalWrapper);

        // 总记录数
        long totalRecords = usStockRssMapper.selectCount(null);

        // 今日新增
        LocalDateTime todayStart = LocalDateTime.now().withHour(0).withMinute(0).withSecond(0);
        QueryWrapper<USStockRss> todayWrapper = new QueryWrapper<>();
        todayWrapper.ge("pub_date_bj", todayStart);
        long todayRecords = usStockRssMapper.selectCount(todayWrapper);

        // 最近更新时间
        QueryWrapper<USStockRss> latestWrapper = new QueryWrapper<>();
        latestWrapper.orderByDesc("pub_date_bj");
        latestWrapper.last("LIMIT 1");
        USStockRss latest = usStockRssMapper.selectOne(latestWrapper);

        overview.put("totalStocks", totalStocks);
        overview.put("totalRecords", totalRecords);
        overview.put("todayRecords", todayRecords);
        overview.put("latestUpdateTime", latest != null ? latest.getPubDateBj() : null);

        log.info("系统概览: {}", overview);
        return overview;
    }
}
