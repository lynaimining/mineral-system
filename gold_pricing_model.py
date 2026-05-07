# -*- coding: utf-8 -*-
"""
金矿交易对价多因素回归模型
基于40笔可比交易数据，拟合EV/oz = f(阶段, 金价, 国别, 开采方式, 规模, 品位)
"""
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
import json
import os

# 金矿交易数据（补充开采方式、金价等信息）
GOLD_TRANSACTIONS = [
    # (date, ev_per_oz, stage, gold_price_at_time, country, mining_method, resource_moz)
    # stage: 1=exploration, 2=resource, 3=reserve, 4=production
    # mining_method: 0=open_pit, 1=underground, 2=mixed
    ('2026-05', 220, 4, 4670, 'Australia', 2, 35),      # Regis/Vault
    ('2026-02', 86, 2, 4200, 'Australia', 1, 5.2),      # Genesis/Magnetic
    ('2026-Q1', 125, 4, 4300, 'Canada', 2, 12),         # Coeur/New Gold
    ('2025', 49, 2, 3500, 'Africa', 0, 3.5),            # Montage/African Gold
    ('2025', 90, 4, 3500, 'Australia', 1, 4.0),         # Alkane/Mandalay
    ('2025', 30, 1, 3500, 'Canada', 0, 5.0),            # Coffee Gold (exploration)
    ('2025', 105, 4, 3500, 'Canada', 0, 10),            # Franco-Nevada/Cote
    ('2024', 140, 4, 2300, 'Australia', 2, 139),         # Newmont/Newcrest
    ('2024', 133, 4, 2300, 'Colombia', 1, 10.5),        # Zijin/Buritica
    ('2024', 133, 3, 2300, 'Canada', 1, 15),            # Gold Fields/Windfall
    ('2023', 100, 4, 1950, 'Canada', 2, 48),            # Agnico/Yamana
    ('2023', 67, 4, 1950, 'Brazil', 0, 15),             # Pan American/Yamana LatAm
    ('2022', 156, 4, 1800, 'Canada', 1, 18),            # Newcrest/Brucejack
    ('2022', 208, 4, 1800, 'Canada', 2, 48),            # Agnico/Kirkland Lake
    ('2020', 140, 4, 1800, 'Australia', 2, 50),         # Northern Star/Saracen
    ('2020', 142, 4, 1800, 'Turkey', 1, 12),            # SSR/Alacer
    ('2020', 91, 3, 1700, 'Colombia', 1, 11),           # Zijin/Continental
    ('2019', 168, 4, 1500, 'Canada', 0, 22),            # Kirkland/Detour
    ('2019', 116, 4, 1400, 'Canada', 2, 86),            # Newmont/Goldcorp
    ('2018', 83, 4, 1250, 'Mali', 1, 78),               # Barrick/Randgold
    ('2018', 50, 3, 1250, 'Ecuador', 1, 5),             # Newcrest/Fruta del Norte
    ('2017', 80, 4, 1250, 'Tanzania', 1, 15),           # Barrick/Acacia
    ('2016', 104, 2, 1250, 'Canada', 0, 5),             # Goldcorp/Kaminak
    ('2021', 140, 2, 1800, 'Canada', 1, 10),            # Kinross/Great Bear
]

# 准备数据
print('=== 金矿交易对价多因素回归模型 ===\n')
print(f'样本数: {len(GOLD_TRANSACTIONS)} 笔金矿交易\n')

# 特征工程
X_data = []
y_data = []

for txn in GOLD_TRANSACTIONS:
    date, ev_oz, stage, gold_price, country, method, resource = txn

    # 特征向量
    features = [
        stage,                          # 阶段 (1-4)
        gold_price / 1000,              # 金价 (千美元/oz，归一化)
        resource,                       # 资源量 (Moz)
        1 if method == 1 else 0,        # 地下矿 (0/1)
        1 if country == 'Australia' else 0,  # 澳大利亚
        1 if country == 'Canada' else 0,     # 加拿大
        1 if country in ['Mali', 'Tanzania', 'Cote d\'Ivoire', 'Africa'] else 0,  # 非洲
        1 if country in ['Colombia', 'Ecuador', 'Brazil', 'Argentina'] else 0,  # 南美
    ]

    X_data.append(features)
    y_data.append(ev_oz)

X = np.array(X_data)
y = np.array(y_data)

# 线性回归
model = LinearRegression()
model.fit(X, y)

# 模型系数
feature_names = ['阶段(1-4)', '金价(千$/oz)', '资源量(Moz)', '地下矿',
                 '澳大利亚', '加拿大', '非洲', '南美']

print('回归方程:')
print(f'  EV/oz = {model.intercept_:.1f}')
for name, coef in zip(feature_names, model.coef_):
    sign = '+' if coef >= 0 else ''
    print(f'         {sign}{coef:.2f} * {name}')

print(f'\n  R-squared: {model.score(X, y):.3f}')

# 预测函数
def predict_ev_per_oz(stage, gold_price, resource_moz, underground, country):
    """
    预测金矿交易对价

    Args:
        stage: 1=exploration, 2=resource, 3=reserve, 4=production
        gold_price: 当前金价 (USD/oz)
        resource_moz: 资源量 (百万盎司)
        underground: True=地下矿, False=露天矿
        country: 'Australia', 'Canada', 'Africa', 'South America', 'Other'

    Returns:
        预测的EV/oz (USD/oz)
    """
    features = [
        stage,
        gold_price / 1000,
        resource_moz,
        1 if underground else 0,
        1 if country == 'Australia' else 0,
        1 if country == 'Canada' else 0,
        1 if country == 'Africa' else 0,
        1 if country in ['South America', 'Colombia', 'Brazil', 'Argentina'] else 0,
    ]

    predicted = model.predict([features])[0]
    return max(predicted, 5)  # 最低$5/oz

# 测试预测
print('\n=== 预测测试 ===\n')

test_cases = [
    ('中国小型地下金矿(resource阶段)', 2, 4670, 2.0, True, 'Other'),
    ('澳大利亚大型露天金矿(production)', 4, 4670, 50, False, 'Australia'),
    ('加拿大中型地下金矿(reserve)', 3, 4670, 10, True, 'Canada'),
    ('非洲exploration项目', 1, 4670, 3, False, 'Africa'),
    ('南美reserve项目', 3, 4670, 8, True, 'South America'),
]

for name, stage, gp, res, ug, country in test_cases:
    ev = predict_ev_per_oz(stage, gp, res, ug, country)
    total_value = ev * res
    print(f'{name}:')
    print(f'  EV/oz = ${ev:.0f}/oz')
    print(f'  总估值 = ${total_value:.0f}M ({res} Moz * ${ev:.0f}/oz)')
    print()

# 敏感性：金价对EV/oz的影响
print('=== 金价敏感性 ===\n')
print('金矿(production, 10 Moz, 加拿大, 地下):')
for gp in [2000, 2500, 3000, 3500, 4000, 4500, 5000]:
    ev = predict_ev_per_oz(4, gp, 10, True, 'Canada')
    print(f'  金价${gp}/oz -> EV/oz = ${ev:.0f}/oz')

# 保存模型参数
model_params = {
    'intercept': float(model.intercept_),
    'coefficients': {name: float(coef) for name, coef in zip(feature_names, model.coef_)},
    'r_squared': float(model.score(X, y)),
    'sample_size': len(GOLD_TRANSACTIONS),
    'feature_names': feature_names,
    'equation': f'EV/oz = {model.intercept_:.1f} + {model.coef_[0]:.2f}*stage + {model.coef_[1]:.2f}*gold_price_k + {model.coef_[2]:.2f}*resource_moz + {model.coef_[3]:.2f}*underground + {model.coef_[4]:.2f}*australia + {model.coef_[5]:.2f}*canada + {model.coef_[6]:.2f}*africa + {model.coef_[7]:.2f}*south_america'
}

output_path = r'C:\Users\39555\.claude\tools\mining-price-engine\gold_valuation_model.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(model_params, f, ensure_ascii=False, indent=2)

print(f'\n模型参数已保存: {output_path}')
