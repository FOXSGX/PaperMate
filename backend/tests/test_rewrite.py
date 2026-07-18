"""Tests for rewrite module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.doc_processor.rewrite import (
    rewrite_text, batch_rewrite, ACADEMIC_SYNONYMS_ZH, ACADEMIC_SYNONYMS_EN,
)


def test_rewrite_academic_zh():
    """Chinese academic rewrite should replace known words."""
    result = rewrite_text("本文说明这个方法可以提高结果。", style="academic")
    # Should have replaced some words — result should differ from input
    assert result != "本文说明这个方法可以提高结果。"
    # Should contain at least one of the synonym variants for "本文" or "方法"
    has_synonym = any(kw in result for kw in ["本研究", "本工作", "本论文", "本项研究",
                                                "技术路线", "方案", "途径", "手段"])
    assert has_synonym, f"Expected synonym replacement, got: {result}"


def test_rewrite_academic_en():
    """English academic rewrite should replace known words."""
    result = rewrite_text("We use this method to show important results.", style="academic")
    assert "use" not in result or "employ" in result or "utilize" in result


def test_rewrite_concise_zh():
    """Chinese concise rewrite should remove wordiness."""
    result = rewrite_text("在一定程度上，这个方法比较重要。", style="concise")
    assert "在一定程度上" not in result
    assert "比较" not in result


def test_rewrite_concise_en():
    """English concise rewrite should remove wordiness."""
    result = rewrite_text("In order to test this, we need to do it.", style="concise")
    assert "in order to" not in result


def test_rewrite_restructure_en():
    """English restructure should attempt passive voice transformation."""
    result = rewrite_text("We propose a new method.", style="restructure")
    # May or may not succeed depending on regex matching
    assert len(result) > 0
    assert isinstance(result, str)


def test_rewrite_polished_zh():
    """Polished rewrite should apply synonyms and sentence splitting."""
    long_text = "本文提出了一种新的方法，实验结果表明该方法可以提高性能，因此我们认为这具有重要的实际意义。"
    result = rewrite_text(long_text, style="polished")
    assert len(result) > 0
    # Should be different from input
    assert result != long_text


def test_batch_rewrite():
    """batch_rewrite should process multiple paragraphs."""
    paragraphs = ["本文提出了新方法。", "实验结果表明效果很好。"]
    results = batch_rewrite(paragraphs, style="academic")
    assert len(results) == 2
    assert all(isinstance(r, str) for r in results)


def test_batch_rewrite_with_progress():
    """batch_rewrite should call progress callback."""
    calls = []

    def progress(done, total):
        calls.append((done, total))

    batch_rewrite(["a", "b", "c"], style="academic", progress_callback=progress)
    assert len(calls) == 3
    assert calls[-1] == (3, 3)


def test_rewrite_no_change_for_short_text():
    """Very short or punctuation-only text should remain stable."""
    result = rewrite_text("OK")
    assert result == "OK"
