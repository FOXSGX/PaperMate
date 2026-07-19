# PaperMate Backend

这是 PaperMate 的中期检查版后端实现，提供可运行的 FastAPI 服务和一组可演示 API。

默认监听 **`0.0.0.0:8000`**，与前端 Vite 开发代理（`frontend/vite.config.js` → `VITE_BACKEND_URL=http://127.0.0.1:8000`）对齐。

## 已实现能力

- `GET /health`：服务健康检查
- `POST /api/search`：arXiv 文献检索，网络不可用时自动返回演示数据
- `POST /api/survey`：综述生成，使用 SSE 流式返回
- `POST /api/upload`：上传 PDF、DOCX、TXT、MD 并建立本地文本索引
- `POST /api/upload/batch`：批量上传
- `POST /api/qa`：基于已上传文档的本地 RAG 问答
- `POST /api/qa/stream`：RAG 问答 SSE 流式返回
- `POST /api/rewrite`：学术文本改写
- `POST /api/format`：DOCX 基础格式排版并返回 `/outputs/...` 下载路径
- `GET /outputs/{file}`：排版结果静态下载

## 本地启动

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# 或: python main.py
```

启动后访问：

- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 与前端联调

| 端 | 地址 |
|----|------|
| 后端 | http://127.0.0.1:8000 |
| 前端开发 | http://localhost:5173 |
| 浏览器请求 API | 同源 `/api/*`（由 Vite 代理到 8000） |
| 排版下载 | 同源 `/outputs/*`（同样代理） |

CORS 已允许 `localhost/127.0.0.1` 的 `5173`、`4173`、`8000`。数据目录相对 `backend/` 解析，与启动工作目录无关。

## 说明

当前版本优先保证中期检查可演示：RAG 检索使用轻量本地词频相似度实现，LLM 生成部分提供规则化降级输出。后续接入 DeepSeek、Qwen 或 LangChain/ChromaDB 时，可以替换 `app/core` 下的实现而不改变 API 层。
