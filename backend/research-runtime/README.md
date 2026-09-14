# Financial DeepResearch Runtime

这是仓库唯一的后端与 Research Runtime 主线。它负责研究问题、任务 DAG、工具执行、证据资格、Claim、Thesis、结构化 IC review、人工决策、checkpoint、事件和评测；FinEvidence 作为外部证据基础设施通过 `EvidenceProvider` 接入。

## 本地运行

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m pytest -q
.\.venv\Scripts\python -m uvicorn deepresearch.api:app --reload --port 8000
```

健康检查：`http://127.0.0.1:8000/api/v1/health`。运行结果可通过
`/api/v1/research-runs/{run_id}/trace` 查看证据资格、provenance 完整性和
claim-to-evidence 链接；其中 `claim_verification` 会按 Claim 展示证据
资格、FinEvidence coverage、验证响应和可解释的 evidence gaps。运行后可通过
`POST /api/v1/research-runs/{run_id}/evaluate` 写入 golden-case evaluation，
再用 `GET /api/v1/research-runs/{run_id}/evaluation` 读取最新结果；所有历史
artifact 保留在 SQLite 中。Completed/partial run 的 deterministic scorer 还会
检查 memo/decision 中的 IC review 链接；golden case 可通过
`required_ic_review_roles` 显式要求角色覆盖，并检查 Red-team review 的
thesis/evidence 链接；`minimum_red_team_reviews` 可显式要求反方审查数量。
FinancialAnalysis/ValuationScenarios 的 evidence links 也会被复核；golden
case 可通过 `requires_financial_analysis` 或
`requires_valuation_scenarios` 显式要求相应 artifact。

长任务可先调用 `POST /api/v1/research-runs/{run_id}/enqueue` 写入 durable
queue intent，再由独立进程执行。没有 Redis 时使用数据库 scan；配置 Redis
时 worker 优先消费 Redis dispatch，再用数据库事件做恢复：

```powershell
.\.venv\Scripts\python.exe -m deepresearch.worker --database .data/deepresearch.sqlite3 --once
.\.venv\Scripts\python.exe -m deepresearch.worker --database .data/deepresearch.sqlite3 --poll-seconds 2
```

worker 复用同一 ResearchEngine、lease、checkpoint 和 failure semantics；
`RUNNING`、`PARTIAL` run 可在进程中断后恢复。PostgreSQL/Redis 版本仍然是
单机进程拓扑，不承诺分布式 exactly-once。

## PostgreSQL + Redis 单机栈

如果要按产品 MVP 的真实后端拓扑运行，而不是使用 SQLite fallback：

```powershell
cd "D:\01_work\ai-investment-research-assistant\ai-investment-research-assistant"
Copy-Item .env.example .env
docker compose up --build
```

Compose 会启动 PostgreSQL、Redis、FastAPI Runtime 和独立 worker：

```text
http://127.0.0.1:8011/api/v1/health
```

健康响应会包含：

```json
{"persistence":"postgresql","queue":"redis"}
```

默认 Compose 使用 deterministic evidence，因此不需要 API key。要连接单独
运行的 FinEvidence，在 `.env` 设置
`FIN_EVIDENCE_BASE_URL=http://host.docker.internal:8000`；Runtime 仍然只通过
FinEvidence v1 HTTP API 通信。PostgreSQL 是本地 named volume，Redis 只负责
dispatch，`RUN_ENQUEUED` 事件和全部研究状态仍保存在 PostgreSQL；Redis 丢失
时 worker 会扫描数据库事件恢复 runnable runs。该配置是单机 MVP，不是 HA 或
生产集群。

## 单机 MVP 完整闭环

要验证产品的完整后端主线，先创建一个 case/run 并执行研究，再调用：

```text
POST /api/v1/research-runs/{run_id}/mvp-complete
```

请求必须显式提供 `financial_facts`、三情景 `valuation`、一条带
counter/conflicting evidence 的 `red_team`、`BULL/BEAR/FINANCIAL/INDUSTRY/PARTNER`
五类 IC review，以及人工 `decision`。这个入口会在本地同步完成：

```text
research execution
→ typed financial facts / calculation ledger
→ Bull / Base / Bear valuation
→ red-team review
→ five-role IC review
→ human decision
→ deterministic evaluation artifact
```

所有事实和 review evidence 都必须引用当前 run 中的 `QUALIFIED` evidence；
系统不会从 excerpt 猜数字，也不会自动伪造 IC 结论。返回的 receipt 包含
各 artifact 的标识，详情继续通过现有 GET endpoints 查询。这个接口是单机
MVP 编排入口，不是生产级事务工作流；长任务仍可使用上面的 enqueue + worker。

## 本地评测与投资报告

真实 LLM planner 回归、同一 FinEvidence catalog 的 deterministic/LLM 对比和
已持久化 run 的 PDF memo 都是本地 artifact，不改变 runtime 的 canonical 依赖方向：

```powershell
python tools/export_runtime_snapshot.py `
  --database-url "postgresql://deepresearch:deepresearch@127.0.0.1:5432/deepresearch" `
  --run-id <completed-run-id> `
  --output evaluation/reports/run-snapshot.json

python tools/export_investment_report_pdf.py `
  --snapshot evaluation/reports/run-snapshot.json `
  --output ../../output/pdf/investment-memo.pdf
```

PDF 只接受已经持久化的 run snapshot，保留 thesis、Bull/Base/Bear、反证、
Claim verification receipts、memo sections、source locator 和 provenance；
`PARTIAL`/`DRAFT` 不会被渲染成已批准结论。比较报告中的 `memo_ready` 只有在
run 为 `COMPLETED` 且 memo 为 `READY_FOR_REVIEW` 时才为 true。

需要把已验证的财务数值送入 calculation ledger 时，可调用
`POST /api/v1/research-runs/{run_id}/financial-facts`。每个 fact 必须明确
声明 snapshot field、decimal value、period、unit、currency、basis 和
evidence IDs；Runtime 只做结构化映射，不从 FinEvidence 的原始文本猜数值，
并且所有 evidence 都必须已经在该 run 中被标记为 `QUALIFIED`。结果会保存
typed facts、field-level evidence links 和 calculation ledger，重启 Runtime
后仍可读取。

设置 canonical 变量 `FIN_EVIDENCE_BASE_URL` 后，API 会使用真实的 FinEvidence v1 HTTP
provider；旧的 `FINEVIDENCE_BASE_URL` 仅作为兼容别名。未设置时使用明确标记的 deterministic provider，保证本地测试不
需要网络或凭证。FinEvidence 的启动方式（另一个冻结仓库）是：

每个 evidence task 都会持久化一份 execution receipt。receipt 包含 provider
名称、绑定 case/task contract 的 `input_hash`，以及 runtime qualification
之后的 evidence 总数、`QUALIFIED`、`NEEDS_REVIEW`、`UNQUALIFIED` 计数；它不
保存原始 HTTP query、response 或 excerpt。旧 SQLite receipt 会以兼容默认值
加载，FinEvidence 仍然只通过下面的 HTTP v1 boundary 接入。

每个 `ResearchTask.tool_name` 都必须通过显式的 `ResearchToolRegistry` 解析。
未注册工具不会静默回退到全局 provider，而是在已持久化的 attempt receipt 上
记录 `FAILED` 和 bounded diagnostic；当不同工具使用不同 evidence provider 时，
qualification authority 与 claim verification 也跟随任务实际解析到的 provider。
未注入 registry 时，现有 deterministic/external/research aliases 会映射到构造
函数传入的单一 provider，保持旧调用方兼容。

当 API 使用真实 `FIN_EVIDENCE_BASE_URL` 自动构造默认 registry 时，还会注册
`financial-table`。它只通过 FinEvidence `/api/v1/table/query` 获取 exact
metadata-first candidate evidence，仍然必须经过 coverage/citation；不会把
table payload 自动转换成 FinancialSnapshot 或投资结论。

`EvidenceRequirement` 还会携带 FinEvidence coverage 所需的 fact type、role、
entity/metric/period 等 slots、criticality 和 evidence role。HTTP provider
原样传递这些字段；缺少的可选 slots 不会被伪造，entity 才会回退到 case target。

默认测试不访问网络。FinEvidence 本地部署可显式运行真实 v1 chain smoke：

```powershell
$env:FIN_EVIDENCE_INTEGRATION = "1"
$env:FIN_EVIDENCE_BASE_URL = "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m pytest -q -m integration
```

该 smoke 验证 health、search、coverage、citation、table 路由以及
`EvidenceRecord` 的 identity/provenance read-back，并通过 runtime API
完成一次 create-case → plan → execute → memo/events 链。search 必须观察到
真实 evidence；宽泛 table query 可以合法返回空结果，空结果或 `PARTIAL`
coverage 是真实观察结果，不会被改写为 eligible 或投资结论。

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

要对真实 LLM Planner 做一次可比较回归，使用独立 runner；它只保存结构化
plan、hash、计数和 gate，不保存 API key、authorization header、prompt 或原始
model response：

```powershell
$env:DEEPRESEARCH_PLANNER = "llm"
$env:FIN_EVIDENCE_BASE_URL = "http://127.0.0.1:8000"
.\.venv\Scripts\python.exe -m deepresearch.evaluation.llm_planner_regression `
  --output evaluation/reports/llm-planner-regression.json
```

runner 会同时输出 deterministic baseline 与 LLM plan score，并用 LLM 生成的
task contract 执行一次隔离 SQLite runtime，报告 evidence qualification、claim
linkage、thesis、memo sections 和 run evaluation。缺少显式 live 配置会生成
`BLOCKED` 报告并返回非零退出码，不会静默改用 deterministic planner。

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
  evidence qualification、evidence-grounded claims/thesis、structured IC review API、human decision API、
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
  fetches prices or infers missing inputs. When these artifacts are recorded,
  the memo projection retains the financial input hash and valuation artifact
  ID for review/export traceability.
- The single-machine MVP endpoint
  `POST /api/v1/research-runs/{run_id}/mvp-complete` composes the typed facts,
  financial calculation, valuation, red-team, five-role IC review, human
  decision, and deterministic evaluation steps. It requires explicit inputs
  and qualified evidence at every review boundary; it is the canonical local
  end-to-end smoke path, not a production transaction coordinator.
- When the configured FinEvidence provider exposes claim verification, every
  evidence-backed claim is sent to /api/v1/evidence/verify. Unsupported claims
  make the run PARTIAL; provider transport or contract failures make it FAILED
  with the original reason in RUN_FAILED. The verification call has its own
  durable ToolExecution receipt: an in-flight receipt is written before the
  call, and the receipt records supported/unsupported as a successful outcome
  or the bounded provider diagnostic as FAILED. Deterministic demo runs stay
  offline.
- Structured IC review records are append-only and role-scoped (`BULL`, `BEAR`,
  `FINANCIAL`, `INDUSTRY`, `PARTNER`). They retain reviewer rationale and
  evidence IDs, and a human decision can reference the review IDs it
  considered; the runtime does not compute panel consensus or generate an
  approval.
- 已实现 FinEvidence v1 provider transport boundary：`FinEvidenceClient` 只
  通过 `/health`、`/api/v1/evidence/search`、`coverage`、`citation`、
  `/api/v1/table/query` 和 `/api/v1/evidence/verify` 消费外部 API，不实现
  FinEvidence 本身；协议版本、来源 identity、URL、page/table locator、hash、
  verification status 和失败语义都在边界校验。每个研究 requirement 只有在
  外部 coverage 为 `ELIGIBLE` 且 evidence 为 `SUPPORTED` 时才会进入
  runtime 的 `QUALIFIED` 集合；runtime 不会重新提升外部 `PARTIAL` 或
  `UNSUPPORTED` 证据。
- Evidence requirement semantics are now typed at the runtime boundary and
  propagated to FinEvidence coverage; the runtime still does not infer missing
  financial values or implement requirement decomposition.
- LLM planner adapter 已实现并通过配置预检；它不是默认路径，也没有静默
  fallback。PostgreSQL/Redis 单机 adapter 已实现。尚未实现：live filing/market
  providers、生产级 auth/tenant policy、文档解析和交易执行。FinEvidence 的 evidence
  retrieval、parser、table IR、evaluation 和 CLIP implementation 不属于本仓库。
