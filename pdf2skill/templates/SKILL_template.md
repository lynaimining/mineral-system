---
name: {slug}
description: >
  {description_cn}
  {description_en}
  触发关键词：{trigger_keywords}
---

# {title}（{title_en}）领域 skill

{one_line_summary}

## 1. 工作模式

| 模式 | 触发短语 | 输出 | 主要文件 |
|------|----------|------|----------|
| **A. 知识查询** | "{query_trigger}" | 直接回答 + 引用 | `knowledge/key_concepts.md` |
| **B. 框架应用** | "{apply_trigger}" | 分析报告 | `knowledge/frameworks.md` |
| **C. 速查** | "{cheatsheet_trigger}" | 决策表 | `cheatsheet.md` |

## 2. 知识库索引

| 文件 | 内容 | 何时读取 |
|------|------|----------|
| `knowledge/key_concepts.md` | 核心概念与定义 | 模式 A 必读 |
| `knowledge/frameworks.md` | 思维框架、决策树 | 模式 B 必读 |
| `knowledge/patterns.md` | 技术/方法/反模式 | 模式 B/C 选读 |
| `glossary.md` | 术语表 | 查术语时读 |
| `cheatsheet.md` | 速查表 | 模式 C 必读 |

## 3. 核心框架摘要

{core_frameworks_summary}

## 4. 使用示例

用户: "{example_query}"
→ 读取 knowledge/frameworks.md
→ 回答: {example_answer_hint}

---
*由 pdf2skill 自动生成，源文件: {source_pdf}*
