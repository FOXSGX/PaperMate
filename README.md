<p align="center">
  <img src="https://img.shields.io/badge/status-MVP%20Draft-orange?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/vue-3-4FC08D?style=flat-square&logo=vue.js" alt="Vue 3"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"/>
</p>

<h1 align="center">📄 PaperMate</h1>

<p align="center">
  <strong>基于 LLM + RAG 的智能学术写作辅助工具</strong>
</p>

<p align="center">
  以 AI 驱动学术写作全流程——文献调研从数天缩短到分钟，格式排版一键完成。
</p>

<br/>

---

## 📋 目录

- [项目简介](#-项目简介)
- [当前版本说明](#-当前版本说明)
- [核心功能](#-核心功能)
- [技术栈](#-技术栈)
- [项目目录结构](#-项目目录结构)
- [API 接口说明](#-api-接口说明)
- [快速启动指南](#-快速启动指南)
- [团队分工](#-团队分工)
- [四人后续任务分工](#-四人后续任务分工)
- [开发状态与路线图](#-开发状态与路线图)
- [已知限制](#-已知限制)
- [程序缺点与改进建议](#-程序缺点与改进建议)
- [联系我们](#-联系我们)

---

## 🎯 项目简介

**PaperMate** 是一款面向科研人员和高校学生的学术写作辅助工具。针对学术写作中文献检索耗时、排版繁琐、重复率控制困难等痛点，PaperMate 基于大语言模型（LLM）与检索增强生成（RAG）技术，提供以下核心能力：

- **文献综述辅助生成** — 输入主题，自动检索 arXiv 并生成结构化综述初稿
- **文档智能问答** — 上传论文，用自然语言提问，系统基于文档片段给出带来源引用的回答
- **格式一键排版** — 按 GB/T 7713、通用/期刊模板等调整 Word 文档格式
- **智能降重改写** — 规则引擎同义改写，降低表面重复率（LLM 深度改写待接入）

> **参赛信息**：2026年EL大赛 · AI智能体创新专项组  
> **仓库**：[FOXSGX/PaperMate](https://github.com/FOXSGX/PaperMate)

---

## 📌 当前版本说明

本仓库为**可运行的中期初稿 / MVP**，前后端主流程已打通，可用于演示与联调。实现策略是「先可演示、后可替换」：

| 模块 | 当前实现 | 后续目标 |
|------|----------|----------|
| 文献检索 | arXiv API 直连；失败时返回内置演示论文 | 多源检索、结果缓存与排序 |
| 综述生成 | 基于检索结果的结构化模板 + SSE 流式输出 | 接入真实 LLM 深度撰写 |
| 文档解析 | pdfplumber / python-docx 抽取文本 | 表格、公式、图表元数据 |
| RAG 检索 | 本地 JSON 切片 + 词频余弦相似度 | LangChain + 向量库（如 ChromaDB） |
| 问答生成 | 基于检索片段的规则化综合回答 | DeepSeek / Qwen 等 LLM 生成 |
| 格式排版 | DOCX 样式引擎（字体/行距/标题编号/页边距等） | 更多期刊模板、参考文献重排 |
| 降重改写 | 中英文学术语典 + 规则改写 | LLM paraphrase + 人工对照审阅 |
| 部署 | 本地双端启动；Docker Compose 提供前后端开发编排 | 生产镜像、健康检查与持久化配置 |

> 未配置 `LLM_API_KEY` 时，服务仍可启动并完成演示链路；接入真实大模型后，主要替换 `backend/app/core/` 下实现，API 层尽量保持稳定。

---

## ✨ 核心功能

### 1️⃣ 文献综述辅助

输入研究主题，系统检索 arXiv 相关论文元数据，并按固定大纲组织生成综述初稿（SSE 流式返回）。

```
输入： "Vision Transformer 在医学图像分割中的应用"
        │
        ▼
    ┌─────────────────────────────────────────────┐
    │  🔍 arXiv 检索     →   获取相关论文元数据      │
    │  📝 模板化组织     →   背景 / 代表文献 / 方法   │
    │  📡 SSE 流式输出   →   前端逐段展示             │
    └─────────────────────────────────────────────┘
        │
        ▼
输出： 可复制的 Markdown 风格综述初稿
```

### 2️⃣ 文档上传与 RAG 智能问答

支持上传 **PDF / DOCX / TXT / MD**（单文件或批量/文件夹），后端解析文本后切块建立本地索引。用户用自然语言提问，系统检索最相关片段并返回答案与引用。

- 上传：`POST /api/upload`、`POST /api/upload/batch`
- 问答：`POST /api/qa`（一次性）、`POST /api/qa/stream`（SSE）
- 前端：上传页可一键跳转问答页并携带 `document_id`

### 3️⃣ 格式自动排版

上传 **DOCX** 后，选择模板一键排版并下载：

| 能力 | 说明 |
|------|------|
| 字体字号 | 按模板统一正文/标题字体（含中文字体 fallback） |
| 行距与缩进 | 行距、首行缩进、对齐方式 |
| 标题编号 | 自动生成多级编号（如 1、1.1、1.1.1） |
| 页边距 / 页眉页脚 | 按样式配置写入 |
| 预置模板 | `gb7713`、`generic`、`ieee` 等（前端目前主推 GB/T 7713 与期刊类） |

### 4️⃣ 降重 / 改写

对文本进行规则驱动的同义改写，支持风格：

| 风格 | 说明 |
|------|------|
| `academic` | 学术同义词替换（默认） |
| `concise` | 删除冗余、精简表达 |
| `polished` | 词汇升级 + 句式变换 |
| `restructure` | 主动↔被动、长句拆分等（后端支持） |

当前为**规则引擎**实现，便于离线演示；LLM 深度改写与逐句对照审阅见 `backend/docs/research/rewrite_feasibility_report.md`。

---

## 🛠 技术栈

### 后端（已落地依赖）

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 运行时 |
| FastAPI + Uvicorn | REST API + SSE |
| Pydantic Settings | 配置与环境变量 |
| pdfplumber | PDF 文本提取 |
| python-docx | Word 读写与排版 |
| pytest / httpx | 单元与接口测试 |
| arXiv API（stdlib） | 文献检索 |

### 前端（已落地依赖）

| 技术 | 用途 |
|------|------|
| Vue 3（Composition API） | 前端框架 |
| Vue Router 4 | 路由（在 `main.js` 内联配置） |
| Vite 6 | 开发与构建 |
| TailwindCSS 3 | 样式 |
| Axios | HTTP 请求 |
| Fetch + ReadableStream | SSE 流式消费 |

### 规划中 / 配置预留

| 技术 | 用途 | 状态 |
|------|------|------|
| DeepSeek / Qwen API | 大模型推理 | `.env` 已预留，业务层待接入 |
| LangChain | RAG 编排 | 目标架构，当前未依赖 |
| ChromaDB | 向量存储 | 配置项已预留目录，当前用本地 JSON 索引 |
| Docker Compose | 容器化 | 已提供前后端开发编排，生产化待完善 |

---

## 📁 项目目录结构

```
PaperMate/
├── backend/                         # 后端服务
│   ├── app/
│   │   ├── api/                     # API 路由
│   │   │   ├── search.py            # 文献检索 + 综述 SSE
│   │   │   ├── qa.py                # RAG 问答（同步 / SSE）
│   │   │   ├── upload.py            # 单文件 / 批量上传与索引
│   │   │   └── format.py            # 排版 & 降重
│   │   ├── core/                    # AI / 检索核心（可替换层）
│   │   │   ├── config.py            # 配置
│   │   │   ├── arxiv_search.py      # arXiv 检索与降级数据
│   │   │   ├── survey_gen.py        # 综述生成
│   │   │   └── rag_engine.py        # 切片索引 + 词频检索问答
│   │   ├── doc_processor/           # 文档处理（角色 C）
│   │   │   ├── pdf_parser.py
│   │   │   ├── docx_parser.py
│   │   │   ├── styles.py
│   │   │   ├── format_engine.py
│   │   │   └── rewrite.py
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic 模型
│   │   └── utils/
│   │       └── file_utils.py
│   ├── data/
│   │   ├── uploads/                 # 上传文件
│   │   ├── indexes/                 # 本地文本索引 JSON
│   │   └── outputs/                 # 排版输出
│   ├── docs/
│   │   ├── doc_processor_tech_spec.md
│   │   └── research/rewrite_feasibility_report.md
│   ├── tests/                       # pytest 用例
│   ├── requirements.txt
│   ├── .env.example
│   ├── README.md
│   └── main.py                      # FastAPI 入口
├── frontend/                        # 前端应用
│   ├── src/
│   │   ├── components/
│   │   │   ├── NavBar.vue
│   │   │   ├── Home.vue
│   │   │   ├── Upload.vue
│   │   │   ├── Chat.vue
│   │   │   ├── Survey.vue
│   │   │   └── Format.vue
│   │   ├── api/index.js             # Axios 封装
│   │   ├── App.vue
│   │   ├── main.js                  # 入口 + 路由
│   │   └── style.css
│   ├── package.json
│   ├── vite.config.js               # 代理 /api、/outputs → :8000
│   └── index.html
├── docker-compose.yml               # 后端容器示例
└── README.md
```

---

## 🔌 API 接口说明

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 健康检查 | GET | `/health` | 服务存活 |
| 文献检索 | POST | `/api/search` | 关键词检索 arXiv |
| 综述生成 | POST | `/api/survey` | SSE 流式返回综述段落 |
| 单文件上传 | POST | `/api/upload` | 上传并建立索引 |
| 批量上传 | POST | `/api/upload/batch` | 多文件 / 文件夹 |
| 智能问答 | POST | `/api/qa` | 基于文档索引的问答 + 引用 |
| 流式问答 | POST | `/api/qa/stream` | SSE 流式问答 |
| 格式排版 | POST | `/api/format` | DOCX 排版，返回 `/outputs/...` 下载链接 |
| 降重改写 | POST | `/api/rewrite` | 文本规则改写 |
| 静态输出 | GET | `/outputs/{filename}` | 排版结果下载 |

> **SSE**：`/api/survey` 与 `/api/qa/stream` 使用 `text/event-stream`，事件体为 `data: {json}`。前端开发服务器通过 Vite 将 `/api`、`/outputs` 代理到 `http://localhost:8000`。

### 请求示例（摘要）

```bash
# 文献检索
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d '{"keyword":"retrieval augmented generation","max_results":5}'

# 降重
curl -X POST http://localhost:8000/api/rewrite \
  -H "Content-Type: application/json" \
  -d '{"text":"本文使用深度学习方法研究图像分割问题。","style":"academic"}'
```

交互式文档：启动后端后访问 `http://localhost:8000/docs`。

---

## 🚀 快速启动指南

### 环境要求

- Python 3.10+
- Node.js 18+
- （可选）Docker / Docker Compose — 当前 compose 主要覆盖后端

### 方式一：本地开发（推荐）

#### 1. 获取代码

```bash
git clone https://github.com/FOXSGX/PaperMate.git
cd PaperMate
```

#### 2. 后端

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# 可选：编辑 .env，填入 LLM_API_KEY 等

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档：http://localhost:8000/docs  
- 健康检查：http://localhost:8000/health  

运行测试：

```bash
cd backend
pytest tests/ -v
```

#### 3. 前端

```bash
cd frontend
npm install
npm run dev
```

前端默认：http://localhost:5173  

### 方式二：Docker（开发编排）

```bash
# 项目根目录
docker compose up
```

当前 `docker-compose.yml` 使用 `python:3.11-slim` 启动后端、`node:20-alpine` 启动前端开发服务器，分别映射 `8000:8000` 与 `5173:5173`。该配置适合本地联调，仍未提供生产镜像构建、健康检查、反向代理和持久化策略。

### 环境变量（`backend/.env`）

```env
LLM_API_KEY=
LLM_MODEL=deepseek-chat
CHROMA_PERSIST_DIR=./data/chroma_db
UPLOAD_DIR=./data/uploads
INDEX_DIR=./data/indexes
OUTPUT_DIR=./data/outputs
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
MAX_UPLOAD_MB=30
```

---

## 👥 团队分工

| 角色 | 职责 | 技术栈 / 范围 | 主要目录 |
|------|------|---------------|----------|
| **角色A：后端 & AI 核心** | RAG 系统、文献检索、综述生成、API 开发与核心可替换层 | Python, FastAPI,（规划）LangChain / 向量库 / LLM API | `backend/app/core/`、`backend/app/api/`、`backend/app/models/`、`backend/main.py` |
| **角色B：前端 & 应用** | 界面设计、交互逻辑、前后端对接、SSE 体验 | Vue 3, Vite, TailwindCSS, Axios, Fetch/SSE | `frontend/` |
| **角色C：文档处理** | PDF/DOCX 解析、自动排版、降重改写、相关测试与技术说明 | Python, pdfplumber, python-docx | `backend/app/doc_processor/`、`backend/docs/`、部分 `backend/tests/` |
| **角色D：项目经理** | 项目规划、Git 管理、集成联调、部署与文档撰写 | Git, Docker, 项目管理 | 根目录 `README.md`、`docker-compose.yml`、流程与里程碑 |

> **说明**：ABCD 分工为长期协作边界，后续迭代、中期检查与结题材料均按此四角色拆分任务与验收。接口契约以 `backend/app/models/schemas.py` 与 FastAPI `/docs` 为准，跨角色改动需先对齐 API。

## 📌 四人后续任务分工

| 角色 | 后续任务 | 对应缺点 |
|------|----------|----------|
| **角色A：后端 & AI 核心** | 接入真实 LLM；把综述、问答、改写从模板逻辑替换为可配置提示词；引入向量检索与更稳定的跨文档检索；扩展多源文献检索、缓存、去重和排序解释；实现鉴权、用户隔离、访问签名和速率限制等后端安全能力；补充 SSE 和异常路径接口测试 | AI 能力仍偏模板化；RAG 检索质量有限；文献检索来源单一；安全、隐私与多用户能力不足；工程化与测试覆盖仍需加强 |
| **角色B：前端 & 应用** | 补齐任务状态、失败重试和进度展示；把“综述大纲”等前端选项真正传到后端；增加文档列表、最近上传和会话管理；补前端单元测试与 E2E 测试 | 前端体验仍是演示级；综述选项未联动；工程化与测试覆盖仍需加强 |
| **角色C：文档处理** | 增强 PDF/DOCX 解析对双栏、表格、公式和扫描件的支持；完善 DOCX 参考文献、目录、图表编号和脚注排版；引入 OCR、版面分析与 CSL 样式支持；补文档处理相关测试 | 文档处理能力不完整；RAG 切片质量有限 |
| **角色D：项目经理** | 补齐前后端完整 Docker 编排与生产配置；建立 lint、format、build、test 的 CI 流程；清理仓库中的构建产物和本地生成数据；制定隐私合规、演示数据标识和发布检查清单；补用户文档、演示脚本和发布说明 | Docker 仍偏开发模式；工程化与测试覆盖仍需加强；产品定位和结果可信度需要进一步打磨 |

---

## 📊 开发状态与路线图

### 已完成（初稿 / 可演示）

- [x] 后端 FastAPI 骨架与 CORS、健康检查
- [x] arXiv 文献检索（含网络失败降级）
- [x] 综述模板生成 + SSE
- [x] 文件上传（单文件 / 批量）与本地索引
- [x] RAG 问答（词频相似度 + 引用片段，同步/流式）
- [x] PDF / DOCX / TXT / MD 文本解析链路
- [x] DOCX 格式排版引擎与样式配置
- [x] 规则化降重改写
- [x] 前端五页：首页、上传、问答、综述、排版降重
- [x] Vite 开发代理与基础 UI（Tailwind）
- [x] 文档处理模块单测与技术说明文档
- [x] Docker Compose 前后端开发编排

### 进行中 / 待完善

- [ ] 接入真实 LLM（问答、综述、深度改写）
- [ ] 向量检索替换词频 RAG（ChromaDB 等）
- [ ] 综述大纲风格与前端选项真正联动
- [ ] 参考文献自动重排与更多期刊模板
- [ ] 前后端完整 Docker 编排与生产配置
- [ ] 端到端集成测试与演示数据集
- [ ] 错误处理、进度与多文档会话体验打磨
- [ ] 用户文档与演示脚本完善

---

## ⚠️ 已知限制

1. **LLM 未强制依赖**：未配置 API Key 时，问答/综述为规则或模板输出，质量低于最终目标形态。  
2. **RAG 为轻量实现**：本地 JSON 切块 + 词频余弦，不是语义向量检索。  
3. **排版仅支持 DOCX**：PDF 可解析用于问答，但 `/api/format` 仅处理 DOCX。  
4. **降重为规则引擎**：词典规模有限，不替代专业查重/AIGC 检测结论。  
5. **Docker 仍偏开发模式**：compose 可启动前后端开发服务，但缺少生产镜像、健康检查、反向代理和持久化策略。  
6. **安全与多用户**：当前为单机演示向，无鉴权、无多租户隔离。

---

## 🔎 程序缺点与改进建议

本项目已经能完成演示链路，但从代码实现和产品完整度来看，仍存在以下不足：

### 1. AI 能力仍偏模板化

- 综述生成主要依赖固定结构组织检索结果，尚未真正调用大模型完成深度总结、对比分析和批判性归纳。
- 文档问答的回答由规则拼接生成，更多是“摘取相关片段并解释”，还不能稳定完成复杂推理、跨段综合或学术化表达。
- 降重改写依赖同义词替换和简单句式规则，改写质量不稳定，可能出现语义漂移、表达生硬或重复替换的问题。

**改进方向**：接入 DeepSeek、Qwen 等 LLM，并为综述、问答、改写分别设计提示词、引用约束和人工校验流程。

### 2. RAG 检索质量有限

- 当前索引是本地 JSON 文件，检索方式是词频余弦相似度，不能理解语义相近但字面不同的问题。
- 文档切片按固定字符长度切分，可能切断标题、表格、公式、参考文献或上下文关系。
- 引用结果只包含 chunk 文本和分数，缺少页码、章节、原文件位置等更可追溯的信息。
- 多文档问答能力较弱，用户需要依赖单个 `document_id`，还没有稳定的文档集合、会话管理和跨文档检索。

**改进方向**：引入 embedding 模型和向量数据库，按章节/段落结构切片，并在索引中保留页码、标题层级和来源文件信息。

### 3. 文献检索来源单一

- 文献检索目前只接入 arXiv，覆盖领域偏计算机、数学和物理，对医学、人文社科、中文论文等覆盖不足。
- 网络请求失败时直接返回内置演示论文，虽然方便演示，但可能让用户误以为是真实检索结果。
- 缺少检索缓存、去重、排序解释和筛选条件，难以支持严肃文献调研。

**改进方向**：增加 Semantic Scholar、Crossref、PubMed、CNKI/万方等来源或可配置检索后端，并明确区分真实结果与演示数据。

### 4. 文档处理能力不完整

- PDF 解析主要抽取文本，对扫描版 PDF、复杂双栏论文、公式、表格和图片说明支持有限。
- DOCX 排版主要处理段落、标题、字体、页边距等基础样式，参考文献格式、图表编号、目录、脚注等学术论文常见结构尚未完整覆盖。
- `/api/format` 只能处理已上传的 DOCX，不能直接将 PDF 转为可编辑文档，也不能对 Markdown/LaTeX 等格式排版。

**改进方向**：增加 OCR、版面分析、表格抽取、参考文献解析与 CSL 样式支持，并提供排版前后的差异预览。

### 5. 前端体验仍是演示级

- 上传、解析、索引和生成过程缺少细粒度状态，例如当前处理到哪一页、哪一步失败、是否可重试。
- 批量上传时后端任一文件失败可能导致整个请求失败，前端只能展示总体错误，部分成功结果不够清晰。
- 问答页需要手动输入或携带文档 ID，缺少文档列表、历史会话、最近上传文件和删除管理。
- 综述页的“综述大纲”选项目前只停留在前端状态，尚未传给后端影响生成逻辑。

**改进方向**：补充任务状态 API、文档管理页、会话历史、失败重试和更明确的进度反馈。

### 6. 工程化与测试覆盖仍需加强

- 后端已有部分 pytest，但主要集中在文档处理模块，API 层、异常路径、前后端联调和 SSE 流式接口测试还不够完整。
- 前端缺少单元测试、组件测试和 Playwright 端到端测试，难以及时发现交互回归。
- 仓库中曾出现构建产物、`node_modules`、`__pycache__` 和本地上传/索引数据，说明项目清理和发布流程还需要规范化。
- Docker Compose 虽然已包含前后端服务，但仍偏开发模式，依赖容器启动时安装，缺少生产镜像构建、健康检查和持久化策略。

**改进方向**：补齐 API/E2E 测试，建立 lint、format、build、test 的 CI 流程，并清理不应纳入仓库的本地生成文件。

### 7. 安全、隐私与多用户能力不足

- 当前没有登录、权限控制和用户隔离，所有上传文件和索引都存放在本地目录中。
- `/outputs` 直接暴露排版结果下载目录，如果部署到公网，可能产生文件枚举或越权访问风险。
- 上传文件缺少更严格的内容校验、病毒扫描、文件生命周期管理和敏感信息处理策略。
- CORS、鉴权、速率限制、审计日志等生产安全配置尚未完善。

**改进方向**：增加认证授权、按用户隔离存储、文件过期清理、访问签名、速率限制和安全审计日志。

### 8. 产品定位和结果可信度需要进一步打磨

- 当前更适合作为比赛或课程项目 MVP，用于展示“检索、上传、问答、排版、改写”的完整流程。
- 如果用于真实科研写作，仍需要加强引用准确性、生成内容可追溯性、误答提示和人工复核机制。
- “降重/去 AI 化”这类能力需要谨慎表述，避免给用户造成可以绕过学术规范或检测系统的误解。

**改进方向**：将产品定位调整为“写作辅助与审阅工具”，强化引用核验、原创性声明、学术诚信提示和人工确认流程。

---

## 📬 联系我们

- **项目主页**：[GitHub - PaperMate](https://github.com/FOXSGX/PaperMate)
- **提交 Issue**：[GitHub Issues](https://github.com/FOXSGX/PaperMate/issues)
- **比赛信息**：2026年EL大赛 · AI智能体创新专项组

---

<p align="center">
  项目仅供学习和比赛使用，部分功能依赖第三方 API 与公开学术接口。
</p>

<p align="center">
  <sub>Built with ❤️ by PaperMate Team · ABCD</sub>
</p>
