# US Stock Monitor

> Real-time US stock anomaly detection with multi-channel push notifications — built on Spring Boot 3 + Java 21.

A production-grade automated pipeline that continuously monitors [StockTitan](https://www.stocktitan.net) RSS feeds, detects unusual stock movements, translates news headlines via Baidu Translate API, persists deduped records to MySQL, and fans out alerts across DingTalk, WeChat, and WeCom (Enterprise WeChat) — all driven by a configurable scheduler.

---

## Architecture

```
StockTitan RSS Feed
        │
        ▼
  RssServiceImpl          ← Spring @Scheduled (every 30s)
        │
        ├── Dedup check   ← MySQL via MyBatis-Plus
        ├── Baidu Translate API  ← EN → ZH title translation
        ├── StockTitanCrawler    ← Jsoup HTML tag extraction
        ├── Anomaly stats        ← 24h / 3-day / 1-week counts
        │
        ▼
  Notify Fan-out (config-driven)
        ├── DingTalk Bot    (dingtalk SDK + HMAC-SHA256 signing)
        ├── WeChat Bot      (Python wxauto subprocess bridge)
        └── WeCom Bot       (Enterprise WeChat Webhook REST)
```

---

## Key Features

- **Zero-duplicate ingestion** — Each RSS entry is fingerprinted by `(stockCode, link)` before persistence; duplicate events are silently skipped.
- **Baidu Translate integration** — English titles are translated to Chinese in real time via the Baidu Translate REST API with MD5-signed requests.
- **HTML tag scraping** — Jsoup crawls StockTitan's live feed page to extract categorization tags (e.g., earnings, M&A, guidance) for each news item, with graceful 429 anti-scraping fallback.
- **Multi-dimensional anomaly stats** — For every alert, the system computes how many times the same stock moved in the past 24 hours, 3 days, and 1 week — surfacing the hottest names at a glance.
- **Config-driven multi-channel fan-out** — Three notification channels (DingTalk, WeChat, WeCom) can be independently toggled in `application.yml` with no code changes.
- **AOP performance monitoring** — A `ServiceLogAspect` wraps all service layer methods with `StopWatch` timing; slow calls (>3s) are flagged as `ERROR`, moderate calls (>2s) as `WARN`.
- **Secure secrets management** — All credentials (API keys, tokens, webhook URLs, DB passwords) are loaded from a `.env` file via `dotenv-java` at startup; no secrets in source code.
- **MCP module** — A companion `stock-mcp` module exposes `StockTool`, `EmailTool`, and `DateTool` as MCP (Model Context Protocol) tools for AI agent integration.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Java 21, Spring Boot 3 |
| Persistence | MySQL 8, MyBatis-Plus 3.5, HikariCP |
| RSS Parsing | ROME 2.1 |
| HTML Scraping | Jsoup 1.21 |
| Translation | Baidu Translate REST API |
| Notification | DingTalk SDK 2.0, WeChat (wxauto / Python), WeCom Webhook |
| HTTP Client | Spring `RestTemplate`, Apache HttpClient 5 |
| AOP | Spring AOP (AspectJ) |
| Observability | SLF4J + Logback |
| Secrets | dotenv-java 3.2 |
| Utilities | Hutool 5.8, Lombok, Commons Lang3 |
| AI Integration | MCP (Model Context Protocol) |

---

## Project Structure

```
us_stock_monitor_dev/
├── stock-web/               # Main web module — scheduler, RSS, notifications
│   └── src/main/java/com/itzixi/
│       ├── Application.java
│       ├── StockScheduler.java
│       ├── ServiceLogAspect.java
│       ├── RestTemplateConfig.java
│       ├── config/
│       │   └── NotifyChannelConfig.java
│       ├── entity/          # USStockRss, USStockMsg, BaiduTransEntity
│       ├── enums/           # StockTag (EN→ZH tag mapping with emoji)
│       ├── mapper/          # MyBatis-Plus mapper
│       ├── service/
│       │   ├── RssService / RssServiceImpl
│       │   ├── StockService / StockServiceImpl
│       │   ├── WechatBotService / WechatBotServiceImpl
│       │   └── WechatWorkBotService / WechatWorkBotServiceImpl
│       └── utils/
│           ├── DingTalkApi.java
│           ├── TransApi.java
│           ├── StockTitanCrawler.java
│           ├── GMTDateConverter.java
│           └── MD5.java
└── stock-mcp/               # MCP module — AI agent tool exposure
    └── src/main/java/com/itzixi/
        └── mcp/tool/        # DateTool, EmailTool, StockTool
```

---

## Getting Started

### Prerequisites

- Java 21+
- Maven 3.9+
- MySQL 8.0+
- Python 3.x + `wxauto` *(only required for WeChat channel)*

### 1. Database setup

```sql
-- Import the provided schema
mysql -u root -p < us_stock_monitor_dev.sql
```

### 2. Configure secrets

Create a `.env` file in the project root (never commit this file):

```env
# Database
# (configured in application-dev.yml — override here for prod)

# Baidu Translate
BAIDU_TRANSLATE_HOST=http://api.fanyi.baidu.com/api/trans/vip/translate
BAIDU_TRANSLATE_APPID=your_appid
BAIDU_TRANSLATE_SECURITYKEY=your_security_key

# DingTalk
DINGDING_TOKEN=your_robot_token
DINGDING_SECRET=your_robot_secret
DINGDING_USERID=your_user_id

# WeChat (optional — Windows only)
WECHAT_PYTHON_EXE=python
WECHAT_SCRIPT_PATH=C:/path/to/send_wx_v3.py

# WeCom / Enterprise WeChat (optional)
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

### 3. Configure notification channels

Edit `stock-web/src/main/resources/application.yml`:

```yaml
notify:
  channels:
    dingtalk: true    # DingTalk group bot
    wechat: false     # WeChat personal client (Windows only)
    wecom: false      # Enterprise WeChat webhook
```

### 4. Build and run

```bash
mvn clean package -DskipTests
java -jar stock-web/target/stock-web-*.jar
```

---

## Notification Channels

### DingTalk
Uses the official DingTalk robot SDK with HMAC-SHA256 signature verification. Alerts are formatted with emoji-tagged stock info and `@mention` support.

### WeChat (Personal Client)
Bridges to a Python `wxauto` script via `ProcessBuilder`. Requires Windows, WeChat desktop client (3.9.x or compatible 4.0.x), and the `wxauto` Python library.

> **Disclaimer:** This integration is for technical learning only. Do not use for commercial or illegal purposes. Compliance with WeChat's Terms of Service is the user's sole responsibility.

### WeCom (Enterprise WeChat)
Posts plain-text messages to a WeCom group bot via Webhook REST API. No additional dependencies required — just configure the webhook URL.

---

## Configuration Reference

| Key | Default | Description |
|-----|---------|-------------|
| `notify.channels.dingtalk` | `true` | Enable DingTalk push |
| `notify.channels.wechat` | `false` | Enable WeChat push |
| `notify.channels.wecom` | `false` | Enable WeCom push |
| `wechat.python-exe` | `python` | Python executable name or path |
| `wechat.script-path` | *(empty)* | Absolute path to `send_wx_v3.py` |
| `wecom.webhook-url` | *(empty)* | WeCom robot webhook URL |
| `spring.profiles.active` | `dev` | Active profile (`dev` / `prod`) |

---

## Observability

All service layer methods are instrumented by `ServiceLogAspect`:

| Execution Time | Log Level | Label |
|----------------|-----------|-------|
| < 2s | `INFO` | `OK` |
| 2s – 3s | `WARN` | `NORMAL` |
| > 3s | `ERROR` | `SLOW` |

Log format: `[className.methodName], [durationMs], [label], [args]`

---

## MCP Integration

The `stock-mcp` module exposes three tools for AI agent workflows via the Model Context Protocol:

- **`StockTool`** — Query stock anomaly records from the database
- **`EmailTool`** — Send email notifications
- **`DateTool`** — Date/time utilities for time-range queries

---

## License

This project is for educational and technical learning purposes only.
