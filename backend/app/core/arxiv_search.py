from __future__ import annotations

import html
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from app.models.schemas import Paper


FALLBACK_PAPERS = [
    Paper(
        title="Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        authors=["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus"],
        summary="A representative paper introducing retrieval-augmented generation, useful for explaining why external evidence improves generated answers.",
        url="https://arxiv.org/abs/2005.11401",
        published="2020-05-22",
        categories=["cs.CL", "cs.AI"],
    ),
    Paper(
        title="Attention Is All You Need",
        authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
        summary="The Transformer architecture paper that underpins many modern LLM-based academic writing assistants.",
        url="https://arxiv.org/abs/1706.03762",
        published="2017-06-12",
        categories=["cs.CL"],
    ),
]


def search_arxiv(keyword: str, max_results: int = 5) -> list[Paper]:
    query = urllib.parse.urlencode(
        {
            "search_query": f"all:{keyword}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
    )
    url = f"https://export.arxiv.org/api/query?{query}"

    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            xml_text = response.read().decode("utf-8", errors="ignore")
        return _parse_arxiv_feed(xml_text)[:max_results] or FALLBACK_PAPERS[:max_results]
    except Exception:
        return FALLBACK_PAPERS[:max_results]


def _parse_arxiv_feed(xml_text: str) -> list[Paper]:
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_text)
    papers: list[Paper] = []
    for entry in root.findall("atom:entry", ns):
        title = _clean(entry.findtext("atom:title", default="", namespaces=ns))
        summary = _clean(entry.findtext("atom:summary", default="", namespaces=ns))
        published = entry.findtext("atom:published", default="", namespaces=ns)[:10]
        authors = [
            _clean(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        ]
        categories = [item.attrib.get("term", "") for item in entry.findall("atom:category", ns)]
        url = entry.findtext("atom:id", default="", namespaces=ns)
        if title:
            papers.append(Paper(title=title, authors=authors, summary=summary, url=url, published=published, categories=categories))
    return papers


def _clean(value: str) -> str:
    return " ".join(html.unescape(value).split())
