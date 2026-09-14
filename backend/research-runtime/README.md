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
claim-to-evidence 链接。运行后可通过
`POST /api/v1/research-runs/{run_id}/evaluate` 写入 golden-case evaluation，
再用 `GET /api/v1/research-runs/{run_id}/evaluation` 读取最新结果；所有历史
artifact 保留在 SQLite 中。

设置 canonical 变量 `FIN_EVIDENCE_BASE_URL` 后，API 会使用真实的 FinEvidence v1 HTTP
provider；旧的 `FINEVIDENCE_BASE_URL` 仅作为兼容别名。未设置时使用明确标记的 deterministic provider，保证本地测试不
需要网络或凭证。FinEvidence 的启动方式（另一个冻结仓库）是：

每个 evidence task 都会持久化一份 execution receipt。receipt 包含 provider
名称、绑定 case/task contract 的 `input_hash`，以及 runtime qualification
之后的 evidence 总数、`QUALIFIED`、`NEEDS_REVIEW`、`UNQUALIFIED` 计数；它不
保存原始 HTTP query、response 或 excerpt。旧 SQLite receipt 会以兼容默认值
加载，FinEvidence 仍然只通过下面的 HTTP v1 boundary 接入。

```powershell
cd "D:\01_work\Enterprise Multimodal RAG\finevidence"
\.venv\Scripts\python.exe -m uvicorn finevidence.api.app:app --host 127.0.0.1 --port 8000
```

随后在本项目启动前设置：

```powershell
$env:FIN_EVIDENCE_BASE_URL = "http://127.0.0.1:8000"
$env:FIN_EVIDENCE_TIMEOUT_SECONDS = "120"
$env:RESEARCH_RUNTIME_LEASE_SECONDS = "300"
```

每次 run 执行都会先获取 SQLite durable lease；同一个 run 的并发执行会返回
HTTP 409，进程崩溃后过期 lease 可以被下一次执行接管。同步 runtime 会以 TTL
的三分之一周期（最多 30 秒）heartbeat renewal；若 ownership 丢失，旧 executor
不会持久化 provider 结果。provider 调用前会先保存 `UNKNOWN_EFFECT` attempt；
如果接管时该 attempt 仍未关闭，run 会变为 `BLOCKED`，不会自动重试，必须通过
`POST /api/v1/research-runs/{run_id}/tool-attempts/{attempt_id}/resolve` 明确选择
`RETRY` 或 `MARK_FAILED`。heartbeat 无法中断正在进行的 provider 调用，真正的
exactly-once 仍需要 provider 幂等键和后续 worker reconciliation。

Planner 默认也是 deterministic。只有显式设置
`DEEPRESEARCH_PLANNER=llm`，并提供 `DEEPSEEK_API_KEY`、
`DEEPSEEK_BASE_URL`、`DEEPSEEK_MODEL`（或对应的 `LLM_*` 变量）时，API
才会调用 OpenAI-compatible planner。LLM 输出必须先通过结构化 schema 和
DAG 校验；调用失败不会静默回退为另一份 plan。

Synthesis 默认也是 deterministic。只有显式设置
`DEEPRESEARCH_SYNTHESIZER=llm` 并提供同一组 LLM 配置时，API 才会调用
structured claim/thesis synthesizer。模型只能提交 claim、qualified evidence
ID 和 Bull/Base/Bear 草案；runtime 仍负责 evidence ID 校验、claim verification、
memo/memory 投影和人工 review。synthesis 请求/响应 hash 会保存在 thesis provenance，
配置失败不会静默回退为 deterministic synthesis。

## 当前能力边界

- 已真实实现：Pydantic domain contracts、deterministic planner boundary、unique durable run identity、带
  planner provenance 的 ResearchPlan、依赖 DAG 校验、SQLite durable state、
  append-only events、checkpoint read-back、resume 去重、带完整 provenance gate 的
  evidence qualification、evidence-grounded claims/thesis、human decision API、
  durable investment memo projection（含 evidence-linked structured sections）、Decimal financial analysis、
  target-level Investment Memory with observed ThesisDelta、run-scoped memory read、case-scoped run history、plan/trace/memo/memory/financial-analysis
  API、case-scoped rerun、durable cancellation、可执行 scorer。`python -m
  deepresearch.evaluation` 会独立输出 planner quality 和 runtime execution
  两组结果，并对 completed/partial run 检查 memo sections 与 artifact links。
- 已实现 durable replan：POST /api/v1/research-runs/{run_id}/replan 只接受
  PARTIAL run，记录 unresolved requirements，保留原 run ID、证据和事件，
  只重置受影响 task 及其下游，并从新 checkpoint 恢复执行。重试不会用重复
  evidence 制造 coverage。
- Deterministic provider 是本地演示数据，不是 live market data，也不是 FinEvidence。
- The run-scoped financial analysis endpoint accepts only an explicit Decimal
  snapshot and field-level evidence_ids. Every non-null financial field must
  link to evidence already present in the same run with QUALIFIED status. The
  runtime does not guess financial fields from table/query responses. The
  legacy financial-analysis endpoint remains backward-compatible but is not
  evidence-backed. A successful run-scoped calculation is persisted on the
  ResearchRun, emits FINANCIAL_ANALYSIS_RECORDED, and can be read back from
  GET /api/v1/research-runs/{run_id}/financial-analysis.
- The run-scoped valuation scenario endpoint accepts exactly one explicit
  BULL, BASE, and BEAR assumption set. Base revenue and every assumption field
  must link to QUALIFIED evidence already present in the same run. The
  Decimal-only terminal-value bridge is illustrative, persists through
  `POST/GET /api/v1/research-runs/{run_id}/valuation-scenarios`, and never
  fetches prices or infers missing inputs.
- When the configured FinEvidence provider exposes claim verification, every
  evidence-backed claim is sent to /api/v1/evidence/verify. Unsupported claims
  make the run PARTIAL; provider transport or contract failures make it FAILED
  with the original reason in RUN_FAILED. Deterministic demo runs stay offline.
- 已实现 FinEvidence v1 provider transport boundary：`FinEvidenceClient` 只
  通过 `/health`、`/api/v1/evidence/search`、`coverage`、`citation`、
  `/api/v1/table/query` 和 `/api/v1/evidence/verify` 消费外部 API，不实现
  FinEvidence 本身；协议版本、来源 identity、URL、page/table locator、hash、
  verification status 和失败语义都在边界校验。每个研究 requirement 只有在
  外部 coverage 为 `ELIGIBLE` 且 evidence 为 `SUPPORTED` 时才会进入
  runtime 的 `QUALIFIED` 集合；runtime 不会重新提升外部 `PARTIAL` 或
  `UNSUPPORTED` 证据。
- LLM planner adapter 已实现并通过一次真实配置预检；它不是默认路径，也没有
  静默 fallback。尚未实现：live filing/market providers、PostgreSQL adapter、
  生产级 auth/tenant policy、文档解析和交易执行。FinEvidence 的 evidence
  retrieval、parser、table IR、evaluation 和 CLIP implementation 不属于本仓库。
