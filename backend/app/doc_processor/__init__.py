"""Document parsing and formatting logic.

Modules
-------
pdf_parser
    PDF text extraction with page-level metadata.
docx_parser
    DOCX text extraction with heading hierarchy preservation.
styles
    Academic formatting style profiles (GB/T 7713, IEEE, generic).
format_engine
    Apply style profiles to DOCX files (font, spacing, margins, etc.).
rewrite
    Academic text rewriting strategies (synonym, concise, restructure, polished).
"""

from .pdf_parser import PdfDocument, PageData, parse_pdf, iter_pages
from .docx_parser import DocxDocument, ParagraphData, parse_docx, heading_tree
from .styles import StyleProfile, FontSpec, HeadingSpec, PageMargins, \
    get_style, list_styles, register_style, GB7713, GENERIC, IEEE
from .format_engine import format_docx, auto_detect_style
from .rewrite import rewrite_text, batch_rewrite

__all__ = [
    # PDF
    "PdfDocument", "PageData", "parse_pdf", "iter_pages",
    # DOCX
    "DocxDocument", "ParagraphData", "parse_docx", "heading_tree",
    # Styles
    "StyleProfile", "FontSpec", "HeadingSpec", "PageMargins",
    "get_style", "list_styles", "register_style",
    "GB7713", "GENERIC", "IEEE",
    # Formatting
    "format_docx", "auto_detect_style",
    # Rewriting
    "rewrite_text", "batch_rewrite",
]
