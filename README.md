# Enterprise Intelligence Workspace

企业智能分析工作空间 - 一个基于 AI 的数据分析产品。

## 项目架构

```
enterprise-intelligence-platform/
├── frontend/                    # React 19 前端
│   └── data-ananlysis-demo/
│       ├── src/
│       │   ├── api/           # API 客户端层
│       │   ├── components/    # 通用组件
│       │   ├── data/          # Mock 数据
│       │   ├── pages/         # 页面组件
│       │   ├── store/         # React Context 状态管理
│       │   └── types/         # TypeScript 类型定义
│       └── vite.config.ts     # Vite 配置（含 API 代理）
│
└── backend/                    # FastAPI 后端
    └── enterprise-data-agent/
        ├── src/eiw/
        │   ├── app.py         # FastAPI 应用入口
        │   ├── workspace/     # 工作空间核心逻辑
        │   ├── persistence/   # 数据持久化
        │   ├── domain/        # 领域模型
        │   └── semantic/       # 语义包
        └── tests/             # 测试套件
```

## 快速启动

### 1. 后端启动

```bash
cd backend/enterprise-data-agent

# 创建虚拟环境（如需要）
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
pip install -e ".[dev]"

# 启动服务器
uvicorn eiw.app:app --reload --host 0.0.0.0 --port 8000
```

后端运行在 `http://localhost:8000`，API 文档访问 `http://localhost:8000/docs`。

### 2. 前端启动

```bash
cd frontend/data-ananlysis-demo

# 安装依赖
npm install

# 开发模式启动
npm run dev
```

前端运行在 `http://localhost:5173`，Vite 配置了代理将 `/api/*` 请求转发到后端。

### 3. 构建生产版本

```bash
# 前端构建
cd frontend/data-ananlysis-demo
npm run build

# 后端使用
cd backend/enterprise-data-agent
uvicorn eiw.app:app --host 0.0.0.0 --port 8000
```

## 前后端通信

### API 代理配置

Vite 开发服务器配置了代理：

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

所有 `/api/v1/*` 请求会被转发到 FastAPI 后端。

### API 端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| GET | `/api/v1/home` | 首页数据 |
| GET | `/api/v1/data/status` | 数据集状态 |
| GET | `/api/v1/analysis-tasks` | 分析任务列表 |
| POST | `/api/v1/analysis-tasks` | 创建分析任务 |
| GET | `/api/v1/analysis-tasks/{id}` | 获取任务详情 |
| GET | `/api/v1/analysis-tasks/{id}/plan` | 获取分析计划 |
| GET | `/api/v1/analysis-tasks/{id}/investigation` | 获取调查结果 |
| GET | `/api/v1/analysis-tasks/{id}/claims` | 获取结论 |
| GET | `/api/v1/analysis-tasks/{id}/evidence` | 获取证据 |
| POST | `/api/v1/analysis-tasks/{id}/follow-ups` | 创建追问 |
| POST | `/api/v1/analysis-tasks/{id}/cancel` | 取消任务 |
| GET | `/api/v1/evaluation` | 评测数据 |
| POST | `/api/v1/evaluation/run` | 运行评测 |

### API Client 使用

```typescript
import { api } from '@/api';

// 获取首页数据
const homeData = await api.fetchHomeData();

// 创建分析任务
const task = await api.createAnalysisTask({
  question: "为什么 7 月销售额下降？"
});

// 获取任务详情
const taskDetail = await api.fetchAnalysisTask(task.id);

// 创建追问
const followUp = await api.createFollowUp(task.id, {
  question: "哪些供应商贡献最大？"
});
```

## 页面说明

| 页面 | 路由 | 功能 |
|------|------|------|
| Today | `/today` | 首页 - 发起新的分析 |
| Analyses | `/analyses` | 历史分析列表 |
| AnalysisWorkspace | `/analyses/:id` | 分析工作空间 |
| DataPage | `/data` | 数据集信息 |
| MetricsPage | `/metrics` | 指标配置 |
| EvaluationPage | `/evaluation` | AI 评测 |
| SettingsPage | `/settings` | 设置 |

## 环境变量

### 前端 (.env)

```bash
VITE_API_BASE_URL=/api/v1
```

### 后端 (.env)

```bash
EIW_DATA_ROOT=data/curated
EIW_MODEL_PROVIDER=deterministic
OPENAI_API_KEY=your-api-key  # 可选，用于 AI 分析
```

## 数据集

使用 Iowa Liquor Sales 数据集（爱荷华州酒类批发销售数据）。

- **快照 ID**: `iowa_liquor_snapshot_2026_07_v1`
- **时间范围**: 2012-01-01 至 2026-07-31
- **数据格式**: Parquet

## 开发说明

### 类型定义

前端使用 TypeScript，所有 API 类型定义在 `src/types/api.ts`：

```typescript
import type {
  Analysis,
  HomeData,
  DataStatus,
  EvaluationData,
} from '@/types/api';
```

### 状态管理

使用 React Context (`src/store/AppContext.tsx`) 管理全局状态：

- `analyses`: 分析任务列表
- `activeAnalysisId`: 当前活动任务 ID
- `createAnalysis()`: 创建新分析
- `appendFollowUp()`: 添加追问

### 错误处理

API 层使用 `ApiClientError` 处理错误：

```typescript
import { ApiClientError } from '@/api';

try {
  const data = await api.fetchHomeData();
} catch (err) {
  if (err instanceof ApiClientError) {
    console.error(err.message, err.status);
  }
}
```

## 测试

### 前端构建测试

```bash
cd frontend/data-ananlysis-demo
npm run build
```

### 后端单元测试

```bash
cd backend/enterprise-data-agent
source .venv/bin/activate
python -m pytest tests/ -v
```

## 技术栈

### 前端
- React 19
- TypeScript 5
- Vite 8
- Tailwind CSS 4
- React Router 7
- Recharts（图表）

### 后端
- Python 3.12+
- FastAPI
- Pydantic 2
- DuckDB（数据分析）
- SQLAlchemy（持久化）
- Alembic（数据库迁移）

## 许可证

Apache-2.0
