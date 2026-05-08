# -*- coding: utf-8 -*-
"""
完整矿业估值引擎 - Level 3
整合所有估值模块：实时价格、可比交易、技术参数、DCF、风险分析
"""
import sys
sys.path.insert(0, r'C:\Users\39555\.claude\tools\mining-price-engine')

from report_integration import get_live_prices, format_price_for_report, calculate_adjusted_opex
from comparable_transactions import estimate_value_by_comparables, initialize_seed_data
from technical_parameters import calculate_adjusted_mining_cost, calculate_support_cost
from dcf_valuation import generate_mining_schedule, calculate_npv_irr_payback, sensitivity_analysis, monte_carlo_simulation
from typing import Dict, Any

def comprehensive_valuation(
    # 项目基本信息
    project_name: str,
    metal_type: str,
    country: str,

    # 资源量参数
    resource_tonnage_mt: float,
    grade_g_t: float,
    recovery_pct: float,

    # 采矿参数
    mining_method: str,  # 'open_pit' or 'underground'
    annual_capacity_mt: float,
    strip_ratio: float = None,
    depth_m: float = None,
    rock_type: str = 'medium',

    # 成本参数（2020年基准）
    base_opex_mining_usd_t: float = None,
    base_opex_processing_usd_t: float = None,
    capex_initial_musd: float = None,

    # 财务参数
    construction_years: int = 2,
    discount_rate: float = 0.08,
    tax_rate: float = 0.25,
    royalty_rate: float = 0.04,

    # 风险分析
    run_sensitivity: bool = True,
    run_monte_carlo: bool = False,

    # 强制刷新实时数据
    force_refresh_prices: bool = False
) -> Dict[str, Any]:
    """
    完整矿业项目估值

    Returns:
        {
            'project_info': {...},
            'live_market_data': {...},
            'technical_adjusted_costs': {...},
            'mining_schedule': {...},
            'dcf_valuation': {...},
            'comparable_valuation': {...},
            'sensitivity_analysis': {...},
            'monte_carlo': {...},
            'summary': {...}
        }
    """
    print(f'\n{"="*60}')
    print(f'矿业项目完整估值 - {project_name}')
    print(f'{"="*60}\n')

    result = {
        'project_info': {
            'name': project_name,
            'metal_type': metal_type,
            'country': country,
            'mining_method': mining_method
        }
    }

    # ========== Step 1: 获取实时市场数据 ==========
    print('Step 1: 获取实时市场数据...')
    live_data = get_live_prices(force_refresh=force_refresh_prices)

    if not live_data:
        print('错误: 无法获取实时数据')
        return None

    metal_price = format_price_for_report(metal_type, live_data)
    usd_cny = live_data['usd_cny']['rate']
    cost_factor = live_data['derived']['cost_adjustment_factor']['value']

    result['live_market_data'] = {
        'metal_price': metal_price,
        'usd_cny': usd_cny,
        'cost_adjustment_factor': cost_factor,
        'data_date': live_data['generated_at']
    }

    print(f'  金属价格: {metal_price["formatted"]}')
    print(f'  汇率: {usd_cny} CNY/USD')
    print(f'  成本调整系数: {cost_factor}x\n')

    # ========== Step 2: 技术参数调整成本 ==========
    print('Step 2: 技术参数调整成本...')

    # 如果没有提供基准成本，使用JORC数据库的平均值
    if base_opex_mining_usd_t is None:
        base_opex_mining_usd_t = 50 if mining_method == 'open_pit' else 120
    if base_opex_processing_usd_t is None:
        base_opex_processing_usd_t = 30

    # 调整采矿成本
    adjusted_mining = calculate_adjusted_mining_cost(
        base_cost_usd_t=base_opex_mining_usd_t,
        mining_method=mining_method,
        strip_ratio=strip_ratio,
        depth_m=depth_m,
        rock_type=rock_type
    )

    # 通胀调整
    adjusted_mining_inflated = adjusted_mining['adjusted_cost'] * cost_factor
    adjusted_processing_inflated = base_opex_processing_usd_t * cost_factor
    total_opex_usd_t = adjusted_mining_inflated + adjusted_processing_inflated

    result['technical_adjusted_costs'] = {
        'mining_base': base_opex_mining_usd_t,
        'mining_technical_adjusted': adjusted_mining['adjusted_cost'],
        'mining_inflated': round(adjusted_mining_inflated, 1),
        'processing_inflated': round(adjusted_processing_inflated, 1),
        'total_opex_usd_t': round(total_opex_usd_t, 1),
        'explanation': adjusted_mining['explanation']
    }

    print(f'  采矿成本（技术调整）: ${adjusted_mining["adjusted_cost"]}/t')
    print(f'  采矿成本（通胀调整）: ${adjusted_mining_inflated:.1f}/t')
    print(f'  选矿成本（通胀调整）: ${adjusted_processing_inflated:.1f}/t')
    print(f'  总OPEX: ${total_opex_usd_t:.1f}/t')
    print(f'  说明: {adjusted_mining["explanation"]}\n')

    # ========== Step 3: 生成采矿计划 ==========
    print('Step 3: 生成采矿计划...')
    schedule = generate_mining_schedule(
        resource_tonnage_mt=resource_tonnage_mt,
        annual_capacity_mt=annual_capacity_mt,
        grade_g_t=grade_g_t,
        recovery_pct=recovery_pct,
        construction_years=construction_years
    )

    result['mining_schedule'] = schedule

    print(f'  矿山寿命: {schedule["lom_years"]}年')
    print(f'  年产金量: {schedule["annual_gold_kg"]:.0f} kg = {schedule["annual_gold_oz"]:.0f} oz')
    print(f'  总项目期: {schedule["total_production_years"]}年\n')

    # ========== Step 4: DCF估值 ==========
    print('Step 4: DCF估值（NPV/IRR/Payback）...')

    # 计算年运营成本
    annual_opex_musd = total_opex_usd_t * annual_capacity_mt

    # 如果没有提供CAPEX，使用经验公式估算
    if capex_initial_musd is None:
        # 经验公式：CAPEX ≈ 年产能 × $150-300/t（地下矿更高）
        capex_per_t = 200 if mining_method == 'open_pit' else 350
        capex_initial_musd = annual_capacity_mt * capex_per_t * cost_factor
    else:
        # 通胀调整用户提供的CAPEX
        capex_initial_musd = capex_initial_musd * cost_factor

    dcf = calculate_npv_irr_payback(
        gold_price_usd_oz=metal_price['price'],
        annual_gold_oz=schedule['annual_gold_oz'],
        annual_opex_musd=annual_opex_musd,
        capex_initial_musd=capex_initial_musd,
        lom_years=int(schedule['lom_years']),
        construction_years=construction_years,
        discount_rate=discount_rate,
        tax_rate=tax_rate,
        royalty_rate=royalty_rate,
        salvage_rate=-0.05,
        working_capital_musd=capex_initial_musd * 0.1
    )

    result['dcf_valuation'] = dcf

    print(f'  NPV({int(discount_rate*100)}%): ${dcf["npv_musd"]:.1f}M = CNY {dcf["npv_musd"] * usd_cny:.0f}M')
    if dcf["irr_pct"]:
        print(f'  IRR: {dcf["irr_pct"]:.1f}%')
    print(f'  Payback: {dcf["payback_years"]}年')
    print(f'  CAPEX: ${capex_initial_musd:.1f}M')
    print(f'  年OPEX: ${annual_opex_musd:.1f}M\n')

    # ========== Step 5: 可比交易估值 ==========
    print('Step 5: 可比交易估值...')

    # 计算资源量（百万盎司）
    resource_moz = resource_tonnage_mt * grade_g_t / 31.1035

    # 确定项目阶段
    if 'production' in project_name.lower() or annual_capacity_mt > 0.5:
        stage = 'production'
    elif 'reserve' in project_name.lower():
        stage = 'reserve'
    else:
        stage = 'resource'

    comparable = estimate_value_by_comparables(
        resource_moz=resource_moz,
        metal_type=metal_type,
        stage=stage,
        country=country
    )

    result['comparable_valuation'] = comparable

    print(f'  估值: ${comparable["valuation_musd"]:.1f}M = CNY {comparable["valuation_musd"] * usd_cny:.0f}M')
    print(f'  使用倍数: ${comparable["ev_per_oz_used"]:.1f}/oz')
    print(f'  估值区间: ${comparable["valuation_range_musd"][0]:.1f}M - ${comparable["valuation_range_musd"][1]:.1f}M')
    print(f'  可比交易数量: {comparable["comparable_count"]}\n')

    # ========== Step 6: 敏感性分析 ==========
    if run_sensitivity:
        print('Step 6: 敏感性分析...')

        sensitivity = sensitivity_analysis(
            base_case={
                'gold_price_usd_oz': metal_price['price'],
                'annual_gold_oz': schedule['annual_gold_oz'],
                'annual_opex_musd': annual_opex_musd,
                'capex_initial_musd': capex_initial_musd,
                'lom_years': int(schedule['lom_years']),
                'construction_years': construction_years,
                'discount_rate': discount_rate,
                'tax_rate': tax_rate,
                'royalty_rate': royalty_rate,
                'salvage_rate': -0.05,
                'working_capital_musd': capex_initial_musd * 0.1
            },
            variables={
                'gold_price': [-30, -20, -10, 0, 10, 20, 30],
                'opex': [-10, 0, 10, 20],
                'capex': [-10, 0, 10, 20]
            }
        )

        result['sensitivity_analysis'] = sensitivity

        print(f'  金价±30%: NPV范围 ${min(sensitivity["gold_price"]):.0f}M - ${max(sensitivity["gold_price"]):.0f}M')
        print(f'  OPEX±20%: NPV范围 ${min(sensitivity["opex"]):.0f}M - ${max(sensitivity["opex"]):.0f}M\n')

    # ========== Step 7: 蒙特卡洛模拟（可选） ==========
    if run_monte_carlo:
        print('Step 7: 蒙特卡洛模拟（1000次）...')

        mc = monte_carlo_simulation(
            base_case={
                'gold_price_usd_oz': metal_price['price'],
                'annual_gold_oz': schedule['annual_gold_oz'],
                'annual_opex_musd': annual_opex_musd,
                'capex_initial_musd': capex_initial_musd,
                'lom_years': int(schedule['lom_years']),
                'construction_years': construction_years,
                'discount_rate': discount_rate,
                'tax_rate': tax_rate,
                'royalty_rate': royalty_rate,
                'salvage_rate': -0.05,
                'working_capital_musd': capex_initial_musd * 0.1
            },
            uncertainties={
                'gold_price': (metal_price['price'] * 0.7, metal_price['price'] * 1.3, 'uniform'),
                'opex': (annual_opex_musd, annual_opex_musd * 0.15, 'normal')
            },
            n_simulations=1000
        )

        result['monte_carlo'] = mc

        print(f'  NPV均值: ${mc["mean"]:.1f}M')
        print(f'  P10-P90区间: ${mc["p10"]:.1f}M - ${mc["p90"]:.1f}M')
        print(f'  NPV>0概率: {mc["prob_positive"]:.1f}%\n')

    # ========== 总结 ==========
    print(f'{"="*60}')
    print('估值总结')
    print(f'{"="*60}\n')

    summary = {
        'dcf_npv_musd': dcf["npv_musd"],
        'dcf_npv_cny': round(dcf["npv_musd"] * usd_cny, 0),
        'comparable_valuation_musd': comparable["valuation_musd"],
        'comparable_valuation_cny': round(comparable["valuation_musd"] * usd_cny, 0),
        'weighted_valuation_musd': round(dcf["npv_musd"] * 0.6 + comparable["valuation_musd"] * 0.4, 1),
        'recommendation': None
    }

    # 加权估值（DCF 60% + 可比交易 40%）
    weighted_val = summary['weighted_valuation_musd']
    summary['weighted_valuation_cny'] = round(weighted_val * usd_cny, 0)

    # 投资建议
    if dcf["npv_musd"] > 0 and dcf.get("irr_pct", 0) > discount_rate * 100:
        summary['recommendation'] = '推荐投资'
    elif dcf["npv_musd"] > 0:
        summary['recommendation'] = '谨慎考虑'
    else:
        summary['recommendation'] = '不推荐'

    result['summary'] = summary

    print(f'DCF估值（NPV）: ${dcf["npv_musd"]:.1f}M = CNY {summary["dcf_npv_cny"]:.0f}M')
    print(f'可比交易估值: ${comparable["valuation_musd"]:.1f}M = CNY {summary["comparable_valuation_cny"]:.0f}M')
    print(f'加权估值（DCF 60% + 可比 40%）: ${weighted_val:.1f}M = CNY {summary["weighted_valuation_cny"]:.0f}M')
    print(f'\n投资建议: {summary["recommendation"]}')
    print(f'{"="*60}\n')

    return result

# 使用示例
if __name__ == '__main__':
    # 初始化可比交易种子数据
    initialize_seed_data()

    # 完整估值示例：湖南醴陵金矿
    result = comprehensive_valuation(
        project_name='湖南醴陵金矿',
        metal_type='gold',
        country='China',

        resource_tonnage_mt=21,
        grade_g_t=2.86,
        recovery_pct=85,

        mining_method='underground',
        annual_capacity_mt=1.5,
        depth_m=500,
        rock_type='medium',

        base_opex_mining_usd_t=120,
        base_opex_processing_usd_t=30,
        capex_initial_musd=150,

        construction_years=2,
        discount_rate=0.08,

        run_sensitivity=True,
        run_monte_carlo=False
    )

    # 保存结果
    import json
    output_path = r'C:\Users\39555\.claude\temp\valuation_result.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        # 移除numpy数组（不能JSON序列化）
        result_copy = result.copy()
        if 'sensitivity_analysis' in result_copy:
            result_copy['sensitivity_analysis'] = {k: [float(v) for v in vals]
                                                   for k, vals in result_copy['sensitivity_analysis'].items()}
        json.dump(result_copy, f, ensure_ascii=False, indent=2)

    print(f'完整估值结果已保存至: {output_path}')
