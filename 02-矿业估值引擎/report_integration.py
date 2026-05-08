# -*- coding: utf-8 -*-
"""
矿业评估报告实时数据集成模块
供所有矿种skill调用,确保报告中使用实时价格和成本数据
"""
import json
import os
import sys
from datetime import datetime

# 添加price_engine所在目录到路径
sys.path.insert(0, r'C:\Users\39555\.claude\tools\mining-price-engine')

try:
    from price_engine import build_report_data
    from mining_knowledge_db import get_country_adjusted_costs, query_comparable_projects
except ImportError as e:
    print(f'警告: 无法导入实时数据引擎: {e}')
    build_report_data = None
    get_country_adjusted_costs = None
    query_comparable_projects = None

CACHE_PATH = r'C:\Users\39555\.claude\temp\mining_prices_cache.json'
CACHE_MAX_AGE_HOURS = 24  # 缓存24小时

def get_live_prices(force_refresh=False):
    """
    获取实时价格数据(带缓存)

    Args:
        force_refresh: 强制刷新,忽略缓存

    Returns:
        dict: 包含金属价格、汇率、成本调整系数等的完整数据包
    """
    # 检查缓存
    if not force_refresh and os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                cached = json.load(f)

            # 检查缓存时间
            cache_time = datetime.fromisoformat(cached['generated_at'])
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600

            if age_hours < CACHE_MAX_AGE_HOURS:
                print(f'使用缓存的价格数据 (生成于 {age_hours:.1f} 小时前)')
                return cached
        except Exception as e:
            print(f'读取缓存失败: {e}')

    # 获取实时数据
    if build_report_data is None:
        print('错误: 实时数据引擎未安装')
        return None

    print('正在获取实时价格数据...')
    try:
        data = build_report_data()
        return data
    except Exception as e:
        print(f'获取实时数据失败: {e}')
        return None

def format_price_for_report(metal_name, live_data):
    """
    格式化金属价格用于报告

    Args:
        metal_name: 'gold', 'copper', 'nickel', 'lithium'
        live_data: get_live_prices()返回的数据

    Returns:
        dict: {
            'price': 价格数值,
            'unit': 单位,
            'date': 日期,
            'source': 数据来源,
            'formatted': 格式化字符串 (用于直接插入报告)
        }
    """
    if not live_data or 'metals' not in live_data:
        return None

    metal_data = live_data['metals'].get(metal_name)
    if not metal_data:
        return None

    price = metal_data['price_raw']
    unit = metal_data['unit']
    date = metal_data['date']
    source = metal_data['source']

    # 格式化字符串
    formatted = f'${price:,.2f}/{unit.split("/")[1]} ({source}, {date})'

    return {
        'price': price,
        'unit': unit,
        'date': date,
        'source': source,
        'formatted': formatted
    }

def calculate_adjusted_opex(base_opex_2020, country, report_year, live_data):
    """
    计算调整后的OPEX(考虑通胀和国别差异)

    Args:
        base_opex_2020: 2020年基准OPEX (USD/t)
        country: 国家名称
        report_year: 报告年份
        live_data: get_live_prices()返回的数据

    Returns:
        dict: {
            'base_opex': 基准OPEX,
            'country_factor': 国别系数,
            'inflation_factor': 通胀系数,
            'adjusted_opex': 调整后OPEX,
            'note': 说明
        }
    """
    if not live_data or 'derived' not in live_data:
        return None

    cost_factor = live_data['derived']['cost_adjustment_factor']['value']

    # 计算时间调整
    current_year = 2026
    years_elapsed = current_year - report_year
    time_factor = cost_factor ** (years_elapsed / 6)  # 假设6年翻倍

    # 获取国别系数
    if get_country_adjusted_costs:
        try:
            result = get_country_adjusted_costs(base_opex_2020, country, report_year, current_year, cost_factor)
            return result
        except Exception as e:
            print(f'获取国别调整成本失败: {e}')

    # 备用方案:只用通胀系数
    adjusted = base_opex_2020 * time_factor
    return {
        'base_opex': base_opex_2020,
        'country_factor': 1.0,
        'inflation_factor': time_factor,
        'adjusted_opex': round(adjusted, 1),
        'note': f'基准OPEX × 通胀系数{time_factor:.2f}'
    }

def calculate_breakeven_grade(metal_price_usd_oz, usd_cny, opex_usd_t, capex_amort_usd_t, recovery_pct):
    """
    动态计算盈亏平衡品位

    Args:
        metal_price_usd_oz: 金属价格 (USD/oz)
        usd_cny: 汇率
        opex_usd_t: OPEX (USD/t矿石)
        capex_amort_usd_t: CAPEX摊销 (USD/t矿石)
        recovery_pct: 回收率 (%)

    Returns:
        float: 盈亏平衡品位 (g/t)
    """
    metal_price_cny_g = metal_price_usd_oz / 31.1035 * usd_cny
    total_cost = opex_usd_t + capex_amort_usd_t
    recovery = recovery_pct / 100.0

    breakeven = total_cost / (metal_price_cny_g * recovery)
    return round(breakeven, 2)

def generate_data_source_section(live_data):
    """
    生成报告的数据来源声明章节

    Returns:
        str: 格式化的数据来源说明文本
    """
    if not live_data:
        return "数据来源: 历史参考数据"

    lines = ["数据来源声明", "=" * 50]
    lines.append(f"数据获取时间: {live_data['generated_at']}")
    lines.append("")

    # 金属价格
    if 'metals' in live_data:
        lines.append("金属价格 (实时):")
        for metal, data in live_data['metals'].items():
            lines.append(f"  - {metal.capitalize()}: {data['price_raw']} {data['unit']} ({data['source']}, {data['date']})")

    # 汇率
    if 'usd_cny' in live_data:
        fx = live_data['usd_cny']
        lines.append(f"\n汇率 (实时): {fx['rate']} CNY/USD ({fx['date']})")

    # 成本调整
    if 'derived' in live_data:
        derived = live_data['derived']
        if 'cost_adjustment_factor' in derived:
            caf = derived['cost_adjustment_factor']
            lines.append(f"\n成本调整系数: {caf['value']}x (基于原油价格相对{caf['base_year']}年)")

        if 'gold_breakeven_grade_underground' in derived:
            be = derived['gold_breakeven_grade_underground']
            lines.append(f"地下开采经济门槛: {be['value']} {be['unit']} (动态计算)")

    lines.append("\n" + "=" * 50)
    return "\n".join(lines)

def get_comparable_projects_data(country, deposit_type, mining_method='underground'):
    """
    从JORC数据库获取同类项目数据

    Returns:
        list: 同类项目列表
    """
    if query_comparable_projects is None:
        return []

    try:
        projects = query_comparable_projects(country, deposit_type, mining_method)
        return projects
    except Exception as e:
        print(f'查询同类项目失败: {e}')
        return []

# 使用示例
if __name__ == '__main__':
    print('=== 矿业评估报告实时数据集成模块测试 ===\n')

    # 1. 获取实时价格
    live_data = get_live_prices()

    if live_data:
        # 2. 格式化金价
        gold_price = format_price_for_report('gold', live_data)
        print(f'金价: {gold_price["formatted"]}')

        # 3. 计算调整后OPEX
        adjusted = calculate_adjusted_opex(380, 'China', 2022, live_data)
        print(f'\n调整后OPEX: {adjusted["adjusted_opex"]} USD/t')
        print(f'说明: {adjusted["note"]}')

        # 4. 计算盈亏平衡品位
        breakeven = calculate_breakeven_grade(
            gold_price['price'],
            live_data['usd_cny']['rate'],
            adjusted['adjusted_opex'],
            125 * 2.01,  # CAPEX摊销也要调整
            85
        )
        print(f'\n盈亏平衡品位: {breakeven} g/t')

        # 5. 生成数据来源声明
        print(f'\n{generate_data_source_section(live_data)}')
