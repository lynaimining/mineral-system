# -*- coding: utf-8 -*-
"""
金矿交易对价多因素回归模型 v2.0
升级：随机森林 + 新增品位/AISC/LOM特征
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, LeaveOneOut
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import json
import os

# 扩充的金矿交易数据（含品位、AISC、LOM）
GOLD_TRANSACTIONS_V2 = [
    # (date, ev_per_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra)
    # stage: 1=exploration, 2=resource, 3=reserve, 4=production
    # method: 0=open_pit, 1=underground, 2=mixed
    # infra: 0=greenfield, 1=brownfield
    ('2026-05', 220, 4, 4670, 'Australia', 2, 35, 1.4, 1650, 12, 1),
    ('2026-02', 86, 2, 4200, 'Australia', 1, 5.2, 2.1, 1450, 10, 1),
    ('2026-Q1', 125, 4, 4300, 'Canada', 2, 12, 0.95, 1580, 14, 1),
    ('2025', 49, 2, 3500, 'Africa', 0, 3.5, 1.6, 1100, 12, 0),
    ('2025', 90, 4, 3500, 'Australia', 1, 4.0, 3.5, 1200, 8, 1),
    ('2025', 30, 1, 3500, 'Canada', 0, 5.0, 0.85, 1400, 12, 0),
    ('2025', 105, 4, 3500, 'Canada', 0, 10, 0.97, 1050, 18, 1),
    ('2024', 140, 4, 2300, 'Australia', 2, 139, 1.8, 1400, 20, 1),
    ('2024', 133, 4, 2300, 'Colombia', 1, 10.5, 8.5, 750, 15, 1),
    ('2024', 133, 3, 2300, 'Canada', 1, 15, 8.1, 850, 12, 0),
    ('2023', 100, 4, 1950, 'Canada', 2, 48, 1.5, 1200, 15, 1),
    ('2023', 67, 4, 1950, 'Brazil', 0, 15, 1.8, 1150, 12, 1),
    ('2022', 156, 4, 1800, 'Canada', 1, 18, 13.5, 950, 12, 1),
    ('2022', 208, 4, 1800, 'Canada', 2, 48, 5.2, 950, 20, 1),
    ('2020', 140, 4, 1800, 'Australia', 2, 50, 2.8, 1150, 15, 1),
    ('2020', 142, 4, 1800, 'Turkey', 1, 12, 1.2, 900, 12, 1),
    ('2020', 91, 3, 1700, 'Colombia', 1, 11, 8.5, 750, 15, 0),
    ('2019', 168, 4, 1500, 'Canada', 0, 22, 1.05, 1100, 22, 1),
    ('2019', 116, 4, 1400, 'Canada', 2, 86, 1.3, 1050, 20, 1),
    ('2018', 83, 4, 1250, 'Mali', 1, 78, 3.2, 850, 18, 1),
    ('2018', 50, 3, 1250, 'Ecuador', 1, 5, 9.0, 650, 20, 0),
    ('2017', 80, 4, 1250, 'Tanzania', 1, 15, 2.5, 900, 15, 1),
    ('2016', 104, 2, 1250, 'Canada', 0, 5, 0.78, 1050, 11, 0),
    ('2021', 140, 2, 1800, 'Canada', 1, 10, 4.5, 900, 15, 0),
]

print('=== 金矿交易对价随机森林模型 v2.0 ===\n')
print(f'样本数: {len(GOLD_TRANSACTIONS_V2)} 笔金矿交易\n')

# 准备数据
X_data = []
y_data = []

for txn in GOLD_TRANSACTIONS_V2:
    date, ev_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra = txn

    # 特征向量（新增品位、AISC、LOM、基建）
    features = [
        stage,                          # 阶段 (1-4)
        gold_price / 1000,              # 金价 (千美元/oz)
        resource,                       # 资源量 (Moz)
        1 if method == 1 else 0,        # 地下矿
        1 if country == 'Australia' else 0,
        1 if country == 'Canada' else 0,
        1 if country in ['Mali', 'Tanzania', 'Africa'] else 0,
        1 if country in ['Colombia', 'Ecuador', 'Brazil'] else 0,
        grade,                          # 品位 (g/t)
        aisc / 1000,                    # AISC (千$/oz)
        lom,                            # 矿山寿命 (年)
        infra,                          # 基建成熟度 (0/1)
        stage * gold_price / 1000,      # 交互项：阶段×金价
    ]

    X_data.append(features)
    y_data.append(ev_oz)

X = np.array(X_data)
y = np.array(y_data)

feature_names = [
    '阶段', '金价(千$/oz)', '资源量(Moz)', '地下矿',
    '澳大利亚', '加拿大', '非洲', '南美',
    '品位(g/t)', 'AISC(千$/oz)', 'LOM(年)', '基建成熟度',
    '阶段×金价'
]

# 随机森林回归
rf_model = RandomForestRegressor(
    n_estimators=100,
    max_depth=8,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42
)
rf_model.fit(X, y)

# 模型评估
y_pred = rf_model.predict(X)
r2 = r2_score(y, y_pred)
mae = mean_absolute_error(y, y_pred)
rmse = np.sqrt(mean_squared_error(y, y_pred))

print('=== 模型性能 ===')
print(f'  R2 = {r2:.3f}')
print(f'  MAE = ${mae:.1f}/oz')
print(f'  RMSE = ${rmse:.1f}/oz')
print()

# 特征重要性
importances = rf_model.feature_importances_
indices = np.argsort(importances)[::-1]

print('=== 特征重要性排序 ===')
for i in range(len(feature_names)):
    idx = indices[i]
    print(f'  {i+1}. {feature_names[idx]}: {importances[idx]:.3f}')
print()

# 留一交叉验证
loo = LeaveOneOut()
loo_scores = []
loo_predictions = []

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    model_loo = RandomForestRegressor(
        n_estimators=100, max_depth=8, min_samples_split=3,
        min_samples_leaf=2, random_state=42
    )
    model_loo.fit(X_train, y_train)
    pred = model_loo.predict(X_test)[0]

    loo_predictions.append((y_test[0], pred))
    loo_scores.append(r2_score([y_test[0]], [pred]))

loo_r2 = np.mean(loo_scores)
print(f'=== 留一交叉验证 ===')
print(f'  LOO R2 = {loo_r2:.3f}')
print()

# 预测误差分析
errors = [(actual, pred, actual - pred, abs(actual - pred) / actual * 100)
          for actual, pred in loo_predictions]
errors_sorted = sorted(errors, key=lambda x: x[3], reverse=True)

print('=== 预测误差 Top 5 ===')
for i, (actual, pred, diff, pct) in enumerate(errors_sorted[:5]):
    print(f'  {i+1}. 实际${actual:.0f}/oz, 预测${pred:.0f}/oz, 误差{pct:.1f}%')
print()

# 保存模型
import pickle
model_path = r'C:\Users\39555\.claude\tools\mining-price-engine\gold_rf_model_v2.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(rf_model, f)

print(f'模型已保存: {model_path}')
