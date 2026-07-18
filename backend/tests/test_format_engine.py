"""Tests for format engine (pure logic, no file I/O)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.doc_processor.format_engine import (
    _pt_to_emu, _mm_to_emu, _heading_number, auto_detect_style,
)


def test_pt_to_emu():
    """1 pt = 12700 EMU."""
    assert _pt_to_emu(1) == 12700
    assert _pt_to_emu(12) == 152400


def test_mm_to_emu():
    """1 mm = 36000 EMU (approx)."""
    assert _mm_to_emu(1) == 36000
    assert _mm_to_emu(25.4) == 914400


def test_heading_number_basic():
    """Simple numbering format 1. for heading level 1."""
    result = _heading_number(1, "1.", [3])
    assert result.startswith("3")


def test_heading_number_multi_level():
    """Multi-level numbering 1.1 for heading level 2."""
    result = _heading_number(2, "1.1", [2, 4])
    # First "1" in "1.1" → 2 (level 1 counter), second "1" → 4 (level 2 counter)
    assert result.startswith("2.4")


def test_heading_number_empty_format():
    """Empty numbering format returns empty string."""
    result = _heading_number(1, "", [1])
    assert result == ""


def test_auto_detect_gb7713():
    """Chinese-heavy text should suggest gb7713."""
    text = "本文研究了一种基于深度学习的图像识别方法，实验结果表明该方法具有较好的性能。"
    assert auto_detect_style(text) == "gb7713"


def test_auto_detect_generic():
    """English text without IEEE keywords should suggest generic."""
    text = "We propose a novel method for image segmentation using deep learning."
    assert auto_detect_style(text) == "generic"


def test_auto_detect_ieee():
    """Text with IEEE keywords should suggest ieee."""
    text = "Abstract—This paper presents a novel approach. Index Terms—deep learning, CNN"
    assert auto_detect_style(text) == "ieee"


def test_auto_detect_ieee_lowercase():
    """IEEE detection should be case-insensitive."""
    text = "abstract—what we do. ieee conference paper using deep learning"
    assert auto_detect_style(text) == "ieee"
