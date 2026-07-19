from pathlib import Path
from typing import List

from app.core.config import settings
from app.core.rag_engine import RagEngine
from app.doc_processor.docx_parser import parse_docx
from app.doc_processor.pdf_parser import parse_pdf
from app.models.schemas import UploadResponse
from app.utils.file_utils import save_upload_file
from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter()
rag_engine = RagEngine(settings.index_dir)


def _extract_text(path: Path) -> str:
    """将解析器返回的结构化文档适配为 RAG 索引所需的纯文本。"""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        doc = parse_pdf(path)
        return getattr(doc, "plain_text", None) or getattr(doc, "full_text", "") or str(doc)
    if suffix == ".docx":
        doc = parse_docx(path)
        return getattr(doc, "plain_text", None) or getattr(doc, "full_text", "") or str(doc)
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")


async def _process_single_file(file: UploadFile) -> UploadResponse:
    """Process a single uploaded file: save, parse, index."""
    try:
        document_id, path, _content = await save_upload_file(
            file,
            settings.upload_dir,
            settings.max_upload_mb * 1024 * 1024,
        )
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    try:
        text = _extract_text(Path(path))
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {exc}") from exc

    if not str(text).strip():
        raise HTTPException(status_code=422, detail="No readable text was extracted from the uploaded file.")

    chunks = rag_engine.index_document(document_id=document_id, text=str(text), source=Path(path).name)
    return UploadResponse(
        document_id=document_id,
        filename=file.filename or Path(path).name,
        content_type=file.content_type or "application/octet-stream",
        chunks=chunks,
        message="File uploaded and indexed successfully.",
    )



@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    """Upload and index a single file."""
    return await _process_single_file(file)


@router.post("/upload/batch", response_model=List[UploadResponse])
async def upload_files(files: List[UploadFile] = File(...)) -> List[UploadResponse]:
    """Upload and index multiple files / a folder."""
    results: List[UploadResponse] = []
    errors: List[dict] = []

    for file in files:
        try:
            result = await _process_single_file(file)
            results.append(result)
        except HTTPException:
            raise  # re-raise fatal errors immediately
        except Exception as exc:
            errors.append({"filename": file.filename, "error": str(exc)})

    if errors:
        raise HTTPException(
            status_code=500,
            detail={"uploaded": len(results), "errors": errors},
        )

    return results
