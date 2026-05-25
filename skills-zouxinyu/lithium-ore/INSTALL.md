# Lithium Ore Skill — 安装与使用说明

## 这是什么

`lithium-ore` 是为 Claude Code 编写的**锂矿地质领域专家 skill**。它把全球主要锂矿分布规律的核心知识（基于 Bradley & McCauley USGS Lithium Deposit Models、Kesler et al. Global Lithium Resources、USGS Lithium Mineral Commodity Summaries 等权威文献）封装成可直接调用的工作流，支持三大功能：

1. **锂矿项目地质评价**（自动判型、构造定位、规模评估、10 项打分、风险与建议）
2. **锂矿专题/技术/勘查报告撰写**（含中国 DZ/T 0033、NI 43-101、JORC、年报四种子格式）
3. **区域成矿潜力分析与靶区预测**（矿床模型驱动 + 证据权重叠加 + A/B/C 级靶区圈定）

## 适用人群

- 矿产地质勘查工程师 / 项目地质师
- 矿业投资分析 / 并购尽调
- 高校与研究院所地学研究人员
- 矿业公司技术决策层

## 系统要求

- **Claude Code** ≥ 最新稳定版（`claude.ai/code` 或本地 CLI）
- 建议同时安装的配套 skill（非必须）：
  - `paper`（论文撰写，与本 skill 互补）
  - `anthropic-skills:docx` / `pptx` / `xlsx`（输出文件）
  - `anthropic-skills:canvas-design`（图件生成）
  - `ref-verify`（文献验证）

## 安装步骤

### 方式 A：直接复制到 user-level skills 目录（推荐）

将整个 `lithium-ore` 文件夹放入：

| 系统 | skills 目录 |
|------|------------|
| Windows | `C:\Users\<用户名>\.claude\skills\` |
| macOS | `~/.claude/skills/` |
| Linux | `~/.claude/skills/` |

最终目录结构：
```
~/.claude/skills/lithium-ore/
├── SKILL.md
├── INSTALL.md（本文件）
├── references.md
├── knowledge/      (6 个 .md 文件)
├── templates/      (3 个 .md 文件)
└── workflows/      (4 个 .md 文件)
```

### 方式 B：从 zip 包安装

1. 解压 `lithium-ore-skill.zip`
2. 把解压出的 `lithium-ore` 文件夹移动到上表对应的 skills 目录
3. 重启 Claude Code（或在新会话中验证）

## 验证安装

打开 Claude Code 任何会话，输入：
```
/lithium-ore
```
或自然语言：
```
帮我分析一个锂矿项目
```
若 skill 正确加载，Claude 会按 `SKILL.md` 中的四种模式之一开始工作。

## 快速使用

### 模式 A：项目分析
```
分析这个锂矿项目（材料在 D:\projects\XXX\ 目录）
```
→ 输出 `Lithium_Project_Assessment_<项目名>_<日期>.docx`

### 模式 B：报告撰写
```
帮我写一份这个矿床的专题地质报告
```
（Claude 会先确认报告类型：专题 / 勘查 / NI 43-101 / 年报）

### 模式 C：成矿潜力预测
```
评价 XX 区的硬岩型锂矿成矿潜力，圈定靶区
```
→ 输出报告 .docx + 靶区打分 .xlsx

### 模式 D：知识查询
```
澳大利亚 Pilbara 锂矿带的成矿模型是什么？
解释一下锂辉石路线和卤水路线的工艺差异。
```

## 知识库覆盖

- **三大锂矿类型**：LCT Pegmatite（硬岩型）/ Brine（盐湖卤水型）/ Clay（粘土型）
- **两大冶炼工艺路线**：锂辉石路线（硫酸法）vs 卤水路线（蒸发沉淀 / DLE）
- **全球成矿域**：澳大利亚 Pilbara / 南美锂三角（Atacama、Uyuni）/ 中国川西（甲基卡、可尔因）/ 加拿大 / 非洲
- **品位—吨位曲线**：每类型累积频率分布 + Tier 1/2/3 分级阈值
- **构造控矿模型**：造山带 / 碰撞带 / 裂谷盆地 3 类
- **找矿要素清单**：每类���独立的"地质 + 化探 + 物探 + 遥感"四元证据组
- **产品分级**：电池级（≥99.5% Li₂CO₃）vs 工业级（≥99.0% Li₂CO₃）

## 自定义与扩展

每个文件都是纯 Markdown，可直接编辑：
- 想加入团队内部的特殊矿床案例？编辑 `knowledge/global_belts.md`
- 想修改打分项权重？编辑 `templates/project_assessment.md` 第 7 节
- 想加入公司专用报告模板？在 `templates/technical_report.md` 内追加子格式
- 想接入新的勘查方法？编辑 `knowledge/exploration_criteria.md`

## 局限性 / 注意事项

1. **不替代正式技术报告**：本 skill 输出仅供内部分析参考；NI 43-101 / JORC / 中国矿产储量评审等正式报告需 QP / CP 资质人员签发。
2. **数据时效性**：知识库中的 Top 矿山产能、储量等数据可能滞后，使用前请核对最新公司年报或 USGS / Benchmark Mineral Intelligence。
3. **无 GIS 功能**：本 skill 不包含真正的空间叠加分析；潜力预测以方法论 + 概念性圈定为主。如需 GIS 量化，请配合 ArcGIS / QGIS / Python 流程。
4. **AI 引用幻觉**：参考文献输出后建议用 `ref-verify` 或 CrossRef 手工核对。

## 反馈与维护

如发现知识错误、术语不准、模板缺漏，请直接修改对应 .md 文件后同步给团队，或在内部协作平台提交 issue。

## 致谢

知识库源自下列权威文献（详见 `references.md`）：
- Bradley, D.C. & McCauley, A.D., 2016 — *A Preliminary Deposit Model for Lithium-Cesium-Tantalum (LCT) Pegmatites* (USGS Open-File Report)
- Kesler, S.E. et al., 2012 — *Global Lithium Resources: Relative Importance of Pegmatite, Brine and Other Deposits*, Ore Geology Reviews
- USGS Mineral Commodity Summaries — Lithium (年度报告)
- Gruber, P.W. et al., 2011 — *Global Lithium Availability: A Constraint for Electric Vehicles?*, Journal of Industrial Ecology

---

**版本**：v1.0
**编制日期**：2026-04-27
**适用 Claude Code 版本**：Opus 4.7+ / Sonnet 4.6+ 均可
**许可**：内部团队使用
