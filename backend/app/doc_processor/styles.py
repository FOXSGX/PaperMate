"""Academic formatting style profiles.

Each style defines font families, sizes, spacing, margins, and
heading conventions for a target publication venue or standard.

Supported profiles (extensible via dict merge):
    - ``gb7713``  : GB/T 7713-1987 (Chinese academic thesis standard)
    - ``generic`` : Sensible defaults for general academic writing
    - ``ieee``    : IEEE conference/journal format (approximation)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# ──────────────────────────────────────────────
#  Style data model
# ──────────────────────────────────────────────


@dataclass
class FontSpec:
    name: str              # Font name (e.g. "SimSun", "Times New Roman")
    size_pt: float         # Font size in points
    bold: bool = False
    italic: bool = False
    color_rgb: Optional[str] = None  # e.g. "000000"


@dataclass
class HeadingSpec:
    font: FontSpec
    before_spacing_pt: float = 6
    after_spacing_pt: float = 3
    numbering_format: str = ""        # e.g. "1.", "1.1", "第1章"
    alignment: str = "left"           # "left", "center", "right", "justify"


@dataclass
class PageMargins:
    top_mm: float = 25.4
    bottom_mm: float = 25.4
    left_mm: float = 31.7
    right_mm: float = 31.7


@dataclass
class StyleProfile:
    """Complete formatting configuration for a target venue."""

    # Required fields (no defaults) come FIRST
    name: str
    display_name: str
    body_font: FontSpec
    heading_1: HeadingSpec
    heading_2: HeadingSpec
    heading_3: HeadingSpec

    # Optional / default fields follow
    body_line_spacing: float = 1.5
    body_first_line_indent_pt: float = 21
    body_alignment: str = "justify"
    heading_4: Optional[HeadingSpec] = None
    heading_5: Optional[HeadingSpec] = None
    heading_6: Optional[HeadingSpec] = None
    abstract_label_font: Optional[FontSpec] = None
    abstract_body_font: Optional[FontSpec] = None
    keyword_font: Optional[FontSpec] = None
    reference_font: Optional[FontSpec] = None
    reference_line_spacing: float = 1.0
    page_margins: PageMargins = field(default_factory=PageMargins)
    header_font: Optional[FontSpec] = None
    footer_font: Optional[FontSpec] = None
    header_text: str = ""
    footer_text: str = ""

    def heading_for_level(self, level: int) -> HeadingSpec:
        """Return the HeadingSpec for a given heading level (1-6)."""
        mapping = {
            1: self.heading_1,
            2: self.heading_2,
            3: self.heading_3,
            4: self.heading_4,
            5: self.heading_5,
            6: self.heading_6,
        }
        spec = mapping.get(level)
        if spec is None:
            raise ValueError(f"Heading level {level} is not defined in profile '{self.name}'")
        return spec


# ──────────────────────────────────────────────
#  Built-in profiles
# ──────────────────────────────────────────────


# Chinese academic thesis (GB/T 7713-1987)
GB7713 = StyleProfile(
    name="gb7713",
    display_name="GB/T 7713 中国学术论文",

    body_font=FontSpec(name="SimSun", size_pt=12),

    heading_1=HeadingSpec(
        font=FontSpec(name="SimHei", size_pt=16, bold=True),
        before_spacing_pt=12,
        after_spacing_pt=6,
        numbering_format="",
        alignment="center",
    ),
    heading_2=HeadingSpec(
        font=FontSpec(name="SimHei", size_pt=14, bold=True),
        before_spacing_pt=8,
        after_spacing_pt=4,
        numbering_format="",
        alignment="left",
    ),
    heading_3=HeadingSpec(
        font=FontSpec(name="SimHei", size_pt=12, bold=True),
        before_spacing_pt=6,
        after_spacing_pt=3,
        numbering_format="",
        alignment="left",
    ),

    body_line_spacing=1.5,
    body_first_line_indent_pt=24,
    body_alignment="justify",
    heading_4=HeadingSpec(
        font=FontSpec(name="SimHei", size_pt=12, bold=False),
        alignment="left",
    ),
    abstract_label_font=FontSpec(name="SimHei", size_pt=14, bold=True),
    abstract_body_font=FontSpec(name="SimSun", size_pt=12),
    keyword_font=FontSpec(name="SimSun", size_pt=12, italic=True),
    reference_font=FontSpec(name="SimSun", size_pt=10.5),
    reference_line_spacing=1.0,
    page_margins=PageMargins(top_mm=25.4, bottom_mm=25.4, left_mm=31.7, right_mm=31.7),
    footer_text="PaperMate formatted draft",
)


# Generic academic profile (sensible defaults)
GENERIC = StyleProfile(
    name="generic",
    display_name="通用学术格式",

    body_font=FontSpec(name="Times New Roman", size_pt=12),

    heading_1=HeadingSpec(
        font=FontSpec(name="Times New Roman", size_pt=16, bold=True),
        before_spacing_pt=12,
        after_spacing_pt=6,
        numbering_format="1.",
        alignment="left",
    ),
    heading_2=HeadingSpec(
        font=FontSpec(name="Times New Roman", size_pt=14, bold=True),
        before_spacing_pt=8,
        after_spacing_pt=4,
        numbering_format="1.1",
        alignment="left",
    ),
    heading_3=HeadingSpec(
        font=FontSpec(name="Times New Roman", size_pt=12, bold=True),
        before_spacing_pt=6,
        after_spacing_pt=3,
        numbering_format="1.1.1",
        alignment="left",
    ),

    body_line_spacing=1.5,
    body_first_line_indent_pt=0,
    body_alignment="justify",
    page_margins=PageMargins(top_mm=25.4, bottom_mm=25.4, left_mm=25.4, right_mm=25.4),
)


# IEEE-style (approximation — real IEEE templates vary by publication)
IEEE = StyleProfile(
    name="ieee",
    display_name="IEEE 格式（近似）",

    body_font=FontSpec(name="Times New Roman", size_pt=10),

    heading_1=HeadingSpec(
        font=FontSpec(name="Times New Roman", size_pt=12, bold=True),
        numbering_format="I.",
        alignment="center",
    ),
    heading_2=HeadingSpec(
        font=FontSpec(name="Times New Roman", size_pt=11, bold=True),
        numbering_format="A.",
        alignment="left",
    ),
    heading_3=HeadingSpec(
        font=FontSpec(name="Times New Roman", size_pt=10, italic=True),
        numbering_format="1)",
        alignment="left",
    ),

    body_line_spacing=1.0,
    body_first_line_indent_pt=0,
    body_alignment="justify",
    reference_font=FontSpec(name="Times New Roman", size_pt=9),
    reference_line_spacing=1.0,
    page_margins=PageMargins(top_mm=19.0, bottom_mm=25.4, left_mm=19.0, right_mm=19.0),
)


# ── Registry ──
_STYLE_REGISTRY: dict[str, StyleProfile] = {
    "gb7713": GB7713,
    "generic": GENERIC,
    "ieee": IEEE,
}


def get_style(name: str) -> StyleProfile:
    """Retrieve a style profile by name.

    Raises KeyError if the profile is not registered.
    """
    if name not in _STYLE_REGISTRY:
        available = ", ".join(sorted(_STYLE_REGISTRY))
        raise KeyError(
            f"Unknown style profile '{name}'. Available: {available}"
        )
    return _STYLE_REGISTRY[name]


def list_styles() -> list[str]:
    """Return the names of all registered style profiles."""
    return list(_STYLE_REGISTRY.keys())


def register_style(name: str, profile: StyleProfile) -> None:
    """Register a custom style profile at runtime."""
    _STYLE_REGISTRY[name] = profile
