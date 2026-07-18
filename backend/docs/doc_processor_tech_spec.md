# PaperMate 文档处理模块 · 技术说明

> **模块**: `backend/app/doc_processor/`  
> **负责角色**: 角色C — 文档处理与格式排版开发  
> **依赖**: pdfplumber 0.11+, python-docx 1.1+

---

## 模块总览

```
doc_processor/
├── __init__.py      # 包入口，暴露统一 API
├── pdf_parser.py    # PDF 文本抽取（保留页码）
├── docx_parser.py   # DOCX 文本抽取（保留标题层级）
├── styles.py        # 排版样式配置（GB/T 7713 等）
├── format_engine.py # 格式排版引擎
└── rewrite.py       # 降重改写引擎
```

---

## 1. PDF 文本抽取 (`pdf_parser.py`)

### 核心数据结构

```python
@dataclass
class PageData:
    page_number: int    # 页码（从1开始）
    text: str           # 该页文本
    num_chars: int      # 字符数

@dataclass
class PdfDocument:
    path: str           # 文件路径
    total_pages: int    # 总页数
    pages: list[PageData]
```

### API

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `parse_pdf(path)` | `str|Path` | `PdfDocument` | 完整解析，返回结构化文档 |
| `iter_pages(path)` | `str|Path` | `Iterator[PageData]` | 惰性逐页迭代，适合大文件 |
| `doc.full_text` | 属性 | `str` | 带 `[Page N]` 标记的拼接文本 |
| `doc.plain_text` | 属性 | `str` | 纯文本拼接 |
| `doc.get_page(n)` | `int` | `PageData|None` | 获取指定页码内容 |

### 使用示例

```python
from doc_processor import parse_pdf

doc = parse_pdf("paper.pdf")
print(f"共 {doc.total_pages} 页")
for page in doc.pages:
    print(f"第{page.page_number}页: {page.num_chars}字符")
```

### 依赖

- **pdfplumber** — PDF 底层解析（基于 pdfminer.six）

---

## 2. DOCX 文本抽取 (`docx_parser.py`)

### 核心数据结构

```python
@dataclass
class ParagraphData:
    text: str               # 段落文本
    style_name: str         # 样式名（"Heading 1", "Normal" 等）
    heading_level: int      # 标题级别（0=正文，1-6=标题）
    is_list_item: bool      # 是否是列表项
    list_level: int         # 列表嵌套层级（-1=非列表）

@dataclass
class DocxDocument:
    path: str
    paragraphs: list[ParagraphData]
```

### API

| 函数 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `parse_docx(path)` | `str|Path` | `DocxDocument` | 完整解析，保留标题层级和列表结构 |
| `heading_tree(doc)` | `DocxDocument` | `list[dict]` | 生成标题的嵌套层级树 |
| `doc.full_text` | 属性 | `str` | 带 `#` 标题标记的 Markdown 风格文本 |
| `doc.plain_text` | 属性 | `str` | 纯文本 |
| `doc.headings` | 属性 | `list[ParagraphData]` | 仅标题段落 |
| `doc.get_section_text(i)` | `int` | `str` | 获取第 i 个标题对应的章节全文 |

### 标题层级解析

DOCX 中通过段落样式识别标题层级：

| Word 样式 | heading_level |
|-----------|:------------:|
| Heading 1 | 1 |
| Heading 2 | 2 |
| Heading 3 | 3 |
| Heading 4-6 | 4-6 |
| Normal / 其他 | 0（正文） |

列表项通过 OOXML 的 `<w:numPr>` 元素检测，支持嵌套列表层级识别。

### 使用示例

```python
from doc_processor import parse_docx, heading_tree

doc = parse_docx("thesis.docx")
print(doc.headings)                     # 所有标题
tree = heading_tree(doc)                # 目录树
section_text = doc.get_section_text(0)  # 第一节内容
```

---

## 3. 排版样式配置 (`styles.py`)

### 预置样式

| 名称 | 适用场景 |
|------|----------|
| `gb7713` | GB/T 7713-1987 中国学术论文标准 |
| `generic` | 通用英文论文格式 |
| `ieee` | IEEE 会议/期刊格式（近似） |

### 扩展自定义样式

```python
from doc_processor import StyleProfile, FontSpec, HeadingSpec, PageMargins, register_style

my_style = StyleProfile(
    name="my_journal",
    display_name="某期刊格式",
    body_font=FontSpec(name="Times New Roman", size_pt=11),
    body_line_spacing=1.15,
    # ... 其他字段
)
register_style("my_journal", my_style)
```

### StyleProfile 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `body_font` | `FontSpec` | 正文字体（名称、字号、粗斜体） |
| `body_line_spacing` | `float` | 行距倍数 |
| `body_first_line_indent_pt` | `float` | 首行缩进（磅值） |
| `body_alignment` | `str` | 对齐方式: left/center/right/justify |
| `heading_1` ~ `heading_6` | `HeadingSpec` | 各级标题设置 |
| `page_margins` | `PageMargins` | 页边距（mm） |
| `header_text` / `footer_text` | `str` | 页眉/页脚文本 |
| `reference_font` | `FontSpec` | 参考文献字体 |

### FontSpec

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | `str` | 字体名（如 SimSun, Times New Roman） |
| `size_pt` | `float` | 字号（磅） |
| `bold` | `bool` | 是否加粗 |
| `italic` | `bool` | 是否斜体 |

---

## 4. 格式排版引擎 (`format_engine.py`)

### 功能

- 字体统一设置（含中文字体 fallback）
- 字号调整
- 行距设置
- 首行缩进
- 标题对齐与编号（自动生成 1., 1.1, 1.1.1 等多级编号）
- 页边距设置
- 页眉/页脚添加

### API

```python
format_docx(
    input_path: str | Path,
    output_dir: str | Path,
    template: str = "gb7713",
    output_filename: str | None = None
) -> Path
```

### 使用示例

```python
from doc_processor import format_docx

output = format_docx(
    input_path="draft.docx",
    output_dir="./output",
    template="gb7713",
)
print(f"格式化完成: {output}")
```

### 标题编号系统

```python
format_engine._heading_number(level=2, numbering_format="1.1", counters=[2, 3])
# → "2.3 "

format_engine._heading_number(level=1, numbering_format="第1章", counters=[3])
# → "第3章 "
```

### 自动样式检测

```python
from doc_processor import auto_detect_style

style = auto_detect_style(document_text)
# → "gb7713" / "generic" / "ieee"
```

基于中/英文字符比例和关键词匹配做启发式判断。

---

## 5. 降重改写引擎 (`rewrite.py`)

### 改写策略

| 策略名 | 说明 | 适合场景 |
|--------|------|----------|
| `academic` | 学术同义词替换（默认） | 基础降重 |
| `concise` | 删除冗余、精简表达 | 使文字更紧凑 |
| `polished` | 升级词汇 + 句式变换 | 综合提升 |
| `restructure` | 仅做句式变换（主动↔被动、长句拆分） | 目标明确的句式调整 |

### API

```python
# 单段改写
rewrite_text(text: str, style: str = "academic") -> str

# 批量改写
batch_rewrite(
    paragraphs: list[str],
    style: str = "academic",
    progress_callback: Callable | None = None
) -> list[str]
```

### 设计原则

1. **分层处理**: 规则引擎做基础改写 → LLM 做深度改写（API 路由层实现）
2. **语义保持**: 改写不改变原意、不引入事实错误
3. **可回退**: 每条改写结果附带原文对照，供用户审阅

### 词库说明

- 中文词典 `ACADEMIC_SYNONYMS_ZH`: 约 20 组高频学术词汇（「本文」→「本研究」等）
- 英文词典 `ACADEMIC_SYNONYMS_EN`: 约 12 组高频学术词汇（"use" → "employ" 等）
- 冗词模式 `WORDY_PATTERNS_ZH/EN`: 中文约 10 组、英文约 10 组

---

## 6. 模块间调用关系

```
RAG 引擎 (rag_engine.py)
     │
     ├──→ pdf_parser.parse_pdf()     ← 用户上传 PDF 论文
     └──→ docx_parser.parse_docx()   ← 用户上传 DOCX 论文
                  │
格式 API (format.py)
     └──→ format_engine.format_docx()
              │
              ├── styles.get_style()     ← 加载样式配置
              └── (python-docx 操作)

降重 API (format.py)
     └──→ rewrite.rewrite_text()
              └── (同义词词典 + 规则)
```

---

## 7. 测试

测试文件位于 `backend/tests/`。

```bash
# 运行所有文档处理模块测试
cd backend
venv\Scripts\pytest tests/ -v

# 仅运行某个测试文件
venv\Scripts\pytest tests/test_pdf_parser.py -v
```

---

## 8. 开发指南

### 添加新样式

1. 在 `styles.py` 中定义 `StyleProfile` 实例
2. 添加到 `_STYLE_REGISTRY` 字典
3. 或者在运行时调用 `register_style()`

### 扩展改写词典

在 `rewrite.py` 的 `ACADEMIC_SYNONYMS_ZH` 或 `ACADEMIC_SYNONYMS_EN` 中添加新词条即可。

---

*— 文档处理团队 · PaperMate · v1.0*
