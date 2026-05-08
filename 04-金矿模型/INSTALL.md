# Gold Ore Skill — 安装与使用说明

## 这是什么

`gold-ore` 是为 Claude Code 编写的**金矿地质领域专家 skill**。它把全球主要金矿分布规律的核心知识（基于 Groves et al. (Orogenic Gold), Cline et al. (Carlin-type), Hedenquist et al. (Epithermal) 等权威文献）封装成可直接调用的工作流，支持三大功能：

1. **金矿项目地质评价**（自动判型、构造定位、规模评估、10 项打分、风险与建议）
2. **金矿专题/技术/勘查报告撰写**（含中国 DZ/T 0033、NI 43-101、JORC、年报四种子格式）
3. **区域成矿潜力分析与靶区预测**（矿床模型驱动 + 证据权重叠加 + A/B/C 级靶区圈定）

## 适用人群

- 矿产地质勘查工程师 / 项目地质师
- 矿业投资分析 / 并购尽调
- 高校与研究院所地学研究人员
- 矿业公司技术决策层

## 系统要求

- **Claude Code** ≥ 最新稳定版（`claude.ai/code` 或本地 CLI）
- 建议同时安装的配套 skill（非必须）：
  - `chinese-paper`（论文撰写，与本 skill 互补）
  - `anthropic-skills:docx` / `pptx` / `xlsx`（输出文件）
  - `anthropic-skills:canvas-design`（图件生成）
  - `ref-verify`（文献验证）

## 安装步骤

### 方式 A：直接复制到 user-level skills 目录（推荐）

将整个 `gold-ore` 文件夹放入：

| 系统 | skills 目录 |
|------|------------|
| Windows | `C:\Users\<用户名>\.claude\skills\` |
| macOS | `~/.claude/skills/` |
| Linux | `~/.claude/skills/` |

最终目录结构：
```
~/.claude/skills/gold-ore/
├── SKILL.md
├── INSTALL.md（本文件）
├── references.md
├── knowledge/      (5-6 个 .md 文件)
├── templates/      (3 个 .md 文件)
└── workflows/      (4 个 .md 文件)
```

## 验证安装

打开 Claude Code 任何会话，输入：
```
/gold-ore
```
或自然语言：
```
帮我分析一个金矿项目
```
若 skill 正确加载，Claude 会按 `SKILL.md` 中的四种模式之一开始工作。

## 快速使用

### 模式 A：项目分析
```
分析这个金矿项目（材料在 D:\projects\XXX\ 目录）
```
→ 输出 `Gold_Ore_Project_Assessment_<项目名>_<日期>.docx`

### 模式 B：报告撰写
```
帮我写一份这个矿床的专题地质报告
```
（Claude 会先确认报告类型：专题 / 勘查 / NI 43-101 / 年报）

### 模式 C：成矿潜力预测
```
评价 XX 区的金矿成矿潜力，圈定靶区
```
→ 输出报告 .docx + 靶区打分 .xlsx

### 模式 D：知识查询
```
金矿的成矿模型是什么？
解释一下 Orogenic 和 Carlin 的差异。
```

## 知识库覆盖

- **矿床类型**：Orogenic / Carlin / Epithermal HS-LS / Porphyry Au-Cu / IOCG-Au / VMS-Au / Intrusion-related / Witwatersrand
- **品位单位**：g/t Au
- **Tier 分级**：Tier 1: ≥5 Moz Au, Tier 2: 1–5 Moz, Tier 3: <1 Moz
- **特色分析**：
  - 品位单位：g/t Au（金矿标准单位）
  - 金赋存状态（自然金粒度、载金矿物、不可见金）
  - 选冶性能（重选—浮��—氰化—生物氧化适用性）
  - nugget effect 警告（品位分布极不均匀）

## 局限性 / 注意事项

1. **不替代正式技术报告**：本 skill 输出仅供内部分析参考；NI 43-101 / JORC / 中国矿产储量评审等正式报告需 QP / CP 资质人员签发。
2. **数据时效性**：知识库中的 Top 矿山产能、储量等数据可能滞后，使用前请核对最新公司年报或 USGS / S&P Global。
3. **无 GIS 功能**：本 skill 不包含真正的空间叠加分析；潜力预测以方法论 + 概念性圈定为主。如需 GIS 量化，请配合 ArcGIS / QGIS / Python 流程。
4. **AI 引用幻觉**：参考文献输出后建议用 `ref-verify` 或 CrossRef 手工核对。

---

**版本**：v1.0
**编制日期**：2026-04-27
**适用 Claude Code 版本**：Opus 4.6+ / Sonnet 4.6+ 均可
**许可**：内部团队使用
