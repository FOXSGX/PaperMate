import json

from app.core.arxiv_search import search_arxiv
from app.core.survey_gen import stream_survey
from app.models.schemas import SearchRequest, SearchResponse, SurveyRequest
from fastapi import APIRouter
from fastapi.responses import StreamingResponse


router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_papers(payload: SearchRequest) -> SearchResponse:
    papers = search_arxiv(payload.keyword, payload.max_results)
    return SearchResponse(keyword=payload.keyword, total=len(papers), papers=papers)


@router.post("/survey")
def generate_survey(payload: SurveyRequest) -> StreamingResponse:
    def event_stream():
        for chunk in stream_survey(payload.topic, payload.max_papers, payload.outline_style):
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
