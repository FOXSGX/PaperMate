<p align="center">
  <img src="https://img.shields.io/badge/status-Developing-blue?style=flat-square" alt="Status"/>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/vue-3-4FC08D?style=flat-square&logo=vue.js" alt="Vue 3"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=flat-square&logo=fastapi" alt="FastAPI"/>
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
- [核心功能](#-核心功能)
- [技术栈](#-技术栈)
- [项目目录结构](#-项目目录结构)
- [API 接口说明](#-api-接口说明)
- [快速启动指南](#-快速启动指南)
- [团队分工](#-团队分工)
- [开发状态](#-开发状态)
- [联系我们](#-联系我们)

---

## 🎯 项目简介

**PaperMate** 是一款面向科研人员和高校学生的学术写作辅助工具。针对学术写作中文献检索耗时、排版繁琐、重复率控制困难等痛点，PaperMate 基于大语言模型（LLM）与检索增强生成（RAG）技术，提供以下核心能力：

- **文献综述自动生成** — 输入主题，自动检索 arXiv 并生成结构化综述
- **PDF 智能问答** — 上传论文，用自然语言提问，系统基于文档内容给出带来源引用的回答
- **格式一键排版** — 按 GB/T 7713、期刊模板等自动调整 Word 文档格式
- **智能降重改写** — 同义改写降低重复率与 AIGC 检测率

> **参赛信息**：2026年EL大赛 · AI智能体创新专项组

---

## ✨ 核心功能

### 1️⃣ 文献综述辅助

输入研究主题，系统自动检索 arXiv 等学术数据库，获取相关论文信息，并按大纲组织生成综述初稿，大幅缩短文献调研周期。

```
输入： "Vision Transformer 在医学图像分割中的应用"
        │
        ▼
    ┌─────────────────────────────────────────────┐
    │  🔍 arXiv 检索     →   获取相关论文元数据      │
    │  🧠 LLM 分析摘要   →   提取关键方法与贡献      │
    │  📝 按大纲组织     →   生成综述初稿             │
    └─────────────────────────────────────────────┘
        │
        ▼
输出： 带分类整理的综述文档（可继续编辑）
```

### 2️⃣ RAG 智能问答

上传 PDF 论文后，系统对文档进行切片、向量化存储。用户用自然语言提问，系统检索最相关片段并结合 LLM 生成精准回答，**每条回答附带引用来源**，方便溯源验证。

- 支持多轮对话
- 上下文感知追问
- 引用段落高亮展示

### 3️⃣ 格式自动排版

上传 Word 文档，选择目标模板，一键完成排版调整：

| 功能 | 说明 |
|------|------|
| 字体字号 | 按模板统一设置正文、标题、摘要字体 |
| 标题编号 | 自动生成多级编号（如 1、1.1、1.1.1） |
| 参考文献 | 按 GB/T 7713 或期刊格式重排引用 |
| 页眉页脚 | 自动添加 |

### 4️⃣ 降重 / 去 AI 化

对文本进行智能同义改写，在保持原意和学术严谨性的前提下：

- **降低文字重复率** — 替换高频重叠短语，调整句式结构
- **降低 AIGC 检测分** — 引入句式多样性与个性化表达，避免机器生成痕迹
- 支持批量处理与逐句对比预览

---

## 🛠 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| Python 3.10+ | 运行时 |
| FastAPI | RESTful API + SSE 流式响应 |
| LangChain | RAG 流程编排、提示词模板 |
| ChromaDB | 向量存储与语义检索 |
| DeepSeek / Qwen API | 大语言模型推理 |
| pdfplumber | PDF 文本提取 |
| python-docx | Word 文档读写与格式排版 |

### 前端

| 技术 | 用途 |
|------|------|
| Vue 3 (Composition API) | 前端框架 |
| Vite | 构建工具 |
| TailwindCSS | 样式框架 |
| Axios | HTTP 请求 |
| EventSource (SSE) | 流式响应处理 |

### 部署

| 技术 | 用途 |
|------|------|
| Docker Compose | 容器化一键部署 |

---

## 📁 项目目录结构

```
PaperMate/
├── backend/                        # 后端服务
│   ├── app/
│   │   ├── api/                    # API 路由
│   │   │   ├── search.py           # 文献检索接口
│   │   │   ├── qa.py               # RAG 问答接口
│   │   │   ├── upload.py           # 文件上传接口
│   │   │   └── format.py           # 排版 & 降重接口
│   │   ├── core/                   # AI 核心逻辑
│   │   │   ├── rag_engine.py       # RAG 检索引擎
│   │   │   ├── survey_gen.py       # 综述生成引擎
│   │   │   └── arxiv_search.py     # arXiv 检索封装
│   │   ├── doc_processor/          # 文档处理
│   │   │   ├── pdf_parser.py       # PDF 解析
│   │   │   ├── docx_parser.py      # DOCX 解析
│   │   │   ├── format_engine.py    # 格式排版引擎
│   │   │   └── rewrite.py          # 降重改写引擎
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic 数据模型
│   │   └── utils/
│   │       └── file_utils.py       # 文件工具函数
│   ├── requirements.txt
│   ├── .env.example
│   └── main.py                     # 应用入口
├── frontend/                       # 前端应用
│   ├── src/
│   │   ├── components/             # 页面组件
│   │   │   ├── Upload.vue          # 文件上传页
│   │   │   ├── Chat.vue            # RAG 问答页
│   │   │   ├── Survey.vue          # 综述生成页
│   │   │   └── Format.vue          # 排版 & 降重页
│   │   ├── api/
│   │   │   └── index.js            # Axios 请求封装
│   │   ├── router/
│   │   │   └── index.js            # Vue Router 配置
│   │   ├── App.vue                 # 根组件
│   │   └── main.js                 # 入口文件
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── docker-compose.yml              # Docker Compose 编排
└── README.md                       # 项目文档
```

---

## 🔌 API 接口说明

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| 文献检索 | POST | `/api/search` | 根据关键词检索 arXiv 论文 |
| 综述生成 | POST | `/api/survey` | 生成综述，SSE 流式返回 |
| 智能问答 | POST | `/api/qa` | RAG 问答，SSE 流式返回，含引用 |
| 文件上传 | POST | `/api/upload` | 上传 PDF / DOCX 文件 |
| 格式排版 | POST | `/api/format` | 一键排版，返回下载链接 |
| 降重改写 | POST | `/api/rewrite` | 同义改写文本 |

> **SSE 流式说明**：`/api/survey` 和 `/api/qa` 使用 Server-Sent Events（SSE）实现逐 token 流式输出，前端通过 `EventSource` 接收，实现打字机效果的实时响应。

---

## 🚀 快速启动指南

### 环境要求

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose（可选，用于容器化部署）

### 方式一：本地开发

#### 1. 克隆项目

```bash
git clone https://github.com/your-org/PaperMate.git
cd PaperMate
```

#### 2. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS / Linux
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制并修改）
cp .env.example .env
# 编辑 .env 文件，填入 LLM API Key 等配置

# 启动后端服务
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端服务启动后，访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

#### 3. 前端启动

```bash
# 新开终端，进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端开发服务器默认运行在 `http://localhost:5173`。

### 方式二：Docker 部署

```bash
# 在项目根目录执行
docker compose up -d
```

启动后：
- 前端：`http://localhost:5173`
- 后端 API：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

### 环境变量配置

在 `backend/.env` 中配置：

```env
# LLM API 配置
LLM_API_KEY=your_api_key_here
LLM_MODEL=deepseek-chat

# 向量数据库
CHROMA_PERSIST_DIR=./chroma_db

# 服务配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

---

## 👥 团队分工

| 角色 | 职责 | 技术栈 |
|------|------|--------|
| **角色A：后端 & AI 核心** | RAG 系统、文献检索、综述生成、API 开发 | Python, FastAPI, LangChain, ChromaDB, LLM API |
| **角色B：前端 & 应用** | 界面设计、交互逻辑、前后端对接 | Vue 3, Vite, TailwindCSS, Axios, SSE |
| **角色C：文档处理** | PDF/DOCX 解析、自动排版、降重改写 | Python, pdfplumber, python-docx |
| **角色D：项目经理** | 项目规划、Git 管理、集成测试、文档撰写 | Git, Docker, 项目管理 |

---

## 📊 开发状态

目前项目处于方案设计阶段，所有模块尚未开始编码实现。以下是整体规划路线图：

### 📅 待开发（按优先级排序）

- [ ] 后端项目骨架搭建（FastAPI + 项目结构初始化）
- [ ] 前端项目骨架搭建（Vue 3 + Vite + 路由配置）
- [ ] arXiv 文献检索模块
- [ ] RAG 引擎（文档切片 → 向量化 → 语义检索）
- [ ] PDF / DOCX 解析模块
- [ ] 综述生成引擎
- [ ] RAG 智能问答 API + 前端对话页面
- [ ] 格式排版引擎
- [ ] 降重改写引擎
- [ ] 前端页面开发（Upload、Chat、Survey、Format）
- [ ] Docker Compose 部署配置
- [ ] 端到端集成测试
- [ ] 用户文档完善

---

## 📬 联系我们

如有问题或建议，欢迎通过以下方式联系我们：

- **项目主页**：[GitHub - PaperMate](https://github.com/your-org/PaperMate)
- **提交 Issue**：[GitHub Issues](https://github.com/your-org/PaperMate/issues)
- **比赛信息**：2026年EL大赛 · AI智能体创新专项组

---

<p align="center">
  项目仅供学习和比赛使用，部分功能依赖第三方 API 服务。
</p>

<p align="center">
  <sub>Built with ❤️ by PaperMate Team</sub>
</p>

