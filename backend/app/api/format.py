from pathlib import Path

from app.core.config import settings
from app.doc_processor.format_engine import format_docx
from app.doc_processor.rewrite import rewrite_text
from app.models.schemas import FormatRequest, FormatResponse, RewriteRequest, RewriteResponse
from fastapi import APIRouter, HTTPException


router = APIRouter()

# 前端「期刊模板」等别名 → 后端 styles 注册名（不改主体排版逻辑）
TEMPLATE_ALIASES = {
    "journal": "generic",
    "gb/t7713": "gb7713",
    "gb_t_7713": "gb7713",
}


def _resolve_template(name: str) -> str:
    key = (name or "gb7713").strip().lower()
    return TEMPLATE_ALIASES.get(key, key)


@router.post("/rewrite", response_model=RewriteResponse)
def rewrite(payload: RewriteRequest) -> RewriteResponse:
    return RewriteResponse(
        original=payload.text,
        rewritten=rewrite_text(payload.text, payload.style),
        style=payload.style,
    )


@router.post("/format", response_model=FormatResponse)
def format_document(payload: FormatRequest) -> FormatResponse:
    matches = list(Path(settings.upload_dir).glob(f"{payload.document_id}.*"))
    if not matches:
        raise HTTPException(status_code=404, detail="Document not found. Please upload it first.")

    input_path = matches[0]
    if input_path.suffix.lower() != ".docx":
        raise HTTPException(status_code=400, detail="Formatting currently supports DOCX files only.")

    template = _resolve_template(payload.template)
    try:
        output_path = format_docx(input_path, settings.output_dir, template)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # 经 Vite 代理时前端可用相对路径 /outputs/...；直连后端时用绝对 URL
    filename = Path(output_path).name
    output_url = f"/outputs/{filename}"
    return FormatResponse(
        document_id=payload.document_id,
        template=template,
        output_url=output_url,
        message="Document formatted successfully.",
    )
