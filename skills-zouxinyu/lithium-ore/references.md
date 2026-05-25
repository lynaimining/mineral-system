# 参考资料索引

Skill 的知识库源自下列文献。**用户工作目录**：`C:\Users\39555\Downloads\paper\Lithium\`（皆为本地可读文件）。

---

## 一、核心权威综述（"圣经"级，必读）

| # | 文献 | 路径 | 用途 |
|---|------|------|------|
| 1 | **Bradley, D.C. & McCauley, A.D. (2016) — USGS A Preliminary Deposit Model for Lithium-Cesium-Tantalum (LCT) Pegmatites** | （USGS Open-File Report，需从用户文件夹或数据库获取） | 硬岩型锂矿（LCT Pegmatite）品位—吨位模型 |
| 2 | **Kesler, S.E. et al. (2012) — Global Lithium Resources: Relative Importance of Pegmatite, Brine and Other Deposits** | Ore Geology Reviews | 全球锂资源分布与类型对比 |
| 3 | **USGS Mineral Commodity Summaries — Lithium** | （年度报告，需从 USGS 网站获取） | 储量、产量、贸易统计 |
| 4 | **Gruber, P.W. et al. (2011) — Global Lithium Availability: A Constraint for Electric Vehicles?** | Journal of Industrial Ecology | 锂资源供需分析 |

---

## 二、专题与近年关键文献（用户文件夹内）

### 2.1 硬岩型锂矿（LCT Pegmatite）
- Greenbushes / Pilbara / 甲基卡 / 可尔因 案例研究（待用户提供）
- 伟晶岩分带与锂矿物分布规律（待用户提供）
- 锂辉石 vs 锂云母冶炼工艺对比（待用户提供）

### 2.2 盐湖型锂矿（Brine）
- Atacama / Uyuni / 察尔汗 / 扎布耶 案例研究（待用户提供）
- Mg/Li 比与提锂工艺选择（待用户提供）
- DLE（直接锂提取）技术进展（待用户提供）

### 2.3 粘土型锂矿（Clay）
- Hectorite / Jadarite 案例研究（待用户提供）
- 粘土型锂矿提锂工艺（待用户提供）

### 2.4 勘查方法学与地球化学
- 花岗岩类侵入体识别（航磁、重力）（待用户提供）
- Li-Ta-Nb-Sn-Be 化探异常解释（待用户提供）
- 遥感蚀变映射（云母化、绿泥石化）（待用户提供）
- 盐湖遥感识别技术（待用户提供）

### 2.5 项目案例
- 澳大利亚 Greenbushes 锂矿技术报告（待用户提供）
- 智利 Atacama 盐湖锂矿可研（待用户提供）
- 中国���基卡锂矿地质报告（待用户提供）

### 2.6 市场—行业—产能
- 全球锂市场年度回顾（待用户提供）
- 电动汽车与储能需求预测（待用户提供）
- 碳酸锂 vs 氢氧化锂价格走势（待用户提供）
- 电池级 vs 工业级锂产品市场（待用户提供）

---

## 三、外部权威数据库（写报告时优先引用）

| 来源 | 用途 | 链接 |
|------|------|------|
| **USGS Mineral Commodity Summaries (Lithium)** | 储量、产量、贸易统计 | usgs.gov |
| **USGS Mineral Resources Database (MRDS)** | 全球矿点信息 | mrdata.usgs.gov |
| **S&P Global Market Intelligence Lithium Database** | 公司、产能、并购 | spglobal.com |
| **Benchmark Mineral Intelligence** | 锂市场价格、供需 | benchmarkminerals.com |
| **Wood Mackenzie Lithium** | 矿山现金成本曲线 | woodmac.com |
| **Mindat** | 矿物学—矿点 | mindat.org |
| **Society of Economic Geologists (SEG)** | 经典文献 | segweb.org |

---

## 四、引用规范

### 中文（GB/T 7714-2015）
```
[作者]. [标题][J/M/D]. [期刊/出版社/学位授予单位], [出版年], [卷(期)]: [起止页]. DOI: ....
```

### 英文（SEG style，与 Economic Geology 一致）
```
Bradley, D.C., and McCauley, A.D., 2016, A preliminary deposit model for lithium-cesium-tantalum (LCT) pegmatites: U.S. Geological Survey Open-File Report 2016-1010, 21 p.
Kesler, S.E., Gruber, P.W., Medina, P.A., Keoleian, G.A., Everson, M.P., and Wallington, T.J., 2012, Global lithium resources: Relative importance of pegmatite, brine and other deposits: Ore Geology Reviews, v. 48, p. 55–69.
```

### AI 输出注意事项
- 所有引用须 CrossRef / OpenAlex 验证（调用 ref-verify skill）
- 用户文件夹内文献的引用，可直接使用其文件名作为初步定位，但仍应通过 CrossRef 找到正式出版信息（DOI、卷、期、页）
- 不擅自添加未在文件夹/已知数据库中的文献
- 模型记忆有时效性——任何关于 "X 矿床数据" 的具体数字（吨位、品位、年代），应优先以最新公司年报 / 学术综述为准；本 skill 给出的数据可能滞后，请在引用前核实
