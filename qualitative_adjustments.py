# -*- coding: utf-8 -*-
"""
定性调整因子模块
在模型预测基础上叠加定性因子调整
"""

def calculate_qualitative_adjustments(
    model_ev_per_oz,
    grade_gt,
    aisc_usd,
    infra_status,
    bidding_context=None,
    strategic_value=None,
    control_premium=None,
    political_risk=None
):
    """
    计算定性调整后的EV/oz

    Args:
        model_ev_per_oz: 模型预测的EV/oz
        grade_gt: 品位 (g/t Au)
        aisc_usd: AISC ($/oz)
        infra_status: 'brownfield' 或 'greenfield'
        bidding_context: 'single' / 'competitive' / None
        strategic_value: 'pipeline' / 'consolidation' / None
        control_premium: True/False (是否100%收购)
        political_risk: 'low' / 'medium' / 'high'

    Returns:
        adjusted_ev_per_oz: 调整后的EV/oz
        adjustment_breakdown: 各因子调整明细
    """

    adjustments = {}
    total_adjustment = 0.0

    # 1. 品位溢价/折价
    if grade_gt >= 5.0:
        grade_adj = 0.20  # 高品位+20%
        adjustments['grade_premium'] = '+20% (高品位 ≥5 g/t)'
    elif grade_gt >= 3.0:
        grade_adj = 0.10  # 中高品位+10%
        adjustments['grade_premium'] = '+10% (中高品位 3-5 g/t)'
    elif grade_gt < 1.5:
        grade_adj = -0.15  # 低品位-15%
        adjustments['grade_discount'] = '-15% (低品位 <1.5 g/t)'
    else:
        grade_adj = 0.0
        adjustments['grade_premium'] = '0% (标准品位)'

    total_adjustment += grade_adj

    # 2. 成本溢价/折价
    if aisc_usd < 800:
        cost_adj = 0.15  # 超低成本+15%
        adjustments['cost_premium'] = '+15% (AISC <$800/oz)'
    elif aisc_usd < 1000:
        cost_adj = 0.08  # 低成本+8%
        adjustments['cost_premium'] = '+8% (AISC $800-1000/oz)'
    elif aisc_usd > 1500:
        cost_adj = -0.12  # 高成本-12%
        adjustments['cost_discount'] = '-12% (AISC >$1500/oz)'
    else:
        cost_adj = 0.0
        adjustments['cost_premium'] = '0% (标准成本)'

    total_adjustment += cost_adj

    # 3. 基建溢价/折价
    if infra_status == 'brownfield':
        infra_adj = 0.15  # 已有基建+15%
        adjustments['infra_premium'] = '+15% (brownfield)'
    else:
        infra_adj = -0.20  # 绿地项目-20%
        adjustments['infra_discount'] = '-20% (greenfield)'

    total_adjustment += infra_adj

    # 4. 竞标溢价
    if bidding_context == 'competitive':
        bidding_adj = 0.30  # 多买家竞标+30%
        adjustments['bidding_premium'] = '+30% (竞标环境)'
    else:
        bidding_adj = 0.0
        adjustments['bidding_premium'] = '0% (无竞标)'

    total_adjustment += bidding_adj

    # 5. 战略溢价
    if strategic_value == 'pipeline':
        strategic_adj = 0.20  # 补充pipeline+20%
        adjustments['strategic_premium'] = '+20% (补充pipeline)'
    elif strategic_value == 'consolidation':
        strategic_adj = 0.15  # 区域整合+15%
        adjustments['strategic_premium'] = '+15% (区域整合)'
    else:
        strategic_adj = 0.0
        adjustments['strategic_premium'] = '0% (无战略溢价)'

    total_adjustment += strategic_adj

    # 6. 控制权溢价
    if control_premium:
        control_adj = 0.25  # 100%收购+25%
        adjustments['control_premium'] = '+25% (100%控制权)'
    else:
        control_adj = 0.0
        adjustments['control_premium'] = '0% (部分股权)'

    total_adjustment += control_adj

    # 7. 政治风险折价
    if political_risk == 'high':
        political_adj = -0.30  # 高风险国家-30%
        adjustments['political_discount'] = '-30% (高政治风险)'
    elif political_risk == 'medium':
        political_adj = -0.15  # 中风险-15%
        adjustments['political_discount'] = '-15% (中政治风险)'
    else:
        political_adj = 0.0
        adjustments['political_discount'] = '0% (低政治风险)'

    total_adjustment += political_adj

    # 计算调整后的EV/oz
    adjusted_ev = model_ev_per_oz * (1 + total_adjustment)

    # 汇总
    adjustment_breakdown = {
        'model_ev_per_oz': model_ev_per_oz,
        'total_adjustment_pct': total_adjustment * 100,
        'adjusted_ev_per_oz': adjusted_ev,
        'factors': adjustments
    }

    return adjusted_ev, adjustment_breakdown


# 测试示例
if __name__ == '__main__':
    print('=== 定性调整因子测试 ===\n')

    # 案例1：高品位地下矿，brownfield，竞标环境
    print('案例1：高品位地下矿 (Brucejack类型)')
    model_ev = 120
    adjusted_ev, breakdown = calculate_qualitative_adjustments(
        model_ev_per_oz=model_ev,
        grade_gt=13.5,
        aisc_usd=950,
        infra_status='brownfield',
        bidding_context='competitive',
        strategic_value='pipeline',
        control_premium=True,
        political_risk='low'
    )

    print(f'  模型预测: ${model_ev}/oz')
    print(f'  总调整: {breakdown["total_adjustment_pct"]:.1f}%')
    print(f'  调整后: ${adjusted_ev:.0f}/oz')
    print('  调整明细:')
    for factor, desc in breakdown['factors'].items():
        print(f'    - {factor}: {desc}')
    print()

    # 案例2：低品位露天矿，greenfield，非洲
    print('案例2：低品位露天矿 (非洲greenfield)')
    model_ev = 80
    adjusted_ev, breakdown = calculate_qualitative_adjustments(
        model_ev_per_oz=model_ev,
        grade_gt=1.2,
        aisc_usd=1100,
        infra_status='greenfield',
        bidding_context=None,
        strategic_value=None,
        control_premium=False,
        political_risk='high'
    )

    print(f'  模型预测: ${model_ev}/oz')
    print(f'  总调整: {breakdown["total_adjustment_pct"]:.1f}%')
    print(f'  调整后: ${adjusted_ev:.0f}/oz')
    print('  调整明细:')
    for factor, desc in breakdown['factors'].items():
        print(f'    - {factor}: {desc}')
    print()

    # 案例3：超高品位，低成本，brownfield
    print('案例3：超高品位低成本 (Fruta del Norte类型)')
    model_ev = 100
    adjusted_ev, breakdown = calculate_qualitative_adjustments(
        model_ev_per_oz=model_ev,
        grade_gt=9.0,
        aisc_usd=650,
        infra_status='brownfield',
        bidding_context='competitive',
        strategic_value='consolidation',
        control_premium=True,
        political_risk='medium'
    )

    print(f'  模型预测: ${model_ev}/oz')
    print(f'  总调整: {breakdown["total_adjustment_pct"]:.1f}%')
    print(f'  调整后: ${adjusted_ev:.0f}/oz')
    print('  调整明细:')
    for factor, desc in breakdown['factors'].items():
        print(f'    - {factor}: {desc}')
