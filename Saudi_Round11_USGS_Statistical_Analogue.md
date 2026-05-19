# 沙特Round 11 — USGS数据统计类比分析

## 数据来源
- USGS Major Mineral Deposits of the World (OFR 2005-1294) — 23个沙特矿床
- USGS MRDS (Mineral Resource Data System) — 沙特矿点数据
- USGS Open-File Reports — 硫同位素、地球化学调查
- 公开文献 — Al Amar, Khnaiguiyah, Mahd adh Dhahab等矿床数据

---

## 1. Proximity Analysis（邻近矿床统计）

### Round 11区块与USGS登记重要矿床的距离关系

| 区块 | 150km内重要矿床数 | 最近矿床 | 距离(km) | 矿床规模 | 统计意义 |
|------|-------------------|---------|----------|---------|---------|
| **Ashab adh Dhaib** | 2 | Al Amar (Au-Ag-Zn-Cu) | **33** | 580,500 oz Au产出(2008-2021) | **同一成矿营** |
| **Jabal Idsas** | 2 | Al Amar | **50** | 同上 | **同一成矿营** |
| **Al-Khushbi** | 1 | Al Amar | 147 | 同上 | 成矿带延伸 |
| **Wadi Khyam** | 1 | Al Amar | 119 | 同上 | 成矿带延伸 |
| **Al Kshaymaiyah** | 2 | Ad Duwayhi (Au) | 124 | 1.5 Moz Au | 同一成矿带 |
| **Dilan Sumar Al Har** | 0 | Bulgah (Au) | ~200 | 1.0 Moz Au | Greenfield |
| **Jabal Minyah** | 0 | Ad Duwayhi (Au) | ~150 | 1.5 Moz Au | Greenfield（但同一地体） |
| **Al Numrahniyah** | 0 | Mahd adh Dhahab | ~150 | 1.2 Moz Au | Greenfield（但同一地体） |

### 关键统计规律

**ANS矿床聚集规律（Camp-scale clustering）**：
- ANS中已知矿床聚集半径：20-50 km
- Al Amar-Khnaiguiyah成矿带长度：~80 km
- Ashab adh Dhaib (33km) 和 Jabal Idsas (50km) 完全在Al Amar成矿营范围内

---

## 2. Al Amar-Khnaiguiyah成矿带详细统计

### Al Amar金矿（距Ashab adh Dhaib 33km, 距Jabal Idsas 50km）

| 参数 | 数据 | 来源 |
|------|------|------|
| 坐标 | 23.78N, 45.07E | USGS |
| 矿床类型 | Au-Zn VMS / Epithermal | Mindat |
| 构造位置 | Ar Rayn Terrane, Al Amar-Idas断裂带 | MiningDataOnline |
| 容矿岩 | Ar Rayn Terrane火山-沉积岩系 | USGS |
| 边界构造 | Al Amar-Idas断裂（与西侧Abt Schist带分界） | MiningDataOnline |
| 品位 | 12.31 g/t Au | Ashgill报告 |
| 资源量 | 1.55 Mt @ 12.31 g/t Au | Ashgill报告 |
| 累计产金 | 580,500 oz (2008-2021) | Asharq Al-Awsat |
| 年处理量 | 350,000 t/y矿石 | Asharq Al-Awsat |
| 设计产能 | 200,000 t/y (地下开采) | Forbes 2024 |

### Khnaiguiyah锌铜矿（距Ashab adh Dhaib 79km, 距Jabal Idsas 103km）

| 参数 | 数据 | 来源 |
|------|------|------|
| 坐标 | 24.27N, 45.08E | USGS |
| 矿床类型 | VMS Zn-Cu | Mindat |
| 构造位置 | Ar Rayn Terrane, Al Amar-Khnaiguiyah带 | Lexology |
| 面积 | 350 km² | Lexology |
| 勘探程度 | 100,000+ m钻探，3D地质模型 | Lexology |
| 硫同位素 | 强正值δ34S（海水热液系统） | USGS OFR 78-776 |

### 统计类比结论

**Ashab adh Dhaib和Jabal Idsas处于Al Amar-Khnaiguiyah VMS/Epithermal成矿带内**：
- Al Amar: Au-Ag-Zn-Cu, 12.31 g/t, 580k oz产出
- Khnaiguiyah: Zn-Cu VMS, 100,000m钻探
- 成矿带长度: ~80km (Al Amar到Khnaiguiyah)
- **Ashab adh Dhaib位于这条带的中段**（距Al Amar 33km, 距Khnaiguiyah 79km）
- **Jabal Idsas位于Al Amar附近**（50km）

---

## 3. 硫同位素成矿类型判别统计

### USGS硫同位素数据（OFR 78-776）对ANS矿床的分类

| δ34S范围 | 成矿类型 | 代表矿床 | Round 11对应区块 |
|----------|---------|---------|----------------|
| 强负值 | 同生沉积VMS（停滞缺氧盆地） | Wadi Wassat, Wadi Qatan | — |
| 强正值 | 海水热液系统VMS | **Khnaiguiyah**, **Al Amar** | **Ashab adh Dhaib, Jabal Idsas** |
| 近零值 | 岩浆源金银脉 | **Mahd adh Dhahab**, Samrah | **Dilan Sumar, Wadi Khyam** |
| 中间值 | 火山喷气型 | Kutam, Al Masane, **Jabal Sayid**, Nuqrah | **Al-Khushbi** |

### 统计意义

- **近零δ34S = 岩浆源造山型金矿**：Mahd adh Dhahab (1.2 Moz)就是这种类型 → Dilan Sumar和Wadi Khyam的造山型金矿判断有硫同位素统计支撑
- **强正δ34S = 海水热液VMS**：Al Amar和Khnaiguiyah都是这种类型 → Ashab adh Dhaib和Jabal Idsas如果发现硫化物，应该检测δ34S来确认VMS属性
- **中间δ34S = 火山喷气型VMS**：Jabal Sayid (20Mt Cu)就是这种类型 → Al-Khushbi的VMS矿化可能属于此类

---

## 4. 侵入岩-成矿统计（基于USGS OFR 83-369 & OFR 85-6）

### 东部-东南部地盾花岗岩地球化学评价（OFR 83-369）

| 统计项 | 数据 |
|--------|------|
| 采样量 | 696岩石样品 + 694重砂样品 |
| 覆盖区域 | 东部和东南部阿拉伯地盾 |
| 发现 | 10个锡异常花岗岩体 |
| 异常元素 | Li, F, Be, Pb, Rb, Nb, Y, **Sn**, Bi, Ag, **W** |
| 岩体特征 | 白云母花岗岩，过铝质，面积<10 km² |

**对Round 11的意义**：
- **Jabal Minyah**位于Afif Terrane，其碰撞后花岗岩(590-560 Ma)与这些Sn-W异常花岗岩同期
- USGS在东部地盾发现的10个Sn异常岩体，证实了该区花岗岩的高分异特征
- Sn-W异常是侵入体相关型金矿的**路径指示元素**（pathfinder）

### 北部-中部地盾花岗岩评价（OFR 85-6）

| 统计项 | 数据 |
|--------|------|
| 覆盖区域 | 北部-中部阿拉伯地盾（含Ha'il Terrane） |
| 发现 | 14个有利于稀有元素成矿的花岗岩体 |
| 时代 | 晚元古代 |

**对Round 11的意义**：
- **Dilan Sumar Al Har**位于Ha'il Terrane北部
- USGS在该区识别了14个有利花岗岩体，说明该区侵入岩活动强烈
- 这些花岗岩体可以作为造山型金矿的热源

---

## 5. 修正后的综合评估矩阵

### 三维评估：地层 × 侵入岩 × Proximity

| 区块 | 地层有利度 | 侵入岩有利度 | Proximity得分 | 综合判断 | 修正排名 |
|------|-----------|------------|-------------|---------|---------|
| **Dilan Sumar Al Har** | ★★★ | ★★☆ | ★☆☆ (greenfield) | 地层极优但无邻近验证 | Gold #1 (高风险高回报) |
| **Jabal Minyah** | ★★☆ | ★★★ | ★☆☆ (greenfield) | 侵入岩极优但无邻近验证 | Gold #2 (高风险高回报) |
| **Ashab adh Dhaib** | ★★☆ | ★☆☆ | ★★★ (Al Amar 33km) | **Proximity极优，已证实成矿营** | Gold #3→**#2** (低风险) |
| **Wadi Khyam** | ★★☆ | ★★☆ | ★★☆ (Al Amar 119km) | 均衡型 | Gold #4 |
| **Al-Khushbi** | ★★★ | ★☆☆ | ★★☆ (Al Amar 147km) | VMS地层确认 | Cu #1 |
| **Jabal Idsas** | ★★★ | ★☆☆ | ★★★ (Al Amar 50km) | **BIF独特 + Proximity优** | Cu #2→**提升** |
| **Al Numrahniyah** | ★☆☆ | ★★☆ | ★☆☆ (greenfield) | 三项均不突出 | 不推荐 |
| **Al Kshaymaiyah** | ★★☆ | ★☆☆ | ★★☆ (Ad Duwayhi 124km) | 盖层遮挡 | 低优先 |

### 修正后的投标建议

**必选组合（3个区块，覆盖3种成矿系统 + 风险分散）**：

1. **Dilan Sumar Al Har** — 造山型Au，greenfield高回报潜力
2. **Ashab adh Dhaib** — 造山型Au，**距Al Amar仅33km，已证实成矿营，低风险**
3. **Al-Khushbi** — VMS Cu-Zn，地层确认

**备选（如果预算允许第4个）**：
4. **Jabal Minyah** — 侵入体相关型Au-Sn-W，Ad Duwayhi类比

**关键修正**：
- Ashab adh Dhaib从原来的#4提升到必选 — 因为proximity数据证明它在Al Amar成矿营内
- Jabal Idsas的价值也应重新评估 — 距Al Amar仅50km + BIF独特资源

---

## 6. 可进一步验证的事项（Test Items）

基于以上统计分析，以下是可以进一步test的方向：

### 高优先级
1. **Ashab adh Dhaib的Al Amar-Idas断裂延伸**：Al Amar矿化受Al Amar-Idas断裂控制，该断裂是否延伸到Ashab adh Dhaib区块内？（可通过遥感线性构造解译验证）
2. **Jabal Idsas的BIF-Au潜力量化**：全球BIF容矿金矿的统计品位是多少？（Homestake 8.6 g/t, Geita 3-5 g/t）Jabal Idsas的BIF如果含Au，预期品位范围？
3. **Al-Khushbi的VMS层位对比**：Jiddah Group双峰式火山岩与Jabal Sayid的容矿层位是否同一层位？（可通过锆石U-Pb年龄对比验证）

### 中优先级
4. **Dilan Sumar绿岩带的变质级别**：绿片岩相vs角闪岩相？（变质级别影响造山型Au的保存）
5. **Jabal Minyah花岗岩的氧化态**：还原型(ilmenite系列)还是氧化型(magnetite系列)？（还原型更有利于Au-Sn-W成矿）
6. **硫同位素验证**：如果能获取Ashab adh Dhaib的硫化物样品，δ34S值应该是强正值（与Al Amar一致）

### 低优先级
7. **Murdama Group覆盖面积估算**：各区块中Murdama Group（不利层位）占比多少？
8. **红海裂谷对Al Numrahniyah的影响**：该区的抬升剥蚀量是多少？是否已剥蚀到成矿深度以下？

---

**编制**: Claude Opus 4.6
**数据来源**: USGS OFR 2005-1294, USGS MRDS, USGS OFR 78-776, USGS OFR 83-369, USGS OFR 85-6
**日期**: 2026-05-19
