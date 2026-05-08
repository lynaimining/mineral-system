# -*- coding: utf-8 -*-
"""
技术参数模型 - 根据地质和采矿参数调整成本
"""
import math
from typing import Dict, Any

def calculate_adjusted_mining_cost(
    base_cost_usd_t: float,
    mining_method: str,
    strip_ratio: float = None,
    depth_m: float = None,
    rock_type: str = 'medium',
    ore_hardness: str = 'medium'
) -> Dict[str, Any]:
    """
    根据技术参数调整采矿成本

    Args:
        base_cost_usd_t: 基准采矿成本 (USD/t)
        mining_method: 'open_pit' 或 'underground'
        strip_ratio: 剥采比（露天矿）
        depth_m: 开采深度（地下矿，米）
        rock_type: 'soft', 'medium', 'hard'
        ore_hardness: 'soft', 'medium', 'hard'

    Returns:
        {
            'adjusted_cost': 调整后成本,
            'factors': 各调整系数,
            'explanation': 说明
        }
    """
    factors = {}
    explanation = []

    adjusted_cost = base_cost_usd_t

    if mining_method == 'open_pit':
        # 露天矿：剥采比调整
        if strip_ratio is not None:
            # 剥采比每增加1:1，成本增加12-15%
            sr_factor = 1 + (strip_ratio - 1) * 0.13
            factors['strip_ratio'] = sr_factor
            adjusted_cost *= sr_factor
            explanation.append(f'剥采比{strip_ratio:.1f}:1 → 成本系数{sr_factor:.2f}x')

        # 深度调整（露天矿深度影响运输距离）
        if depth_m is not None and depth_m > 100:
            # 每100m深度，运输成本增加5%
            depth_factor = 1 + (depth_m / 100 - 1) * 0.05
            factors['depth'] = depth_factor
            adjusted_cost *= depth_factor
            explanation.append(f'开采深度{depth_m}m → 成本系数{depth_factor:.2f}x')

    elif mining_method == 'underground':
        # 地下矿：深度调整
        if depth_m is not None:
            # 深度每增加100m，成本增加10-12%
            depth_factor = 1 + (depth_m / 100) * 0.11
            factors['depth'] = depth_factor
            adjusted_cost *= depth_factor
            explanation.append(f'开采深度{depth_m}m → 成本系数{depth_factor:.2f}x')

        # 支护成本（根据岩石类型）
        rock_factors = {'soft': 0.85, 'medium': 1.0, 'hard': 1.25}
        rock_factor = rock_factors.get(rock_type, 1.0)
        factors['rock_type'] = rock_factor
        adjusted_cost *= rock_factor
        explanation.append(f'岩石类型{rock_type} → 支护系数{rock_factor:.2f}x')

    # 矿石硬度调整（影响破碎成本）
    hardness_factors = {'soft': 0.90, 'medium': 1.0, 'hard': 1.15}
    hardness_factor = hardness_factors.get(ore_hardness, 1.0)
    factors['ore_hardness'] = hardness_factor
    adjusted_cost *= hardness_factor
    explanation.append(f'矿石硬度{ore_hardness} → 破碎系数{hardness_factor:.2f}x')

    return {
        'base_cost': base_cost_usd_t,
        'adjusted_cost': round(adjusted_cost, 1),
        'total_factor': round(adjusted_cost / base_cost_usd_t, 2),
        'factors': factors,
        'explanation': ' | '.join(explanation)
    }

def calculate_support_cost(
    mining_method: str,
    depth_m: float,
    rock_quality: str,
    tunnel_length_km: float = None
) -> Dict[str, Any]:
    """
    计算地下矿支护成本

    Args:
        mining_method: 'underground' only
        depth_m: 深度（米）
        rock_quality: 'poor', 'fair', 'good', 'excellent' (基于RQD)
        tunnel_length_km: 巷道总长度（公里）

    Returns:
        支护成本估算
    """
    if mining_method != 'underground':
        return {'support_cost_usd_t': 0, 'note': '露天矿无支护成本'}

    # 基准支护成本（USD/m巷道）
    base_support_cost = {
        'poor': 1500,      # RQD < 25%
        'fair': 1000,      # RQD 25-50%
        'good': 600,       # RQD 50-75%
        'excellent': 300   # RQD > 75%
    }

    unit_cost = base_support_cost.get(rock_quality, 1000)

    # 深度调整
    if depth_m > 500:
        depth_factor = 1 + (depth_m - 500) / 1000 * 0.2
        unit_cost *= depth_factor

    # 如果提供了巷道长度，计算总成本
    if tunnel_length_km:
        total_cost = unit_cost * tunnel_length_km * 1000  # 转换为米
        return {
            'unit_cost_usd_m': round(unit_cost, 0),
            'total_cost_musd': round(total_cost / 1e6, 1),
            'rock_quality': rock_quality,
            'depth_m': depth_m
        }

    return {
        'unit_cost_usd_m': round(unit_cost, 0),
        'rock_quality': rock_quality,
        'depth_m': depth_m,
        'note': '需要巷道长度数据以计算总成本'
    }

# 使用示例
if __name__ == '__main__':
    print('=== 技术参数模型测试 ===\n')

    # 测试1：露天矿（高剥采比）
    print('测试1：露天金矿（剥采比5:1，深度200m）')
    result1 = calculate_adjusted_mining_cost(
        base_cost_usd_t=50,
        mining_method='open_pit',
        strip_ratio=5.0,
        depth_m=200,
        rock_type='medium',
        ore_hardness='hard'
    )
    print(f'  基准成本: ${result1["base_cost"]}/t')
    print(f'  调整后成本: ${result1["adjusted_cost"]}/t')
    print(f'  总系数: {result1["total_factor"]}x')
    print(f'  说明: {result1["explanation"]}\n')

    # 测试2：地下矿（深度500m）
    print('测试2：地下金矿（深度500m，硬岩）')
    result2 = calculate_adjusted_mining_cost(
        base_cost_usd_t=120,
        mining_method='underground',
        depth_m=500,
        rock_type='hard',
        ore_hardness='hard'
    )
    print(f'  基准成本: ${result2["base_cost"]}/t')
    print(f'  调整后成本: ${result2["adjusted_cost"]}/t')
    print(f'  总系数: {result2["total_factor"]}x')
    print(f'  说明: {result2["explanation"]}\n')

    # 测试3：支护成本
    print('测试3：地下矿支护成本（深度500m，岩石质量fair）')
    result3 = calculate_support_cost(
        mining_method='underground',
        depth_m=500,
        rock_quality='fair',
        tunnel_length_km=15
    )
    print(f'  单位成本: ${result3["unit_cost_usd_m"]}/m')
    print(f'  总成本: ${result3["total_cost_musd"]}M')
