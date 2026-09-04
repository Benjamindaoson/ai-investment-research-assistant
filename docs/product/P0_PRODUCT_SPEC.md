# AI & Embodied Intelligence Research Agent 产品说明书

## 1. 产品名称

**AI & Embodied Intelligence Research Agent**

中文名：

**AI 与具身智能产业智能投研平台**

产品副标题：

> 面向 AI、AI Agent、机器人与具身智能产业的 Evidence-first 智能研究与决策工作台

---

# 2. 产品定位

这不是：

* 股票行情软件
* AI 聊天机器人
* 普通 RAG 知识库
* 自动生成研报工具
* DeepResearch 的简单封装

它是一套面向专业研究人员的：

> **AI-native Research Workspace**

核心目标是让 AI 完成大量原本由研究员手工完成的：

**找资料 → 阅读 → 提取 → 验证 → 比较 → 形成观点 → 找反证 → 持续更新**

工作。

最终不是简单生成一篇报告，而是形成一个可以持续维护的：

> **Research Case + Evidence + Findings + Thesis + Living Brief**

---

# 3. 目标用户

P0 优先服务以下三类用户。

### 3.1 VC / PE / 科技投资研究人员

典型问题：

> 未来三年具身智能产业最大的价值池在哪里？

> Figure 是否值得持续关注？

> AI Agent Infrastructure 哪些环节可能产生平台型公司？

### 3.2 企业战略 / 战投部门

典型问题：

> 公司是否应该进入具身智能行业？

> 应该投资模型、数据、仿真还是机器人本体？

> 哪些竞争对手未来两年最值得监控？

### 3.3 AI / 机器人行业研究员

典型问题：

> VLA 是否正在成为机器人主流技术路线？

> World Model 在具身智能中的实际价值是什么？

> 中国和美国人形机器人公司的路线有什么差异？

---

# 4. 第一阶段产业范围

P0 聚焦：

## AI

* Foundation Models
* AI Infrastructure
* AI Agent
* Agent Infrastructure
* AI Coding
* AI Research Agents
* Agentic RL
* Model Serving / Inference

## Embodied Intelligence

* Humanoid Robotics
* VLA
* World Models
* Robot Foundation Models
* Manipulation
* Navigation
* Robot Data
* Simulation
* Synthetic Data

## 具身智能产业链

* 机器人本体
* 执行器
* 灵巧手
* 传感器
* 数据采集
* 仿真
* 基础模型
* 训练基础设施
* 开发平台

第一版不追求覆盖整个市场。

优先围绕少量代表性公司和技术方向完成高质量研究闭环。

---

# 5. 核心产品价值

产品解决五个核心问题。

| 传统研究问题      | 产品能力                                |
| ----------- | ----------------------------------- |
| 信息散落在几十个网站  | Multi-source Research               |
| 阅读大量资料耗时    | AI Research Worker                  |
| AI 容易编造结论   | Evidence Intelligence               |
| 研究只找支持观点的资料 | Counter-Evidence                    |
| 报告写完就过期     | Living Research / Thesis Versioning |

最终实现：

> **Evidence before prose.**

先建立证据，再形成观点，最后生成报告。

---

# 6. 产品核心闭环

整个产品只有一条最重要的主链：

```text
Research Question
        ↓
Research Case
        ↓
Research Plan
        ↓
Multi-source Research
        ↓
Evidence Intelligence
        ↓
Research Findings
        ↓
Counter-Evidence
        ↓
Thesis
        ↓
Risk / Catalyst
        ↓
Human Review
        ↓
Living Brief
```

这是 P0 必须完整跑通的闭环。

---

# 7. 信息架构

主导航建议：

```text
Today

Research
Companies
Industries
Watchlist
Library

────────────────

Recent Research
```

顶部：

```text
Global Search
Command Palette
New Research
Notifications
User
```

快捷键：

> `Cmd / Ctrl + K`

---

# 8. 产品页面

P0 只做 7 个核心页面。

---

## 8.1 Today

### 页面目标

成为研究员每天打开系统后的工作首页。

不是行情 Dashboard。

### 核心模块

#### Ask a Research Question

大型研究输入框：

> Ask anything about AI, agents or embodied intelligence...

支持：

* 输入研究问题
* 上传文件
* 添加公司
* 添加行业
* 选择时间范围

#### Continue Research

继续尚未完成的研究任务。

#### Needs Review

展示需要人工介入的：

* Evidence
* Claims
* Thesis
* Conflict

#### What Changed

展示最近研究对象发生的重要变化。

P0 可使用 Mock Data。

#### Recent Research

最近完成或进行中的 Research Case。

---

# 9. New Research

用户正式创建一次研究任务。

例如输入：

> 未来三年具身智能产业最大的价值池在哪里？

系统进入 Research Setup。

### 用户可以设置

**Research Scope**

* Quick Research
* Deep Research

**Targets**

* Companies
* Technologies
* Industries

**Time Range**

例如：

* 12 months
* 3 years
* Custom

**Sources**

例如：

* Official
* Research Papers
* News
* GitHub
* Patents
* Hiring
* Uploaded Documents

点击：

> **Start Research**

进入 Research Case。

---

# 10. Research Case

这是整个产品最重要的页面。

它代表一个完整研究项目。

例如：

> **未来三年具身智能产业最大的价值池在哪里？**

顶部展示：

```text
Deep Research

Running

Last Updated 2m ago

Evidence Coverage 78%
```

---

## 10.1 Research Question

保留最初问题。

同时展示结构化后的：

### Research Goal

寻找未来三年具身智能产业中：

* 市场空间大
* 竞争尚未固化
* 技术壁垒高
* 商业化可行

的高价值环节。

---

# 11. Research Plan

AI 首先生成研究计划。

例如：

### Market

* 市场规模
* 增长速度
* 商业化节奏

### Technology

* VLA
* World Models
* Robot Foundation Models

### Competition

* Tesla
* Figure
* Physical Intelligence
* 智元
* 宇树

### Value Chain

* Model
* Data
* Simulation
* Hardware
* Deployment

### Risk

* 技术成熟度
* 成本
* 数据瓶颈
* 需求验证

每个 Research Task 有状态：

```text
Completed
Running
Pending
Needs Review
```

用户可以：

* 添加问题
* 删除问题
* 调整优先级
* 重新运行

---

# 12. Research Execution

AI 研究过程中不能只显示一个 Loading Spinner。

需要完整的 Streaming Research Experience。

例如：

```text
Planning research...

Searching official sources...

Reading Figure AI...

Found 14 relevant documents

Reading 3 VLA papers...

Extracting evidence...

Found conflicting commercialization estimates

Searching additional sources...

Updating findings...
```

用户随时知道：

> AI 在做什么。

---

# 13. Research Findings

研究结果首先形成结构化 Findings，而不是直接写报告。

例如：

## Finding

> 机器人数据基础设施可能成为具身智能产业的重要价值池。

### Supporting signals

* 多家公司扩大数据采集规模
* Robot Foundation Model 对高质量数据需求快速增长
* Physical Intelligence 等公司持续扩大数据基础设施

### Confidence

High

### Evidence

12 sources

### Counter Evidence

3 sources

用户可以展开每个 Finding。

---

# 14. Evidence Intelligence

这是产品核心差异化能力。

系统不是：

> AI 说了什么？

而是：

> AI 为什么这么说？

核心结构：

```text
Claim
   ↓
Evidence
   ↓
Source
```

---

# 15. Evidence Workspace

独立页面。

采用三栏布局。

```text
Claims
│
│    Selected Claim
│
│                   Evidence
```

---

## 15.1 Claim

例如：

> 人形机器人训练的数据瓶颈正在成为产业商业化的重要约束。

---

## 15.2 Supporting Evidence

每条 Evidence 显示：

**Source**

Physical Intelligence Blog

**Publish Date**

2026-06-12

**Evidence**

原始证据文本。

**Status**

Verified

---

## 15.3 Counter Evidence

必须单独展示反方证据。

例如：

> Synthetic Data may significantly reduce dependence on real-world robot data.

不能让系统只寻找支持当前 Thesis 的材料。

---

# 16. Evidence 状态

不要简单显示：

> Confidence 87%

前端优先使用可解释状态：

### Verified

多个高质量来源直接支持。

### Partially Supported

存在支持，但证据不足。

### Conflicting

不同来源存在冲突。

### Needs Review

无法可靠判断。

### Rejected

人工或系统确认不能使用。

---

# 17. Source Intelligence

所有 Source 保存：

* Publisher
* Author
* URL
* Publish Date
* Retrieved Date
* Source Type
* Original Document
* Citation Location

来源类型包括：

```text
Official
Financial Filing
Paper
Patent
GitHub
Hiring
Interview
News
Industry Report
User Upload
```

---

# 18. Company Research

针对公司建立长期 Research Workspace。

例如：

# Figure

页面顶部不应该首先是股价。

而应该是：

### Current Thesis

Figure 正在尝试通过 Foundation Model + Commercial Deployment 建立通用机器人平台。

### What Changed

过去 30 天：

* 新合作
* 产品更新
* 招聘变化
* 技术发布

### Technology

* Helix
* VLA
* Manipulation
* Data

### Commercialization

* Customers
* Deployment
* Manufacturing

### Competition

* Tesla Optimus
* 1X
* Physical Intelligence
* 中国公司

### Talent Signals

关键招聘和组织变化。

### Funding / Financial

融资、估值及公开财务信号。

### Risks

技术、商业、制造和竞争风险。

### Evidence Coverage

当前 Research Coverage。

---

# 19. Thesis Workspace

这是整个产品从：

> Research

走向：

> Decision Intelligence

的核心页面。

一个 Thesis 不是一段 Markdown。

而是一个结构化对象。

---

## 19.1 Current Thesis

例如：

> 未来三年具身智能最有可能首先产生超额价值的并非整机制造，而是数据、模型与机器人开发基础设施。

---

## 19.2 Key Assumptions

例如：

1. 通用机器人模型持续扩大；
2. 高质量机器人数据继续稀缺；
3. 整机厂愿意采购外部基础设施；
4. 机器人开发栈不会完全被头部整机厂垂直整合。

---

## 19.3 Supporting Evidence

直接关联 Evidence。

---

## 19.4 Counter Evidence

展示可能反驳 Thesis 的信息。

---

## 19.5 Disconfirming Conditions

非常重要。

明确：

> 什么情况发生后，我们应该认为当前观点错了？

例如：

* Synthetic Data 基本解决现实数据瓶颈；
* 大型整机厂全部建立闭源训练平台；
* Robot Foundation Models 没有表现出跨任务泛化能力。

---

# 20. Risk

独立维护风险。

例如：

### Technology Risk

VLA Scaling 不一定转化为实际机器人性能。

### Commercial Risk

机器人商业化周期可能明显长于市场预期。

### Competitive Risk

基础设施可能被 NVIDIA / Google 等平台公司吸收。

---

# 21. Catalyst

记录未来可能推动 Thesis 的事件。

例如：

* Figure 大规模商业部署
* 新 Robot Foundation Model
* NVIDIA Robotics Platform 更新
* 大额机器人采购订单
* 数据基础设施融资增加

---

# 22. What to Monitor

系统明确告诉研究员：

> 接下来应该持续观察什么？

例如：

```text
Robot deployment volume
Inference cost
Training data scale
VLA benchmark
Commercial contracts
Hiring signals
```

---

# 23. Human Review

AI 不应该自动成为最终决策者。

专业用户可以：

* Approve Claim
* Reject Claim
* Edit Finding
* Change Evidence Status
* Add Analyst Note
* Challenge Thesis
* Request More Research
* Approve Brief

所有操作留下记录。

---

# 24. Living Brief

最终输出不是“一次性的 PDF”。

而是：

> **Living Research Brief**

结构：

### Executive Summary

核心结论。

### Current Thesis

当前研究观点。

### Key Findings

主要 Findings。

### Industry Landscape

行业研究。

### Competitive Landscape

竞争格局。

### Technology Landscape

技术分析。

### Evidence

主要证据。

### Counter Evidence

反方证据。

### Risks

主要风险。

### Catalysts

催化因素。

### Open Questions

仍未解决的问题。

### Analyst Notes

人工判断。

---

# 25. Versioning

每次研究更新生成新版本。

例如：

```text
V1 — Aug 12
V2 — Aug 20
V3 — Aug 30
```

支持：

### What Changed

系统总结：

> 自上个版本以来发生了什么？

### Version Diff

对比：

* Thesis Changed
* Evidence Added
* Evidence Removed
* Risk Changed
* Confidence Changed

---

# 26. Research Library

管理所有研究资料：

* Uploaded Files
* Reports
* Papers
* Company Documents
* Evidence
* Saved Sources

支持：

* Search
* Filter
* Tag
* Company
* Industry
* Source Type

---

# 27. P0 功能清单

最终 P0 可以冻结成：

| 模块                    | P0   |
| --------------------- | ---- |
| Today                 | ✅    |
| New Research          | ✅    |
| Research Planner      | ✅    |
| Deep Research UX      | ✅    |
| Research Findings     | ✅    |
| Evidence Intelligence | ✅    |
| Company Research      | ✅    |
| Thesis Workspace      | ✅    |
| Risk / Catalyst       | ✅    |
| Counter Evidence      | ✅    |
| Human Review          | ✅    |
| Living Brief          | ✅    |
| Versioning            | ✅    |
| Library               | 基础版  |
| Continuous Monitoring | ❌ P1 |
| Portfolio             | ❌    |
| 自动交易                  | ❌    |
| 自动买卖建议                | ❌    |

---

# 28. P1

产品成立以后增加：

### Continuous Monitoring

自动监控：

* Company
* Industry
* Technology
* Papers
* Hiring
* Products
* Funding

### Thesis Change Detection

发现：

> 新证据是否影响原有 Thesis？

### Research Memory

跨 Research Case 复用历史知识。

### Watchlist

持续跟踪公司和技术。

### Signal Feed

例如：

> Figure 发布新技术

系统判断：

```text
Material to Thesis
```

还是：

```text
Low Importance
```

### Collaboration

* Team Workspace
* Reviewer
* Comments
* Permissions

---

# 29. P0 明确不做

这一部分必须冻结，否则范围会不断膨胀。

不做：

* K 线交易终端
* 股票实时行情系统
* Portfolio Management
* 自动交易
* 买入 / 卖出
* 自动目标价
* 全市场 Screening
* Bloomberg 替代
* 十几个互相聊天的 Agent
* 全自动黑箱 Research
* 复杂权限系统
* Kubernetes
* Temporal

---

# 30. 设计原则

## 30.1 AI-native

AI 应该嵌入：

* Research
* Evidence
* Thesis
* Review

而不是右下角放一个 Chat Bot。

---

## 30.2 Evidence-first

所有重要结论：

> 必须能回到 Evidence。

没有 Evidence：

> Needs Review。

---

## 30.3 Human-controllable

用户永远知道：

* AI 正在做什么
* 为什么这么判断
* 用了什么来源
* 哪里不确定
* 怎么修改

---

## 30.4 High Information Density

参考：

**Rogo / Linear / Ramp / Vercel**

视觉关键词：

> Professional · Dense · Calm · Precise · Premium

避免：

* 大面积渐变
* Glassmorphism
* 巨型圆角卡片
* Dashboard 模板感
* ChatGPT Clone

---

# 31. 前端技术栈

### Core

**Next.js 16 · React 19 · TypeScript · Tailwind CSS 4**

### Design System

**Radix UI Primitives · CVA · 自研 Design Tokens**

### State

**TanStack Query · Zustand**

### Tables

**TanStack Table · TanStack Virtual**

### Editor

**Tiptap**

### Research Graph

**React Flow**

### Charts

**Visx · Recharts**

### Documents

**PDF.js / react-pdf**

### Animation

**Motion / Framer Motion**

### Mock

**MSW**

### Testing

**Vitest · React Testing Library · Playwright**

### Development

**Storybook · Biome · pnpm**

---

# 32. 第一阶段开发目标

第一阶段完全 **Frontend First**。

全部使用 Mock Data。

需要达到：

> 即使后端一行代码都没有，产品已经可以完整演示。

第一阶段 Demo：

### Demo 1

> 未来三年具身智能产业最大的价值池在哪里？

### Demo 2

> Figure 与 Tesla Optimus 的技术路线和商业化路径有什么差异？

### Demo 3

> Agent Infrastructure 哪些环节最可能形成平台型公司？

完整展示：

```text
New Research
→ Plan
→ Streaming Research
→ Findings
→ Evidence
→ Counter Evidence
→ Thesis
→ Human Review
→ Living Brief
```

---

# 33. 产品成功标准

P0 成功不是：

> 做了多少页面。

而是测试一个完全不了解系统的人，能不能在 Demo 后马上理解：

### 第一

> AI 不只是帮我搜资料，它真的在帮我做研究。

### 第二

> 我能看到每个重要结论从哪里来。

### 第三

> AI 会主动找反证，而不是顺着自己的观点编故事。

### 第四

> 我可以修改和接管研究过程。

### 第五

> Research 是持续演进的，不是一篇生成后就废弃的报告。

如果这五件事能通过产品界面直接感知，这个产品的 P0 就成立了。
