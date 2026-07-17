from __future__ import annotations

import hashlib
import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def safe_filename(filename: str) -> str:
    cleaned = SAFE_NAME_PATTERN.sub("_", Path(filename).name).strip("._")
    return cleaned or f"upload-{uuid4().hex}"


def make_document_id(filename: str, content: bytes) -> str:
    digest = hashlib.sha1(content[:2048] + filename.encode("utf-8")).hexdigest()[:12]
    return f"doc_{digest}"


async def save_upload_file(upload: UploadFile, upload_dir: str, max_bytes: int) -> tuple[str, Path, bytes]:
    content = await upload.read()
    if len(content) > max_bytes:
        raise ValueError(f"File exceeds max size of {max_bytes // (1024 * 1024)} MB.")

    filename = safe_filename(upload.filename or "document")
    document_id = make_document_id(filename, content)
    suffix = Path(filename).suffix.lower()
    output_path = Path(upload_dir) / f"{document_id}{suffix}"
    output_path.write_bytes(content)
    return document_id, output_path, content
