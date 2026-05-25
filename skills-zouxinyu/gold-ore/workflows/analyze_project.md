# Workflow A：金矿项目分析

## 步骤

### Step 0：获取实时市场数据（强制，不可跳过）

**本步骤在任何其他步骤之前执行，无例外。**

```python
import sys
sys.path.insert(0, r'C:\Users\39555\.claude\tools\mining-price-engine')
from report_integration import get_live_prices, format_price_for_report, calculate_adjusted_opex, calculate_breakeven_grade

# 获取实时数据
live_data = get_live_prices()
```

如果 `get_live_prices()` 失败（网络问题），则：
1. 检查缓存文件 `C:\Users\39555\.claude\temp\mining_prices_cache.json` 是否存在
2. 如果缓存存在且<7天，使用缓存并标注"数据截至XX日"
3. 如果缓存不存在或>7天，**必须告知用户数据可能过时**，不得使用训练数据中的价格

**本步骤获取的数据用于：**
- 第7章经济性分析（金属价格、汇率）
- 经济门槛计算（动态计算，非历史固定值）
- OPEX/CAPEX调整（成本调整系数）
- 盈亏平衡分析（基于实时价格）
- 敏感性分析（实时价格±20%）

**绝对禁止：**
- ❌ 使用训练数据中的金属价格（如"$2,000-2,500/oz"）
- ❌ 使用历史固定的经济门槛（如"3.5 g/t"）
- ❌ 使用未经通胀调整的OPEX/CAPEX
- ❌ 在报告中出现无来源、无日期的价格数据

---

### Step 1：材料扫描
- 扫描用户当前工作目录（默认 `C:\Users\39555\Downloads\paper\Gold\` 或用户指定）
- 列出所有 .docx / .pdf / .pptx / .xlsx / 图像文件
- 优先读取：项目可研、地质报告、PPT 摘要、最新公告

### Step 2：读取必读知识
- `knowledge/deposit_types.md`（必读）
- `knowledge/grade_tonnage.md`（必读）
- `knowledge/global_belts.md`（按地理范围选读）
- `knowledge/tectonic_controls.md`（按构造背景选读）

### Step 3：类型识别（决策树）
回答 deposit_types.md 决策树，给出 confidence ranking（最像 X，其次 Y）。
重点区分：
- Orogenic（造山型）vs Carlin（卡林型）vs Epithermal（浅成低温热液）
- Porphyry Au-Cu（斑岩型）vs IOCG-Au（铁氧化物铜金）
- VMS-Au（块状硫化物）vs Intrusion-related（侵入岩相关）vs Witwatersrand（古砾岩型）

### Step 4：构造定位
对照 global_belts.md，把项目归入成矿带，列举同带头部矿床。

### Step 5：规模—品位评估
- 在该类型 grade-tonnage 累积频率上定位
- **品位单位：g/t Au**（金矿标准单位）
- 给出 Tier 分级（Tier 1: ≥5 Moz Au, Tier 2: 1–5 Moz, Tier 3: <1 Moz）
- 估算可能的资源量量级

### Step 6：成矿要素 10 项打分
按 `templates/project_assessment.md` 第 7 节执行。

### Step 6.5：完整估值分析（强制，用于第7章经济性分析）

**本步骤在生成第7章"经济性分析"之前必须执行。**

```python
import sys
sys.path.insert(0, r'C:\Users\39555\.claude\tools\mining-price-engine')
from valuation_engine import comprehensive_valuation

# 调用完整估值引擎
valuation_result = comprehensive_valuation(
    project_name='项目名称',
    metal_type='gold',
    country='国家',

    # 从Step 5获取的资源量参数
    resource_tonnage_mt=资源量_百万吨,
    grade_g_t=品位_克每吨,
    recovery_pct=回收率_百分比,

    # 采矿参数（从材料中提取或合理假设）
    mining_method='underground',  # 或 'open_pit'
    annual_capacity_mt=年处理能力_百万吨,
    strip_ratio=剥采比,  # 露天矿必填，地下矿=None
    depth_m=开采深度_米,  # 地下矿必填，露天矿=开采深度
    rock_type='medium',  # 'soft', 'medium', 'hard'

    # 成本参数（优先从材料中提取，否则使用JORC数据库平均值）
    base_opex_mining_usd_t=基准采矿成本,  # 可选，默认值：露天50，地下120
    base_opex_processing_usd_t=基准选矿成本,  # 可选，默认30
    capex_initial_musd=初始资本支出_百万美元,  # 可选，系统会估算

    # 财务参数
    construction_years=2,
    discount_rate=0.08,

    # 风险分析
    run_sensitivity=True,
    run_monte_carlo=False  # 可选，耗时较长
)
```

**估值结果包含：**
1. **DCF估值**：NPV、IRR、Payback（考虑税收、特许权使用费、残值）
2. **可比交易估值**：基于EV/Resource倍数
3. **加权估值**：DCF 60% + 可比交易 40%
4. **敏感性分析**：金价±30%、OPEX±20%、CAPEX±20%
5. **投资建议**：推荐投资/谨慎考虑/不推荐

**第7章必须包含的内容：**
- 实时金属价格（来自Step 0）
- 技术参数调整后的OPEX/CAPEX（考虑剥采比、深度、支护）
- 完整的NPV/IRR/Payback计算
- 可比交易估值
- 敏感性分析图表
- 投资建议

**绝对禁止：**
- ❌ 跳过本步骤直接写第7章
- ❌ 使用简化的经济计算（必须使用完整DCF模型）
- ❌ 不考虑剥采比、深度、支护成本
- ❌ 不提供可比交易估值
- ❌ 不进行敏感性分析

---

### Step 7：风险与建议
特别关注：
- 难选冶金矿物（砷黄铁矿、碲化物、含碳物质）
- 品位分布不均匀性（nugget effect）
- 深部盲矿预测（造山型常有多期叠加）

### Step 8：输出
按 `templates/project_assessment.md` 渲染成 .docx，保存至桌面。
- 使用 `anthropic-skills:docx` 生成 docx
- 文件名：`Gold_Project_Assessment_<项目名>_<YYYYMMDD>.docx`
- 保存路径：`Desktop/02-矿业评估/<项目名>/`

## 输出前自检清单

- [ ] **Step 0已执行：实时价格数据已获取并使用**
- [ ] **报告中无任何来自训练数据的价格/成本/门槛数据**
- [ ] **所有价格数据标注来源和日期（如"$4,670/oz, yfinance, 2026-05-06"）**
- [ ] **经济门槛为动态计算值（非历史固定的3.5 g/t）**
- [ ] 类型判断有 ≥3 条独立证据支撑
- [ ] 至少 3 个对比矿床（同类型 + 同成矿带）
- [ ] 10 项打分有依据简述
- [ ] 品位单位统一为 g/t Au
- [ ] 数据来源已标注
- [ ] 推论与假设已独立列出
- [ ] 最大风险已明确陈述（特别是选冶风险）
- [ ] 下一步建议含具体工作量级
