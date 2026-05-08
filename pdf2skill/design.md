# pdf2skill 设计文档

**日期**：2026-05-08
**状态**：进行中（边做边完善）

---

## 目标

把任意 PDF（技术规范、学术论文、项目报告）编译成与现有 skill 生态兼容的 Claude Code skill，
让 Claude 不是在"搜索文本"，而是在"调用思维框架"。

## 核心原则（来自 Book2Skill）

- **编译阶段做智能分析**，不在查询时切片
- **密度优于完整**：提炼框架，不 dump 原文
- **实践者口吻**："当 Y 时用 X"，不是"本文解释了 X"
- **按需加载**：SKILL.md 核心 ~4000 tokens，子文件用到才读

## 架构

```
用户: "把这个 PDF 转成 skill"
        ↓
pdf2skill skill
        ↓
Phase 1: Python 脚本提取文本
  - 技术书/规范 → docling（保留表格）
  - 纯文本/报告 → pdftotext → PyMuPDF fallback
  - 中文 PDF → 强制 UTF-8
        ↓
Phase 2: Claude 分析结构
  - 识别文档类型（规范/论文/报告）
  - 提取：标题、作者、章节结构、核心框架、术语
        ↓
Phase 3: 生成 skill 文件包
  - 输出到 Desktop/_skill_package/<slug>/
  - 结构与 copper-ore 兼容
        ↓
Phase 4: 验证
  - 检查文件完整性
  - 输出 skill 调用示例
```

## 生成的 skill 文件结构

```
_skill_package/<slug>/
├── SKILL.md              # YAML frontmatter + 核心框架 + 工作模式
├── knowledge/
│   ├── key_concepts.md   # 核心概念与定义
│   ├── frameworks.md     # 思维框架、决策树
│   └── patterns.md       # 技术/方法/反模式
├── workflows/
│   └── query.md          # 查询工作流
├── cheatsheet.md         # 速查表
└── glossary.md           # 术语表（带章节引用）
```

## PDF 类型自适应

| PDF 类型 | 提取工具 | 特殊处理 |
|---------|---------|---------|
| 技术规范（JORC、NI43-101）| pdftotext | 提取条款编号、定义表 |
| 学术论文/专著 | docling | 保留表格、公式 |
| 项目报告 | PyMuPDF | 提取数据表 |
| 中文 PDF | pdftotext | UTF-8 强制 |

## 待决策

- [ ] 生成的 skill 是否支持中英双语（参考 copper-ore 风格）
- [ ] 是否需要注册机制（自动加入 skill 列表）
- [ ] 批量处理多个 PDF 的优先级
