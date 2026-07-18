"""Academic text rewriting engine.

Provides multiple rewriting strategies:

- **synonym**      : Academic synonym replacement (basic, no external calls)
- **restructure**  : Sentence structure transformation (active ↔ passive,
                     long ↔ short, negation flipping)
- **polish**       : Upgrade vocabulary and sentence flow
- **concise**      : Remove wordy phrases and tighten prose

For deep rewriting (LLM-based), see the ``format.py`` API route which
calls an external LLM endpoint.
"""

from __future__ import annotations

import re
from typing import Callable


# ──────────────────────────────────────────────
#  Academic synonym dictionary (Chinese)
# ──────────────────────────────────────────────

ACADEMIC_SYNONYMS_ZH: dict[str, list[str]] = {
    "本文": ["本研究", "本工作", "本论文", "此项研究"],
    "说明": ["表明", "揭示", "显示", "证实", "反映出"],
    "很多": ["大量", "诸多", "众多", "为数众多"],
    "重要": ["关键", "至关重要", "举足轻重", "核心"],
    "使用": ["采用", "利用", "运用", "借助"],
    "方法": ["方法", "技术路线", "方案", "途径", "手段"],
    "提高": ["提升", "增强", "改善", "增进", "优化"],
    "可以": ["能够", "可", "得以", "便于"],
    "问题": ["问题", "议题", "课题", "难题", "挑战"],
    "影响": ["影响", "作用", "效应", "干扰"],
    "不同": ["不同", "差异", "差别", "各异"],
    "结果": ["结果", "结论", "成果", "发现"],
    "实验": ["实验", "试验", "测试", "实测"],
    "数据": ["数据", "资料", "数值", "指标"],
    "分析": ["分析", "解析", "剖析", "探讨"],
    "研究": ["研究", "探讨", "探究", "考察", "调研"],
    "目的": ["目的", "目标", "意图", "宗旨"],
    "过程": ["过程", "流程", "步骤", "环节"],
    "系统": ["系统", "体系", "平台", "框架"],
    "模型": ["模型", "模式", "架构", "范式"],
}

ACADEMIC_SYNONYMS_EN: dict[str, list[str]] = {
    "use": ["employ", "utilize", "leverage", "deploy"],
    "show": ["demonstrate", "reveal", "indicate", "illustrate", "exhibit"],
    "important": ["crucial", "critical", "essential", "pivotal", "significant"],
    "many": ["numerous", "substantial", "considerable", "a wealth of"],
    "method": ["approach", "methodology", "technique", "framework"],
    "result": ["finding", "outcome", "conclusion", "observation"],
    "improve": ["enhance", "optimize", "refine", "augment", "ameliorate"],
    "problem": ["challenge", "issue", "difficulty", "limitation"],
    "different": ["distinct", "diverse", "varying", "heterogeneous"],
    "big": ["large", "substantial", "considerable", "extensive"],
    "good": ["effective", "efficient", "robust", "promising"],
    "new": ["novel", "innovative", "emerging", "cutting-edge"],
}

# ──────────────────────────────────────────────
#  Wordiness patterns (Chinese & English)
# ──────────────────────────────────────────────

WORDY_PATTERNS_ZH: list[tuple[str, str]] = [
    (r"在一定程度上", ""),
    (r"较为", ""),
    (r"比较", ""),
    (r"非常", ""),
    (r"可以说是", "是"),
    (r"不得不说", ""),
    (r"众所周知，?", ""),
    (r"事实上，?", ""),
    (r"需要注意的是，?", ""),
    (r"换句话说，?", "即"),
]

WORDY_PATTERNS_EN: list[tuple[str, str]] = [
    (r"\bin order to\b", "to"),
    (r"\bdue to the fact that\b", "because"),
    (r"\bin spite of the fact that\b", "although"),
    (r"\bas a matter of fact\b", ""),
    (r"\bit is worth noting that\b", ""),
    (r"\bneedless to say\b", ""),
    (r"\bit should be noted that\b", ""),
    (r"\bin a nutshell\b", ""),
    (r"\blast but not least\b", ""),
]

# ──────────────────────────────────────────────
#  Strategy implementations
# ──────────────────────────────────────────────


def _synonym_replace(text: str, dictionary: dict[str, list[str]]) -> str:
    """Replace words with random synonyms from the dictionary."""
    import random

    result = text
    for word, synonyms in dictionary.items():
        # Only replace if the word is used as a standalone token
        pattern = re.compile(rf"(?<!\w){re.escape(word)}(?!\w)")
        matches = list(pattern.finditer(result))
        if not matches:
            # Also try substring match for Chinese (no word boundaries)
            result = result.replace(word, random.choice(synonyms))
        else:
            # Replace from right to left to preserve positions
            for m in reversed(matches):
                replacement = random.choice(synonyms)
                result = result[:m.start()] + replacement + result[m.end():]
    return result


def _detect_language(text: str) -> str:
    """Simple heuristic: count CJK vs Latin characters."""
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    latin = sum(1 for c in text if c.isascii() and c.isalpha())
    return "zh" if cjk > latin else "en"


def _active_to_passive(sentence: str) -> str:
    """Convert a simple active-voice sentence to passive voice (English)."""
    # Simple heuristic:  subject + verb + object → object + be + past participle + by + subject
    # This is a very basic attempt; for production, use a dependency parser or LLM.
    patterns = [
        (r"^(.+?)\s+(proposes|presents|introduces|develops|proposes|demonstrates|shows)\s+(.+?)\.?$",
         r"\3 is \2d by \1."),
        (r"^(.+?)\s+(conducted|performed|carried out|implemented|evaluated|tested)\s+(.+?)\.?$",
         r"\3 was \2 by \1."),
        (r"^(.+?)\s+(uses|employs|utilizes|applies)\s+(.+?)\.?$",
         r"\3 is used by \1."),
    ]
    for pattern, replacement in patterns:
        if re.match(pattern, sentence, re.IGNORECASE):
            return re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
    return sentence


def _split_long_sentence(sentence: str, max_len: int = 80) -> list[str]:
    """Split overly long sentences at conjunctions."""
    if len(sentence) <= max_len:
        return [sentence]

    # Try splitting at Chinese/English conjunctions
    split_points = []
    for conj in ["并且", "而且", "此外", "同时", "然而", "但是",
                 "and", "moreover", "furthermore", "however",
                 "in addition", "consequently", "therefore"]:
        idx = sentence.find(conj)
        if idx > max_len // 2:
            split_points.append(idx)

    if not split_points:
        # Try comma at a reasonable position
        for i, c in enumerate(sentence):
            if c in ("，", ",") and max_len // 3 < i < max_len:
                split_points.append(i)

    if split_points:
        split_at = min(split_points, key=lambda x: abs(x - max_len // 2))
        first = sentence[:split_at].strip()
        second = sentence[split_at + 1:].strip()
        first = first.rstrip("，,")
        result = [first + "。", second[0].upper() + second[1:] + "." if second else ""]
        return [r for r in result if r]
    return [sentence]


# ──────────────────────────────────────────────
#  Public API
# ──────────────────────────────────────────────


def rewrite_text(text: str, style: str = "academic") -> str:
    """Rewrite academic text using the specified strategy.

    Args:
        text: Input text to rewrite.
        style: Rewriting strategy — one of:
            - ``"academic"``  : Synonym replacement (default)
            - ``"concise"``   : Remove wordiness, tighten prose
            - ``"polished"``  : Upgrade vocabulary + restructure
            - ``"restructure"``: Sentence transformation only

    Returns:
        Rewritten text.
    """
    lang = _detect_language(text)

    if style == "concise":
        patterns = WORDY_PATTERNS_ZH if lang == "zh" else WORDY_PATTERNS_EN
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        return result

    if style == "restructure":
        lines = text.split("\n")
        results = []
        for line in lines:
            if not line.strip():
                results.append(line)
                continue
            # Try active → passive for English
            if lang == "en":
                line = _active_to_passive(line)
            # Split long sentences
            sentences = _split_long_sentence(line)
            results.extend(sentences)
        return "\n".join(results)

    if style == "polished":
        # Synonym + restructure combination
        dict_zh = ACADEMIC_SYNONYMS_ZH if lang == "zh" else {}
        dict_en = ACADEMIC_SYNONYMS_EN if lang == "en" else {}
        result = _synonym_replace(text, dict_zh or dict_en)
        # Apply restructure on top
        lines = result.split("\n")
        results = []
        for line in lines:
            if not line.strip():
                results.append(line)
                continue
            sentences = _split_long_sentence(line)
            results.extend(sentences)
        return "\n".join(results)

    # Default: academic synonym replacement
    dict_zh = ACADEMIC_SYNONYMS_ZH if lang == "zh" else {}
    dict_en = ACADEMIC_SYNONYMS_EN if lang == "en" else {}
    return _synonym_replace(text, dict_zh or dict_en)


def batch_rewrite(
    paragraphs: list[str],
    style: str = "academic",
    strategy_fn: Callable[[str, str], str] = rewrite_text,
    progress_callback: Callable[[int, int], None] = None,
) -> list[str]:
    """Rewrite multiple paragraphs in batch.

    Args:
        paragraphs: List of text paragraphs.
        style: Rewriting strategy name.
        strategy_fn: Rewriting function (default: ``rewrite_text``).
        progress_callback: Optional callback(report_rewritten, total).

    Returns:
        List of rewritten paragraphs.
    """
    total = len(paragraphs)
    results: list[str] = []
    for i, para in enumerate(paragraphs):
        results.append(strategy_fn(para, style))
        if progress_callback:
            progress_callback(i + 1, total)
    return results
