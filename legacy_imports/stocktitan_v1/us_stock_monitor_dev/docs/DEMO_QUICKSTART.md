# Demo Quickstart

## 1) 启动演示版

```powershell
.\scripts\demo-run.ps1
```

默认端口 `6060`，启动后打开：

- `http://127.0.0.1:6060/demo/index.html`（可视化演示页）
- `http://127.0.0.1:6060/api/demo/health`

## 2) 自动演示脚本（可录屏）

在服务启动后执行：

```powershell
.\scripts\demo-smoke.ps1
```

会顺序调用：

1. `GET /api/demo/health`
2. `POST /api/demo/one-click`
3. `GET /api/ai/product/signals/metrics`

## 3) 你可以怎么讲

1. 系统是“AI 交易信号闭环”，不是一次性问答。
2. 一键演示展示了四步：`watchlist -> 订阅 -> 可执行信号 -> T+1/T+5/T+20 回看统计`。
3. 即使外部依赖不可用（Redis/AI key），演示链路仍可跑通（有降级回退）。

