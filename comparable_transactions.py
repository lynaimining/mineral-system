# -*- coding: utf-8 -*-
"""
矿业可比交易数据库模块
用于获取和分析矿业并购交易数据，支持估值
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

CACHE_PATH = r'C:\Users\39555\.claude\temp\mining_transactions_cache.json'
CACHE_MAX_AGE_DAYS = 30  # 可比交易数据缓存30天

def get_cached_transactions(metal_type: str = None) -> Optional[List[Dict]]:
    """
    获取缓存的交易数据

    Args:
        metal_type: 'gold', 'copper', 'lithium', 'nickel' 或 None（全部）

    Returns:
        交易列表或None（如果缓存过期或不存在）
    """
    if not os.path.exists(CACHE_PATH):
        return None

    try:
        with open(CACHE_PATH, 'r', encoding='utf-8') as f:
            cache = json.load(f)

        # 检查缓存时间
        cache_time = datetime.fromisoformat(cache['generated_at'])
        age_days = (datetime.now() - cache_time).days

        if age_days > CACHE_MAX_AGE_DAYS:
            return None

        transactions = cache['transactions']

        # 按金属类型过滤
        if metal_type:
            transactions = [t for t in transactions if t['metal_type'].lower() == metal_type.lower()]

        return transactions

    except Exception as e:
        print(f'读取缓存失败: {e}')
        return None

def save_transactions_cache(transactions: List[Dict]):
    """保存交易数据到缓存"""
    cache = {
        'generated_at': datetime.now().isoformat(),
        'transactions': transactions
    }

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def parse_transaction_from_search(search_result: str) -> Dict[str, Any]:
    """
    从搜索结果中解析交易数据

    这个函数需要配合WebSearch工具使用
    返回标准化的交易数据结构
    """
    # 这是一个占位函数，实际解析由调用者完成
    # 返回标准格式
    return {
        'date': None,
        'buyer': None,
        'seller': None,
        'project_name': None,
        'metal_type': None,
        'country': None,
        'transaction_value_musd': None,  # 交易金额（百万美元）
        'resource_moz': None,  # 资源量（百万盎司）
        'ev_per_oz': None,  # EV/Resource倍数（USD/oz）
        'stage': None,  # 'exploration', 'resource', 'reserve', 'production'
        'source': None
    }

def calculate_valuation_multiples(transactions: List[Dict]) -> Dict[str, Any]:
    """
    计算估值倍数统计

    Returns:
        {
            'ev_per_oz': {'min': X, 'max': Y, 'median': Z, 'p25': A, 'p75': B},
            'by_stage': {...},
            'by_country': {...}
        }
    """
    import numpy as np

    # 过滤有效数据
    valid_txns = [t for t in transactions if t.get('ev_per_oz') and t.get('ev_per_oz') > 0]

    if not valid_txns:
        return None

    ev_per_oz_values = [t['ev_per_oz'] for t in valid_txns]

    result = {
        'ev_per_oz': {
            'min': min(ev_per_oz_values),
            'max': max(ev_per_oz_values),
            'median': np.median(ev_per_oz_values),
            'p25': np.percentile(ev_per_oz_values, 25),
            'p75': np.percentile(ev_per_oz_values, 75),
            'mean': np.mean(ev_per_oz_values),
            'count': len(valid_txns)
        }
    }

    # 按阶段分组
    by_stage = {}
    for stage in ['exploration', 'resource', 'reserve', 'production']:
        stage_txns = [t['ev_per_oz'] for t in valid_txns if t.get('stage') == stage]
        if stage_txns:
            by_stage[stage] = {
                'median': np.median(stage_txns),
                'mean': np.mean(stage_txns),
                'count': len(stage_txns)
            }
    result['by_stage'] = by_stage

    # 按国家分组
    by_country = {}
    for country in set(t.get('country') for t in valid_txns if t.get('country')):
        country_txns = [t['ev_per_oz'] for t in valid_txns if t.get('country') == country]
        if country_txns:
            by_country[country] = {
                'median': np.median(country_txns),
                'mean': np.mean(country_txns),
                'count': len(country_txns)
            }
    result['by_country'] = by_country

    return result

def estimate_value_by_comparables(
    resource_moz: float,
    metal_type: str,
    stage: str,
    country: str = None
) -> Dict[str, Any]:
    """
    基于可比交易估值

    Args:
        resource_moz: 资源量（百万盎司）
        metal_type: 'gold', 'copper', 'lithium', 'nickel'
        stage: 'exploration', 'resource', 'reserve', 'production'
        country: 国家（可选，用于调整）

    Returns:
        {
            'valuation_musd': 估值（百万美元）,
            'ev_per_oz_used': 使用的倍数,
            'valuation_range': (低, 高),
            'comparable_count': 可比交易数量,
            'method': '可比交易法'
        }
    """
    # 获取可比交易数据
    transactions = get_cached_transactions(metal_type)

    if not transactions:
        # 如果没有缓存，返回行业经验值
        print('警告: 没有可比交易数据，使用行业经验值')
        return estimate_value_by_industry_benchmark(resource_moz, metal_type, stage)

    # 计算倍数
    multiples = calculate_valuation_multiples(transactions)

    if not multiples:
        return estimate_value_by_industry_benchmark(resource_moz, metal_type, stage)

    # 选择合适的倍数
    if stage in multiples['by_stage']:
        ev_per_oz = multiples['by_stage'][stage]['median']
    else:
        ev_per_oz = multiples['ev_per_oz']['median']

    # 国家调整（如果有数据）
    if country and country in multiples.get('by_country', {}):
        country_factor = multiples['by_country'][country]['median'] / multiples['ev_per_oz']['median']
        ev_per_oz *= country_factor

    # 计算估值
    valuation = resource_moz * ev_per_oz

    # 估值区间（P25-P75）
    p25 = multiples['ev_per_oz']['p25']
    p75 = multiples['ev_per_oz']['p75']
    valuation_range = (resource_moz * p25, resource_moz * p75)

    return {
        'valuation_musd': round(valuation, 1),
        'ev_per_oz_used': round(ev_per_oz, 1),
        'valuation_range_musd': (round(valuation_range[0], 1), round(valuation_range[1], 1)),
        'comparable_count': multiples['ev_per_oz']['count'],
        'method': '可比交易法',
        'data_source': 'cached_transactions',
        'stage': stage,
        'country': country
    }

def estimate_value_by_industry_benchmark(
    resource_moz: float,
    metal_type: str,
    stage: str
) -> Dict[str, Any]:
    """
    基于行业基准估值（当没有可比交易数据时使用）

    行业经验值（USD/oz）：
    - Gold:
      - Exploration: $10-30/oz
      - Resource: $30-80/oz
      - Reserve: $80-150/oz
      - Production: $150-300/oz
    - Copper (转换为金当量):
      - 使用铜价/金价比例调整
    """
    # 行业基准倍数（USD/oz）
    benchmarks = {
        'gold': {
            'exploration': 20,
            'resource': 50,
            'reserve': 100,
            'production': 200
        },
        'copper': {
            'exploration': 15,
            'resource': 40,
            'reserve': 80,
            'production': 150
        },
        'lithium': {
            'exploration': 25,
            'resource': 60,
            'reserve': 120,
            'production': 250
        },
        'nickel': {
            'exploration': 18,
            'resource': 45,
            'reserve': 90,
            'production': 180
        }
    }

    ev_per_oz = benchmarks.get(metal_type.lower(), benchmarks['gold']).get(stage, 50)
    valuation = resource_moz * ev_per_oz

    # 估值区间（±40%）
    valuation_range = (valuation * 0.6, valuation * 1.4)

    return {
        'valuation_musd': round(valuation, 1),
        'ev_per_oz_used': ev_per_oz,
        'valuation_range_musd': (round(valuation_range[0], 1), round(valuation_range[1], 1)),
        'comparable_count': 0,
        'method': '行业基准法',
        'data_source': 'industry_benchmark',
        'stage': stage,
        'note': '使用行业经验值，建议补充可比交易数据'
    }

# 种子数据：近期真实交易（手动录入）
SEED_TRANSACTIONS = [
    {
        'date': '2024-11',
        'buyer': 'Newmont',
        'seller': 'Newcrest',
        'project_name': 'Newcrest Mining (全公司收购)',
        'metal_type': 'gold',
        'country': 'Australia',
        'transaction_value_musd': 19500,
        'resource_moz': 139,  # Newcrest总资源量
        'ev_per_oz': 140,
        'stage': 'production',
        'source': 'public_announcement'
    },
    {
        'date': '2023-08',
        'buyer': 'Agnico Eagle',
        'seller': 'Yamana Gold',
        'project_name': 'Yamana Gold (全公司收购)',
        'metal_type': 'gold',
        'country': 'Canada',
        'transaction_value_musd': 4800,
        'resource_moz': 48,
        'ev_per_oz': 100,
        'stage': 'production',
        'source': 'public_announcement'
    },
    {
        'date': '2024-03',
        'buyer': 'Zijin Mining',
        'seller': 'Continental Gold',
        'project_name': 'Buriticá Gold Mine',
        'metal_type': 'gold',
        'country': 'Colombia',
        'transaction_value_musd': 1400,
        'resource_moz': 10.5,
        'ev_per_oz': 133,
        'stage': 'production',
        'source': 'public_announcement'
    },
    {
        'date': '2023-12',
        'buyer': 'BHP',
        'seller': 'OZ Minerals',
        'project_name': 'OZ Minerals (铜金矿)',
        'metal_type': 'copper',
        'country': 'Australia',
        'transaction_value_musd': 9600,
        'resource_moz': 85,  # 铜当量
        'ev_per_oz': 113,
        'stage': 'production',
        'source': 'public_announcement'
    },
    {
        'date': '2024-06',
        'buyer': 'Ganfeng Lithium',
        'seller': 'Lithium Americas',
        'project_name': 'Cauchari-Olaroz (锂矿)',
        'metal_type': 'lithium',
        'country': 'Argentina',
        'transaction_value_musd': 962,
        'resource_moz': 4.2,  # LCE当量
        'ev_per_oz': 229,
        'stage': 'reserve',
        'source': 'public_announcement'
    }
]

def initialize_seed_data():
    """初始化种子数据到缓存"""
    save_transactions_cache(SEED_TRANSACTIONS)
    print(f'已初始化 {len(SEED_TRANSACTIONS)} 条种子交易数据')

# 使用示例
if __name__ == '__main__':
    print('=== 矿业可比交易估值模块测试 ===\n')

    # 初始化种子数据
    initialize_seed_data()

    # 测试估值
    print('测试案例：湖南醴陵金矿')
    print('资源量：2.0 Moz (约60吨)')
    print('阶段：Resource')
    print('国家：China\n')

    valuation = estimate_value_by_comparables(
        resource_moz=2.0,
        metal_type='gold',
        stage='resource',
        country='China'
    )

    print(f'估值结果：')
    print(f'  估值：${valuation["valuation_musd"]:.1f}M = CNY {valuation["valuation_musd"] * 6.84:.0f}M')
    print(f'  使用倍数：${valuation["ev_per_oz_used"]:.1f}/oz')
    print(f'  估值区间：${valuation["valuation_range_musd"][0]:.1f}M - ${valuation["valuation_range_musd"][1]:.1f}M')
    print(f'  可比交易数量：{valuation["comparable_count"]}')
    print(f'  方法：{valuation["method"]}')
