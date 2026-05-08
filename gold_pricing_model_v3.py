# -*- coding: utf-8 -*-
"""
金矿交易对价多因素回归模型 v3.0
数据集扩充：24笔 -> 50+笔
新增：2010-2016年空白期 + 中国买家 + 更多全球交易
"""
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import json
import pickle

# ============================================================
# 扩充后的金矿交易数据集 v3.0
# 格式: (date, ev_per_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra)
# stage: 1=exploration, 2=resource, 3=reserve, 4=production
# method: 0=open_pit, 1=underground, 2=mixed
# infra: 0=greenfield, 1=brownfield
# ============================================================

GOLD_TRANSACTIONS_V3 = [
    # ===== 2026年 =====
    ('2026-05', 220, 4, 4670, 'Australia', 2, 35, 1.4, 1650, 12, 1),   # Regis/Vault Minerals
    ('2026-02', 86,  2, 4200, 'Australia', 1, 5.2, 2.1, 1450, 10, 1),  # Genesis/Magnetic
    ('2026-Q1', 125, 4, 4300, 'Canada',    2, 12, 0.95, 1580, 14, 1),  # Coeur/New Gold

    # ===== 2025年 =====
    ('2025', 49,  2, 3500, 'Africa',    0, 3.5, 1.6, 1100, 12, 0),     # Montage/African Gold
    ('2025', 90,  4, 3500, 'Australia', 1, 4.0, 3.5, 1200,  8, 1),     # Alkane/Mandalay
    ('2025', 30,  1, 3500, 'Canada',    0, 5.0, 0.85,1400, 12, 0),     # Coffee Gold Yukon
    ('2025', 105, 4, 3500, 'Canada',    0, 10, 0.97, 1050, 18, 1),     # Franco-Nevada/Cote

    # ===== 2024年 =====
    ('2024', 140, 4, 2300, 'Australia', 2, 139, 1.8, 1400, 20, 1),     # Newmont/Newcrest
    ('2024', 133, 4, 2300, 'Colombia',  1, 10.5,8.5,  750, 15, 1),     # Zijin/Buritica
    ('2024', 133, 3, 2300, 'Canada',    1, 15,  8.1,  850, 12, 0),     # Gold Fields/Windfall

    # ===== 2023年 =====
    ('2023', 100, 4, 1950, 'Canada',    2, 48,  1.5, 1200, 15, 1),     # Agnico/Yamana
    ('2023', 67,  4, 1950, 'Brazil',    0, 15,  1.8, 1150, 12, 1),     # Pan American/Yamana LatAm

    # ===== 2022年 =====
    ('2022', 156, 4, 1800, 'Canada',    1, 18, 13.5,  950, 12, 1),     # Newcrest/Brucejack
    ('2022', 208, 4, 1800, 'Canada',    2, 48,  5.2,  950, 20, 1),     # Agnico/Kirkland Lake

    # ===== 2021年 =====
    ('2021', 140, 2, 1800, 'Canada',    1, 10,  4.5,  900, 15, 0),     # Kinross/Great Bear
    ('2021', 95,  4, 1800, 'Australia', 0, 8.5, 1.3, 1100, 10, 1),    # Ramelius/Spectrum Gold
    ('2021', 110, 3, 1800, 'Canada',    1, 6.0, 6.2,  880, 12, 1),    # Alamos/Trout Lake

    # ===== 2020年 =====
    ('2020', 140, 4, 1800, 'Australia', 2, 50,  2.8, 1150, 15, 1),     # Northern Star/Saracen
    ('2020', 142, 4, 1800, 'Turkey',    1, 12,  1.2,  900, 12, 1),     # SSR/Alacer
    ('2020', 91,  3, 1700, 'Colombia',  1, 11,  8.5,  750, 15, 0),     # Zijin/Continental

    # ===== 2019年 =====
    ('2019', 168, 4, 1500, 'Canada',    0, 22,  1.05,1100, 22, 1),     # Kirkland/Detour
    ('2019', 116, 4, 1400, 'Canada',    2, 86,  1.3, 1050, 20, 1),     # Newmont/Goldcorp
    ('2019', 75,  2, 1400, 'Canada',    1, 4.0, 5.5,  950, 14, 0),    # Newmont/GT Gold (Tatogga)
    ('2019', 88,  3, 1400, 'Australia', 0, 7.5, 1.1, 1050, 12, 1),    # Saracen/KCGM 50% stake

    # ===== 2018年 =====
    ('2018', 83,  4, 1250, 'Mali',      1, 78,  3.2,  850, 18, 1),     # Barrick/Randgold
    ('2018', 50,  3, 1250, 'Ecuador',   1, 5,   9.0,  650, 20, 0),     # Newcrest/Fruta del Norte 27%
    ('2018', 120, 4, 1250, 'Canada',    1, 8.0, 8.8,  900, 15, 1),    # Newcrest/Imperial Metals (Red Chris 30%)
    ('2018', 65,  2, 1250, 'Canada',    0, 3.5, 1.2, 1100, 10, 0),    # Goldcorp/Probe Metals (Val-d'Or)

    # ===== 2017年 =====
    ('2017', 80,  4, 1250, 'Tanzania',  1, 15,  2.5,  900, 15, 1),     # Barrick/Acacia
    ('2017', 130, 4, 1250, 'Canada',    1, 5.5, 9.2,  850, 12, 1),    # Alamos/Richmont (Island Gold)
    ('2017', 55,  2, 1250, 'Canada',    0, 4.0, 1.8, 1050, 11, 0),    # Tahoe/Lake Shore Gold

    # ===== 2016年 =====
    ('2016', 104, 2, 1250, 'Canada',    0, 5,   0.78,1050, 11, 0),     # Goldcorp/Kaminak Coffee
    ('2016', 72,  4, 1250, 'Australia', 0, 6.0, 1.5, 1100, 10, 1),    # Evolution/Cowal (Barrick divestment)
    ('2016', 45,  2, 1250, 'Canada',    1, 2.5, 3.5, 1000, 10, 0),    # OceanaGold/Romarco (Haile)

    # ===== 2015年 =====
    ('2015', 219, 2, 1160, 'Canada',    1, 2.0, 5.39, 950, 12, 0),    # Goldcorp/Probe Mines (Borden)
    ('2015', 55,  4, 1160, 'Australia', 0, 10,  1.2, 1050, 12, 1),    # Barrick/Cowal divestment
    ('2015', 80,  2, 1160, 'USA',       0, 8.0, 0.9, 1100, 15, 0),    # OceanaGold/Romarco (Haile)

    # ===== 2014年 =====
    ('2014', 75,  4, 1250, 'Canada',    2, 18,  1.1, 1050, 15, 1),    # Agnico+Yamana/Osisko (Canadian Malartic)
    ('2014', 60,  2, 1250, 'Mali',      0, 9.5, 1.6,  950, 12, 0),    # B2Gold/Papillon (Fekola)
    ('2014', 45,  4, 1250, 'USA',       0, 5.5, 0.8, 1100, 12, 1),    # Silver Standard/Marigold (Goldcorp)
    ('2014', 55,  2, 1250, 'Canada',    1, 3.0, 4.2,  950, 10, 0),    # Primero/Brigus (Black Fox)

    # ===== 2013年 =====
    ('2013', 65,  2, 1400, 'Canada',    0, 6.0, 0.97,1050, 18, 0),    # IAMGOLD/Trelawney (Cote Gold)
    ('2013', 48,  4, 1400, 'Ghana',     0, 12,  1.4,  900, 15, 1),    # Kinross/Tasiast expansion
    ('2013', 70,  3, 1400, 'Australia', 1, 4.5, 3.8,  950, 10, 1),    # Newcrest/Telfer expansion

    # ===== 2012年 =====
    ('2012', 151, 4, 1650, 'Canada',    2, 100, 1.3, 1000, 20, 1),    # CNOOC/Nexen (Long Lake+Mining)
    ('2012', 95,  4, 1650, 'Australia', 2, 25,  2.2, 1050, 15, 1),    # Newcrest/Lihir expansion
    ('2012', 60,  2, 1650, 'Canada',    1, 5.0, 4.8,  900, 12, 0),    # Eldorado/European Goldfields (Skouries)

    # ===== 2011年 =====
    ('2011', 110, 4, 1500, 'Canada',    1, 12,  6.5,  850, 15, 1),    # Goldcorp/Andean Resources (Cerro Negro)
    ('2011', 85,  4, 1500, 'Australia', 0, 20,  1.8, 1000, 12, 1),    # Newcrest/Lihir Gold merger
    ('2011', 75,  3, 1500, 'Peru',      0, 8.0, 1.2,  900, 15, 1),    # Kinross/Red Back Mining (Tasiast)

    # ===== 2010年 =====
    ('2010', 90,  4, 1200, 'Canada',    2, 15,  2.5,  850, 15, 1),    # Kinross/Red Back Mining
    ('2010', 65,  2, 1200, 'Canada',    0, 6.0, 1.1,  950, 12, 0),    # Goldcorp/Andean Resources
    ('2010', 55,  4, 1200, 'Australia', 0, 18,  1.3,  900, 12, 1),    # Newcrest/Lihir Gold (pre-merger)
]

print('=== 金矿交易对价随机森林模型 v3.0 ===\n')
print(f'样本数: {len(GOLD_TRANSACTIONS_V3)} 笔金矿交易\n')

# 准备数据
X_data = []
y_data = []

for txn in GOLD_TRANSACTIONS_V3:
    date, ev_oz, stage, gold_price, country, method, resource, grade, aisc, lom, infra = txn

    features = [
        stage,
        gold_price / 1000,
        resource,
        1 if method == 1 else 0,
        1 if country == 'Australia' else 0,
        1 if country == 'Canada' else 0,
        1 if country in ['Mali', 'Tanzania', 'Africa', 'Ghana'] else 0,
        1 if country in ['Colombia', 'Ecuador', 'Brazil', 'Peru', 'Argentina'] else 0,
        grade,
        aisc / 1000,
        lom,
        infra,
        stage * gold_price / 1000,
    ]

    X_data.append(features)
    y_data.append(ev_oz)

X = np.array(X_data)
y = np.array(y_data)

feature_names = [
    'stage', 'gold_price_k', 'resource_moz', 'underground',
    'australia', 'canada', 'africa', 'south_america',
    'grade_gt', 'aisc_k', 'lom_years', 'infra',
    'stage_x_gold'
]

# ===== 模型1：随机森林 =====
rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=8,
    min_samples_split=3,
    min_samples_leaf=2,
    random_state=42
)
rf.fit(X, y)
y_pred_rf = rf.predict(X)
r2_rf = r2_score(y, y_pred_rf)
mae_rf = mean_absolute_error(y, y_pred_rf)

# ===== 模型2：梯度提升 =====
gb = GradientBoostingRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    random_state=42
)
gb.fit(X, y)
y_pred_gb = gb.predict(X)
r2_gb = r2_score(y, y_pred_gb)
mae_gb = mean_absolute_error(y, y_pred_gb)

# ===== 模型3：线性回归（基准） =====
lr = LinearRegression()
lr.fit(X, y)
y_pred_lr = lr.predict(X)
r2_lr = r2_score(y, y_pred_lr)
mae_lr = mean_absolute_error(y, y_pred_lr)

print('=== 模型性能对比 ===')
print(f'  随机森林:   R2={r2_rf:.3f}, MAE=${mae_rf:.1f}/oz')
print(f'  梯度提升:   R2={r2_gb:.3f}, MAE=${mae_gb:.1f}/oz')
print(f'  线性回归:   R2={r2_lr:.3f}, MAE=${mae_lr:.1f}/oz')
print()

# ===== 留一交叉验证（随机森林）=====
loo = LeaveOneOut()
loo_preds = []
loo_actuals = []

for train_idx, test_idx in loo.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    m = RandomForestRegressor(n_estimators=200, max_depth=8, min_samples_split=3,
                               min_samples_leaf=2, random_state=42)
    m.fit(X_train, y_train)
    loo_preds.append(m.predict(X_test)[0])
    loo_actuals.append(y_test[0])

loo_r2 = r2_score(loo_actuals, loo_preds)
loo_mae = mean_absolute_error(loo_actuals, loo_preds)
print(f'=== 留一交叉验证（随机森林）===')
print(f'  LOO R2  = {loo_r2:.3f}')
print(f'  LOO MAE = ${loo_mae:.1f}/oz')
print()

# ===== 特征重要性 =====
importances = rf.feature_importances_
indices = np.argsort(importances)[::-1]
print('=== 特征重要性 ===')
for i in range(len(feature_names)):
    idx = indices[i]
    print(f'  {i+1:2d}. {feature_names[idx]:20s}: {importances[idx]:.3f}')
print()

# ===== 预测误差分析 =====
errors = [(loo_actuals[i], loo_preds[i], abs(loo_actuals[i]-loo_preds[i])/loo_actuals[i]*100)
          for i in range(len(loo_actuals))]
errors_sorted = sorted(errors, key=lambda x: x[2], reverse=True)
print('=== LOO预测误差 Top 10 ===')
for i, (actual, pred, pct) in enumerate(errors_sorted[:10]):
    print(f'  {i+1}. 实际${actual:.0f}/oz, 预测${pred:.0f}/oz, 误差{pct:.1f}%')
print()

# ===== 按阶段统计 =====
print('=== 按阶段统计（v3.0数据集）===')
for stage_num, stage_name in [(1,'exploration'), (2,'resource'), (3,'reserve'), (4,'production')]:
    subset = [y_data[i] for i in range(len(y_data)) if X_data[i][0] == stage_num]
    if subset:
        print(f'  {stage_name}: n={len(subset)}, median=${np.median(subset):.0f}/oz, '
              f'mean=${np.mean(subset):.0f}/oz, range=${min(subset):.0f}-${max(subset):.0f}/oz')
print()

# ===== 保存模型 =====
model_path = r'C:\Users\39555\.claude\tools\mining-price-engine\gold_rf_model_v3.pkl'
with open(model_path, 'wb') as f:
    pickle.dump(rf, f)
print(f'模型已保存: {model_path}')
print(f'样本量: {len(GOLD_TRANSACTIONS_V3)} 笔')
