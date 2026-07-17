from pathlib import Path

from app.core.config import settings
from app.core.rag_engine import RagEngine
from app.doc_processor.docx_parser import parse_docx
from app.doc_processor.pdf_parser import parse_pdf
from app.models.schemas import UploadResponse
from app.utils.file_utils import save_upload_file
from fastapi import APIRouter, File, HTTPException, UploadFile


router = APIRouter()
rag_engine = RagEngine(settings.index_dir)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    try:
        document_id, path, _content = await save_upload_file(
            file,
            settings.upload_dir,
            settings.max_upload_mb * 1024 * 1024,
        )
    except ValueError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc

    suffix = Path(path).suffix.lower()
    try:
        if suffix == ".pdf":
            text = parse_pdf(path)
        elif suffix == ".docx":
            text = parse_docx(path)
        elif suffix in {".txt", ".md"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
        else:
            raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT and MD files are supported.")
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    if not text.strip():
        raise HTTPException(status_code=422, detail="No readable text was extracted from the uploaded file.")

    chunks = rag_engine.index_document(document_id=document_id, text=text, source=path.name)
    return UploadResponse(
        document_id=document_id,
        filename=file.filename or path.name,
        content_type=file.content_type or "application/octet-stream",
        chunks=chunks,
        message="File uploaded and indexed successfully.",
    )
