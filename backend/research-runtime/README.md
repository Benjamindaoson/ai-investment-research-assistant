# Financial DeepResearch Runtime

这是仓库唯一的后端与 Research Runtime 主线。它负责研究问题、任务 DAG、工具执行、证据资格、Claim、Thesis、人工决策、checkpoint、事件和评测；FinEvidence 作为外部证据基础设施通过 `EvidenceProvider` 接入。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8000
```

健康检查：`http://127.0.0.1:8000/api/v1/health`。运行结果可通过
`/api/v1/research-runs/{run_id}/trace` 查看证据资格、provenance 完整性和
claim-to-evidence 链接。

设置 `FINEVIDENCE_BASE_URL` 后，API 会使用 HTTP provider；未设置时使用
明确标记的 deterministic provider，保证本地测试不需要网络或凭证。

## 当前能力边界

- 已真实实现：Pydantic domain contracts、依赖 DAG 校验、SQLite durable state、append-only events、checkpoint read-back、resume 去重、evidence qualification、claims/thesis、human decision API、可执行 scorer。
- Deterministic provider 是本地演示数据，不是 live market data，也不是 FinEvidence。
- 已实现 provider transport boundary：`HttpEvidenceProvider` 只消费
  FinEvidence-compatible payload，不实现 FinEvidence 本身；协议版本、来源
  identity、URL、locator、hash、source version 和失败语义都在边界校验。
- 尚未实现：真实 FinEvidence deployment、live filing/market providers、LLM
  planner、PostgreSQL adapter、生产级 auth/tenant policy、文档解析和交易执行。
