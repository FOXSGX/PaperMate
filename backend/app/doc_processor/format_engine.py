from __future__ import annotations

from pathlib import Path
from shutil import copyfile


def format_docx(input_path: str | Path, output_dir: str | Path, template: str = "gb7713") -> Path:
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}_{template}_formatted.docx"

    try:
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.shared import Pt
    except ImportError:
        copyfile(input_path, output_path)
        return output_path

    document = Document(input_path)
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        if text.startswith("#") or len(text) < 30:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(text) < 18 else WD_ALIGN_PARAGRAPH.LEFT
            for run in paragraph.runs:
                run.bold = True
                run.font.name = "SimHei"
                run.font.size = Pt(16 if len(text) < 18 else 14)
        else:
            paragraph.paragraph_format.first_line_indent = Pt(21)
            paragraph.paragraph_format.line_spacing = 1.5
            for run in paragraph.runs:
                run.font.name = "SimSun"
                run.font.size = Pt(12)

    section = document.sections[0]
    section.header.paragraphs[0].text = "PaperMate formatted draft"
    document.save(output_path)
    return output_path
