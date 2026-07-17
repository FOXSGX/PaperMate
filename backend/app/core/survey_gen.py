from collections.abc import Iterable

from app.core.arxiv_search import search_arxiv
from app.models.schemas import Paper


def generate_survey(topic: str, max_papers: int = 5) -> str:
    papers = search_arxiv(topic, max_papers)
    sections = [
        f"# {topic} 文献综述初稿",
        "## 1. 研究背景",
        f"围绕“{topic}”这一主题，近期研究主要关注模型能力、数据质量、应用场景与可解释性之间的平衡。",
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


def stream_survey(topic: str, max_papers: int = 5) -> Iterable[str]:
    survey = generate_survey(topic, max_papers)
    for paragraph in survey.split("\n\n"):
        yield paragraph
