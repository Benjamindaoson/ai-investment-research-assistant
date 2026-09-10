# US Stock AI Monitor

一个面向美股监控与交易决策支持的 AI 应用系统。核心目标是把新闻/行情异动转成可执行信号，并形成可回看验证的策略闭环。

## 项目定位

- 监控：抓取美股新闻与异动，形成事件流
- 分析：AI 做原因分析、风险评估、情绪分析、案例检索
- 决策：输出结构化可执行计划（方向/触发/失效/止损/止盈/仓位/风险预算/预期R）
- 闭环：Watchlist + 订阅 + 告警 + T+1/T+5/T+20 命中率回看

## 模块结构

- `stock-web`：主业务 API（监控、AI、产品闭环、演示页）
- `stock-mcp`：MCP 工具服务（供 Agent/工具调用）
- `stock-common`：公共配置、响应、异常、重试等

## 当前核心能力（已实现）

### 1) 数据能力

- 实时行情与基础财务数据（`MarketDataClient` + `StockDataTools`）
- 期权快照与异常指标（volume/open-interest）
- 新闻检索与热门股票聚合

### 2) AI 能力

- 多类 AI 分析接口：原因、风险、趋势、组合建议、情绪
- RAG 历史案例检索（向量召回 + 多路融合）
- 交易信号结构化输出：`/api/ai/enhanced/chat/signal`

### 3) 产品闭环能力

- Watchlist 管理
- 告警订阅管理（symbol + strategy）
- 策略模板（earnings/regulatory/ma/volatility）
- 信号记录与回看验证（T+1/T+5/T+20）
- 信号信用评分（Signal Credit Score：历史命中率/市场状态匹配/数据新鲜度/多源一致性/模型置信）
- 命中率与策略有效性排名 + 自动降权治理（Active/Downweight/Retired）
- 周有效信号数（NSM 代理指标）与策略实验指标（Sharpe近似/Profit Factor/MDD）

## 关键 API

### 主分析接口

- `POST /api/ai/analyze/reason`
- `POST /api/ai/analyze/risk`
- `GET /api/ai/analyze/trend/{stockCode}`
- `POST /api/ai/enhanced/chat`
- `POST /api/ai/enhanced/chat/signal`

### 产品闭环接口

- `GET/POST/DELETE /api/ai/product/watchlist`
- `GET/POST/DELETE /api/ai/product/subscriptions`
- `POST /api/ai/product/subscriptions/scan`
- `POST /api/ai/product/signals/generate`
- `POST /api/ai/product/signals/generate/batch`
- `POST /api/ai/product/signals/validate/run`
- `GET /api/ai/product/signals/metrics`
- `GET /api/ai/product/signals/governance`

### 演示接口

- `GET /api/demo/health`
- `POST /api/demo/one-click`
- `GET /demo/index.html`
- `GET /decision-os/index.html`（Decision OS 专业可视化控制台）

## 运行方式

## 1) 本地快速演示（推荐）

```powershell
.\scripts\demo-run.ps1
```

打开：

- `http://127.0.0.1:6060/demo/index.html`

自动 smoke：

```powershell
.\scripts\demo-smoke.ps1
```

## 2) 常规开发运行

```powershell
# 构建
.\.tools\apache-maven-3.9.12\bin\mvn.cmd -DskipTests package

# 启动 stock-web
java -jar stock-web\target\stock-web-1.0-SNAPSHOT.jar --spring.profiles.active=dev

# 启动 stock-mcp
java -jar stock-mcp\target\stock-mcp-1.0-SNAPSHOT.jar --spring.profiles.active=dev
```

## 3) 全项目打包验证

```powershell
.\.tools\apache-maven-3.9.12\bin\mvn.cmd -DskipTests package
```

## 环境变量（关键）

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `OPENAI_MODEL`
- `DB_URL` / `DB_USERNAME` / `DB_PASSWORD`
- `REDIS_HOST` / `REDIS_PORT`

> 若 Redis 不可用，聊天历史与部分状态已支持内存回退，不会阻塞核心演示链路。

## 技术栈

- Java 21
- Spring Boot 3.4.x
- Spring AI
- MyBatis-Plus
- Redis
- Caffeine
- H2（demo profile）
- Apache ECharts（开源图表库，前端可视化）

## 说明

本仓库当前优先保证“可运行的核心价值链路”，适合用于简历展示与面试演示；生产化补强项（如统一鉴权、灰度、完备压测与审计）可在后续迭代继续增强。
