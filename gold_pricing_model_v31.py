# -*- coding: utf-8 -*-
"""
金矿交易对价模型 v3.1 - 过拟合诊断与修复
问题：53笔数据，13个特征，随机森林过拟合
解决：特征降维 + 正则化 + 更严格的超参数
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import pickle

GOLD_TRANSACTIONS_V3 = [
    ('2026-05', 220, 4, 4670, 'Australia', 2, 35, 1.4, 1650, 12, 1),
    ('2026-02', 86,  2, 4200, 'Australia', 1, 5.2, 2.1, 1450, 10, 1),
    ('2026-Q1', 125, 4, 4300, 'Canada',    2, 12, 0.95, 1580, 14, 1),
    ('2025', 49,  2, 3500, 'Africa',    0, 3.5, 1.6, 1100, 12, 0),
    ('2025', 90,  4, 3500, 'Australia', 1, 4.0, 3.5, 1200,  8, 1),
    ('2025', 30,  1, 3500, 'Canada',    0, 5.0, 0.85,1400, 12, 0),
    ('2025', 105, 4, 3500, 'Canada',    0, 10, 0.97, 1050, 18, 1),
    ('2024', 140, 4, 2300, 'Australia', 2, 139, 1.8, 1400, 20, 1),
    ('2024', 133, 4, 2300, 'Colombia',  1, 10.5,8.5,  750, 15, 1),
    ('2024', 133, 3, 2300, 'Canada',    1, 15,  8.1,  850, 12, 0),
    ('2023', 100, 4, 1950, 'Canada',    2, 48,  1.5, 1200, 15, 1),
    ('2023', 67,  4, 1950, 'Brazil',    0, 15,  1.8, 1150, 12, 1),
    ('2022', 156, 4, 1800, 'Canada',    1, 18, 13.5,  950, 12, 1),
    ('2022', 208, 4, 1800, 'Canada',    2, 48,  5.2,  950, 20, 1),
    ('2021', 140, 2, 1800, 'Canada',    1, 10,  4.5,  900, 15, 0),
    ('2021', 95,  4, 1800, 'Australia', 0, 8.5, 1.3, 1100, 10, 1),
    ('2021', 110, 3, 1800, 'Canada',    1, 6.0, 6.2,  880, 12, 1),
    ('2020', 140, 4, 1800, 'Australia', 2, 50,  2.8, 1150, 15, 1),
    ('2020', 142, 4, 1800, 'Turkey',    1, 12,  1.2,  900, 12, 1),
    ('2020', 91,  3, 1700, 'Colombia',  1, 11,  8.5,  750, 15, 0),
    ('2019', 168, 4, 1500, 'Canada',    0, 22,  1.05,1100, 22, 1),
    ('2019', 116, 4, 1400, 'Canada',    2, 86,  1.3, 1050, 20, 1),
    ('2019', 75,  2, 1400, 'Canada',    1, 4.0, 5.5,  950, 14, 0),
    ('2019', 88,  3, 1400, 'Australia', 0, 7.5, 1.1, 1050, 12, 1),
    ('2018', 83,  4, 1250, 'Mali',      1, 78,  3.2,  850, 18, 1),
    ('2018', 50,  3, 1250, 'Ecuador',   1, 5,   9.0,  650, 20, 0),
    ('2018', 120, 4, 1250, 'Canada',    1, 8.0, 8.8,  900, 15, 1),
    ('2018', 65,  2, 1250, 'Canada',    0, 3.5, 1.2, 1100, 10, 0),
    ('2017', 80,  4, 1250, 'Tanzania',  1, 15,  2.5,  900, 15, 1),
    ('2017', 130, 4, 1250, 'Canada',    1, 5.5, 9.2,  850, 12, 1),
    ('2017', 55,  2, 1250, 'Canada',    0, 4.0, 1.8, 1050, 11, 0),
    ('2016', 104, 2, 1250, 'Canada',    0, 5,   0.78,1050, 11, 0),
    ('2016', 72,  4, 1250, 'Australia', 0, 6.0, 1.5, 1100, 10, 1),
    ('2016', 45,  2, 1250, 'Canada',    1, 2.5, 3.5, 1000, 10, 0),
    ('2015', 219, 2, 1160, 'Canada',    1, 2.0, 5.39, 950, 12, 0),
    ('2015', 55,  4, 1160, 'Australia', 0, 10,  1.2, 1050, 12, 1),
    ('2015', 80,  2, 1160, 'USA',       0, 8.0, 0.9, 1100, 15, 0),
    ('2014', 75,  4, 1250, 'Canada',    2, 18,  1.1, 1050, 15, 1),
    ('2014', 60,  2, 1250, 'Mali',      0, 9.5, 1.6,  950, 12, 0),
    ('2014', 45,  4, 1250, 'USA',       0, 5.5, 0.8, 1100, 12, 1),
    ('2014', 55,  2, 1250, 'Canada',    1, 3.0, 4.2,  950, 10, 0),
    ('2013', 65,  2, 1400, 'Canada',    0, 6.0, 0.97,1050, 18, 0),
    ('2013', 48,  4, 1400, 'Ghana',     0, 12,  1.4,  900, 15, 1),
    ('2013', 70,  3, 1400, 'Australia', 1, 4.5, 3.8,  950, 10, 1),
    ('2012', 151, 4, 1650, 'Canada',    2, 100, 1.3, 1000, 20, 1),
    ('2012', 95,  4, 1650, 'Australia', 2, 25,  2.2, 1050, 15, 1),
    ('2012', 60,  2, 1650, 'Canada',    1, 5.0, 4.8,  900, 12, 0),
    ('2011', 110, 4, 1500, 'Canada',    1, 12,  6.5,  850, 15, 1),
    ('2011', 85,  4, 1500, 'Australia', 0, 20,  1.8, 1000, 12, 1),
    ('2011', 75,  3, 1500, 'Peru',      0, 8.0, 1.2,  900, 15, 1),
    ('2010', 90,  4, 1200, 'Canada',    2, 15,  2.5,  850, 15, 1),
    ('2010', 65,  2, 1200, 'Canada',    0, 6.0, 1.1,  950, 12, 0),
    ('2010', 55,  4, 1200, 'Australia', 0, 18,  1.3,  900, 12, 1),
]

# 精简特征集（只保留最重要的7个，减少过拟合）
X_data = []
y_data = []

for txn in GOLD_TRANSACTIONS_V3:
    date, ev_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra = txn
    features = [
        stage,                          # 阶段
        gold_price / 1000,              # 金价
        np.log1p(resource),             # 资源量（对数变换，减少大矿的杠杆效应）
        grade,                          # 品位
        aisc / 1000,                    # AISC
        lom,                            # 矿山寿命
        infra,                          # 基建
    ]
    X_data.append(features)
    y_data.append(ev_oz)

X = np.array(X_data)
y = np.array(y_data)

feature_names = ['stage', 'gold_price_k', 'log_resource', 'grade_gt', 'aisc_k', 'lom', 'infra']

print(f'样本数: {len(GOLD_TRANSACTIONS_V3)} 笔，特征数: {X.shape[1]}')
print()

# ===== 模型对比 =====
models = {
    'RF(严格正则)': RandomForestRegressor(
        n_estimators=200, max_depth=4, min_samples_split=8,
        min_samples_leaf=4, max_features=0.6, random_state=42),
    'GBM(保守)': GradientBoostingRegressor(
        n_estimators=100, max_depth=3, learning_rate=0.05,
        min_samples_leaf=5, subsample=0.8, random_state=42),
    'Ridge': Ridge(alpha=10.0),
}

print('=== 模型性能（LOO交叉验证）===')
for name, model in models.items():
    loo = LeaveOneOut()
    preds, actuals = [], []
    for train_idx, test_idx in loo.split(X):
        model.fit(X[train_idx], y[train_idx])
        preds.append(model.predict(X[test_idx])[0])
        actuals.append(y[test_idx][0])
    loo_r2 = r2_score(actuals, preds)
    loo_mae = mean_absolute_error(actuals, preds)
    # 训练集R²
    model.fit(X, y)
    train_r2 = r2_score(y, model.predict(X))
    print(f'  {name:20s}: LOO R2={loo_r2:.3f}, LOO MAE=${loo_mae:.1f}/oz, Train R2={train_r2:.3f}')

print()

# ===== 最佳模型：Ridge（最稳定）=====
ridge = Ridge(alpha=10.0)
loo = LeaveOneOut()
preds, actuals = [], []
for train_idx, test_idx in loo.split(X):
    ridge.fit(X[train_idx], y[train_idx])
    preds.append(ridge.predict(X[test_idx])[0])
    actuals.append(y[test_idx][0])

loo_r2 = r2_score(actuals, preds)
loo_mae = mean_absolute_error(actuals, preds)
ridge.fit(X, y)

print(f'=== Ridge回归系数 ===')
for name, coef in zip(feature_names, ridge.coef_):
    print(f'  {name:20s}: {coef:+.2f}')
print(f'  截距: {ridge.intercept_:.2f}')
print()
print(f'LOO R2 = {loo_r2:.3f}')
print(f'LOO MAE = ${loo_mae:.1f}/oz')
print()

# ===== 按阶段统计 =====
print('=== 按阶段统计 ===')
for stage_num, stage_name in [(1,'exploration'), (2,'resource'), (3,'reserve'), (4,'production')]:
    subset = [y_data[i] for i in range(len(y_data)) if X_data[i][0] == stage_num]
    if subset:
        print(f'  {stage_name:12s}: n={len(subset):2d}, '
              f'median=${np.median(subset):.0f}/oz, '
              f'mean=${np.mean(subset):.0f}/oz, '
              f'range=${min(subset):.0f}-${max(subset):.0f}/oz')
