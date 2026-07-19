from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ 目录（…/backend/app/core/config.py → parents[2]）
BACKEND_ROOT = Path(__file__).resolve().parents[2]


def _resolve_dir(value: str) -> str:
    """相对路径统一落到 backend 根目录，避免工作目录不同导致前后端数据目录错位。"""
    path = Path(value)
    if not path.is_absolute():
        path = BACKEND_ROOT / path
    return str(path.resolve())


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PaperMate"
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    llm_api_key: Optional[str] = None
    llm_model: str = "deepseek-chat"
    chroma_persist_dir: str = "./data/chroma_db"
    upload_dir: str = "./data/uploads"
    index_dir: str = "./data/indexes"
    output_dir: str = "./data/outputs"
    max_upload_mb: int = 30
    # 开发前端 Vite 默认 5173；预览/直连后端时的常见来源一并放开
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:4173",
            "http://127.0.0.1:4173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]
    )

    @field_validator(
        "chroma_persist_dir",
        "upload_dir",
        "index_dir",
        "output_dir",
        mode="after",
    )
    @classmethod
    def resolve_data_dirs(cls, value: str) -> str:
        return _resolve_dir(value)

    def ensure_dirs(self) -> None:
        for directory in [self.upload_dir, self.index_dir, self.output_dir, self.chroma_persist_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    current = Settings()
    current.ensure_dirs()
    return current


settings = get_settings()
