"""Tests for PDF parser module."""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure the backend src is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.doc_processor.pdf_parser import PageData, PdfDocument, parse_pdf


def test_pagedata_creation():
    """PageData should store page info correctly."""
    page = PageData(page_number=1, text="Hello world", num_chars=11)
    assert page.page_number == 1
    assert page.text == "Hello world"
    assert page.num_chars == 11


def test_pdfdocument_empty():
    """A PdfDocument with no pages should return empty text."""
    doc = PdfDocument(path="/fake/path.pdf", total_pages=0)
    assert doc.full_text == ""
    assert doc.plain_text == ""
    assert doc.get_page(1) is None


def test_pdfdocument_with_pages():
    """Full text and plain text properties."""
    doc = PdfDocument(
        path="/fake/path.pdf",
        total_pages=2,
        pages=[
            PageData(page_number=1, text="Page one content", num_chars=17),
            PageData(page_number=2, text="Page two content", num_chars=17),
        ],
    )
    expected_full = "[Page 1]\nPage one content\n\n[Page 2]\nPage two content"
    assert doc.full_text == expected_full
    assert doc.plain_text == "Page one content\n\nPage two content"


def test_pdfdocument_get_page():
    """get_page should return the correct page or None."""
    doc = PdfDocument(
        path="/fake/path.pdf",
        total_pages=2,
        pages=[
            PageData(page_number=1, text="Page 1"),
            PageData(page_number=2, text="Page 2"),
        ],
    )
    assert doc.get_page(1).text == "Page 1"
    assert doc.get_page(2).text == "Page 2"
    assert doc.get_page(3) is None


def test_parse_pdf_file_not_found():
    """parse_pdf should raise FileNotFoundError for missing files."""
    try:
        parse_pdf("/nonexistent/file.pdf")
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


@patch("app.doc_processor.pdf_parser.Path.exists", return_value=True)
def test_parse_pdf_success(mock_exists):
    """parse_pdf should correctly extract text from mock PDF pages."""
    from pdfplumber.pdf import PDF
    # Small valid PDF as bytes
    minimal_pdf = (
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
        b"xref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n"
        b"0000000058 00000 n \n0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    )

    with patch("pdfplumber.open") as mock_open:
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 text\nline 2"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 text"

        mock_pdf = MagicMock(spec=PDF)
        mock_pdf.pages = [mock_page1, mock_page2]
        mock_pdf.__enter__.return_value = mock_pdf
        mock_open.return_value = mock_pdf

        doc = parse_pdf("/fake/doc.pdf")
        assert doc.total_pages == 2
        assert doc.pages[0].page_number == 1
        assert doc.pages[0].text == "Page 1 text\nline 2"
        assert doc.pages[0].num_chars == 18
        assert doc.pages[1].page_number == 2
        assert doc.pages[1].text == "Page 2 text"
