# Spatial Embedding 层设计补充

**文档**: 数据JSON化方案 — Spatial Embedding补充设计
**日期**: 2026-05-18
**版本**: v1.1

---

## 一、问题诊断

### 1.1 当前设计的不足

**现状**：
- Layer 2的`spatial_anchors`只是记录空间信息（坐标、距离、方位）
- 空间信息是"文本描述"，不是"可计算的向量"
- 无法用于相似度检索、空间推理、跨尺度查询

**缺失**：
1. ❌ 地质概念的空间向量表达（如"钾化带"的空间嵌入向量）
2. ❌ 可计算的空间关系图谱（支持图查询和推理）
3. ❌ 多尺度统一空间索引（跨尺度空间查询）
4. ❌ 空间相似度检索（找到空间特征相似的矿床）

---

## 二、Spatial Embedding 层架构

### 2.1 层级定位

```
Layer 1: 文档提取（Marker产出）
    ↓
Layer 2: 知识结构化（空间锚点、实体、关系）
    ↓
Layer 2.5: Spatial Embedding（新增）
    ├── 概念空间向量化
    ├── 空间关系图谱
    ├── 多尺度空间索引
    └── 空间相似度索引
    ↓
Layer 3: 训练数据（CPT/SFT/DPO）
```

### 2.2 核心组件

#### 组件1：概念空间向量库

**目的**：为每个地质概念生成空间嵌入向量

**文件**: `spatial_embeddings/concept_vectors.json`

```json
{
  "concept_id": "alteration_potassic",
  "concept_name": "钾化带 (Potassic Alteration)",
  "spatial_embedding": {
    "vector": [0.23, -0.45, 0.67, ...],  // 512维向量
    "encoding_method": "spatial_bert",
    "spatial_features": {
      "typical_distance_from_center_m": [0, 500],
      "typical_temperature_c": [400, 600],
      "typical_depth_m": [0, 1000],
      "spatial_pattern": "concentric_core",
      "scale": "deposit",
      "morphology": "cylindrical_to_ellipsoidal"
    }
  },
  "co_occurrence_concepts": [
    {"concept": "biotite", "spatial_relation": "within", "frequency": 0.95},
    {"concept": "magnetite", "spatial_relation": "within", "frequency": 0.88},
    {"concept": "phyllic_alteration", "spatial_relation": "outward", "distance_m": 500}
  ],
  "source_docs": ["paper_a1b2c3d4", "thesis_zhang2019", ...]
}
```

**关键点**：
- `vector`: 512维空间嵌入向量（编码空间特征）
- `spatial_features`: 显式的空间参数（距离、温度、深度、形态）
- `co_occurrence_concepts`: 空间共生关系

---

#### 组件2：空间关系图谱

**目的**：显式建模可计算的空间关系

**文件**: `spatial_embeddings/spatial_graph.json`

```json
{
  "graph_id": "porphyry_cu_spatial_graph",
  "deposit_type": "porphyry_cu",
  "nodes": [
    {
      "node_id": "n_001",
      "concept": "potassic_core",
      "spatial_embedding_ref": "alteration_potassic",
      "spatial_coords": {"x": 0, "y": 0, "z": 0},  // 相对坐标系
      "scale": "deposit"
    },
    {
      "node_id": "n_002",
      "concept": "phyllic_zone",
      "spatial_embedding_ref": "alteration_phyllic",
      "spatial_coords": {"x": 500, "y": 0, "z": 0},
      "scale": "deposit"
    }
  ],
  "edges": [
    {
      "edge_id": "e_001",
      "from": "n_001",
      "to": "n_002",
      "relation_type": "zoning_sequence",
      "spatial_attributes": {
        "direction": "outward",
        "distance_m": 500,
        "distance_range_m": [400, 600],
        "transition_type": "gradational",
        "transition_width_m": 50
      },
      "confidence": 0.92,
      "evidence_docs": ["paper_a1b2c3d4", "paper_xyz789"]
    }
  ],
  "spatial_constraints": [
    {
      "constraint_type": "distance_order",
      "rule": "potassic < phyllic < propylitic",
      "from_center": true
    }
  ]
}
```

**关键点**：
- 节点有相对空间坐标（可以做空间查询）
- 边有定量的空间属性（距离、方向、过渡类型）
- 支持图查询："从钾化带出发，向外500m会遇到什么？"

---

#### 组件3：多尺度空间索引

**目的**：同一观察在不同尺度的统一空间表达

**文件**: `spatial_embeddings/multiscale_index.json`

```json
{
  "observation_id": "obs_chalcopyrite_pyrite",
  "phenomenon": "黄铜矿交代黄铁矿",
  "scales": {
    "microscopic": {
      "scale_level": 1,
      "spatial_extent_mm": [0.1, 1.0],
      "spatial_coords": null,  // 显微尺度无绝对坐标
      "spatial_pattern": "veinlet_replacement",
      "embedding_vector": [0.12, -0.34, ...],
      "source_docs": ["paper_a1b2c3d4#fig_08"]
    },
    "outcrop": {
      "scale_level": 2,
      "spatial_extent_m": [1, 10],
      "spatial_coords": {"lat": -34.08, "lon": -70.35, "elevation": 2500},
      "spatial_pattern": "stockwork_veins",
      "embedding_vector": [0.15, -0.32, ...],
      "source_docs": ["paper_a1b2c3d4#section_3.4"]
    },
    "deposit": {
      "scale_level": 3,
      "spatial_extent_m": [100, 2000],
      "spatial_coords": {"lat": -34.08, "lon": -70.35},
      "spatial_pattern": "pipe_shaped_orebody",
      "embedding_vector": [0.18, -0.30, ...],
      "implication": "主矿体呈筒状产出，受构造控制",
      "source_docs": ["paper_a1b2c3d4#section_5.2"]
    },
    "regional": {
      "scale_level": 4,
      "spatial_extent_km": [10, 100],
      "spatial_coords": {"lat": -34.0, "lon": -70.0},
      "spatial_pattern": "metallogenic_belt",
      "embedding_vector": [0.20, -0.28, ...],
      "implication": "位于中智利斑岩成矿带",
      "source_docs": ["paper_a1b2c3d4#section_2.1"]
    }
  },
  "scale_linking": {
    "microscopic_to_outcrop": "黄铜矿交代黄铁矿 → 网脉状硫化物矿化",
    "outcrop_to_deposit": "网脉状矿化 → 筒状矿体",
    "deposit_to_regional": "筒状矿体 → 斑岩成矿带"
  }
}
```

**关键点**：
- 每个尺度都有独立的空间嵌入向量
- 支持跨尺度查询："显微观察X在矿床尺度意味着什么？"
- 尺度间有显式的关联逻辑

---

#### 组件4：空间相似度索引

**目的**：基于空间特征的矿床相似度检索

**文件**: `spatial_embeddings/spatial_similarity_index.json`

```json
{
  "deposit_id": "el_teniente",
  "deposit_name": "El Teniente",
  "spatial_signature": {
    "embedding_vector": [0.45, -0.23, 0.67, ...],  // 512维
    "spatial_features": {
      "alteration_zoning_pattern": "concentric",
      "orebody_morphology": "pipe_shaped",
      "vertical_extent_m": 1500,
      "horizontal_extent_m": 2000,
      "depth_to_top_m": 0,
      "structural_control": "fault_intersection"
    }
  },
  "similar_deposits": [
    {
      "deposit_id": "chuquicamata",
      "similarity_score": 0.87,
      "spatial_similarity_breakdown": {
        "zoning_pattern": 0.92,
        "morphology": 0.85,
        "scale": 0.88,
        "structural_control": 0.83
      },
      "key_differences": ["Chuquicamata更浅", "蚀变分带更宽"]
    }
  ]
}
```

**关键点**：
- 每个矿床有一个"空间签名"向量
- 可以做向量相似度检索："找到空间特征与El Teniente最相似的矿床"
- 相似度可以分解到各个空间维度

---

## 三、Spatial Embedding 生成流程

### 3.1 概念空间向量生成

**输入**: Layer 2的`spatial_anchors` + 全文内容
**模型**: Spatial-BERT（基于BERT微调，专门编码空间关系）
**输出**: 512维空间嵌入向量

**流程**:
```python
# 伪代码
def generate_concept_embedding(concept_name, spatial_features, context_docs):
    # 1. 构建空间描述文本
    spatial_text = f"{concept_name} typically occurs at {spatial_features['distance']}m from center, "
    spatial_text += f"with temperature {spatial_features['temperature']}°C, "
    spatial_text += f"spatial pattern: {spatial_features['pattern']}"

    # 2. 用Spatial-BERT编码
    embedding = spatial_bert.encode(spatial_text)

    # 3. 融合多文档的空间上下文
    for doc in context_docs:
        doc_embedding = spatial_bert.encode(doc.spatial_context)
        embedding = weighted_average(embedding, doc_embedding)

    return embedding
```

---

### 3.2 空间关系图谱构建

**输入**: Layer 2的`spatial_relationships`
**方法**: 知识图谱构建 + 空间约束推理
**输出**: Neo4j图数据库 或 JSON图结构

**流程**:
```python
# 伪代码
def build_spatial_graph(spatial_relationships):
    graph = SpatialGraph()

    for rel in spatial_relationships:
        # 创建节点
        node_from = graph.add_node(rel['from'], spatial_coords=rel['coords_from'])
        node_to = graph.add_node(rel['to'], spatial_coords=rel['coords_to'])

        # 创建边（带空间属性）
        edge = graph.add_edge(
            node_from, node_to,
            relation_type=rel['type'],
            distance=rel['distance'],
            direction=rel['direction']
        )

    # 空间约束推理
    graph.infer_spatial_constraints()

    return graph
```

---

### 3.3 多尺度空间索引构建

**输入**: 博士论文的`scale_linking_cases`
**方法**: 尺度对齐 + 向量插值
**输出**: 多尺度统一索引

**流程**:
```python
# 伪代码
def build_multiscale_index(scale_linking_cases):
    index = MultiscaleIndex()

    for case in scale_linking_cases:
        obs_id = case['phenomenon']

        # 为每个尺度生成嵌入向量
        for scale, data in case['scales'].items():
            embedding = generate_scale_embedding(scale, data)
            index.add_scale_entry(obs_id, scale, embedding, data)

        # 建立尺度间的映射关系
        index.link_scales(obs_id, case['scale_linking'])

    return index
```

---

## 四、与训练管线的集成

### 4.1 CPT阶段

**不变**：全文喂入，建立知识底座

### 4.2 SFT阶段

**新增**：空间推理QA对生成时，利用Spatial Embedding

**示例QA**:
```json
{
  "qa_type": "spatial_similarity_reasoning",
  "question": "给定以下空间特征：[同心环状蚀变分带，筒状矿体，垂向延伸1500m]，全球哪些矿床与之空间特征最相似？",
  "answer": "基于空间嵌入向量相似度检索，最相似的矿床是：\n1. Chuquicamata (相似度0.87)...\n2. Oyu Tolgoi (相似度0.82)...",
  "spatial_embedding_used": true,
  "similarity_scores": [...]
}
```

### 4.3 GraphRAG阶段

**增强**：LazyGraphRAG不仅是文本图谱，还是**空间图谱**

**查询示例**:
- "从钾化带出发，向外移动500m，会遇到什么蚀变带？"（图查询）
- "找到与El Teniente空间特征相似的矿床"（向量检索）
- "显微观察到黄铜矿交代黄铁矿，在矿床尺度意味着什么？"（跨尺度推理）

---

## 五、技术选型

### 5.1 空间向量生成

**方案A**: 微调BERT（Spatial-BERT）
- 基于BERT-base，在地质文本+空间描述上微调
- 输入：概念名称 + 空间特征文本
- 输出：512维向量

**方案B**: 使用现成的Sentence-BERT + 空间特征拼接
- 用Sentence-BERT编码文本描述
- 手工提取的空间特征（距离、温度、深度）作为额外维度拼接

**推荐**：先用方案B快速验证，效果好再投入方案A

---

### 5.2 空间图谱存储

**方案A**: Neo4j图数据库
- 原生支持图查询（Cypher语言）
- 可以存储节点/边的空间属性
- 支持空间索引和最短路径查询

**方案B**: JSON + 内存图结构
- 轻量级，不需要额外数据库
- 用NetworkX做图查询
- 适合MVP阶段

**推荐**：MVP用方案B，全量用方案A

---

### 5.3 向量检索

**方案**: FAISS（Facebook AI Similarity Search）
- 高效的向量相似度检索
- 支持百万级向量索引
- 可以做ANN（近似最近邻）查询

---

## 六、MVP验证方案

### 6.1 验证目标

**问题**：Spatial Embedding是否真的能提升空间推理能力？

**验证方式**：
1. 生成50个矿床的空间嵌入向量
2. 做相似度检索，看结果是否符合地质学家的判断
3. 用空间图谱做推理查询，看答案是否合理

### 6.2 验证数据

- 50篇论文（斑岩Cu 25篇 + 造山Au 25篇）
- 提取100个地质概念的空间向量
- 构建2个空间图谱（斑岩Cu系统 + 造山Au系统）

### 6.3 评估指标

- **相似度检索准确率**：Top-5检索结果中，有几个是地质学家认可的相似矿床？
- **图查询合理性**：空间推理查询的答案，地质学家打分（1-5分）
- **跨尺度推理一致性**：显微→矿床的推理链条，是否逻辑自洽？

---

## 七、实施路线图

### Phase 1: MVP验证（Week 1-2）

1. 用Sentence-BERT生成50个概念的空间向量
2. 构建2个空间图谱（JSON格式）
3. 用FAISS做相似度检索验证
4. **Go/No-Go决策**

### Phase 2: 全量构建（Week 3-5）

1. 微调Spatial-BERT（如果MVP效果好）
2. 生成10,000+概念的空间向量
3. 构建Neo4j空间图谱
4. 建立多尺度空间索引

### Phase 3: 集成训练（Week 6-8）

1. 生成空间推理QA对（利用Spatial Embedding）
2. GraphRAG集成空间图谱
3. 训练时注入空间向量作为额外特征

---

## 八、风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 空间向量质量不高 | 高 | MVP阶段人工评估，不行就调整编码方法 |
| 图谱构建成本高 | 中 | 先用规则提取，再用LLM补充 |
| 向量检索不准确 | 中 | 调整相似度计算方法，加入空间约束 |
| 多尺度对齐困难 | 中 | 先做2-3个尺度，逐步扩展 |

---

## 九、与现有设计的关系

**Layer 2 (spatial_anchors)** → 提供原始空间信息
**Layer 2.5 (Spatial Embedding)** → 将空间信息向量化、图谱化、索引化
**Layer 3 (训练数据)** → 利用Spatial Embedding生成更高质量的QA对

**关键**：Layer 2.5不是替代Layer 2，而是在Layer 2基础上的**增强和结构化**。

---

**文档版本**: v1.1
**最后更新**: 2026-05-18
**补充内容**: Spatial Embedding层设计

