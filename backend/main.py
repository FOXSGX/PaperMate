from pathlib import Path

from app.api import format, qa, search, upload
from app.core.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI(
    title="PaperMate Backend",
    description="LLM + RAG powered academic writing assistant.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api", tags=["Literature"])
app.include_router(upload.router, prefix="/api", tags=["Files"])
app.include_router(qa.router, prefix="/api", tags=["RAG QA"])
app.include_router(format.router, prefix="/api", tags=["Writing"])

# 使用配置中的绝对输出目录，保证 /outputs 下载与 /api/format 返回链接一致
Path(settings.output_dir).mkdir(parents=True, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=settings.output_dir), name="outputs")


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "PaperMate Backend",
        "host": settings.server_host,
        "port": str(settings.server_port),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
    )
