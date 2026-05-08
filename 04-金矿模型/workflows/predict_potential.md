# Workflow C：区域成矿潜力分析与预测

## 步骤

### Step 1：明确范围与主攻类型
- 与用户确认评价范围（经纬度 / 矿权 / 行政区）
- 与用户确认主攻类型（如不确定，先用 Workflow A 思路做"类型适配性分析"）
- **金矿类型选择**：Orogenic / Carlin / Epithermal HS-LS / Porphyry Au-Cu / IOCG-Au / VMS-Au / Intrusion-related

### Step 2：读取必读知识
- `knowledge/global_belts.md`（必读，定位区域）
- `knowledge/deposit_types.md`（必读，明确目标类型特征）
- `knowledge/tectonic_controls.md`（必读，理解控矿机制）
- `knowledge/exploration_criteria.md`（必读，列出找矿要素）
- `knowledge/grade_tonnage.md`（按需）

### Step 3：构建控矿模型
- 写出"金属源—流体—通道—沉淀—保存"五要素答案
- **金矿特色控矿因素**：
  - Orogenic：造山带剪切带、变质流体、碳酸盐化
  - Carlin：碳酸盐岩容矿、低温热液、微细粒金
  - Epithermal：火山弧、浅成侵入、硅化—明矾石化
- 给出概念成矿模式图（ASCII / SVG / 调用 canvas-design）

### Step 4：列出证据层清单
按 `templates/potential_prediction.md` 第 4–5 节，列出 GIS 证据层 + 权重。

**金矿特色证据层**：
- 构造：剪切带 / 断裂交汇 / 背斜轴部
- 岩性：碳酸盐岩 / 浊积岩 / 火山岩
- 蚀变：As-Sb-Hg 异常 / 硅化 / 碳酸盐化
- 地球物理：低磁 / 高电阻率（硅化体）/ IP 异常（黄铁矿化）

### Step 5：分析与赋分
- **有 GIS 数据时**：
  - 调用 `anthropic-skills:xlsx` 处理网格数据
  - 用 logistic regression / WofE / fuzzy logic 叠加
  - 输出 0–100 分潜力分布
- **无 GIS 数据时**：
  - 用知识驱动 + 专家判断打分
  - 在区域地质底图上手工 / AI 圈定靶区
  - 给出方法论清单供用户后续 GIS 化

### Step 6：靶区圈定与分级
按 A（≥80）/ B（60–80）/ C（40–60）/ D（<40）分四级。

### Step 7：靶区描述与建议工程
A 级靶区每个详细描述（一节）；B 级靶区列表式描述；C/D 级仅清单。

**金矿勘查建议**：
- 土壤地化（Au-As-Sb-Hg 组合）
- IP / 激电测深（黄铁矿化体）
- 槽探 / 浅钻验证（nugget effect 需密集采样）

### Step 8：资源量量级估算
按目标类型典型品位—吨位 + 靶区面积/深度做概念估算（明确为推断 speculative）。
- 品位单位：g/t Au
- 资源量单位：Moz Au（百万盎司）

### Step 9：输出
- 主报告：`anthropic-skills:docx` 生成 .docx
- 打分表：`anthropic-skills:xlsx` 生成 .xlsx（如有数据）
- 模式图：`anthropic-skills:canvas-design` 或简化 SVG 图
- 文件名：`Gold_Potential_<区域>_<YYYYMMDD>.docx` + `.xlsx`
- 保存至 `Desktop/02-矿业评估/<项目名>/`

## 关键提醒

- **不要凭空编造矿点位置**：靶区需有证据支撑（构造 / 异常 / 类比）
- **明确不确定性**：尤其无 GIS 数据时，所有分级是相对 / 概念性的
- **正样本偏差**：known 矿点训练的模型只能找到"和已发现矿相似"的矿，对真正的盲区识别力有限
- **nugget effect 警告**：金矿品位分布极不均匀，资源量估算需密集采样
- **不替代实测验证**：所有 A 级靶区都需要钻孔验证；本 skill 仅提供"哪里去钻"的优先级建议

## 与 paper skill 的衔接

潜力分析报告产出后，可作为 `chinese-paper` skill 的素材撰写"区域成矿规律与靶区预测"主题论文。
