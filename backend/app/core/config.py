from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

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
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"])

    def ensure_dirs(self) -> None:
        for directory in [self.upload_dir, self.index_dir, self.output_dir, self.chroma_persist_dir]:
            Path(directory).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    current = Settings()
    current.ensure_dirs()
    return current


settings = get_settings()
