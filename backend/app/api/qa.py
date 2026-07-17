import json

from app.core.config import settings
from app.core.rag_engine import RagEngine
from app.models.schemas import Citation, QARequest, QAResponse
from fastapi import APIRouter
from fastapi.responses import StreamingResponse


router = APIRouter()
rag_engine = RagEngine(settings.index_dir)


@router.post("/qa", response_model=QAResponse)
def ask_document(payload: QARequest) -> QAResponse:
    answer, citations = rag_engine.answer(payload.document_id, payload.question, payload.top_k)
    return QAResponse(
        answer=answer,
        citations=[Citation(chunk_id=item["chunk_id"], score=item["score"], text=item["text"]) for item in citations],
    )


@router.post("/qa/stream")
def ask_document_stream(payload: QARequest) -> StreamingResponse:
    answer, citations = rag_engine.answer(payload.document_id, payload.question, payload.top_k)

    def event_stream():
        for line in answer.splitlines():
            if line.strip():
                yield f"data: {json.dumps({'content': line}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'citations': citations, 'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
