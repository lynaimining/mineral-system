# -*- coding: utf-8 -*-
"""
金矿交易数据库 v4.0 - 整合搜索结果 + 异常值分析
目标：建立高质量数据集，而非追求样本量
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics import r2_score, mean_absolute_error
import pickle

# ============================================================
# 完整数据集 v4.0（含新搜索结果）
# 格式: (date, ev_per_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra, note)
# ============================================================

ALL_TRANSACTIONS = [
    # ===== 2026年 =====
    ('2026-05', 220, 4, 4670, 'Australia', 2, 35,   1.4,  1650, 12, 1, 'Regis/Vault'),
    ('2026-02', 86,  2, 4200, 'Australia', 1, 5.2,  2.1,  1450, 10, 1, 'Genesis/Magnetic'),
    ('2026-Q1', 125, 4, 4300, 'Canada',    2, 12,   0.95, 1580, 14, 1, 'Coeur/New Gold'),

    # ===== 2025年 =====
    ('2025', 49,  2, 3500, 'Africa',    0, 3.5,  1.6,  1100, 12, 0, 'Montage/African Gold'),
    ('2025', 90,  4, 3500, 'Australia', 1, 4.0,  3.5,  1200,  8, 1, 'Alkane/Mandalay'),
    ('2025', 30,  1, 3500, 'Canada',    0, 5.0,  0.85, 1400, 12, 0, 'Coffee Gold Yukon'),
    ('2025', 105, 4, 3500, 'Canada',    0, 10,   0.97, 1050, 18, 1, 'Franco-Nevada/Cote'),

    # ===== 2024年 =====
    ('2024', 140, 4, 2300, 'Australia', 2, 139,  1.8,  1400, 20, 1, 'Newmont/Newcrest'),
    ('2024', 133, 4, 2300, 'Colombia',  1, 10.5, 8.5,   750, 15, 1, 'Zijin/Buritica'),
    ('2024', 133, 3, 2300, 'Canada',    1, 15,   8.1,   850, 12, 0, 'Gold Fields/Windfall'),

    # ===== 2023年 =====
    ('2023', 100, 4, 1950, 'Canada',    2, 48,   1.5,  1200, 15, 1, 'Agnico/Yamana'),
    ('2023', 67,  4, 1950, 'Brazil',    0, 15,   1.8,  1150, 12, 1, 'Pan American/Yamana LatAm'),

    # ===== 2022年 =====
    ('2022', 156, 4, 1800, 'Canada',    1, 18,  13.5,   950, 12, 1, 'Newcrest/Brucejack'),
    ('2022', 208, 4, 1800, 'Canada',    2, 48,   5.2,   950, 20, 1, 'Agnico/Kirkland Lake'),

    # ===== 2021年 =====
    ('2021', 140, 2, 1800, 'Canada',    1, 10,   4.5,   900, 15, 0, 'Kinross/Great Bear'),
    ('2021', 95,  4, 1800, 'Australia', 0, 8.5,  1.3,  1100, 10, 1, 'Ramelius/Spectrum'),
    ('2021', 110, 3, 1800, 'Canada',    1, 6.0,  6.2,   880, 12, 1, 'Alamos/Trout Lake'),

    # ===== 2020年 =====
    ('2020', 140, 4, 1800, 'Australia', 2, 50,   2.8,  1150, 15, 1, 'Northern Star/Saracen'),
    ('2020', 142, 4, 1800, 'Turkey',    1, 12,   1.2,   900, 12, 1, 'SSR/Alacer'),
    ('2020', 91,  3, 1700, 'Colombia',  1, 11,   8.5,   750, 15, 0, 'Zijin/Continental'),
    ('2020', 34,  4, 1700, 'Guyana',    0, 6.9,  2.1,   950, 12, 1, 'Zijin/Guyana Goldfields'),  # 新增
    ('2020', 43,  2, 1700, 'Ghana',     0, 5.1,  1.13,  950, 12, 0, 'Shandong/Cardinal Namdini'), # 新增

    # ===== 2019年 =====
    ('2019', 168, 4, 1500, 'Canada',    0, 22,   1.05, 1100, 22, 1, 'Kirkland/Detour'),
    ('2019', 116, 4, 1400, 'Canada',    2, 86,   1.3,  1050, 20, 1, 'Newmont/Goldcorp'),
    ('2019', 75,  2, 1400, 'Canada',    1, 4.0,  5.5,   950, 14, 0, 'Newmont/GT Gold'),
    ('2019', 88,  3, 1400, 'Australia', 0, 7.5,  1.1,  1050, 12, 1, 'Saracen/KCGM 50%'),

    # ===== 2018年 =====
    ('2018', 83,  4, 1250, 'Mali',      1, 78,   3.2,   850, 18, 1, 'Barrick/Randgold'),
    ('2018', 50,  3, 1250, 'Ecuador',   1, 5,    9.0,   650, 20, 0, 'Newcrest/Fruta del Norte 27%'),
    ('2018', 120, 4, 1250, 'Canada',    1, 8.0,  8.8,   900, 15, 1, 'Newcrest/Red Chris 30%'),
    ('2018', 65,  2, 1250, 'Canada',    0, 3.5,  1.2,  1100, 10, 0, 'Goldcorp/Probe Metals'),

    # ===== 2017年 =====
    ('2017', 80,  4, 1250, 'Tanzania',  1, 15,   2.5,   900, 15, 1, 'Barrick/Acacia'),
    ('2017', 130, 4, 1250, 'Canada',    1, 5.5,  9.2,   850, 12, 1, 'Alamos/Richmont Island Gold'),
    ('2017', 55,  2, 1250, 'Canada',    0, 4.0,  1.8,  1050, 11, 0, 'Tahoe/Lake Shore Gold'),
    ('2017', 107, 4, 1250, 'Argentina', 0, 9.0,  0.8,  1000, 15, 1, 'Shandong/Veladero 50%'),  # 新增

    # ===== 2016年 =====
    ('2016', 78,  2, 1250, 'Canada',    0, 5.2,  1.38, 1050, 11, 0, 'Goldcorp/Kaminak Coffee'),  # 修正USD
    ('2016', 72,  4, 1250, 'Australia', 0, 6.0,  1.5,  1100, 10, 1, 'Evolution/Cowal'),
    ('2016', 45,  2, 1250, 'Canada',    1, 2.5,  3.5,  1000, 10, 0, 'OceanaGold/Romarco Haile'),

    # ===== 2015年 =====
    ('2015', 220, 2, 1160, 'Canada',    1, 2.0,  5.39,  950, 12, 0, 'Goldcorp/Probe Borden'),  # 新增
    ('2015', 55,  4, 1160, 'Australia', 0, 10,   1.2,  1050, 12, 1, 'Barrick/Cowal divestment'),
    ('2015', 126, 4, 1160, 'USA',       0, 6.5,  0.6,  1000, 15, 1, 'Newmont/CC&V'),  # 新增
    ('2015', 76,  4, 1160, 'USA',       0, 8.0,  0.7,  1050, 12, 1, 'Kinross/Bald Mtn+Round Mtn'),  # 新增
    ('2015', 30,  4, 1160, 'PNG',       2, 10,   3.5,   900, 15, 1, 'Zijin/Porgera 50%'),  # 新增

    # ===== 2014年 =====
    ('2014', 75,  4, 1250, 'Canada',    2, 18,   1.1,  1050, 15, 1, 'Agnico+Yamana/Osisko'),
    ('2014', 86,  4, 1250, 'USA',       0, 3.2,  0.5,  1000, 12, 1, 'Silver Standard/Marigold'),  # 新增
    ('2014', 60,  2, 1250, 'Mali',      0, 9.5,  1.6,   950, 12, 0, 'B2Gold/Papillon Fekola'),
    ('2014', 55,  2, 1250, 'Canada',    1, 3.0,  4.2,   950, 10, 0, 'Primero/Brigus Black Fox'),

    # ===== 2013年 =====
    ('2013', 65,  2, 1400, 'Canada',    0, 6.0,  0.97, 1050, 18, 0, 'IAMGOLD/Trelawney Cote'),
    ('2013', 48,  4, 1400, 'Ghana',     0, 12,   1.4,   900, 15, 1, 'Kinross/Tasiast expansion'),
    ('2013', 70,  3, 1400, 'Australia', 1, 4.5,  3.8,   950, 10, 1, 'Newcrest/Telfer expansion'),

    # ===== 2012年 =====
    ('2012', 151, 4, 1650, 'Canada',    2, 100,  1.3,  1000, 20, 1, 'CNOOC/Nexen'),
    ('2012', 95,  4, 1650, 'Australia', 2, 25,   2.2,  1050, 15, 1, 'Newcrest/Lihir expansion'),
    ('2012', 60,  2, 1650, 'Canada',    1, 5.0,  4.8,   900, 12, 0, 'Eldorado/European Goldfields'),
    ('2012', 296, 2, 1650, 'Argentina', 1, 1.36, 7.4,   900, 12, 0, 'Yamana/Extorre Cerro Moro'),  # 新增
    ('2012', 64,  2, 1650, 'Australia', 0, 3.5,  1.8,  1050, 10, 1, 'Shandong/Focus Minerals'),  # 新增

    # ===== 2011年 =====
    ('2011', 110, 4, 1500, 'Canada',    1, 12,   6.5,   850, 15, 1, 'Goldcorp/Andean Cerro Negro'),
    ('2011', 85,  4, 1500, 'Australia', 0, 20,   1.8,  1000, 12, 1, 'Newcrest/Lihir Gold merger'),
    ('2011', 75,  3, 1500, 'Peru',      0, 8.0,  1.2,   900, 15, 1, 'Kinross/Red Back Tasiast'),
    ('2011', 261, 3, 1500, 'Greece',    1, 9.2,  None,  950, 15, 0, 'Eldorado/European Goldfields'),  # 新增

    # ===== 2010年 =====
    ('2010', 90,  4, 1200, 'Canada',    2, 15,   2.5,   850, 15, 1, 'Kinross/Red Back'),
    ('2010', 65,  2, 1200, 'Canada',    0, 6.0,  1.1,   950, 12, 0, 'Goldcorp/Andean Resources'),
    ('2010', 55,  4, 1200, 'Australia', 0, 18,   1.3,   900, 12, 1, 'Newcrest/Lihir pre-merger'),
    ('2010', 148, 2, 1200, 'Canada',    1, 5.0,  7.9,   900, 15, 0, 'Agnico/Comaplex Meliadine'),  # 新增
]

# ============================================================
# 异常值分析
# ============================================================
print('=== 数据集统计 ===')
print(f'总样本数: {len(ALL_TRANSACTIONS)}')

ev_values = [t[1] for t in ALL_TRANSACTIONS]
print(f'EV/oz 范围: ${min(ev_values):.0f} - ${max(ev_values):.0f}/oz')
print(f'EV/oz 中位数: ${np.median(ev_values):.0f}/oz')
print(f'EV/oz 均值: ${np.mean(ev_values):.0f}/oz')
print(f'EV/oz 标准差: ${np.std(ev_values):.0f}/oz')
print()

# 识别异常值（>3倍IQR）
q1, q3 = np.percentile(ev_values, 25), np.percentile(ev_values, 75)
iqr = q3 - q1
upper_fence = q3 + 3 * iqr
lower_fence = q1 - 3 * iqr
print(f'IQR: ${q1:.0f} - ${q3:.0f}/oz, 3*IQR上限: ${upper_fence:.0f}/oz')
print()

outliers = [(t[11], t[1]) for t in ALL_TRANSACTIONS if t[1] > upper_fence]
if outliers:
    print('=== 异常值（>3*IQR）===')
    for name, ev in sorted(outliers, key=lambda x: x[1], reverse=True):
        print(f'  {name}: ${ev:.0f}/oz')
    print()

# ============================================================
# 过滤策略：去除极端异常值（>300/oz），保留合理范围
# ============================================================
FILTERED = [t for t in ALL_TRANSACTIONS if t[1] <= 300]
print(f'过滤后样本数: {len(FILTERED)} (去除 {len(ALL_TRANSACTIONS)-len(FILTERED)} 个极端异常值)')
print()

# 准备特征（精简版，7个特征）
X_data, y_data = [], []
for txn in FILTERED:
    date, ev_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra, note = txn
    if grade is None:
        grade = 2.0  # 用中位数填充缺失品位
    features = [
        stage,
        gold_price / 1000,
        np.log1p(resource),
        grade,
        aisc / 1000,
        lom,
        infra,
    ]
    X_data.append(features)
    y_data.append(ev_oz)

X = np.array(X_data)
y = np.array(y_data)

feature_names = ['stage', 'gold_price_k', 'log_resource', 'grade_gt', 'aisc_k', 'lom', 'infra']

print(f'建模样本数: {len(y_data)}')
print()

# ===== LOO交叉验证对比 =====
models = {
    'Ridge(alpha=10)': Ridge(alpha=10.0),
    'Ridge(alpha=50)': Ridge(alpha=50.0),
    'RF(保守)': RandomForestRegressor(
        n_estimators=200, max_depth=4, min_samples_split=8,
        min_samples_leaf=4, max_features=0.6, random_state=42),
}

print('=== LOO交叉验证结果 ===')
best_model = None
best_loo_r2 = -999

for name, model in models.items():
    loo = LeaveOneOut()
    preds, actuals = [], []
    for train_idx, test_idx in loo.split(X):
        model.fit(X[train_idx], y[train_idx])
        preds.append(model.predict(X[test_idx])[0])
        actuals.append(y[test_idx][0])
    loo_r2 = r2_score(actuals, preds)
    loo_mae = mean_absolute_error(actuals, preds)
    model.fit(X, y)
    train_r2 = r2_score(y, model.predict(X))
    print(f'  {name:20s}: LOO R2={loo_r2:.3f}, LOO MAE=${loo_mae:.1f}/oz, Train R2={train_r2:.3f}')
    if loo_r2 > best_loo_r2:
        best_loo_r2 = loo_r2
        best_model = model

print()

# ===== 按阶段统计 =====
print('=== 按阶段统计（过滤后）===')
for stage_num, stage_name in [(1,'exploration'), (2,'resource'), (3,'reserve'), (4,'production')]:
    subset = [y_data[i] for i in range(len(y_data)) if X_data[i][0] == stage_num]
    if subset:
        print(f'  {stage_name:12s}: n={len(subset):2d}, '
              f'median=${np.median(subset):.0f}/oz, '
              f'mean=${np.mean(subset):.0f}/oz, '
              f'range=${min(subset):.0f}-${max(subset):.0f}/oz')
print()

# ===== 按年代统计 =====
print('=== 按年代统计 ===')
for era, years in [('2010-2013', range(2010,2014)), ('2014-2017', range(2014,2018)),
                    ('2018-2021', range(2018,2022)), ('2022-2026', range(2022,2027))]:
    subset = [t[1] for t in FILTERED if int(str(t[0])[:4]) in years]
    if subset:
        gold_avg = np.mean([t[3] for t in FILTERED if int(str(t[0])[:4]) in years])
        print(f'  {era}: n={len(subset):2d}, median=${np.median(subset):.0f}/oz, '
              f'avg gold=${gold_avg:.0f}/oz')
