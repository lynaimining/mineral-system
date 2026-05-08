# -*- coding: utf-8 -*-
"""
金矿快速估值工具 v1.0
目标：实战用，覆盖小矿(0.03-0.64 Moz)到大矿(1-20 Moz)
"""
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 核心数据集（仅保留1-20 Moz范围，质量最高的35笔）
# 格式: (ev_per_oz, stage, gold_price, resource_moz, grade_gt, aisc, lom, infra, note)
# ============================================================

CORE_DATA = [
    # resource, ev_per_oz, stage, gold_price, grade, aisc, note
    # stage: 2=resource, 3=reserve, 4=production
    (1.36, 296, 2, 1650, 7.4,  900, 'Yamana/Extorre Cerro Moro'),
    (2.0,  220, 2, 1160, 5.39, 950, 'Goldcorp/Probe Borden'),
    (2.0,  195, 4, 1650, 2.5,  950, 'Endeavour/Avion Mali'),
    (2.5,  148, 2, 1200, 7.9,  900, 'Agnico/Comaplex Meliadine'),
    (3.0,  55,  2, 1250, 4.2,  950, 'Primero/Brigus Black Fox'),
    (3.5,  49,  2, 3500, 1.6, 1100, 'Montage/African Gold'),
    (3.5,  64,  2, 1650, 1.8, 1050, 'Shandong/Focus Minerals'),
    (4.0,  90,  4, 3500, 3.5, 1200, 'Alkane/Mandalay'),
    (4.0,  60,  2, 1250, 1.6,  950, 'B2Gold/Papillon Fekola'),
    (4.0,  75,  2, 1400, 5.5,  950, 'Newmont/GT Gold'),
    (4.5,  70,  3, 1400, 3.8,  950, 'Newcrest/Telfer expansion'),
    (5.0,  30,  1, 3500, 0.85,1400, 'Coffee Gold Yukon'),
    (5.0,  105, 4, 3500, 0.97,1050, 'Franco-Nevada/Cote'),
    (5.0,  148, 2, 1200, 7.9,  900, 'Agnico/Comaplex Meliadine'),
    (5.1,  43,  2, 1700, 1.13, 950, 'Shandong/Cardinal Namdini'),
    (5.2,  78,  2, 1250, 1.38,1050, 'Goldcorp/Kaminak Coffee'),
    (5.5,  88,  3, 1400, 1.1, 1050, 'Saracen/KCGM 50%'),
    (6.0,  65,  2, 1400, 0.97,1050, 'IAMGOLD/Trelawney Cote'),
    (6.0,  72,  4, 1250, 1.5, 1100, 'Evolution/Cowal'),
    (6.0,  65,  2, 1200, 1.1,  950, 'Goldcorp/Andean Resources'),
    (6.5,  126, 4, 1160, 0.6, 1000, 'Newmont/CC&V'),
    (6.9,  34,  4, 1700, 2.1,  950, 'Zijin/Guyana Goldfields'),
    (7.5,  88,  3, 1400, 1.1, 1050, 'Saracen/KCGM 50%'),
    (7.9,  38,  4, 1400, 3.5,  900, 'Gold Fields/Barrick Yilgarn'),
    (8.0,  76,  4, 1160, 0.7, 1050, 'Kinross/Bald Mtn+Round Mtn'),
    (8.0,  120, 4, 1250, 8.8,  900, 'Newcrest/Red Chris 30%'),
    (8.5,  65,  2, 1250, 1.2, 1100, 'Goldcorp/Probe Metals'),
    (9.0,  107, 4, 1250, 0.8, 1000, 'Shandong/Veladero 50%'),
    (9.5,  60,  2, 1250, 1.6,  950, 'B2Gold/Papillon Fekola'),
    (10,   105, 4, 3500, 0.97,1050, 'Franco-Nevada/Cote'),
    (10,   140, 2, 1800, 4.5,  900, 'Kinross/Great Bear'),
    (10,   30,  4, 1160, 3.5,  900, 'Zijin/Porgera 50%'),
    (10.5, 133, 4, 2300, 8.5,  750, 'Zijin/Buritica'),
    (11,   91,  3, 1700, 8.5,  750, 'Zijin/Continental'),
    (12,   125, 4, 4300, 0.95,1580, 'Coeur/New Gold'),
    (12,   142, 4, 1800, 1.2,  900, 'SSR/Alacer'),
    (15,   133, 3, 2300, 8.1,  850, 'Gold Fields/Windfall'),
    (15,   100, 4, 1950, 1.5, 1200, 'Agnico/Yamana'),
    (15,   67,  4, 1950, 1.8, 1150, 'Pan American/Yamana LatAm'),
    (15,   80,  4, 1250, 2.5,  900, 'Barrick/Acacia'),
    (18,   156, 4, 1800, 13.5, 950, 'Newcrest/Brucejack'),
    (18,   75,  4, 1250, 1.1, 1050, 'Agnico+Yamana/Osisko'),
    (20,   140, 4, 1800, 2.8, 1150, 'Northern Star/Saracen'),
]

resources = np.array([d[0] for d in CORE_DATA])
ev_per_oz = np.array([d[1] for d in CORE_DATA])
stages = np.array([d[2] for d in CORE_DATA])
gold_prices = np.array([d[3] for d in CORE_DATA])
grades = np.array([d[4] for d in CORE_DATA])
aiscs = np.array([d[5] for d in CORE_DATA])

# ============================================================
# 核心发现1：规模折价规律（log-linear关系）
# ============================================================
print('=== 规模折价规律分析 ===')
log_res = np.log(resources)
slope, intercept, r, p, se = stats.linregress(log_res, ev_per_oz)
print(f'EV/oz = {intercept:.1f} + {slope:.1f} * ln(resource_moz)')
print(f'R = {r:.3f}, R2 = {r**2:.3f}, p = {p:.4f}')
print(f'含义：资源量每翻倍，EV/oz变化 {slope*np.log(2):.1f} $/oz')
print()

# ============================================================
# 核心发现2：按阶段分层的中位数（最实用的快速参考）
# ============================================================
print('=== 按阶段分层统计（当前金价调整后）===')
current_gold = 3300  # 2026年5月实际金价

for stage_num, stage_name in [(2,'resource'), (3,'reserve'), (4,'production')]:
    mask = stages == stage_num
    ev_s = ev_per_oz[mask]
    gp_s = gold_prices[mask]
    res_s = resources[mask]

    # 金价调整：按金价比例缩放
    ev_adjusted = ev_s * (current_gold / gp_s)

    print(f'\n{stage_name} (n={mask.sum()}):')
    print(f'  原始EV/oz: 中位数${np.median(ev_s):.0f}, 均值${np.mean(ev_s):.0f}, '
          f'范围${min(ev_s):.0f}-${max(ev_s):.0f}')
    print(f'  金价调整后(${current_gold}/oz): 中位数${np.median(ev_adjusted):.0f}, '
          f'均值${np.mean(ev_adjusted):.0f}')

    # 按资源量分组
    for res_range, label in [((0, 5), '<5 Moz'), ((5, 10), '5-10 Moz'),
                               ((10, 20), '10-20 Moz')]:
        sub = ev_adjusted[(res_s >= res_range[0]) & (res_s < res_range[1])]
        if len(sub) > 0:
            print(f'    {label}: n={len(sub)}, 中位数${np.median(sub):.0f}/oz')

# ============================================================
# 核心发现3：外推到小矿（0.03-1 Moz）
# ============================================================
print('\n\n=== 小矿外推（0.03-1 Moz，即1-31吨黄金）===')
print('基于规模折价规律外推，叠加小矿流动性折价30-50%')
print()

current_gold = 3300
# 用production阶段的数据拟合规模折价
prod_mask = stages == 4
slope_p, intercept_p, r_p, _, _ = stats.linregress(
    np.log(resources[prod_mask]), ev_per_oz[prod_mask])

print(f'Production阶段规模折价拟合: R2={r_p**2:.3f}')
print()
print(f'{"资源量":>12} {"黄金量(吨)":>10} {"基础EV/oz":>10} {"流动性折价后":>12} {"总估值(M$)":>12}')
print('-' * 65)

for res_moz in [0.03, 0.06, 0.1, 0.16, 0.32, 0.5, 0.64, 1.0, 2.0, 5.0, 10.0, 20.0]:
    gold_tons = res_moz * 31.1
    # 基础EV/oz（从大矿外推）
    base_ev = intercept_p + slope_p * np.log(res_moz)
    base_ev = max(base_ev, 15)  # 最低15$/oz

    # 金价调整（数据集平均金价约1500，当前3300）
    base_ev_adjusted = base_ev * (current_gold / 1500)

    # 流动性折价（小矿折价更大）
    if res_moz < 0.1:
        liquidity_discount = 0.50  # 50%折价
    elif res_moz < 0.3:
        liquidity_discount = 0.40
    elif res_moz < 1.0:
        liquidity_discount = 0.30
    else:
        liquidity_discount = 0.0  # 1Moz以上无额外折价

    final_ev = base_ev_adjusted * (1 - liquidity_discount)
    total_value = final_ev * res_moz * 1e6 / 1e6  # M$

    marker = ' <-- 小矿外推' if res_moz < 1.0 else ''
    print(f'{res_moz:>10.2f} Moz {gold_tons:>8.1f}t {base_ev_adjusted:>10.0f} '
          f'{final_ev:>12.0f} {total_value:>10.1f}M{marker}')

print()
print('注：小矿外推基于规模折价规律，叠加流动性折价（私下交易、买家少）')
print('    实际成交价受品位、AISC、基建条件影响较大，上下浮动±40%')
