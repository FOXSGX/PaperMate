from __future__ import annotations

import json
import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[\w\u4e00-\u9fff]+")


@dataclass
class Chunk:
    chunk_id: str
    text: str
    source: str


class RagEngine:
    def __init__(self, index_dir: str):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def index_document(self, document_id: str, text: str, source: str, chunk_size: int = 650, overlap: int = 120) -> int:
        chunks = self._split_text(text, chunk_size, overlap)
        payload = [asdict(Chunk(chunk_id=f"{document_id}_{index:04d}", text=chunk, source=source)) for index, chunk in enumerate(chunks)]
        self._index_path(document_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return len(payload)

    def retrieve(self, document_id: str, question: str, top_k: int = 3) -> list[dict]:
        chunks = self._load_chunks(document_id)
        query_tokens = self._tokenize(question)
        scored = []
        for chunk in chunks:
            chunk_tokens = self._tokenize(chunk["text"])
            score = self._cosine(query_tokens, chunk_tokens)
            if score > 0:
                scored.append({**chunk, "score": round(score, 4)})
        if not scored:
            scored = [{**chunk, "score": 0.0} for chunk in chunks[:top_k]]
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:top_k]

    def answer(self, document_id: str, question: str, top_k: int = 3) -> tuple[str, list[dict]]:
        citations = self.retrieve(document_id, question, top_k)
        if not citations:
            return "暂未找到该文档的索引，请先上传 PDF 或 DOCX 文件。", []

        evidence = "\n".join(f"[{index}] {item['text'][:260]}" for index, item in enumerate(citations, start=1))
        answer = (
            f"根据已上传文档中最相关的 {len(citations)} 个片段，问题“{question}”可以这样回答：\n\n"
            f"{self._synthesize(question, citations)}\n\n"
            f"参考依据：\n{evidence}"
        )
        return answer, citations

    def _index_path(self, document_id: str) -> Path:
        return self.index_dir / f"{document_id}.json"

    def _load_chunks(self, document_id: str) -> list[dict]:
        path = self._index_path(document_id)
        if not path.exists():
            return []
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
        normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
        if not normalized:
            return []
        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + chunk_size, len(normalized))
            chunks.append(normalized[start:end].strip())
            if end == len(normalized):
                break
            start = max(0, end - overlap)
        return [chunk for chunk in chunks if chunk]

    @staticmethod
    def _tokenize(text: str) -> dict[str, int]:
        tokens = [token.lower() for token in TOKEN_PATTERN.findall(text)]
        counts: dict[str, int] = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        return counts

    @staticmethod
    def _cosine(left: dict[str, int], right: dict[str, int]) -> float:
        shared = set(left) & set(right)
        numerator = sum(left[token] * right[token] for token in shared)
        left_norm = math.sqrt(sum(value * value for value in left.values()))
        right_norm = math.sqrt(sum(value * value for value in right.values()))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    @staticmethod
    def _synthesize(question: str, citations: list[dict]) -> str:
        lead = citations[0]["text"].strip().replace("\n", " ")
        if len(lead) > 360:
            lead = lead[:360] + "..."
        return f"文档证据显示，{lead} 因此，可围绕该证据对问题进行解释，并结合引用片段继续核验。"
