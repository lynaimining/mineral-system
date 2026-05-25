# Workflow A：铜矿项目分析

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
- 第7章经济性分析（铜价、伴生金银钼价格、汇率）
- 经济门槛计算（动态计算，非历史固定值）
- OPEX/CAPEX调整（成本调整系数）
- 盈亏平衡分析（基于实时价格）
- 敏感性分析（实时价格±20%）

**绝对禁止：**
- ❌ 使用训练数据中的金属价格
- ❌ 使用历史固定的经济门槛
- ❌ 使用未经通胀调整的OPEX/CAPEX
- ❌ 在报告中出现无来源、无日期的价格数据

---

### Step 1：材料扫描
- 扫描用户当前工作目录（默认 `C:\Users\xuanc\Downloads\paper\Copper\` 或用户指定）
- 列出所有 .docx / .pdf / .pptx / .xlsx / 图像文件
- 优先读取：项目可研、地质报告、PPT 摘要、最新公告

### Step 2：读取必读知识
- `knowledge/deposit_types.md`（必读）
- `knowledge/grade_tonnage.md`（必读）
- `knowledge/global_belts.md`（按地理范围选读）
- `knowledge/tectonic_controls.md`（按构造背景选读）

### Step 3：类型识别（决策树）
回答 deposit_types.md 决策树三问，给出 confidence ranking（最像 X，其次 Y）。

### Step 4：构造定位
对照 global_belts.md，把项目归入成矿带，列举同带头部矿床。

### Step 5：规模—品位评估
- 在该类型 grade-tonnage 累积频率上定位
- 给出 Tier 分级
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
    metal_type='copper',
    country='国家',
    resource_tonnage_mt=资源量_百万吨,
    grade_g_t=品位_百分比,  # 铜矿用%表示
    recovery_pct=回收率_百分比,
    mining_method='open_pit',  # 或 'underground'
    annual_capacity_mt=年处理能力_百万吨,
    strip_ratio=剥采比,  # 露天矿必填
    depth_m=开采深度_米,
    rock_type='medium',
    run_sensitivity=True,
    run_monte_carlo=False
)
```

**估值结果包含：** DCF估值（NPV/IRR/Payback）、可比交易估值、加权估值、敏感性分析、投资建议

**绝对禁止：** 跳过本步骤、使用简化计算、不考虑技术参数、不提供可比交易估值

---

### Step 7：风险与建议

### Step 8：输出
按 `templates/project_assessment.md` 渲染成 .docx，保存至桌面。
- 使用 `anthropic-skills:docx` 生成 docx
- 文件名：`Copper_Project_Assessment_<项目名>_<YYYYMMDD>.docx`

## 输出前自检清单

- [ ] 类型判断有 ≥3 条独立证据支撑
- [ ] 至少 3 个对比矿床
- [ ] 10 项打分有依据简述
- [ ] 数据来源已标注
- [ ] 推论与假设已独立列出
- [ ] 最大风险已明确陈述
- [ ] 下一步建议含具体工作量级
