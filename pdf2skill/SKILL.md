---
name: pdf2skill
description: >
  PDF 转 Skill 工具——将任意 PDF（技术规范、学术论文、项目报告）编译成
  与现有 skill 生态兼容的 Claude Code skill 文件包。
  基于 Book2Skill 思路：在导入阶段做智能分析，提炼作者思维框架，
  而不是在查询时切片搜索。
  触发关键词：pdf转skill、把这个PDF转成skill、把这个文档变成skill、
  pdf2skill、convert pdf to skill、book to skill、文档转技能。
  即使用户说"帮我把这个规范做成skill"或"把这篇论文变成可以调用的知识"也应触发。
---

# pdf2skill — PDF 转 Skill 工具

将 PDF 编译成 Claude Code skill，让 Claude 调用"思维框架"而不是"搜索碎片"。

## 工作流程

```
Phase 1: 提取  →  Phase 2: 分析  →  Phase 3: 生成  →  Phase 4: 验证
```

## Phase 1: PDF 文本提取

运行提取脚本：

```bash
python "C:/Users/39555/Desktop/07-平台开发/pdf2skill/scripts/extract_pdf.py" \
  "<pdf_path>" \
  --output "C:/Users/39555/.claude/temp/pdf2skill_raw.txt"
```

提取完成后，读取 `C:/Users/39555/.claude/temp/pdf2skill_raw.txt` 的前 3000 字符，
判断文档类型：
- **技术规范**（JORC、NI43-101、国标）：重点提取条款编号、定义表、决策树
- **学术论文/专著**：重点提取研究框架、方法论、结论
- **项目报告**：重点提取数据表、关键参数、建议

## Phase 2: 结构分析（Claude 执行）

读取完整提取文本，分析以下内容：

### 2.1 基本信息提取
- 标题、作者/机构、发布年份
- 文档类型（规范/论文/报告）
- 主要章节结构（目录）
- 语言（中文/英文/双语）

### 2.2 核心框架提炼
提炼作者的**思维框架**，不是摘抄原文：
- 分类体系（如 JORC 的 Measured/Indicated/Inferred）
- 决策树（如"什么情况下用 X"）
- 关键定义（术语 + 适用条件）
- 反模式（文档中明确说"不应该"的做法）

### 2.3 术语表构建
提取所有专业术语，格式：
```
术语: 定义（来源章节）
```

## Phase 3: 生成 Skill 文件包

### 3.1 确定 slug
- 英文小写，用连字符，如 `jorc-code`、`ni43-101`、`orogenic-gold-review`
- 询问用户确认或自动生成

### 3.2 创建目录结构

```bash
mkdir -p "C:/Users/39555/Desktop/_skill_package/<slug>/knowledge"
mkdir -p "C:/Users/39555/Desktop/_skill_package/<slug>/workflows"
```

### 3.3 生成各文件

按以下顺序生成，每个文件生成后立即写入磁盘：

**SKILL.md**（参考模板 `templates/SKILL_template.md`）：
- YAML frontmatter：name、description（含触发关键词）
- 工作模式表
- 知识库索引表
- 核心框架摘要（~500字，最重要的内容）
- 使用示例

**knowledge/key_concepts.md**：
- 文档中所有核心概念的定义
- 格式：概念名 → 定义 → 适用条件 → 来源章节

**knowledge/frameworks.md**：
- 作者的思维框架、分类体系、决策逻辑
- 用表格或流程图（Markdown）呈现
- 实践者口吻："当 Y 时，用 X"

**knowledge/patterns.md**：
- 技术方法、最佳实践
- 反模式（明确标注 ❌）

**glossary.md**：
- 按字母/拼音排序的术语表
- 每条：术语 | 定义 | 来源章节

**cheatsheet.md**：
- 速查决策表
- 格式：场景 → 适用规则/方法 → 注意事项

**workflows/query.md**：
- 如何用这个 skill 回答问题的标准流程

### 3.4 写入文件

每个文件使用 Write 工具写入，路径：
`C:/Users/39555/Desktop/_skill_package/<slug>/<filename>`

## Phase 4: 验证

- 检查所有文件已生成：`ls C:/Users/39555/Desktop/_skill_package/<slug>/`
- 检查 SKILL.md 有 YAML frontmatter
- 检查 knowledge/ 目录有 3 个文件
- 输出调用示例：

```
skill 已生成：<slug>
位置：Desktop/_skill_package/<slug>/
调用方式：在 Claude Code 中说 "<trigger_phrase>"
```

## 质量标准

- SKILL.md 核心内容 ≤ 5000 tokens（按需加载原则）
- 所有文件使用实践者口吻，不摘抄原文
- 触发关键词覆盖中英文常见表达
- 与现有 skill（copper-ore、gold-ore）风格一致
