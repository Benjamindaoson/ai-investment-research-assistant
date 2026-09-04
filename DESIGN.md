# Enterprise DeepResearch System - Design Document

## Product Vision

**产品定位**: AI投研深度研究助手 (AI Research Agent for Financial Analysis)

**目标用户**: 券商分析师、资管研究员、企业战略研究人员

**核心流程**:
```
动态规划 → 多源研究 → 证据验证 → 动态调整 → 投资判断 → Investment Memo
```

---

## 1. 产品概念重构

### 当前问题
- 页面结构过于通用（Today/Analyses/Data...）
- 没有体现投研工作流
- 术语不专业（Finding → Claim）
- 缺少投资判断相关概念

### 目标概念

| 当前 | 目标 |
|------|------|
| Analysis Task | Research Task |
| Finding | Claim |
| Evidence Library | Evidence Vault |
| Dashboard | Investment Thesis |
| Report | Investment Memo |

---

## 2. 信息架构

### 页面结构

```
Research Hub (首页)
├── Research Task Board
│   ├── Active Research
│   ├── Task Contract (目标/范围/预算)
│   └── Research Progress
├── Evidence Vault
│   ├── Evidence States (未支持/冲突/已验证/阻塞)
│   ├── Evidence Search
│   └── Evidence Linking
├── Thesis Builder
│   ├── Key Claims
│   ├── Investment Thesis
│   ├── Bull / Base / Bear
│   └── Catalyst / Risk
├── Scenario Analysis
│   ├── Bull Case
│   ├── Base Case
│   └── Bear Case
└── Investment Memo
    ├── Executive Summary
    ├── Evidence Summary
    ├── Investment Thesis
    └── Risk Factors
```

---

## 3. 核心数据模型 (对齐后端)

### Evidence States (证据状态)
```typescript
enum EvidenceState {
  UNSUPPORTED = "未支持"      // 假设未被证据支持
  PARTIAL = "部分支持"        // 部分证据支持
  CONFLICTING = "冲突"       // 存在冲突证据
  NEEDS_CALCULATION = "需计算" // 需要计算验证
  EXPIRED = "已过期"         // 数据已过期
  VERIFIED = "已验证"         // 证据确认
  BLOCKING = "阻塞"           // 阻塞研究进展
}
```

### Claim Types (结论类型)
```typescript
enum ClaimType {
  FACT = "事实"              // 可直接验证的数据
  INFERENCE = "推断"          // 基于证据的推断
  QUALIFIED = "限定"          // 有条件的结论
  RECOMMENDATION = "建议"     // 行动建议
}
```

### Investment Output
```typescript
interface InvestmentThesis {
  summary: string
  keyAssumptions: Claim[]
  bullCase: Scenario
  baseCase: Scenario
  bearCase: Scenario
  catalysts: string[]
  risks: string[]
  confidence: number  // 0-1
}
```

---

## 4. API 端点 (已实现)

### Research Task
- `POST /api/v1/analysis-tasks` - 创建研究任务
- `GET /api/v1/analysis-tasks/{task_id}` - 获取任务详情
- `GET /api/v1/analysis-tasks` - 列出所有任务

### Investigation
- `GET /api/v1/analysis-tasks/{task_id}/investigation` - 获取研究状态
  - Returns: hypotheses, observations, contributions, events

### Evidence
- `GET /api/v1/analysis-tasks/{task_id}/evidence` - 获取证据列表
- `GET /api/v1/analysis-tasks/{task_id}/evidence/{evidence_id}` - 获取证据详情

### Claims
- `GET /api/v1/analysis-tasks/{task_id}/claims` - 获取结论列表

### Artifacts
- `GET /api/v1/analysis-tasks/{task_id}/artifacts` - 获取报告/图表
- `GET /api/v1/analysis-tasks/{task_id}/artifacts/report.md` - 获取Markdown报告

---

## 5. 前端设计

### 视觉风格
- **色调**: 专业金融风格 (深蓝 #1A1A2E + 青绿 #00D4AA)
- **字体**: Inter (正文) + JetBrains Mono (数据/代码)
- **布局**: 高信息密度，卡片式设计
- **动画**: 克制，仅用于状态变化提示

### 组件系统

#### ResearchTaskCard
- 研究问题
- 状态进度 (CREATED/RUNNING/COMPLETED/PARTIAL/FAILED)
- 关键结论数量
- 证据验证状态

#### EvidenceCard
- 证据类型图标
- 证据状态标签
- 验证状态 (METRIC/TIME/JOIN/RECON/FRESH)
- 支持的Claims

#### ClaimCard
- Claim类型 (FACT/INFERENCE/QUALIFIED)
- 置信度条
- 关联证据列表
- 状态 (DRAFT/VERIFIED/QUALIFIED/REJECTED)

#### ThesisSection
- Bull/Base/Bear 切换
- 关键假设
- 催化剂/风险

---

## 6. 实现优先级

### Phase 1: 基础改造
- [ ] 重命名页面术语 (Analysis → Research)
- [ ] 修复API对接错误
- [ ] Evidence状态显示

### Phase 2: 投研流程
- [ ] Research Task Board
- [ ] Evidence Vault with states
- [ ] Claim- Evidence linking

### Phase 3: 投资输出
- [ ] Thesis Builder
- [ ] Scenario Analysis
- [ ] Investment Memo template

---

## 7. 技术栈

### Frontend
- React 19 + TypeScript
- Vite
- TanStack Query (数据获取)
- TanStack Router (路由)
- Tailwind CSS

### Backend
- FastAPI
- Pydantic (Domain Models)
- SQLite (持久化)

---

## 8. 设计参考

- **Bloomberg Terminal**: 高信息密度
- **S&P Capital IQ**: 金融数据展示
- **Notion**: 文档协作
- **Linear**: 任务流程
