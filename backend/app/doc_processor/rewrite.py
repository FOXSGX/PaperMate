import re


ACADEMIC_REPLACEMENTS = {
    "本文": "本研究",
    "说明": "表明",
    "很多": "大量",
    "重要": "关键",
    "使用": "采用",
    "方法": "技术路径",
    "提高": "提升",
    "可以": "能够",
}


def rewrite_text(text: str, style: str = "academic") -> str:
    rewritten = text.strip()
    for source, target in ACADEMIC_REPLACEMENTS.items():
        rewritten = rewritten.replace(source, target)

    rewritten = re.sub(r"([。！？])", r"\1\n", rewritten)
    sentences = [sentence.strip() for sentence in rewritten.splitlines() if sentence.strip()]

    if style == "concise":
        sentences = [re.sub(r"(在一定程度上|较为|比较|非常)", "", sentence) for sentence in sentences]
    elif style == "polished":
        sentences = [sentence.replace("因此", "由此可见，") for sentence in sentences]

    return "".join(sentences)
