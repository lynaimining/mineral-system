# 矿业评估报告实时数据系统 - 快速开始

## 🎯 核心价值

将矿业评估报告中的所有关键数据从历史训练数据升级为实时市场数据。

**一句话总结：** 金价从$2,000涨到$4,670，经济门槛从3.5 g/t降到0.98 g/t，同一个项目从"不可行"变成"高度有利"——这就是实时数据的价值。

---

## 🚀 快速使用

### 在报告生成中使用实时数据

```python
import sys
sys.path.insert(0, r'C:\Users\39555\.claude\tools\mining-price-engine')
from report_integration import get_live_prices, format_price_for_report

# 获取实时数据
live_data = get_live_prices()

# 使用实时金价
gold = format_price_for_report('gold', live_data)
print(gold['formatted'])
# 输出: $4,670.60/oz (yfinance:GC=F, 2026-05-06)
```

### 计算调整后成本

```python
from report_integration import calculate_adjusted_opex

adjusted = calculate_adjusted_opex(
    base_opex_2020=380,  # 2020年基准OPEX
    country='China',
    report_year=2022,
    live_data=live_data
)

print(f"调整后OPEX: {adjusted['adjusted_opex']} USD/t")
# 输出: 调整后OPEX: 605.2 USD/t
```

### 动态计算经济门槛

```python
from report_integration import calculate_breakeven_grade

breakeven = calculate_breakeven_grade(
    metal_price_usd_oz=4670.6,
    usd_cny=6.84,
    opex_usd_t=605,
    capex_amort_usd_t=251,
    recovery_pct=85
)

print(f"盈亏平衡品位: {breakeven} g/t")
# 输出: 盈亏平衡品位: 0.98 g/t
```

---

## 📊 实时数据对比

| 指标 | 历史数据 | 实时数据 | 差异 |
|------|---------|---------|------|
| 金价 | $2,000-2,500/oz | **$4,670.6/oz** | +87-134% |
| 经济门槛 | 3.5 g/t | **0.98 g/t** | -72% |
| OPEX | 380元/t | **605元/t** | +59% |
| 成本调整 | 无 | **2.01x** | 新增 |

---

## 📁 核心文件

```
mining-price-engine/
├── price_engine.py           # 实时价格引擎
├── report_integration.py     # 报告集成模块（主要使用这个）
├── mining_knowledge_db.py    # JORC数据库
├── mining_knowledge.db       # SQLite数据库
└── README.md                 # 完整文档
```

---

## ⚠️ 重要提示

1. **金价风险：** 当前$4,670/oz处于历史极高位，投资决策应考虑金价回归均值风险
2. **成本上涨：** 成本也在涨（2.01x），不能只看金价
3. **数据缓存：** 价格数据缓存24小时，可用`force_refresh=True`强制刷新

---

## 📖 完整文档

详见 [README.md](README.md)

---

**创建日期：** 2026-05-07
**版本：** v1.1
