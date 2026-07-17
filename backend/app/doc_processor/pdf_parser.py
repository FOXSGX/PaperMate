from __future__ import annotations

from pathlib import Path


def parse_pdf(path: str | Path) -> str:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("pdfplumber is required to parse PDF files.") from exc

    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {index}]\n{text.strip()}")
    return "\n\n".join(pages).strip()
