"""Tests for style profiles."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from app.doc_processor.styles import (
    FontSpec, HeadingSpec, PageMargins, StyleProfile,
    get_style, list_styles, register_style, GB7713, GENERIC, IEEE,
)


def test_fontspec_creation():
    f = FontSpec(name="SimSun", size_pt=12)
    assert f.name == "SimSun"
    assert f.size_pt == 12.0
    assert f.bold is False

    f2 = FontSpec(name="SimHei", size_pt=16, bold=True)
    assert f2.bold is True


def test_heading_spec_creation():
    h = HeadingSpec(font=FontSpec("SimHei", 14, bold=True), numbering_format="1.")
    assert h.font.name == "SimHei"
    assert h.numbering_format == "1."


def test_pagemargins_defaults():
    m = PageMargins()
    assert m.top_mm == 25.4
    assert m.left_mm == 31.7


def test_get_style_known():
    """Known styles should be retrievable."""
    gb = get_style("gb7713")
    assert gb.name == "gb7713"
    assert gb.body_font.name == "SimSun"
    assert gb.heading_1.font.name == "SimHei"
    assert gb.heading_1.font.size_pt == 16.0

    gen = get_style("generic")
    assert gen.name == "generic"

    ieee = get_style("ieee")
    assert ieee.name == "ieee"


def test_get_style_unknown():
    """Unknown style should raise KeyError."""
    with pytest.raises(KeyError):
        get_style("nonexistent_style")


def test_list_styles():
    styles = list_styles()
    assert "gb7713" in styles
    assert "generic" in styles
    assert "ieee" in styles


def test_register_style():
    new = StyleProfile(
        name="test_custom",
        display_name="Test Custom Style",
        body_font=FontSpec("Arial", 11),
        body_line_spacing=1.15,
        body_first_line_indent_pt=0,
        body_alignment="left",
        heading_1=HeadingSpec(FontSpec("Arial", 14, bold=True)),
        heading_2=HeadingSpec(FontSpec("Arial", 12, bold=True)),
        heading_3=HeadingSpec(FontSpec("Arial", 11, italic=True)),
    )
    register_style("test_custom", new)
    retrieved = get_style("test_custom")
    assert retrieved.name == "test_custom"
    assert retrieved.body_font.name == "Arial"


def test_heading_for_level():
    profile = GENERIC
    h1 = profile.heading_for_level(1)
    assert h1 is not None
    assert h1.font.size_pt == 16.0

    h2 = profile.heading_for_level(2)
    assert h2 is not None

    with pytest.raises(ValueError):
        profile.heading_for_level(5)  # generic only defines 1-3
