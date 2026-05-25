# 参考资料索引

Skill 的知识库源自下列文献。**用户工作目录**：`C:\Users\39555\Downloads\paper\Nickel\`（皆为本地可读文件）。

---

## 一、核心权威综述（"圣经"级，必读）

| # | 文献 | 路径 | 用途 |
|---|------|------|------|
| 1 | **Naldrett, A.J. (2004) — Magmatic Sulfide Deposits: Geology, Geochemistry and Exploration** | （经典教材，需从用户文件夹或数据库获取） | 岩浆型镍矿全球综述权威 |
| 2 | **Butt, C.R.M. & Cluzel, D. (2013) — Nickel Laterite Ore Deposits: Weathered Serpentinites** | （Elements 专刊，需从用户文件夹或数据库获取） | 红土型镍矿成因与勘查 |
| 3 | **USGS — Descriptive models and grade-tonnage relations for Ni-Co laterite deposits** | （USGS Open-File Report，需从数据库获取） | 红土型镍矿品位—吨位曲线 |
| 4 | **Barnes, S.J. & Lightfoot, P.C. (2005) — Formation of magmatic nickel sulfide deposits and processes affecting their copper and platinum group element contents** | Econ. Geol. 100th Anniversary Volume | 岩浆型镍矿成矿机制 |

---

## 二、专题与近年关键文献（用户文件夹内）

### 2.1 红土型镍矿（Laterite）
- 印尼/菲律宾红土镍矿专题（待用户提供）
- HPAL / RKEF / Ferronickel 工艺对比文献（待用户提供）
- Class 1 vs Class 2 镍产品市场分析（待用户提供）

### 2.2 岩浆型镍矿（Magmatic Ni-Cu-PGE）
- Norilsk / Voisey's Bay / Jinchuan / Sudbury 案例研究（待用户提供）
- Komatiite-hosted Ni deposits（Kambalda 等）（待用户提供）
- 硫化物熔离与重力沉降机制（待用户提供）

### 2.3 勘查方法学与地球化学
- 超镁铁质岩体识别（航磁、重力）（待用户提供）
- Ni-Co-Cr 化探异常解释（待用户提供）
- PGE 地球化学与勘查指标（待用户提供）

### 2.4 项目案例
- 印尼红土镍矿项目可研（待用户提供）
- 加拿大 Voisey's Bay 技术报告（待用户提供）
- 中国金川镍矿地质报告（待用户提供）

### 2.5 市场—行业—产能
- 全球镍市场年度回顾（待用户提供）
- 印尼镍矿出口禁令影响分析（待用户提供）
- 电池级镍 vs 不锈钢级镍需求预测（待用户提供）

---

## 三、外部权威数据库（写报告时优先引用）

| 来源 | 用途 | 链接 |
|------|------|------|
| **USGS Mineral Commodity Summaries (Nickel)** | 储量、产量、贸易统计 | usgs.gov |
| **USGS Mineral Resources Database (MRDS)** | 全球矿点信息 | mrdata.usgs.gov |
| **S&P Global Market Intelligence Nickel Database** | 公司、产能、并购 | spglobal.com |
| **Wood Mackenzie Nickel** | 矿山现金成本曲线 | woodmac.com |
| **International Nickel Study Group (INSG)** | 供需平衡 | insg.org |
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
Naldrett, A.J., 2004, Magmatic Sulfide Deposits: Geology, Geochemistry and Exploration: Berlin, Springer-Verlag, 727 p.
Butt, C.R.M., and Cluzel, D., 2013, Nickel laterite ore deposits: weathered serpentinites: Elements, v. 9, p. 123–128.
Barnes, S.J., and Lightfoot, P.C., 2005, Formation of magmatic nickel sulfide deposits and processes affecting their copper and platinum group element contents: Economic Geology 100th Anniversary Volume, p. 179–213.
```

### AI 输出注意事项
- 所有引用须 CrossRef / OpenAlex 验证（调用 ref-verify skill）
- 用户文件夹内文献的引用，可直接使用其文件名作为初步定位，但仍应通过 CrossRef 找到正式出版信息（DOI、卷、期、页）
- 不擅自添加未在文件夹/已知数据库中的文献
- 模型记忆有时效性——任何关于 "X 矿床数据" 的具体数字（吨位、品位、年代），应优先以最新公司年报 / 学术综述为准；本 skill 给出的数据可能滞后，请在引用前核实
