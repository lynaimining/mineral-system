# 地质空间推理后训练 — 数据JSON化研发档案

**项目**: LynAI Mining 地质空间推理后训练
**版本**: v1.1（已整合Spatial Embedding设计）
**日期**: 2026-05-18
**负责人**: 邹心宇

---

## 一、方案概述

### 1.1 核心原则

**全链路JSON化** — 从文档提取到训练数据生成，每个环节都使用统一的JSON Schema，确保数据可追溯、可复现、可迭代。

**可逆性保证** — 原始PDF文件始终保留，每一层都是派生物，任何环节不满意都可以重跑。

**分层存储** — 提取层、知识层、训练层独立存储，用`doc_id`关联，支持并行处理和增量更新。

### 1.2 数据源清单

| 数据源 | 数量 | 核心价值 | 主要用途 |
|--------|------|----------|----------|
| 学术期刊论文 | 100,000篇 | 成矿机理、空间推理逻辑 | SFT核心 + CPT |
| 博士论文 | ~500篇 | **完整推理链条**、多尺度关联 | SFT推理链条 + DPO chosen + CoT训练 |
| JORC报告 | 1,139家 | 标准化定量数据、矿体几何 | CPT + RAG + 定量QA |
| NI 43-101报告 | ~9,721份 | 北美项目数据、可研分析 | CPT + RAG (Phase 2) |
| 专业书籍 | 443本 | 系统性知识框架、术语体系 | CPT知识底座 |

### 1.3 架构层级

**核心创新**：增加Layer 2.5 Spatial Embedding层，解决"把知识属性嵌入到空间"的需求

```
Layer 1: 文档提取（Marker/Camelot产出）
    ↓
Layer 2: 知识结构化（空间锚点、实体、关系）
    ↓
Layer 2.5: Spatial Embedding（新增 — 核心创新）
    ├── 概念空间向量化
    ├── 空间关系图谱
    ├── 多尺度空间索引
    └── 空间相似度索引
    ↓
Layer 3: 训练数据（CPT/SFT/DPO）
```

### 1.4 目录结构

```
data/
├── layer1_extraction/           # 提取层（Marker/Camelot产出）
│   ├── papers/                  # 期刊论文
│   ├── theses/                  # 博士论文
│   ├── jorc/                    # JORC报告
│   ├── ni43101/                 # NI 43-101
│   └── books/                   # 书籍
├── layer2_knowledge/            # 知识结构化层（LLM提取）
│   ├── spatial_anchors/         # 空间锚点
│   ├── figures/                 # 图件元数据
│   └── tables/                  # 表格结构化
├── layer2.5_spatial_embedding/  # 空间嵌入层（新增）
│   ├── concept_vectors/         # 概念空间向量
│   ├── spatial_graphs/          # 空间关系图谱
│   ├── multiscale_index/        # 多尺度空间索引
│   └── similarity_index/        # 空间相似度索引
├── layer3_training/             # 训练数据层
│   ├── cpt/                     # CPT语料 (JSONL)
│   ├── sft/                     # SFT QA对 (JSONL)
│   └── dpo/                     # DPO偏好对 (JSONL)
├── manifest.json                # 全局索引
└── schema/                      # JSON Schema定义文件
```

---

## 二、Layer 1: 文档提取层

### 2.1 学术期刊论文 Schema

**文件命名**: `paper_{doi_hash}.json`

**关键字段**:
- `doc_id`: 全局唯一标识符
- `meta.deposit_type`: **矿床类型标注**（用于按类型筛选，MVP阶段关键）
- `meta.deposit_names`: 论文涉及的具体矿床名称
- `meta.region`: 区域归属
- `content.sections`: 递归章节结构（保持Marker原始输出）
- `figures`: 图件列表（含caption、路径、页码）
- `tables`: 表格列表（含表头、数据行）

**设计决策**:
- ✅ Layer 1就标注矿床类型（方便筛选）
- ✅ 引用文献简单存字符串数组（重点是论文内部空间关系，不是引用关系）
- ✅ 细粒度标注（如`contains_spatial_info`）在Layer 2做

**Schema示例**:
```json
{
  "doc_id": "paper_a1b2c3d4",
  "doc_type": "journal_paper",
  "meta": {
    "title": "Alteration Zoning at El Teniente Porphyry Cu-Mo Deposit",
    "authors": ["Sillitoe, R.H.", "Perelló, J."],
    "journal": "Economic Geology",
    "year": 2005,
    "doi": "10.2113/gsecongeo.100.5.863",
    "language": "en",
    "keywords": ["porphyry copper", "alteration zoning"],
    "deposit_type": "porphyry_cu_mo",
    "deposit_names": ["El Teniente"],
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
      "caption": "Alteration zoning map...",
      "image_path": "images/paper_a1b2c3d4/fig_01.png",
      "page": 5
    }
  ],
  "tables": [...],
  "processing": {
    "extracted_at": "2026-05-18T10:00:00Z",
    "marker_version": "0.3.2",
    "extraction_quality": 0.92
  }
}
```

---

### 2.2 博士论文 Schema — 核心创新

**文件命名**: `thesis_{id}.json`

**核心洞察**: 博士论文 ≠ 更长的期刊论文，而是**完整的推理教程**

**独特价值**:
- 完整的推理链条："观察 → 背景整合 → 假设检验 → 推断 → 验证"
- 多尺度因果关联：显微观察如何支撑矿床尺度的解释
- 推理过程透明：为什么这样解释？排除了哪些可能？

**关键字段**:
- `reasoning_cases`: **跨章节推理案例**（核心价值）
- `scale_linking_cases`: 多尺度关联案例
- `knowledge_structure`: 知识图谱骨架（从文献综述提取）
- `contrastive_cases`: 对比辨析案例（从讨论章节提取）

**Schema示例**:
```json
{
  "doc_id": "thesis_zhang2019",
  "doc_type": "doctoral_thesis",
  "meta": {
    "title": "冈底斯成矿带东段斑岩铜矿成矿作用研究",
    "author": "张三",
    "university": "中国地质大学（北京）",
    "year": 2019,
    "deposit_type": "porphyry_cu",
    "deposit_names": ["驱龙", "甲玛"],
    "region": "冈底斯成矿带"
  },

  "reasoning_cases": [
    {
      "case_id": "rc_01",
      "title": "从蚀变分带推断成矿类型",
      "reasoning_type": "inductive",
      "scale_from": "outcrop",
      "scale_to": "deposit",
      "steps": [
        {
          "step": 1,
          "type": "observation",
          "content": "野外观察到钾化带→绢英岩化带→青磐岩化带的同心环状分带",
          "evidence": "第3章3.2节，图3-5"
        },
        {
          "step": 2,
          "type": "background_integration",
          "content": "结合区域上斑岩铜矿的典型特征",
          "evidence": "第2章文献综述"
        },
        {
          "step": 3,
          "type": "hypothesis_testing",
          "content": "排除了浅成低温热液的可能（缺少明矾石等典型矿物）",
          "evidence": "第4章4.3节讨论"
        },
        {
          "step": 4,
          "type": "inference",
          "content": "推断为斑岩系统，蚀变分带反映温度-压力梯度",
          "evidence": "第5章综合讨论"
        },
        {
          "step": 5,
          "type": "verification",
          "content": "锆石U-Pb年龄（45.2±0.8 Ma）与区域斑岩成矿期一致",
          "evidence": "第4章4.5节"
        }
      ],
      "cot_format": "让我们一步步分析：\n1. 首先观察到...\n2. 结合区域背景...\n3. 排除了...的可能\n4. 因此推断为...\n5. 这个推断可以用...验证",
      "usage": ["sft_cot", "dpo_chosen"]
    }
  ],

  "scale_linking_cases": [
    {
      "phenomenon": "黄铜矿-黄铁矿交代关系",
      "scales": {
        "microscopic": {"observation": "黄铜矿沿黄铁矿裂隙交代", "source": "Ch4.3"},
        "outcrop": {"observation": "网脉状硫化物矿化", "source": "Ch3.4"},
        "deposit": {"implication": "矿体呈筒状产出", "source": "Ch5.2"},
        "regional": {"implication": "位于斑岩成矿带", "source": "Ch2.5"}
      },
      "usage": ["sft_scale_linking"]
    }
  ],

  "knowledge_structure": {
    "deposit_type": "porphyry_cu",
    "global_examples": ["El Teniente", "Chuquicamata", "Oyu Tolgoi"],
    "key_features": ["concentric zoning", "telescoping"],
    "source": "Ch2 Literature Review",
    "usage": ["graph_rag_skeleton", "cpt"]
  },

  "contrastive_cases": [
    {
      "question": "为什么是斑岩型而不是矽卡岩型？",
      "option_a": {"type": "porphyry", "evidence": "...", "reasoning": "..."},
      "option_b": {"type": "skarn", "rejected_because": "缺少典型矽卡岩矿物组合"},
      "source": "Ch5.3 Discussion",
      "usage": ["evaluation_benchmark"]
    }
  ],

  "chapters": [...]
}
```

**博士论文的多种用法**:

| 用法 | 数据来源 | 训练阶段 | 价值 |
|------|----------|----------|------|
| 推理链条训练 | `reasoning_cases` | SFT | 教模型完整推理过程（CoT格式） |
| 多尺度关联 | `scale_linking_cases` | SFT | 训练尺度转换能力 |
| 知识图谱骨架 | `knowledge_structure` | GraphRAG | 构建矿床类型知识框架 |
| DPO偏好对齐 | `reasoning_cases` | DPO | 作为chosen样本（详细推理） |
| 评估基准 | `contrastive_cases` | Evaluation | 生成对比推理题 |
| 系统性知识 | `chapters` | CPT | 全文喂入建立知识底座 |

---

### 2.3 JORC报告 Schema

**文件命名**: `jorc_{company}_{project}_{year}.json`

**核心价值**: 标准化定量数据、矿体几何、钻孔数据

**关键字段**:
- `resource_estimate`: 资源量估算（保留原文分类，不强行映射）
- `drillhole_data`: **钻孔数据存为CSV/Parquet**，JSON只存路径
- `orebody_geometry`: 矿体几何参数
- `economic_analysis`: 经济分析（NI 43-101特有）

**设计决策**:
- ✅ 钻孔数据用CSV/Parquet单独存（JSON会很臃肿）
- ✅ 资源量分类保留原文（Measured/Indicated/Inferred或331/332/333）

**Schema示例**:
```json
{
  "doc_id": "jorc_newcrest_cadia_2023",
  "doc_type": "jorc_report",
  "meta": {
    "company": "Newcrest Mining",
    "project": "Cadia Valley",
    "country": "Australia",
    "commodity": ["Au", "Cu"],
    "report_date": "2023-06-30",
    "deposit_type": "porphyry_au_cu",
    "deposit_names": ["Cadia East", "Cadia Hill"],
    "region": "Lachlan Fold Belt, NSW"
  },
  "resource_estimate": {
    "effective_date": "2023-06-30",
    "cutoff_grade": {"value": 0.2, "unit": "g/t Au_eq"},
    "categories": [
      {
        "category": "Measured",
        "tonnage_mt": 120.5,
        "grades": {"Au_gpt": 0.85, "Cu_pct": 0.32},
        "contained_metal": {"Au_moz": 3.29, "Cu_kt": 385.6}
      }
    ]
  },
  "drillhole_data": {
    "collar_file": "data/jorc_newcrest_cadia_2023/collar.csv",
    "survey_file": "data/jorc_newcrest_cadia_2023/survey.csv",
    "assay_file": "data/jorc_newcrest_cadia_2023/assay.csv",
    "total_holes": 1250,
    "total_meters": 485000
  },
  "orebody_geometry": {
    "strike": "NNW",
    "strike_length_m": 2500,
    "dip": "70W",
    "width_m": {"min": 50, "max": 400, "avg": 200},
    "depth_extent_m": 1200
  }
}
```

---

### 2.4 NI 43-101 Schema

与JORC类似，额外包含`economic_analysis`字段（NPV、IRR、CAPEX、OPEX等）。

---

### 2.5 专业书籍 Schema

**文件命名**: `book_{isbn_or_id}.json`

按章节切分，保留层级结构，用于CPT知识底座。

---

## 三、Layer 2.5: Spatial Embedding层（核心创新）

> **完整设计文档**: 请参阅 `Spatial_Embedding补充设计.md`

### 3.0 设计背景

**问题诊断**：当前Layer 2的`spatial_anchors`只是记录空间信息（坐标、距离、方位），但没有：
- ❌ 为地质概念生成空间嵌入向量
- ❌ 显式建模可计算的空间关系图谱
- ❌ 建立多尺度统一空间索引
- ❌ 让空间信息可以用于相似度检索和推理

**核心洞察**：地质知识的本质是空间的，不能只是把空间当作"属性"来记录，而应该让**空间成为知识表达的核心维度**。

### 3.1 四大核心组件

#### 组件1：概念空间向量库
- **目的**：为每个地质概念（如"钾化带"、"斑岩铜矿"）生成空间嵌入向量
- **向量设计**：分层向量（512维文本嵌入 + 128维显式空间特征）
- **文件**：`spatial_embeddings/concept_vectors.json`

#### 组件2：空间关系图谱
- **目的**：显式建模可计算的空间关系（支持图查询）
- **架构**：分层图谱（矿床类型模板层 + 具体矿床实例层）
- **存储**：MVP用JSON+NetworkX，全量用Neo4j
- **文件**：`spatial_embeddings/spatial_graphs/`

#### 组件3：多尺度空间索引
- **目的**：同一观察在不同尺度的统一空间表达
- **尺度层级**：显微 → 露头 → 矿床 → 区域
- **文件**：`spatial_embeddings/multiscale_index.json`

#### 组件4：空间相似度索引
- **目的**：基于空间特征的矿床相似度检索
- **技术**：FAISS向量检索
- **检索策略**：纯语义检索 / 空间约束检索 / 混合检索
- **文件**：`spatial_embeddings/similarity_index/`

### 3.2 实现细节

**向量维度设计**：
- 文本嵌入512维：用Sentence-BERT编码语义和隐式空间模式
- 显式特征128维：距离、温度、深度、形态等归一化特征
- 分层存储，检索时可灵活组合

**图谱粒度设计**：
- 模板层：通用概念 + 典型空间关系（用于QA生成、类比推理）
- 实例层：具体观察 + 实测数据（用于定量预测、相似度检索）
- 用`instance_of`关系连接两层

**多尺度索引设计**：
- 每个尺度有独立的嵌入向量
- `scale_normalized`字段（0-1）支持跨尺度查询
- 尺度间有显式的过渡逻辑

### 3.3 与训练管线的集成

**CPT阶段**：不变，全文喂入建立知识底座

**SFT阶段**：利用Spatial Embedding生成空间推理QA对
- 空间相似度推理QA："找到与El Teniente空间特征最相似的矿床"
- 图查询推理QA："从钾化带出发，向外500m会遇到什么？"
- 跨尺度推理QA："显微观察X在矿床尺度意味着什么？"

**GraphRAG阶段**：LazyGraphRAG不仅是文本图谱，还是**空间图谱**

### 3.4 MVP验证方案

**验证数据**：50篇论文 → 100个概念 → 2个空间图谱
**评估指标**：
- 相似度检索准确率（Top-5中地质学家认可的比例）
- 图查询合理性（地质学家打分1-5分）
- 跨尺度推理一致性（逻辑自洽性）

**技术选型**：
- 向量生成：Sentence-BERT（MVP）→ Spatial-BERT（全量）
- 图谱存储：JSON+NetworkX（MVP）→ Neo4j（全量）
- 向量检索：FAISS

---

## 四、Layer 2: 知识结构化层

### 3.1 空间锚点 Schema

**文件命名**: `anchor_{doc_id}.json`

**核心内容**:
- 地理坐标、成矿带归属、构造背景
- 矿床分类（类型、亚类、规模）
- 观察尺度（district/deposit/outcrop/thin_section）
- **空间关系**（分带序列、构造控制、垂向分带）

**Schema示例**:
```json
{
  "doc_id": "paper_a1b2c3d4",
  "spatial_anchors": {
    "location": {
      "coordinates": {"lat": -34.08, "lon": -70.35},
      "geo_names": ["El Teniente", "Chile", "Andes"],
      "metallogenic_belt": "Central Chilean Porphyry Belt"
    },
    "deposit_classification": {
      "type": "Porphyry Cu-Mo",
      "size_class": "Giant (>10 Mt Cu)"
    },
    "spatial_relationships": [
      {
        "relation_type": "zoning_sequence",
        "from": "potassic core",
        "to": "propylitic halo",
        "direction": "outward",
        "distance_m": 2000,
        "evidence": "Section 3.2, Fig. 4"
      }
    ]
  }
}
```

---

### 3.2 图件元数据 Schema

**文件命名**: `fig_{doc_id}.json`

**核心内容**:
- CLIP分类结果（地质图/剖面图/照片）
- VLM富化描述（只对caption缺失或质量差的图做）
- 空间信息（地图比例尺、方位、空间特征）

---

## 四、Layer 3: 训练数据层

### 4.1 CPT语料 (JSONL)

**文件**: `cpt_{source}.jsonl`（每行一条）

```json
{"doc_id": "paper_a1b2c3d4", "source_type": "journal_paper", "text": "...", "token_count": 2450}
```

---

### 4.2 SFT QA对 (JSONL)

**文件**: `sft_spatial_reasoning.jsonl`

**QA类型**:
- 分带推理（Zoning）
- 构造控制（Structural）
- 尺度关联（Scale-linking）
- 类比推理（Analog）
- 预测推理（Predictive）
- 定量预测（Quantitative，来自JORC）
- 推理链条（Reasoning Chain，来自博士论文）

**Schema示例**:
```json
{
  "qa_id": "sft_001",
  "doc_id": "paper_a1b2c3d4",
  "source_type": "journal_paper",
  "qa_type": "zoning_reasoning",
  "tier": 1,
  "system": "你是一位资深经济地质学家，擅长空间推理和成矿预测。",
  "conversations": [
    {
      "role": "user",
      "content": "在El Teniente斑岩铜矿中，从钾化带核心向外移动2km，你会依次观察到什么蚀变组合变化？"
    },
    {
      "role": "assistant",
      "content": "从El Teniente钾化带核心向外2km，蚀变分带序列如下：\n1. 钾化带（0-500m）：钾长石+黑云母+磁铁矿...\n2. 绢英岩化带（500-1200m）：石英+绢云母+黄铁矿...\n..."
    }
  ],
  "metadata": {
    "generated_by": "claude-opus-4",
    "verified_by": "o3",
    "human_reviewed": true,
    "quality_score": 0.95
  }
}
```

---

### 4.3 DPO偏好对 (JSONL)

**文件**: `dpo_pairs.jsonl`

**chosen来源**: Claude Opus（详细推理）或博士论文推理段落
**rejected来源**: Claude Sonnet（简化版本）或期刊论文简化描述

```json
{
  "dpo_id": "dpo_001",
  "prompt": "什么构造要素控制了El Teniente矿化的空间分布？",
  "chosen": "El Teniente矿化受三组构造要素控制：(1) NW向Teniente断裂带...[详细]",
  "rejected": "El Teniente矿化主要受断裂控制...[笼统]",
  "chosen_model": "claude-opus-4",
  "rejected_model": "claude-sonnet-4"
}
```

---

## 五、分阶段使用策略

### 5.1 博士论文 vs 期刊论文的差异化使用

| 训练阶段 | 博士论文用法 | 期刊论文用法 |
|----------|-------------|-------------|
| **CPT** | 全文喂入（包括文献综述），建立系统性知识框架 | 全文喂入，覆盖广度 |
| **SFT** | 只用`reasoning_cases`和`scale_linking_cases`，训练推理能力 | 生成"快速判断"类QA |
| **DPO** | `reasoning_cases`作为chosen（详细推理） | 简化版本作为rejected |
| **GraphRAG** | `knowledge_structure`作为图谱骨架 | 作为图谱节点 |
| **Evaluation** | `contrastive_cases`生成评估题 | 补充评估题 |

---

### 5.2 数据配比建议

**CPT阶段** (1-2B tokens):
- 期刊论文: 60%
- JORC/NI 43-101: 30%
- 书籍: 10%
- 博士论文: 全文喂入（不单独计入配比，作为质量提升）

**SFT阶段** (8-15K QA对):
- 期刊论文: 50%（快速判断类）
- 博士论文: 30%（推理链条类）
- JORC: 15%（定量预测类）
- 书籍: 5%（教学式QA）

**DPO阶段** (5-10K偏好对):
- 博士论文推理段落 vs 期刊论文简化版本: 70%
- Opus vs Sonnet生成对: 30%

---

## 六、ID体系与文件管理

### 6.1 doc_id生成规则

**格式**: `{type}_{unique_identifier}`

**示例**:
- 期刊论文: `paper_{doi_hash}` (如 `paper_a1b2c3d4`)
- 博士论文: `thesis_{author_year}` (如 `thesis_zhang2019`)
- JORC: `jorc_{company}_{project}_{year}` (如 `jorc_newcrest_cadia_2023`)
- NI 43-101: `ni43101_{company}_{project}_{year}`
- 书籍: `book_{isbn}` 或 `book_{id}`

**唯一性保证**: 使用SHA256哈希前8位或标准化命名

---

### 6.2 Manifest全局索引

**文件**: `manifest.json`

**作用**: 追踪所有文档的处理状态

```json
{
  "project": "lynai_geo_spatial_reasoning",
  "version": "1.0",
  "updated_at": "2026-05-18T10:00:00Z",
  "stats": {
    "papers": {"total": 100000, "extracted": 0, "anchored": 0, "qa_generated": 0},
    "theses": {"total": 500, "extracted": 0, "anchored": 0, "qa_generated": 0},
    "jorc": {"total": 1139, "extracted": 0, "anchored": 0, "qa_generated": 0}
  },
  "processing_log": [
    {"timestamp": "2026-05-18T10:00:00Z", "action": "extraction_started", "doc_id": "paper_a1b2c3d4"}
  ]
}
```

---

## 七、实施路线图

### Phase 1: MVP验证（Week 1-2）

1. 精选50篇论文（斑岩Cu 25篇 + 造山Au 25篇）
2. 提取为Layer 1 JSON
3. 生成200条QA对
4. LoRA微调验证效果
5. **Go/No-Go决策**

### Phase 2: 全量处理（Week 3-7）

1. Marker多机并行解析100K论文
2. CLIP图件筛选 + 按需VLM富化
3. 空间锚点提取（Layer 2）
4. Opus+o3精标 + Gemini批量QA生成

### Phase 3: 训练与评估（Week 8-12）

1. CPT (1-2B tokens)
2. LoRA SFT (8-15K QA对)
3. DPO对齐 (5-10K偏好对)
4. LazyGraphRAG搭建
5. MSM-Bench评估

---

## 八、关键决策记录

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 存储粒度 | 每文档每层一个JSON | 并行友好，单篇失败不影响全局 |
| 矿床类型标注 | Layer 1就标注 | 方便按类型筛选，MVP阶段关键 |
| 引用关系 | 简单存字符串数组 | 重点是论文内部空间关系 |
| 细粒度标注 | Layer 2做 | Layer 1保持Marker原始输出 |
| 钻孔数据 | CSV/Parquet单独存 | JSON会臃肿，表格数据用表格格式 |
| 资源量分类 | 保留原文 | 不同标准不完全等价，强行映射丢失信息 |
| 博士论文处理 | 独立Schema，提取推理案例 | 核心价值是推理链条，不是信息量 |

---

## 九、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| Schema后期需要调整 | 中 | 可逆设计，写批量迁移脚本即可 |
| 博士论文推理案例提取质量 | 高 | 用Opus+人工审核，建立黄金标准 |
| 钻孔数据量过大 | 中 | 用Parquet压缩存储，按需加载 |
| 不同数据源格式差异 | 中 | 统一Schema接口，内部字段灵活 |

---

## 十、附录

### 10.1 标准化矿床类型列表

- `porphyry_cu_mo`
- `porphyry_cu_au`
- `orogenic_au`
- `carlin_au`
- `epithermal_au_ag`
- `vms_cu_zn`
- `iocg_cu_au`
- `magmatic_ni_cu_pge`
- `sediment_hosted_cu`
- `skarn_cu_fe`
- ...

### 10.2 空间关系类型列表

- `zoning_sequence` (分带序列)
- `structural_control` (构造控制)
- `vertical_telescoping` (垂向分带)
- `scale_linking` (尺度关联)
- `temporal_sequence` (时间序列)

---

**文档版本**: v1.0
**最后更新**: 2026-05-18
**维护者**: 邹心宇
**审核者**: 王选策

