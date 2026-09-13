# Financial DeepResearch Runtime

这是仓库唯一的后端与 Research Runtime 主线。它负责研究问题、任务 DAG、工具执行、证据资格、Claim、Thesis、人工决策、checkpoint、事件和评测；FinEvidence 作为外部证据基础设施通过 `EvidenceProvider` 接入。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8000
```

健康检查：`http://127.0.0.1:8000/api/v1/health`。

## 当前能力边界

- 已真实实现：Pydantic domain contracts、依赖 DAG 校验、SQLite durable state、append-only events、checkpoint read-back、resume 去重、evidence qualification、claims/thesis、human decision API、可执行 scorer。
- Deterministic provider 是本地演示数据，不是 live market data，也不是 FinEvidence。
- 尚未实现：FinEvidence production adapter、live filing/market providers、LLM planner、PostgreSQL adapter、生产级 auth/tenant policy、文档解析和交易执行。
