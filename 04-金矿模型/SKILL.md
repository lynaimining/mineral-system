---
name: gold-ore
description: >
  金矿（Gold Ore）领域专家 skill，用于（1）金矿项目地质分析与评价（2）撰写金矿专题/技术/勘查报告（3）区域成矿潜力分析与预测。
  知识库基于全球主要金矿分布规律的权威参考（Groves et al. Orogenic Gold 综述、Cline et al. Carlin-type 综述、
  Hedenquist et al. Epithermal 综述、USGS 品位-吨位模型等），
  覆盖**七大金矿类型**（Orogenic / Carlin-type / Epithermal HS-LS / Porphyry Au-Cu / IOCG-Au / Witwatersrand / VMS-Au / Intrusion-related）
  和**五大全球成矿域**（环太平洋、特提斯、太古宙克拉通、古生代造山带、新生代火山弧）。
  当用户说"分析这个金矿项目"、"评价这个金矿床"、"写金矿报告"、"金矿成矿潜力"、"找矿预测"、"成矿规律分析"、
  "对比这两个金矿"、"判断这是什么类型金矿"、"画金矿成矿带"、"区域金矿评价"、"gold exploration target"、
  "orogenic gold potential"、"Carlin-type assessment"、"epithermal potential"、"gold district analysis"、
  "metallogenic prediction for Au"等，触发此 skill。
  也可以与 chinese-paper skill 配合：先用 gold-ore 提取并整合地质素材，再用 chinese-paper 撰写发表级论文。
---

# Gold Ore（金矿）领域 skill

金矿地质 / 找矿 / 成矿潜力分析的领域知识与工作流。**核心理念：类型识别 → 构造定位 → 规模—品位评估 → 成矿要素打分 → 预测靶区**。

## 1. 工作模式（按用户意图自动选择）

| 模式 | 触发短语 | 输出 | 主要文件 |
|------|----------|------|----------|
| **A. 项目分析** | "分析这个金矿"、"评价这个矿床"、"判断类型" | 项目地质评价（.docx 或 .md） | `workflows/analyze_project.md` + `templates/project_assessment.md` |
| **B. 报告撰写** | "写金矿报告"、"勘查报告"、"专题报告" | 技术/勘查报告（.docx） | `workflows/write_report.md` + `templates/technical_report.md` |
| **C. 潜力预测** | "成矿潜力"、"找矿预测"、"成矿区划" | 区域潜力评价（.docx + 打分表） | `workflows/predict_potential.md` + `templates/potential_prediction.md` |
| **D. 知识查询** | "造山型金矿什么特征"、"Carlin-type"、"Yilgarn" | 直接回答 + 引用 | `knowledge/*.md` |

> 默认所有输出语言与用户提问语言一致；地质术语保留英文原词（orogenic, Carlin-type, epithermal, IOCG 等）。

## 2. 知识库索引（必读时机：每次进入 workflow 之前）

| 文件 | 内容 | 何时读取 |
|------|------|----------|
| `knowledge/deposit_types.md` | 七大金矿类型的特征、矿物、蚀变、典型矿床、规模—品位 | 模式 A/D 必读；模式 B/C 选读 |
| `knowledge/global_belts.md` | 五大成矿域、各成矿带的代表矿床、构造背景 | 模式 C 必读；其他选读 |
| `knowledge/tectonic_controls.md` | 造山带 / 火山弧 / 克拉通的成矿差异 | 模式 A/C 必读 |
| `knowledge/grade_tonnage.md` | 各类型品位—吨位曲线、Tier 1/2 阈值、经济门槛 | 模式 A/C 必读 |
| `knowledge/exploration_criteria.md` | 各类型勘查要素、地化—地球物理—遥感标志、靶区识别 | 模式 C 必读 |

## 3. 模式 A：金矿项目分析（默认）

**目标**：基于用户提供的项目材料（钻孔、化探、报告、PPT、影像），给出"它是什么、有多大、好不好、还该做什么"的专业判断。

### 流程
```
材料扫描 → 类型识别 → 构造定位 → 规模—品位评估 → 成矿要素打分（10 项） → 风险与建议 → 质量审查 → 输出
```

### Step 1：材料扫描
扫描用户工作目录中的：钻孔报告、地质图、化探数据、岩相学描述、年代学、同位素、PPT、可研。

### Step 2：类型识别（决定后续所有分析）
按 `knowledge/deposit_types.md` 的"诊断特征矩阵"判定。**关键诊断要素**：
- **构造背景**：造山带剪切带→Orogenic；火山弧→Epithermal；碳酸盐岩台地→Carlin；克拉通盆地→Witwatersrand
- **蚀变组合**：碳酸盐化-绢云母化→Orogenic；明矾石-叶蜡石→HS Epithermal；成人石-绢云母→LS Epithermal；脱碳酸盐化-硅化→Carlin
- **共生元素**：Au-As-Sb-W→Orogenic；Au-As-Sb-Hg-Tl→Carlin；Au-Ag-As→Epithermal；Au-Cu→Porphyry/IOCG

### Step 3：构造定位
按 `knowledge/global_belts.md` 把项目放入全球成矿带（Yilgarn、Abitibi、Nevada、环太平洋等），并对比同带头部矿床。

### Step 4：规模—品位评估
- 用 `knowledge/grade_tonnage.md` 的对应曲线，把项目的资源量/品位标在该类型的累积频率曲线上。
- 给出 Tier 1（>100 t Au）/ Tier 2（10-100 t Au）/ Tier 3（<10 t Au）分级。

### Step 5：成矿要素打分（10 项，每项 0-10 分）
按 `templates/project_assessment.md` 第 5 节的打分卡执行。10 项总分 ≥70 分为 Tier 1 候选，50-70 为 Tier 2，<50 为高风险。

### Step 6：质量审查
按 `workflows/quality_review.md` 执行双 Reviewer 审查：
- Reviewer-1：地质技术准确性
- Reviewer-2：逻辑与风险平衡
- 问题 severity 分级（Critical/High/Medium/Low）
- Tier 1 项目或用户要求高质量时，启动迭代修复循环（MAX_ROUNDS = 2）

### Step 7：输出
按 `templates/project_assessment.md` 模板输出 .docx。文件名 `Gold_Project_Assessment_<项目名>_<YYYYMMDD>.docx`。
输出位置按 CLAUDE.md 规定（矿业评估类→Desktop/02-矿业评估/）。

## 4. 模式 B：金矿报告撰写

**触发**：用户说"写金矿报告"、"勘查报告"、"专题报告"、"年报金矿章节"等。

### 流程
```
确认报告类型 → 材料整合 → 按模板撰写 → 图件清单 → 输出
```

报告类型与对应模板（在 `templates/technical_report.md` 内分章节）：
1. **专题地质报告**：聚焦单一矿床/区带的成矿规律
2. **勘查报告**（中国 DZ/T 0033 规范）：含资源量估算与可行性
3. **NI 43-101 / JORC 摘要**：英文技术报告标准章节

> 撰写规范遵循 `chinese-paper` skill：图文并茂、数据翔实、参考文献用 CrossRef 验证；中文用 GB/T 7714 引用格式。

## 5. 模式 C：区域成矿潜力分析与预测（核心特色）

**触发**：用户说"成矿潜力"、"找矿预测"、"区划"、"靶区"、"远景"等。

### 流程（**矿床模型驱动 + 要素叠加**）
```
1. 区域类型选定（按用户提供的范围 + global_belts 匹配）
2. 选择控矿模型（按 deposit_types + tectonic_controls）
3. 列出关键控矿要素清单（exploration_criteria）
4. 各要素 GIS 化—权重—叠加（用户若有数据则量化；否则给出方法论）
5. 圈定 A/B/C 三级靶区
6. 给出钻探/化探/地球物理建议
7. 输出：报告 .docx + 打分表 .xlsx（如有数据）
```

### 关键产出（`templates/potential_prediction.md`）
- **潜力评分卡**：每 km² 网格 0-100 分
- **靶区清单**：A 级（>80 分，立即工程验证）、B 级（60-80，地表加密）、C 级（40-60，进一步勘查）
- **找矿模型简图**：含构造、岩性、蚀变、地化、地球物理标志
- **下一步工作建议**：钻孔/槽探/化探/地球物理优先级

## 6. 跨 skill 协作

- **copper-ore**：Cu-Au 共生矿床（Porphyry Au-Cu、IOCG-Au）调用 copper-ore 的知识库
- **mineral-system-eval**：通用五要素框架 + gold-ore 专项知识库
- **chinese-paper**：gold-ore 提取地质素材 → chinese-paper 撰写论文
- **xlsx**：定量打分、品位—吨位绘图
- **canvas-design / docx**：成矿模式图、勘查工程部署图

## 7. 参考资料

详见 `references.md`。**核心文献**：
1. **Groves et al. (1998, 2003) — Orogenic gold deposits: A proposed classification**（造山型金矿权威综述）
2. **Cline et al. (2005) — Carlin-type gold deposits in Nevada**（卡林型金矿综述）
3. **Hedenquist et al. (2000) — Exploration for epithermal gold deposits**（浅成低温金矿综述）
4. **USGS — Grade and tonnage models for gold deposits**（品位-吨位模型）

## 8. 输出规范

- **默认输出位置**：按 CLAUDE.md 规定的桌面目录规范输出（矿业评估类→Desktop/02-矿业评估/，调研报告类→Desktop/04-调研报告/）。
- **文件命名**：`Gold_<模式>_<对象名>_<YYYYMMDD>.<docx|xlsx|md>`。
- **图件**：成矿模式图、品位—吨位投影、地质平面、蚀变剖面、靶区图——优先用 SVG / PNG 嵌入 docx；不可幻觉数据。
- **数据可信度声明**：所有引用资源量、品位、坐标必须注明来源（公司年报、可研、文献）；模型参数注明来源文献。
- **不确定时**：宁可少说也不编造。AI 不能替代实测数据；建议用户用真实钻孔/化探/物探数据驱动。

---

**入口指引**：用户提问后，Claude 应：
1. 判断模式（A/B/C/D）；
2. 读取对应 workflow + 必读 knowledge 文件；
3. 扫描用户提供的材料（默认从当前工作目录开始）；
4. 按模板执行；
5. 在最终输出中明确标注：方法、假设、引用、置信度。
