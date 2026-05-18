# Mineral System Model — 数据JSON化研发档案 v2.0

**项目**: LynAI Mining · Mineral System Model (MSM)
**版本**: v2.0（融合版 — 工程化交付标准 + 奥卡姆剃刀选型 + 核心创新）
**日期**: 2026-05-18
**负责人**: 邹心宇
**审核者**: 王选策

> **本文档聚焦 Phase A（数据准备阶段）**，Phase B（后训练）由后训练工程师接手。
> 邹心宇的职责：产出高质量训练数据，以标准化JSON格式交付。

***

## 一、项目定位与设计哲学

### 1.1 最终产品形态

**输入**：一个区域（可能提供资料，也可能不提供资料）
**输出**：

1. 该区域的地质背景综述

2. 最可能形成的矿种预测

3. 完整的 Mineral System Model 报告

### 1.2 设计哲学

**奥卡姆剃刀原则**：在保障90%以上质量的前提下，尽量降低工作流复杂性。

* Marker够用就不引入DocLayout-YOLO + GOT-OCR2

* 不需要bbox就不做版面检测

* KG用JSON存储，不部署Neo4j（Phase A不需要）

* 精力集中在核心价值：KG抽取(M5) + 样本合成(M6) + 博士论文推理链条 + Spatial Embedding

**全链路JSON化**：每个环节统一JSON Schema，可追溯、可复现、可迭代。

**可逆性保证**：原始PDF始终保留，每一层都是派生物，任何环节可重跑。

### 1.3 六大矿系（冻结口径）

| &#x23; | 矿系           | 标签代号        | 典型矿床                                  |
| ------ | ------------ | ----------- | ------------------------------------- |
| 1      | 造山型金矿        | `OROG-AU`   | Kalgoorlie, Kirkland Lake, Sukhoi Log |
| 2      | 斑岩Cu-Au-(Mo) | `PORP-CUMO` | El Teniente, Chuquicamata, Oyu Tolgoi |
| 3      | VMS          | `VMS`       | Kidd Creek, Neves-Corvo               |
| 4      | IOCG         | `IOCG`      | Olympic Dam, Candelaria               |
| 5      | 超基性Cu-Ni-PGE | `MUM-CUNI`  | Norilsk, Voisey's Bay, Jinchuan       |
| 6      | 硬岩锂矿LCT      | `LCT-LI`    | Greenbushes, Pilgangoora              |

### 1.4 数据源清单

| 数据源         | 数量        | 核心价值             | 主要用途                       |
| ----------- | --------- | ---------------- | -------------------------- |
| 学术期刊论文      | ~100,000篇 | 成矿机理、空间推理逻辑      | SFT核心 + CPT                |
| 博士论文        | ~500篇     | **完整推理链条**（核心创新） | SFT推理链条 + DPO chosen + CoT |
| JORC报告      | 1,139家    | 标准化定量数据、矿体几何     | CPT + 定量QA                 |
| NI 43-101报告 | ~9,721份   | 北美项目数据、可研分析      | CPT（Phase 2接入）             |
| 专业书籍        | 443本      | 系统性知识框架、术语体系     | CPT知识底座                    |

### 1.5 架构层级

```
原始PDF/文档
    ↓
Layer 1: 文档提取（Marker为主，M1-M3）
    ↓
Layer 2: 知识结构化（KG实体/关系 + 空间锚点，M4-M5）
    ↓
Layer 2.5: Spatial Embedding（核心创新）
    ├── 概念空间向量化（512+128维）
    ├── 空间关系图谱（分层架构）
    ├── 多尺度空间索引
    └── 空间相似度索引
    ↓
Layer 3: 训练样本合成（M6 → S1-S4）
    ↓
交付给后训练工程师
```

***

## 二、数据处理管线（M1-M6）

### 2.0 精力分配原则

| 模块    | 性质    | 精力占比 | 说明                           |
| ----- | ----- | ---- | ---------------------------- |
| M1-M3 | 流水线工作 | 20%  | 跑一遍就行，用成熟工具                  |
| M4    | 图件分类  | 10%  | VLM zero-shot                |
| M5    | KG抽取  | 30%  | 核心价值，分层质量策略                  |
| M6    | 样本合成  | 40%  | 核心价值，含推理链条+Spatial Embedding |

### 2.1 M1+M2 文档解析（合并为一步）

**工具**：Marker（端到端，一键提取）
**兜底**：Qwen3-VL（Marker失败的扫描版老论文）

**输出**：

* 全文结构化Markdown（保留章节层级）

* 原始图片文件（自动提取）

* Figure Caption（自动关联）

* 基础表格提取

**DoD**：

* 文本完整性：抽样100篇，无明显丢段 ≥ 95%

* 图片提取率：≥ 90%

**为什么不用DocLayout-YOLO + GOT-OCR2**：

* Marker对英文学术PDF效果已经很好（端到端）

* 不需要bbox信息（按文档整体组织，不按页面）

* 地质论文公式不多，Marker OCR够用

* 奥卡姆剃刀：一个工具能解决的不用两个

### 2.2 M3 表格精提取 + 单位归一

**工具**：

* 标准表格：Camelot / Tabula（规则引擎，快速准确）

* 复杂跨页表格：Qwen3-VL（VLM兜底）

* 单位归一：pint库（g/t ↔ ppm；wt% ↔ ppm；oz/t 自动转换）

**输出**：每张表 → 结构化JSON（含表头、数据行、单位标准化标记）

**DoD**：

* 标准表格 cell-F1 ≥ 0.88

* 单位归一覆盖率 ≥ 95%

### 2.3 M4 图件分类 + VLM富化

**工具**：Qwen3-VL zero-shot 12类分类（不自训练head）

**12类图件分类**：

```
location_map / regional_geology / deposit_geology / cross_section /
drillhole_log / alteration_map / geochem_anomaly / geophysics_map /
ore_photo / thin_section / model_diagram / other
```

**按需VLM富化**：只对caption缺失或质量差的图做VLM描述

**DoD**：12类分类 macro-F1 ≥ 0.80

### 2.4 M5 知识图谱实体+关系抽取（核心）

**分层质量策略**：

* **Tier 1**：Claude Opus 精标100篇 → 黄金标准（人工逐条审核）

* **Tier 2**：Gemini 2.5 Pro 批量处理（1M上下文，整篇论文一次喂入）

* **全程**：Opus 抽检10%，不合格整批重跑

**实体类型（12类）**：

```
Deposit / Commodity / HostRock / Alteration / Fluid /
StructuralControl / Age / TectonicSetting / SourceRock /
Mineral / Element / MineralizationStyle
```

**关系类型（11类）**：

```
hosts / altered_by / dated_at / formed_in / derived_from /
controlled_by / associated_with / overprinted_by / contains /
spatially_with / temporally_with
```

**按文档类型的最低提取要求**：

* 期刊论文：至少 Deposit + Alteration + StructuralControl + Age

* JORC报告：至少 Deposit + Commodity + HostRock + MineralizationStyle

* 博士论文：尽量全部12类（信息最丰富）

**新增：七要素证据归属标注**（反向审视新增需求）

M5提取时，不仅提取实体/关系，还要标注每条证据支撑Mineral System七要素中的哪个：
- energy_source（能量源）
- fluid_source（流体源）
- fluid_pathway（流体通道）
- metal_source（金属源）
- precipitation_mechanism（沉淀机制）
- trap（圈闭/富集）
- preservation（保存条件）

**DoD**：entity-F1 ≥ 0.78，relation-F1 ≥ 0.65，七要素归属覆盖率 ≥ 80%

### 2.5 M6 训练样本合成（核心）

**产出4类训练样本**：

| 类型 | 描述        | 目标量        | 生成方式                                          |
| -- | --------- | ---------- | --------------------------------------------- |
| S1 | 长上下文文本预训练 | 1-2B token | 全文Markdown按矿系打tag                             |
| S2 | 多模态VQA对   | ≥200万对     | 图+caption+KG自动生成                              |
| S3 | 空间推理trace | 1-3万条      | Opus+o3精标 + Gemini批量 + 博士论文推理链条               |
| S4 | RL偏好对     | ≥10万对      | Opus(chosen) vs Sonnet(rejected) + KG验证reward |

**S1目标说明**：原方案S1≥50B token不现实（100K论文×5000token=5亿token），修正为1-2B token。

**S3是核心差异化产出**：利用博士论文推理链条 + Spatial Embedding生成高质量空间推理trace。

***

## 三、统一数据契约 MSM-DocSchema v2

### 3.1 设计决策

| 决策点       | 选择      | 理由                          |
| --------- | ------- | --------------------------- |
| 组织方式      | 按文档整体   | Marker输出是整篇Markdown，按页面切分多余 |
| bbox      | 不保留     | 非刚需，后训练工程师需要时可后补            |
| 矿系标签      | 6个标准化标签 | 冻结口径                        |
| KG内嵌      | 是       | 文档和KG一体化                    |
| quality字段 | 是       | 质量自报告，下游可过滤                 |

### 3.2 Schema示例

```json
{
  "doc_id": "sha256[:16]",
  "doc_type": "journal_paper",
  "source": {
    "platform": "Scopus",
    "url": "https://doi.org/10.2113/...",
    "license": "Subscription",
    "downloaded_at": "2026-05-18T10:00:00Z"
  },
  "meta": {
    "title": "Alteration Zoning at El Teniente...",
    "authors": [{"name": "Sillitoe, R.H.", "affiliation": "..."}],
    "year": 2005,
    "doi": "10.2113/gsecongeo.100.5.863",
    "language": "en",
    "mineral_system_tags": ["PORP-CUMO"],
    "deposit_examples": ["El Teniente"],
    "region": "Central Chilean Andes"
  },
  "content": {
    "abstract": "...",
    "sections": [
      {"heading": "Introduction", "level": 1, "text": "...", "subsections": []}
    ],
    "references": ["Sillitoe, 2010", "Seedorff et al., 2005"]
  },
  "figures": [
    {
      "fig_id": "fig_01",
      "caption": "Alteration zoning map of El Teniente...",
      "image_path": "images/{doc_id}/fig_01.png",
      "fig_type": "alteration_map"
    }
  ],
  "tables": [
    {
      "table_id": "tab_01",
      "caption": "Resource estimate",
      "headers": ["Category", "Tonnage (Mt)", "Au (g/t)"],
      "rows": [["Measured", "120.5", "0.85"]],
      "units_normalized": true
    }
  ],
  "kg_extracted": {
    "entities": [
      {"id": "e_001", "type": "Deposit", "name": "El Teniente", "props": {"size_class": "Giant"}}
    ],
    "relations": [
      {"head": "e_001", "rel": "altered_by", "tail": "e_002", "confidence": 0.92}
    ]
  },
  "quality": {
    "extraction_quality": 0.92,
    "kg_entity_f1": 0.79,
    "needs_review": false
  }
}
```

***

## 四、博士论文独立处理管线（核心创新）

### 4.1 核心洞察

**博士论文 ≠ 更长的期刊论文，而是"完整的推理教程"**

* 期刊论文：篇幅限制，推理过程被压缩（"观察A → 所以B"）

* 博士论文：完整推理链条（"观察A → 结合背景C → 排除D → 推断B → 验证E"）

### 4.2 博士论文扩展字段

在MSM-DocSchema基础上，博士论文额外包含：

```json
{
  "doc_type": "doctoral_thesis",
  "reasoning_cases": [
    {
      "case_id": "rc_01",
      "title": "从蚀变分带推断成矿类型",
      "reasoning_type": "inductive",
      "scale_from": "outcrop",
      "scale_to": "deposit",
      "steps": [
        {"step": 1, "type": "observation", "content": "...", "evidence": "Ch3.2"},
        {"step": 2, "type": "background_integration", "content": "...", "evidence": "Ch2"},
        {"step": 3, "type": "hypothesis_testing", "content": "...", "evidence": "Ch4.3"},
        {"step": 4, "type": "inference", "content": "...", "evidence": "Ch5"},
        {"step": 5, "type": "verification", "content": "...", "evidence": "Ch4.5"}
      ],
      "cot_format": "让我们一步步分析：\n1. ...\n2. ...",
      "usage": ["sft_cot", "dpo_chosen"]
    }
  ],
  "scale_linking_cases": [
    {
      "phenomenon": "黄铜矿交代黄铁矿",
      "scales": {
        "microscopic": {"observation": "...", "source": "Ch4.3"},
        "deposit": {"implication": "...", "source": "Ch5.2"}
      },
      "usage": ["sft_scale_linking"]
    }
  ],
  "knowledge_structure": {
    "deposit_type": "porphyry_cu",
    "global_examples": ["El Teniente", "Chuquicamata"],
    "key_features": ["concentric zoning", "telescoping"],
    "usage": ["graph_rag_skeleton", "cpt"]
  },
  "contrastive_cases": [
    {
      "question": "为什么是斑岩型而不是矽卡岩型？",
      "option_a": {"type": "porphyry", "evidence": "..."},
      "option_b": {"type": "skarn", "rejected_because": "..."},
      "usage": ["evaluation_benchmark"]
    }
  ]
}
```

### 4.3 博士论文多种用法

| 用法      | 数据来源                | 训练阶段       | 价值             |
| ------- | ------------------- | ---------- | -------------- |
| 推理链条训练  | reasoning_cases     | SFT        | 教模型完整推理过程（CoT） |
| 多尺度关联   | scale_linking_cases | SFT        | 训练尺度转换能力       |
| 知识图谱骨架  | knowledge_structure | GraphRAG   | 构建矿床类型知识框架     |
| DPO偏好对齐 | reasoning_cases     | DPO        | 作为chosen样本     |
| 评估基准    | contrastive_cases   | Evaluation | 生成对比推理题        |

***

## 五、Spatial Embedding层（Layer 2.5，核心创新）

### 5.1 问题诊断

当前只是"记录"空间信息（坐标、距离），没有让**空间成为知识表达的核心维度**。

### 5.2 四大组件

**组件1：概念空间向量库**

* 为每个地质概念生成空间嵌入向量

* 分层向量：512维文本嵌入（Sentence-BERT）+ 128维显式空间特征

* 显式特征：距离、温度、深度、形态等归一化到[0,1]

**组件2：空间关系图谱**

* 分层架构：矿床类型模板层（通用概念+典型关系）+ 具体矿床实例层（实测数据）

* 存储：JSON文件（Phase A不部署Neo4j）

* 支持图查询："从钾化带出发，向外500m会遇到什么？"

**组件3：多尺度空间索引**

* 尺度层级：显微 → 露头 → 矿床 → 区域

* 每个尺度有独立嵌入向量

* 支持跨尺度查询："显微观察X在矿床尺度意味着什么？"

**组件4：空间相似度索引**

* 技术：FAISS向量检索

* 检索策略：纯语义 / 空间约束 / 混合

* 支持："找到与El Teniente空间特征最相似的矿床"

### 5.3 与训练管线的集成

* **S3空间推理trace**：利用Spatial Embedding生成高质量空间推理QA

* **GraphRAG**：空间图谱增强多跳推理

* **评估**：空间相似度检索准确率作为评估指标

### 5.4 MVP验证

* 50篇论文 → 100个概念向量 → 2个空间图谱

* 评估：Top-5检索准确率 ≥ 70%

* 技术：Sentence-BERT（MVP）→ 微调Spatial-BERT（全量）

***

## 六、训练样本产出规格

### 6.1 S1 长上下文文本预训练（JSONL）

```json
{"mineral_system_tag": "OROG-AU", "text": "...", "source_doc_id": "sha", "token_count": 2450}
```

**目标**：1-2B token
**配比**：论文60% + JORC/NI43-101 30% + 书籍10%

### 6.2 S2 多模态VQA对（JSONL）

```json
{"image": "images/{doc_id}/fig_01.png", "question": "这张蚀变分带图显示了什么空间规律？", "answer": "...", "mineral_system_tag": "PORP-CUMO"}
```

**目标**：≥200万对

### 6.3 S3 空间推理trace（JSONL）— 核心差异化

```json
{
  "images": ["images/map.png", "images/section.png"],
  "question": "给定这些野外观察和区域背景，推断成矿类型并说明推理过程",
  "thought": "Step 1: 观察到同心环状蚀变分带... Step 2: 结合区域构造背景... Step 3: 排除浅成低温可能... Step 4: 推断为斑岩系统...",
  "answer": "斑岩型Cu-Mo矿床",
  "kg_grounding": [{"entity": "El Teniente", "relation": "altered_by", "evidence": "Section 3.2"}],
  "source": "thesis_zhang2019/reasoning_case_01"
}
```

**目标**：1-3万条（质量优先于数量）
**来源**：博士论文推理链条 + Spatial Embedding生成

### 6.4 S4 RL偏好对（JSONL）

```json
{
  "prompt": "什么构造要素控制了El Teniente矿化的空间分布？",
  "chosen": "El Teniente矿化受三组构造要素控制：(1) NW向断裂带...[详细推理]",
  "rejected": "El Teniente矿化主要受断裂控制...[笼统]",
  "reward_breakdown": {"kg_consistency": 0.9, "spatial_logic": 0.85, "completeness": 0.88}
}
```

**目标**：≥10万对
**生成**：Opus(chosen) vs Sonnet(rejected) + KG验证reward

***

## 七、质量门控与验收标准

### 7.1 各模块DoD

| 模块      | 指标           | 目标值           | 测量方法           |
| ------- | ------------ | ------------- | -------------- |
| M1+M2   | 文本完整性        | ≥ 95%         | 抽样100篇人工核对     |
| M1+M2   | 图片提取率        | ≥ 90%         | 自动统计           |
| M3      | 表格cell-F1    | ≥ 0.88        | 抽样50张表人工标注对比   |
| M4      | 图件分类macro-F1 | ≥ 0.80        | 200张图人工标注对比    |
| M5      | entity-F1    | ≥ 0.78        | 200篇标注集        |
| M5      | relation-F1  | ≥ 0.65        | 200篇标注集        |
| M6-S3   | 推理trace质量    | 人工审核通过率 ≥ 90% | Opus抽检 + 10%人工 |
| Spatial | 相似度检索Top-5   | ≥ 70%         | 地质学家评估         |

### 7.2 质量分层策略

* **Tier 1**（黄金标准）：Opus+o3精标，人工逐条审核，幻觉率=0%

* **Tier 2**（批量生产）：Gemini 2.5 Pro，Opus抽检10%，通过率≥90%

* **不合格处理**：整批重跑，不做局部修补

***

## 八、关键设计决策记录

| &#x23; | 决策点               | 选择                | 否决方案                    | 理由                     |
| ------ | ----------------- | ----------------- | ----------------------- | ---------------------- |
| 1      | 文档解析工具            | Marker            | DocLayout-YOLO+GOT-OCR2 | 奥卡姆剃刀，Marker端到端够用      |
| 2      | Schema组织方式        | 按文档整体             | 按页面(pages数组)            | 不需要bbox，Marker输出是整篇    |
| 3      | KG存储              | JSON文件            | Neo4j                   | Phase A不需要图数据库         |
| 4      | 图件分类              | VLM zero-shot 12类 | CLIP+自训练head            | 2026年VLM直接能做，不需要训练     |
| 5      | S1目标量             | 1-2B token        | 50B token(原方案)          | 100K论文撑死5亿token，50B不现实 |
| 6      | S3目标量             | 1-3万条             | 5万条(原方案)                | 质量优先于数量，Opus生成成本高      |
| 7      | 博士论文处理            | 独立管线+推理链条         | 与期刊论文相同                 | 核心创新，推理链条是独特价值         |
| 8      | Spatial Embedding | 分层向量512+128       | 纯512维隐式                 | 显式特征可解释、可调试            |
| 9      | 空间图谱粒度            | 模板层+实例层           | 全局大图                    | 支持类比推理                 |
| 10     | 矿系标签              | 6个固定标签            | 开放式deposit_type         | 采用原方案口径                |

***

## 九、实施路线图

### Phase A.1（3天）— 缺失目录 + 采集计划

* Day 1：既有材料盘点 + 去重脚本

* Day 2：6矿系×4类型缺失目录初稿

* Day 3：缺失目录定稿 + 采集计划

### Phase A.2（11天）— 采集 + 结构化处理

* Day 4-9：并行采集（论文+JORC+博士论文）

* Day 7-14：M1-M4结构化处理（与采集后段并行）

* Day 10-14：M5 KG抽取（分层：Opus精标 + Gemini批量）

### Phase A.3（7天）— 核心创新

* Day 15-17：博士论文推理链条提取

* Day 18-19：Spatial Embedding构建（概念向量+空间图谱）

* Day 20-21：M6训练样本合成（S1-S4）+ 质量验收

### 交付物清单

| 交付物               | 格式                     | 说明                                    |
| ----------------- | ---------------------- | ------------------------------------- |
| 结构化文档集            | JSON（MSM-DocSchema v2） | 全量文档的Layer 1产出                        |
| 知识图谱              | JSONL（kg_dump.jsonl）   | 实体+关系，后训练工程师可导入Neo4j                  |
| 博士论文推理案例          | JSON                   | reasoning_cases + scale_linking_cases |
| Spatial Embedding | JSON + FAISS索引         | 概念向量 + 空间图谱 + 相似度索引                   |
| S1预训练语料           | JSONL                  | 1-2B token                            |
| S2 VQA对           | JSONL                  | ≥200万对                                |
| S3空间推理trace       | JSONL                  | 1-3万条                                 |
| S4偏好对             | JSONL                  | ≥10万对                                 |
| 数据集卡              | Markdown               | 统计信息+质量报告                             |

***

## 十、反向审视：新增数据需求（从输出倒推）

> 基于Mineral System Assessment统一输出模板的反向审视，发现5个新增数据需求。
> 没有这些数据，模型无法生成模板中最核心的内容。

### 10.1 新需求1：矿床类型判别规则库 ⭐⭐⭐⭐⭐

**支撑模板模块**：§2 矿床类型判别（排除法推理+逐特征对比）

**数据结构**：每对容易混淆的矿床类型，提取5-8个判别特征

```json
{
  "comparison_pair": ["orogenic_gold", "intrusion_related_gold"],
  "discriminating_features": [
    {
      "feature": "与侵入体空间关系",
      "type_a_value": "无需直接接触，可距侵入体>5km",
      "type_b_value": "必须在侵入体<1km范围内",
      "diagnostic_power": "high"
    }
  ],
  "decision_logic": "如果无侵入体接触 + 无钾长石化 + Au-As-Sb-W → 造山型"
}
```

**需要覆盖的对比对**：造山金vsIRGS、造山金vs浅成低温、斑岩vs矽卡岩、VMSvsSEDEX、IOCGvs斑岩、岩浆Nivs热液Ni

**提取来源**：教科书+综述论文（Groves, Sillitoe, Hedenquist等）
**提取方式**：Opus精标

### 10.2 新需求2：七要素证据归属标注 ⭐⭐⭐⭐⭐

**支撑模板模块**：§3 Mineral System七要素评估

**数据结构**：每篇论文中的关键证据标注其支撑的要素

```json
{
  "mineral_system_evidence": [
    {
      "evidence": "花岗闪长斑岩侵入（620 Ma）",
      "supports_element": "energy_source",
      "strength": "strong",
      "source_section": "Section 3.1"
    }
  ]
}
```

**实现方式**：M5 KG抽取时增加标注（工作量+30%）
**DoD**：七要素归属覆盖率 ≥ 80%

### 10.3 新需求3：空间分带模型 ⭐⭐⭐⭐⭐（最关键）

**支撑模板模块**：§5 成矿模型与找矿标志体系

**数据结构**：每个矿床类型的"距离-矿物-元素-蚀变"定量分带模型

```json
{
  "deposit_type": "orogenic_gold_mesozonal",
  "based_on_deposits": ["Obuasi", "Kalgoorlie", "Geita"],
  "zones": [
    {
      "zone_name": "ore_zone",
      "distance_m": 0,
      "alteration": ["silicification", "Fe-dolomite"],
      "geochemistry": {"Au_gpt": ">1", "As_ppm": ">1000", "Sb_ppm": ">100"}
    },
    {
      "zone_name": "proximal",
      "distance_m": [0, 20],
      "alteration": ["silicification", "Fe-dolomite_veinlets"],
      "geochemistry": {"As_ppm": "200-1000", "Sb_ppm": "30-100"}
    },
    {
      "zone_name": "medial",
      "distance_m": [20, 100],
      "alteration": ["carbonate_veinlets"],
      "geochemistry": {"As_ppm": "50-200", "W_ppm": "5-20"}
    },
    {
      "zone_name": "distal",
      "distance_m": [100, 500],
      "geochemistry": {"As_ppm": "20-50 (2-3x background)"}
    }
  ],
  "pathfinder_priority": ["As", "Sb", "W", "Bi", "Au"],
  "along_strike": {
    "towards_shallow": "Sb增加, As/Au升高",
    "towards_deep": "Bi增加, 磁黄铁矿出现"
  }
}
```

**提取来源**：综述论文（通用模型）+ 具体矿床论文（实测数据）
**每个矿系需要**：1个通用模型 + 5-10个实测数据

### 10.4 新需求4：勘探方法论知识 ⭐⭐⭐⭐

**支撑模板模块**：§7 勘探方法论建议

**数据结构**：什么地质情况用什么方法最有效

```json
{
  "method": "IP_survey",
  "effective_for": ["orogenic_gold", "vms", "porphyry"],
  "target_anomaly": "高极化率(>20mV/V) + 中低电阻率",
  "limitations": ["碳质片岩假异常", "深度<200m"],
  "when_not_to_use": "目标为氧化物矿物（用磁测替代）",
  "field_tips": ["必须结合地质图区分假异常", "异常轴向平行矿体走向"]
}
```

**提取来源**：教科书 + JORC报告"Exploration"章节
**覆盖方法**：地质填图、化探、物探（磁/重/激电/CSAMT）、钻探设计

### 10.5 新需求5：矿床对比差异点 ⭐⭐⭐⭐

**支撑模板模块**：§4 全球类比矿床

**数据结构**：矿床间的具体相似点+差异点+对勘探的启示

```json
{
  "deposit_a": "Kadoma_Cam_Motor",
  "deposit_b": "Obuasi",
  "similarity_score": 0.93,
  "similarities": ["太古宙绿岩带", "剪切带控矿", "石英脉+浸染型"],
  "differences": [
    {"aspect": "围岩", "a": "基性火山岩", "b": "沉积岩turbidite"}
  ],
  "exploration_implications": [
    "Obuasi浸染型贡献60%资源量 → Kadoma必须系统评估浸染型规模"
  ]
}
```

**提取来源**：对比研究论文 + 综述论文
**每个矿系需要**：10-20对高质量对比

### 10.6 对M5/M6工作量的影响

| 新增任务 | 影响模块 | 工作量增加 | 优先级 |
|---------|---------|-----------|--------|
| 判别规则库 | M6新增 | 新任务 | 必须有 |
| 七要素归属 | M5增强 | +30% | 必须有 |
| 空间分带模型 | M6新增 | 新任务（最重） | 必须有 |
| 勘探方法论 | M6新增 | 新任务 | 锦上添花 |
| 矿床对比差异 | M6新增 | 新任务 | 锦上添花 |

---

## 十一、风险与对策

| 风险                     | 影响 | 对策                     |
| ---------------------- | -- | ---------------------- |
| Marker在某类PDF上质量不达标     | 中  | 用Qwen3-VL兜底；先跑50篇样本验证  |
| 博士论文推理链条提取质量不够         | 高  | Opus精标+人工审核；建立黄金标准后再批量 |
| Spatial Embedding效果不明显 | 中  | MVP先验证50篇；效果不好则简化为纯KG  |
| S3空间推理trace数量不足        | 中  | 质量优先；1万条高质量 > 5万条低质量   |
| 采集速度不够                 | 低  | 已有大量资料，增量采集为主          |

***

**文档版本**: v2.0
**最后更新**: 2026-05-18
**维护者**: 邹心宇
