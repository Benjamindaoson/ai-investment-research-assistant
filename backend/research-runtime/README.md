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

Planner 默认也是 deterministic。只有显式设置
`DEEPRESEARCH_PLANNER=llm`，并提供 `DEEPSEEK_API_KEY`、
`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`（或对应的 `LLM_*` 变量）时，API
才会调用 OpenAI-compatible planner。LLM 输出必须先通过结构化 schema 和
DAG 校验；调用失败不会静默回退为另一份 plan。

## 当前能力边界

- 已真实实现：Pydantic domain contracts、deterministic planner boundary、带
  planner provenance 的 ResearchPlan、依赖 DAG 校验、SQLite durable state、
  append-only events、checkpoint read-back、resume 去重、evidence
  qualification、evidence-grounded claims/thesis、human decision API、
  durable investment memo projection、Decimal financial analysis、
  target-level Investment Memory with observed ThesisDelta、plan/trace/memo/memory/financial-analysis
  API、durable cancellation、可执行 scorer。`python -m
  deepresearch.evaluation` 会独立输出 planner quality 和 runtime execution
  两组结果。
- Deterministic provider 是本地演示数据，不是 live market data，也不是 FinEvidence。
- 已实现 provider transport boundary：`HttpEvidenceProvider` 只消费
  FinEvidence-compatible payload，不实现 FinEvidence 本身；协议版本、来源
  identity、URL、locator、hash、source version 和失败语义都在边界校验。
- LLM planner adapter 已实现并通过一次真实配置预检；它不是默认路径，也没有
  静默 fallback。尚未实现：真实 FinEvidence deployment、live filing/market
  providers、PostgreSQL adapter、生产级 auth/tenant policy、文档解析和交易
  执行。
