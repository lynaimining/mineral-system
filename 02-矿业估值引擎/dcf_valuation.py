# -*- coding: utf-8 -*-
"""
完整DCF估值模型 - 包含税收、融资、残值等
"""
import numpy as np
from typing import Dict, List, Any, Optional

def generate_mining_schedule(
    resource_tonnage_mt: float,
    annual_capacity_mt: float,
    grade_g_t: float,
    recovery_pct: float,
    construction_years: int = 2
) -> Dict[str, Any]:
    """
    生成采矿计划

    Args:
        resource_tonnage_mt: 资源量（百万吨）
        annual_capacity_mt: 年处理能力（百万吨）
        grade_g_t: 品位（g/t）
        recovery_pct: 回收率（%）
        construction_years: 建设期（年）

    Returns:
        采矿计划参数
    """
    # 矿山寿命（年）
    lom_years = resource_tonnage_mt / annual_capacity_mt

    # 年产金量（kg）
    annual_gold_kg = annual_capacity_mt * 1e6 * grade_g_t / 1000 * recovery_pct / 100

    # 年产金量（盎司）
    annual_gold_oz = annual_gold_kg * 32.1507  # kg转oz

    return {
        'lom_years': round(lom_years, 1),
        'annual_capacity_mt': annual_capacity_mt,
        'annual_gold_kg': round(annual_gold_kg, 0),
        'annual_gold_oz': round(annual_gold_oz, 0),
        'construction_years': construction_years,
        'total_production_years': construction_years + int(lom_years)
    }

def calculate_npv_irr_payback(
    gold_price_usd_oz: float,
    annual_gold_oz: float,
    annual_opex_musd: float,
    capex_initial_musd: float,
    lom_years: int,
    construction_years: int = 2,
    discount_rate: float = 0.08,
    tax_rate: float = 0.25,
    royalty_rate: float = 0.04,
    salvage_rate: float = -0.05,
    working_capital_musd: float = 0
) -> Dict[str, Any]:
    """
    计算NPV、IRR、Payback

    Args:
        gold_price_usd_oz: 金价（USD/oz）
        annual_gold_oz: 年产金量（oz）
        annual_opex_musd: 年运营成本（百万美元）
        capex_initial_musd: 初始资本支出（百万美元）
        lom_years: 矿山寿命（年）
        construction_years: 建设期（年）
        discount_rate: 折现率（WACC）
        tax_rate: 企业所得税率
        royalty_rate: 特许权使用费率
        salvage_rate: 残值率（负数表示关闭成本）
        working_capital_musd: 营运资金（百万美元）

    Returns:
        NPV、IRR、Payback及详细现金流
    """
    cash_flows = []
    cumulative_cf = []
    years = []

    # 建设期（负现金流）
    capex_per_year = capex_initial_musd / construction_years
    for year in range(construction_years):
        cf = -capex_per_year
        if year == 0:
            cf -= working_capital_musd  # 第一年投入营运资金
        cash_flows.append(cf)
        cumulative_cf.append(sum(cash_flows))
        years.append(year)

    # 生产期
    annual_revenue = annual_gold_oz * gold_price_usd_oz / 1e6  # 转换为百万美元

    for year in range(construction_years, construction_years + int(lom_years)):
        # 收入
        revenue = annual_revenue

        # 特许权使用费
        royalty = revenue * royalty_rate

        # EBITDA
        ebitda = revenue - annual_opex_musd - royalty

        # 税前利润
        ebit = ebitda  # 简化：不考虑折旧

        # 税收
        tax = max(0, ebit * tax_rate)

        # 自由现金流
        fcf = ebit - tax

        # 最后一年：回收营运资金 + 残值
        if year == construction_years + int(lom_years) - 1:
            fcf += working_capital_musd  # 回收营运资金
            fcf += capex_initial_musd * salvage_rate  # 残值（负数=关闭成本）

        cash_flows.append(fcf)
        cumulative_cf.append(sum(cash_flows))
        years.append(year)

    # 计算NPV
    npv = sum([cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows)])

    # 计算IRR（使用numpy-financial）
    try:
        import numpy_financial as npf
        irr = npf.irr(cash_flows)
    except:
        # 备用方案：简单估算
        try:
            irr = np.irr(cash_flows)
        except:
            # 如果numpy.irr不可用，用简单估算
            if npv > 0:
                irr = discount_rate + 0.1  # 粗略估算
            else:
                irr = discount_rate - 0.05
            print(f'警告: IRR计算失败，使用估算值')

    # 计算Payback Period
    payback = None
    for i, cum_cf in enumerate(cumulative_cf):
        if cum_cf > 0:
            payback = i
            break

    return {
        'npv_musd': round(npv, 1),
        'irr_pct': round(irr * 100, 1) if irr else None,
        'payback_years': payback,
        'cash_flows': cash_flows,
        'cumulative_cf': cumulative_cf,
        'years': years,
        'assumptions': {
            'gold_price_usd_oz': gold_price_usd_oz,
            'discount_rate': discount_rate,
            'tax_rate': tax_rate,
            'royalty_rate': royalty_rate,
            'salvage_rate': salvage_rate
        }
    }

def sensitivity_analysis(
    base_case: Dict[str, Any],
    variables: Dict[str, List[float]]
) -> Dict[str, List[float]]:
    """
    敏感性分析

    Args:
        base_case: 基准情景参数
        variables: 变量及其变化范围
            例如: {
                'gold_price': [-20, -10, 0, 10, 20],  # 百分比变化
                'opex': [-10, 0, 10, 20],
                'grade': [-15, 0, 15],
                'recovery': [-5, 0, 5]
            }

    Returns:
        每个变量对应的NPV列表
    """
    results = {}

    for var_name, changes in variables.items():
        npvs = []
        for change_pct in changes:
            # 复制基准情景
            case = base_case.copy()

            # 调整变量
            if var_name == 'gold_price':
                case['gold_price_usd_oz'] *= (1 + change_pct / 100)
            elif var_name == 'opex':
                case['annual_opex_musd'] *= (1 + change_pct / 100)
            elif var_name == 'grade':
                case['annual_gold_oz'] *= (1 + change_pct / 100)
            elif var_name == 'recovery':
                case['annual_gold_oz'] *= (1 + change_pct / 100)
            elif var_name == 'capex':
                case['capex_initial_musd'] *= (1 + change_pct / 100)

            # 重新计算NPV
            result = calculate_npv_irr_payback(**case)
            npvs.append(result['npv_musd'])

        results[var_name] = npvs

    return results

def monte_carlo_simulation(
    base_case: Dict[str, Any],
    uncertainties: Dict[str, tuple],
    n_simulations: int = 1000
) -> Dict[str, Any]:
    """
    蒙特卡洛模拟

    Args:
        base_case: 基准情景参数
        uncertainties: 不确定性参数及其分布
            例如: {
                'gold_price': (4000, 5000, 'uniform'),  # (min, max, distribution)
                'opex': (50, 80, 'normal'),  # (mean, std, distribution)
            }
        n_simulations: 模拟次数

    Returns:
        NPV分布统计
    """
    npvs = []

    for _ in range(n_simulations):
        case = base_case.copy()

        # 随机采样
        for var_name, (param1, param2, dist) in uncertainties.items():
            if dist == 'uniform':
                value = np.random.uniform(param1, param2)
            elif dist == 'normal':
                value = np.random.normal(param1, param2)
            elif dist == 'triangular':
                # param1=min, param2=max, mode=(param1+param2)/2
                mode = (param1 + param2) / 2
                value = np.random.triangular(param1, mode, param2)
            else:
                value = param1

            # 更新参数
            if var_name == 'gold_price':
                case['gold_price_usd_oz'] = value
            elif var_name == 'opex':
                case['annual_opex_musd'] = value
            elif var_name == 'capex':
                case['capex_initial_musd'] = value

        # 计算NPV
        result = calculate_npv_irr_payback(**case)
        npvs.append(result['npv_musd'])

    # 统计
    npvs = np.array(npvs)
    return {
        'mean': round(np.mean(npvs), 1),
        'median': round(np.median(npvs), 1),
        'std': round(np.std(npvs), 1),
        'p10': round(np.percentile(npvs, 10), 1),
        'p90': round(np.percentile(npvs, 90), 1),
        'prob_positive': round(np.sum(npvs > 0) / len(npvs) * 100, 1),
        'min': round(np.min(npvs), 1),
        'max': round(np.max(npvs), 1),
        'npvs': npvs.tolist()
    }

# 使用示例
if __name__ == '__main__':
    print('=== 完整DCF估值模型测试 ===\n')

    # 测试案例：湖南醴陵金矿
    print('测试案例：湖南醴陵金矿')
    print('资源量：21 Mt @ 2.86 g/t')
    print('年处理能力：1.5 Mt/年')
    print('回收率：85%\n')

    # 1. 生成采矿计划
    schedule = generate_mining_schedule(
        resource_tonnage_mt=21,
        annual_capacity_mt=1.5,
        grade_g_t=2.86,
        recovery_pct=85,
        construction_years=2
    )
    print('采矿计划：')
    print(f'  矿山寿命：{schedule["lom_years"]}年')
    print(f'  年产金量：{schedule["annual_gold_kg"]:.0f} kg = {schedule["annual_gold_oz"]:.0f} oz')
    print(f'  建设期：{schedule["construction_years"]}年')
    print(f'  总项目期：{schedule["total_production_years"]}年\n')

    # 2. 计算NPV/IRR/Payback
    dcf = calculate_npv_irr_payback(
        gold_price_usd_oz=4670,
        annual_gold_oz=schedule['annual_gold_oz'],
        annual_opex_musd=90,  # 1.5Mt * 60 USD/t
        capex_initial_musd=200,
        lom_years=int(schedule['lom_years']),
        construction_years=2,
        discount_rate=0.08,
        tax_rate=0.25,
        royalty_rate=0.04,
        salvage_rate=-0.05,
        working_capital_musd=20
    )
    print('DCF估值结果：')
    print(f'  NPV(8%)：${dcf["npv_musd"]:.1f}M')
    if dcf["irr_pct"]:
        print(f'  IRR：{dcf["irr_pct"]:.1f}%')
    else:
        print(f'  IRR：无法计算')
    print(f'  Payback：{dcf["payback_years"]}年\n')

    # 3. 敏感性分析
    print('敏感性分析：')
    sensitivity = sensitivity_analysis(
        base_case={
            'gold_price_usd_oz': 4670,
            'annual_gold_oz': schedule['annual_gold_oz'],
            'annual_opex_musd': 90,
            'capex_initial_musd': 200,
            'lom_years': int(schedule['lom_years']),
            'construction_years': 2,
            'discount_rate': 0.08,
            'tax_rate': 0.25,
            'royalty_rate': 0.04,
            'salvage_rate': -0.05,
            'working_capital_musd': 20
        },
        variables={
            'gold_price': [-20, -10, 0, 10, 20],
            'opex': [-10, 0, 10, 20]
        }
    )
    print(f'  金价变化：{sensitivity["gold_price"]}')
    print(f'  OPEX变化：{sensitivity["opex"]}\n')

    # 4. 蒙特卡洛模拟
    print('蒙特卡洛模拟（1000次）：')
    mc = monte_carlo_simulation(
        base_case={
            'gold_price_usd_oz': 4670,
            'annual_gold_oz': schedule['annual_gold_oz'],
            'annual_opex_musd': 90,
            'capex_initial_musd': 200,
            'lom_years': int(schedule['lom_years']),
            'construction_years': 2,
            'discount_rate': 0.08,
            'tax_rate': 0.25,
            'royalty_rate': 0.04,
            'salvage_rate': -0.05,
            'working_capital_musd': 20
        },
        uncertainties={
            'gold_price': (4000, 5500, 'uniform'),
            'opex': (90, 15, 'normal')  # mean=90, std=15
        },
        n_simulations=1000
    )
    print(f'  NPV均值：${mc["mean"]:.1f}M')
    print(f'  NPV中位数：${mc["median"]:.1f}M')
    print(f'  P10-P90区间：${mc["p10"]:.1f}M - ${mc["p90"]:.1f}M')
    print(f'  NPV>0概率：{mc["prob_positive"]:.1f}%')
