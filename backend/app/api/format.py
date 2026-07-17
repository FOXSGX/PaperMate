from pathlib import Path

from app.core.config import settings
from app.doc_processor.format_engine import format_docx
from app.doc_processor.rewrite import rewrite_text
from app.models.schemas import FormatRequest, FormatResponse, RewriteRequest, RewriteResponse
from fastapi import APIRouter, HTTPException, Request


router = APIRouter()


@router.post("/rewrite", response_model=RewriteResponse)
def rewrite(payload: RewriteRequest) -> RewriteResponse:
    return RewriteResponse(
        original=payload.text,
        rewritten=rewrite_text(payload.text, payload.style),
        style=payload.style,
    )


@router.post("/format", response_model=FormatResponse)
def format_document(payload: FormatRequest, request: Request) -> FormatResponse:
    matches = list(Path(settings.upload_dir).glob(f"{payload.document_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Document not found. Please upload it first.")

    input_path = matches[0]
    if input_path.suffix.lower() != ".docx":
        raise HTTPException(status_code=400, detail="Formatting currently supports DOCX files only.")

    output_path = format_docx(input_path, settings.output_dir, payload.template)
    output_url = str(request.base_url).rstrip("/") + f"/outputs/{output_path.name}"
    return FormatResponse(
        document_id=payload.document_id,
        template=payload.template,
        output_url=output_url,
        message="Document formatted successfully.",
    )
