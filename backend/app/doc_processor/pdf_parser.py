"""PDF text extraction module.

Preserves page numbering and returns structured output with
page-level metadata for downstream RAG and formatting pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

import pdfplumber


@dataclass
class PageData:
    """Text content and metadata for a single PDF page."""

    page_number: int
    text: str
    num_chars: int = 0


@dataclass
class PdfDocument:
    """Structured representation of an extracted PDF document."""

    path: str
    total_pages: int
    pages: list[PageData] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        """Return concatenated text with [Page N] markers."""
        parts = []
        for page in self.pages:
            text = page.text.strip()
            if text:
                parts.append(f"[Page {page.page_number}]\n{text}")
        return "\n\n".join(parts)

    @property
    def plain_text(self) -> str:
        """Return plain concatenated text without page markers."""
        return "\n\n".join(p.text.strip() for p in self.pages if p.text.strip())

    def get_page(self, num: int) -> Optional[PageData]:
        """Retrieve a specific page by its page number (1-indexed)."""
        for page in self.pages:
            if page.page_number == num:
                return page
        return None


def parse_pdf(path: str | Path) -> PdfDocument:
    """Parse a PDF file and return structured text with page information.

    Args:
        path: Path to the PDF file.

    Returns:
        A PdfDocument containing per-page extracted text.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    doc = PdfDocument(path=str(path.resolve()), total_pages=0)

    with pdfplumber.open(path) as pdf:
        doc.total_pages = len(pdf.pages)
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            # Clean up excessive whitespace
            text_lines = [line.strip() for line in text.splitlines()]
            cleaned = "\n".join(line for line in text_lines if line)
            doc.pages.append(
                PageData(
                    page_number=index,
                    text=cleaned,
                    num_chars=len(cleaned),
                )
            )

    return doc


def iter_pages(path: str | Path) -> Iterator[PageData]:
    """Lazily iterate over PDF pages without loading the entire document.

    Useful for large PDFs where keeping all pages in memory is prohibitive.
    """
    with pdfplumber.open(path) as pdf:
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            text_lines = [line.strip() for line in text.splitlines()]
            cleaned = "\n".join(line for line in text_lines if line)
            yield PageData(page_number=index, text=cleaned, num_chars=len(cleaned))
