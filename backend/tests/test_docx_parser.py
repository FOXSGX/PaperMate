"""Tests for DOCX parser module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.doc_processor.docx_parser import ParagraphData, DocxDocument, heading_tree


def test_paragraphdata_creation():
    """ParagraphData should store paragraph info correctly."""
    p = ParagraphData(
        text="Introduction",
        style_name="Heading 1",
        heading_level=1,
    )
    assert p.text == "Introduction"
    assert p.heading_level == 1
    assert p.is_list_item is False
    assert p.list_level == -1


def test_docxdocument_empty():
    """Empty document should return empty text."""
    doc = DocxDocument(path="/fake/doc.docx")
    assert doc.full_text == ""
    assert doc.plain_text == ""
    assert doc.headings == []


def test_docxdocument_with_content():
    """Full text with heading markers."""
    doc = DocxDocument(
        path="/fake/doc.docx",
        paragraphs=[
            ParagraphData(text="# Introduction", style_name="Heading 1", heading_level=1),
            ParagraphData(text="Some intro text.", style_name="Normal", heading_level=0),
            ParagraphData(text="Background", style_name="Heading 2", heading_level=2),
            ParagraphData(text="More text.", style_name="Normal", heading_level=0),
        ],
    )
    expected = "# # Introduction\n\nSome intro text.\n\n## Background\n\nMore text."
    assert doc.full_text == expected


def test_docxdocument_plain_text():
    """Plain text should not include markers."""
    doc = DocxDocument(
        path="/fake/doc.docx",
        paragraphs=[
            ParagraphData(text="Intro", style_name="Heading 1", heading_level=1),
            ParagraphData(text="Body", style_name="Normal", heading_level=0),
        ],
    )
    assert doc.plain_text == "Intro\n\nBody"


def test_docxdocument_headings_property():
    """headings should return only heading paragraphs."""
    doc = DocxDocument(
        path="/fake/doc.docx",
        paragraphs=[
            ParagraphData(text="1", style_name="Heading 1", heading_level=1),
            ParagraphData(text="body", style_name="Normal", heading_level=0),
            ParagraphData(text="2", style_name="Heading 2", heading_level=2),
        ],
    )
    assert len(doc.headings) == 2
    assert doc.headings[0].text == "1"
    assert doc.headings[1].text == "2"


def test_heading_tree():
    """heading_tree should build nested structure."""
    doc = DocxDocument(
        path="/fake/doc.docx",
        paragraphs=[
            ParagraphData(text="Intro", style_name="Heading 1", heading_level=1),
            ParagraphData(text="Background", style_name="Heading 2", heading_level=2),
            ParagraphData(text="Related Work", style_name="Heading 2", heading_level=2),
            ParagraphData(text="Method", style_name="Heading 1", heading_level=1),
            ParagraphData(text="Data", style_name="Heading 2", heading_level=2),
        ],
    )
    tree = heading_tree(doc)
    assert len(tree) == 2  # Two top-level headings
    assert tree[0]["text"] == "Intro"
    assert tree[0]["level"] == 1
    assert len(tree[0]["children"]) == 2
    assert tree[0]["children"][0]["text"] == "Background"
    assert tree[0]["children"][1]["text"] == "Related Work"

    assert tree[1]["text"] == "Method"
    assert len(tree[1]["children"]) == 1
    assert tree[1]["children"][0]["text"] == "Data"


def test_get_section_text():
    """get_section_text should extract heading + body until next same-level heading."""
    doc = DocxDocument(
        path="/fake/doc.docx",
        paragraphs=[
            ParagraphData(text="Intro", style_name="Heading 1", heading_level=1),
            ParagraphData(text="First para", style_name="Normal", heading_level=0),
            ParagraphData(text="Second para", style_name="Normal", heading_level=0),
            ParagraphData(text="Method", style_name="Heading 1", heading_level=1),
            ParagraphData(text="Method body", style_name="Normal", heading_level=0),
        ],
    )
    section = doc.get_section_text(0)
    assert "Intro" in section
    assert "First para" in section
    assert "Second para" in section
    assert "Method" not in section
    assert "Method body" not in section
