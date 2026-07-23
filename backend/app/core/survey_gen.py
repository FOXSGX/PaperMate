from collections.abc import Iterable

from app.core.arxiv_search import search_arxiv
from app.models.schemas import Paper


def generate_survey(topic: str, max_papers: int = 5, outline_style: str = "standard") -> str:
    papers = search_arxiv(topic, max_papers)

    if outline_style == "method":
        return _generate_method_survey(topic, papers)
    elif outline_style == "timeline":
        return _generate_timeline_survey(topic, papers)
    else:
        return _generate_standard_survey(topic, papers)


def _generate_standard_survey(topic: str, papers: list) -> str:
    sections = [
        f"# {topic} 文献综述初稿",
        "## 1. 研究背景",
        f"围绕‘{topic}’这一主题，近期研究主要关注模型能力、数据质量、应用场景与可解释性之间的平衡。",
        "## 2. 代表性文献",
    ]

    for index, paper in enumerate(papers, start=1):
        authors = ", ".join(paper.authors[:3]) or "Unknown"
        sections.append(f"### 2.{index} {paper.title}")
        sections.append(f"- 作者：{authors}")
        sections.append(f"- 时间：{paper.published or 'N/A'}")
        sections.append(f"- 摘要要点：{paper.summary[:420]}")

    sections.extend(
        [
            "## 3. 方法归纳",
            "现有方法通常可以归纳为数据驱动建模、检索增强推理、任务特定微调和人工规则约束四类。",
            "## 4. 发展趋势",
            "后续工作可重点关注高质量数据构建、跨领域泛化、引用可追溯生成以及面向真实写作流程的人机协同。",
        ]
    )
    return "\n\n".join(sections)


def _generate_method_survey(topic: str, papers: list) -> str:
    sections = [
        f"# {topic} 文献综述（方法导向）",
        "## 1. 问题定义",
        f"针对‘{topic}’这一研究问题，学术界已提出多种技术路径。本综述按方法类别组织，梳理不同技术路线的演进与关联。",
        "## 2. 方法分类与代表工作",
    ]

    method_categories = [
        ("数据驱动方法", "以大规模标注数据为基础，利用统计学习或深度学习建模"),
        ("检索增强方法", "引入外部知识库或检索机制，提升模型的事实准确性与覆盖范围"),
        ("规则与约束方法", "基于领域知识手工设计规则、模板或逻辑约束"),
        ("端到端学习方法", "直接从原始输入到最终输出的联合建模"),
    ]

    for idx, (cat_name, cat_desc) in enumerate(method_categories, start=1):
        sections.append(f"### 2.{idx} {cat_name}")
        sections.append(cat_desc)
        # Assign papers round-robin to categories
        cat_papers = [p for i, p in enumerate(papers) if i % len(method_categories) == idx - 1]
        for paper in cat_papers:
            authors = ", ".join(paper.authors[:2]) or "Unknown"
            sections.append(f"- **{paper.title}** ({authors}, {paper.published or 'N/A'}): {paper.summary[:200]}")

    sections.extend(
        [
            "## 3. 方法对比分析",
            "各类方法在适用场景、数据需求、可解释性与性能表现方面各有优劣。数据驱动方法在标注充分时表现优异，检索增强方法更适合知识密集型任务。",
            "## 4. 未来方向",
            "结合多种方法优势的混合架构有望成为主流，尤其是在小样本学习和跨领域迁移场景中。",
        ]
    )
    return "\n\n".join(sections)


def _generate_timeline_survey(topic: str, papers: list) -> str:
    sorted_papers = sorted(papers, key=lambda p: p.published or "0000")

    sections = [
        f"# {topic} 文献综述（时间线）",
        "## 1. 概述",
        f"本文按时间顺序梳理‘{topic}’领域的关键研究进展，揭示技术演进的脉络与重要转折点。",
        "## 2. 发展历程",
    ]

    for index, paper in enumerate(sorted_papers, start=1):
        authors = ", ".join(paper.authors[:3]) or "Unknown"
        year = (paper.published or "N/A")[:4]
        sections.append(f"### 2.{index} [{year}] {paper.title}")
        sections.append(f"- 作者：{authors}")
        sections.append(f"- 贡献概述：{paper.summary[:350]}")

    sections.extend(
        [
            "## 3. 技术演进趋势",
            "从早期方法到最新进展，该领域呈现出从规则驱动到数据驱动、从单一模态到多模态融合、从静态模型到持续学习的演进趋势。",
            "## 4. 未来展望",
            "未来研究应关注模型的可解释性、数据效率以及在实际部署中的鲁棒性。",
        ]
    )
    return "\n\n".join(sections)


def stream_survey(topic: str, max_papers: int = 5, outline_style: str = "standard") -> Iterable[str]:
    survey = generate_survey(topic, max_papers, outline_style)
    for paragraph in survey.split("\n\n"):
        yield paragraph
