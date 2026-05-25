# -*- coding: utf-8 -*-
"""
金矿项目评价报告 - 图件生成脚本模板
用于生成品位-吨位对比图、成矿要素雷达图、风险矩阵图等
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from pathlib import Path

# 中文字体设置
matplotlib.rcParams['font.family'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def generate_grade_tonnage_plot(project_data, benchmark_deposits, output_path, deposit_type='Orogenic'):
    """
    生成品位-吨位对比图

    Args:
        project_data: dict, {'tonnage': float, 'grade': float, 'name': str}
        benchmark_deposits: list of dict, [{'name': str, 'tonnage': float, 'grade': float, 'tier': str}, ...]
        output_path: str, 输出文件路径
        deposit_type: str, 矿床类型名称
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    # 绘制标杆矿床
    tier_colors = {'Tier 0': '#d62728', 'Tier 1': '#ff7f0e', 'Tier 2': '#2ca02c', 'Tier 3': '#1f77b4'}

    for deposit in benchmark_deposits:
        color = tier_colors.get(deposit['tier'], '#7f7f7f')
        ax.scatter(deposit['tonnage'], deposit['grade'], s=150, c=color,
                  alpha=0.6, edgecolors='black', linewidths=1.5)
        ax.annotate(deposit['name'], (deposit['tonnage'], deposit['grade']),
                   xytext=(8, 8), textcoords='offset points', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))

    # 绘制项目
    ax.scatter(project_data['tonnage'], project_data['grade'], s=400, c='#9467bd',
              marker='*', edgecolors='black', linewidths=2.5, label=project_data['name'], zorder=10)
    ax.annotate(project_data['name'], (project_data['tonnage'], project_data['grade']),
               xytext=(10, -20), textcoords='offset points', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))

    # 设置坐标轴
    ax.set_xlabel('金属量（t Au）', fontsize=14, fontweight='bold')
    ax.set_ylabel('品位（g/t Au）', fontsize=14, fontweight='bold')
    ax.set_title(f'{deposit_type}金矿品位-吨位对比', fontsize=16, fontweight='bold', pad=20)
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3, linestyle='--')

    # 图例
    legend_elements = [plt.scatter([], [], s=150, c=color, alpha=0.6, edgecolors='black',
                                  linewidths=1.5, label=tier)
                      for tier, color in tier_colors.items()]
    legend_elements.append(plt.scatter([], [], s=400, c='#9467bd', marker='*',
                                      edgecolors='black', linewidths=2.5, label='本项目'))
    ax.legend(handles=legend_elements, loc='best', fontsize=11, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"✓ 品位-吨位对比图已生成：{output_path}")


def generate_radar_chart(scores, labels, output_path, max_score=10):
    """
    生成成矿要素雷达图

    Args:
        scores: list of float, 10项评分
        labels: list of str, 10项标签
        output_path: str, 输出文件路径
        max_score: int, 最高分
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

    # 计算角度
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    scores_plot = scores + scores[:1]  # 闭合
    angles += angles[:1]

    # 绘制雷达图
    ax.plot(angles, scores_plot, 'o-', linewidth=2.5, color='#1f77b4', label='项目评分')
    ax.fill(angles, scores_plot, alpha=0.25, color='#1f77b4')

    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, max_score)
    ax.set_yticks(range(0, max_score+1, 2))
    ax.set_yticklabels([str(i) for i in range(0, max_score+1, 2)], fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)

    # 标题
    ax.set_title('成矿要素系统评分（满分90分）', fontsize=16, fontweight='bold', pad=30)

    # 在每个点上标注分数
    for angle, score, label in zip(angles[:-1], scores, labels):
        ax.text(angle, score + 0.5, f'{score}', ha='center', va='center',
               fontsize=10, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"✓ 成矿要素雷达图已生成：{output_path}")


def generate_risk_matrix(risks, output_path):
    """
    生成风险矩阵图

    Args:
        risks: list of dict, [{'name': str, 'impact': int (1-5), 'probability': int (1-5)}, ...]
        output_path: str, 输出文件路径
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # 绘制背景色块
    for i in range(1, 6):
        for j in range(1, 6):
            risk_level = i * j
            if risk_level <= 6:
                color = '#2ca02c'  # 低风险 - 绿色
            elif risk_level <= 12:
                color = '#ff7f0e'  # 中风险 - 橙色
            else:
                color = '#d62728'  # 高风险 - 红色
            ax.add_patch(plt.Rectangle((j-0.5, i-0.5), 1, 1, facecolor=color, alpha=0.3))

    # 绘制风险点
    for risk in risks:
        ax.scatter(risk['probability'], risk['impact'], s=300, c='blue',
                  alpha=0.7, edgecolors='black', linewidths=2, zorder=10)
        ax.annotate(risk['name'], (risk['probability'], risk['impact']),
                   xytext=(10, 10), textcoords='offset points', fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9),
                   arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    # 设置坐标轴
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 6))
    ax.set_xticklabels(['很低', '低', '中', '高', '很高'], fontsize=12)
    ax.set_yticklabels(['很低', '低', '中', '高', '很高'], fontsize=12)
    ax.set_xlabel('发生概率', fontsize=14, fontweight='bold')
    ax.set_ylabel('影响程度', fontsize=14, fontweight='bold')
    ax.set_title('风险矩阵图', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')

    # 图例
    legend_elements = [
        plt.scatter([], [], s=100, c='#2ca02c', alpha=0.3, label='低风险 (≤6)'),
        plt.scatter([], [], s=100, c='#ff7f0e', alpha=0.3, label='中风险 (7-12)'),
        plt.scatter([], [], s=100, c='#d62728', alpha=0.3, label='高风险 (>12)')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=11, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"✓ 风险矩阵图已生成：{output_path}")


def generate_sensitivity_analysis(base_npv, sensitivity_data, output_path):
    """
    生成敏感性分析图

    Args:
        base_npv: float, 基准NPV
        sensitivity_data: dict, {'金价': [(变化%, NPV), ...], 'OPEX': [...], ...}
        output_path: str, 输出文件路径
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    for i, (param, data) in enumerate(sensitivity_data.items()):
        changes = [d[0] for d in data]
        npvs = [d[1] for d in data]
        ax.plot(changes, npvs, 'o-', linewidth=2.5, markersize=8,
               color=colors[i % len(colors)], label=param)

    # 基准线
    ax.axhline(y=base_npv, color='black', linestyle='--', linewidth=1.5,
              label=f'基准NPV (${base_npv:.1f}M)')
    ax.axhline(y=0, color='red', linestyle=':', linewidth=1.5, alpha=0.5)

    # 设置
    ax.set_xlabel('参数变化（%）', fontsize=14, fontweight='bold')
    ax.set_ylabel('NPV@8% ($M)', fontsize=14, fontweight='bold')
    ax.set_title('敏感性分析', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=12, framealpha=0.9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=180, bbox_inches='tight')
    plt.close()
    print(f"✓ 敏感性分析图已生成：{output_path}")


# 示例用法
if __name__ == "__main__":
    output_dir = Path("C:/Users/39555/Desktop/02-矿业评估/示例项目/figures")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. 品位-吨位对比图
    project = {'tonnage': 150, 'grade': 4.5, 'name': '示例项目'}
    benchmarks = [
        {'name': 'Kalgoorlie', 'tonnage': 1500, 'grade': 4.5, 'tier': 'Tier 0'},
        {'name': 'Bendigo', 'tonnage': 300, 'grade': 5.2, 'tier': 'Tier 1'},
        {'name': 'Val-d\'Or', 'tonnage': 250, 'grade': 4.8, 'tier': 'Tier 1'},
        {'name': 'Yilgarn-A', 'tonnage': 80, 'grade': 3.5, 'tier': 'Tier 2'},
        {'name': 'Abitibi-B', 'tonnage': 50, 'grade': 6.0, 'tier': 'Tier 2'},
    ]
    generate_grade_tonnage_plot(project, benchmarks, output_dir / "grade_tonnage.png")

    # 2. 成矿要素雷达图
    scores = [8, 7, 6, 8, 7, 5, 6, 7, 8, 6]
    labels = ['构造控制', '岩性条件', '蚀变强度', '地化异常', '地球物理',
             '成矿时代', '区域对比', '资源潜力', '开采条件', '基础设施']
    generate_radar_chart(scores, labels, output_dir / "radar_chart.png")

    # 3. 风险矩阵图
    risks = [
        {'name': '资源量不确定', 'impact': 4, 'probability': 3},
        {'name': '选冶风险', 'impact': 3, 'probability': 3},
        {'name': '政策风险', 'impact': 5, 'probability': 2},
        {'name': '基建成本', 'impact': 3, 'probability': 4},
        {'name': '金属价格', 'impact': 4, 'probability': 3},
    ]
    generate_risk_matrix(risks, output_dir / "risk_matrix.png")

    # 4. 敏感性分析图
    base_npv = 150.0
    sensitivity = {
        '金价': [(-30, 50), (-20, 80), (-10, 115), (0, 150), (10, 185), (20, 220), (30, 255)],
        'OPEX': [(20, 100), (10, 125), (0, 150), (-10, 175), (-20, 200)],
        'CAPEX': [(20, 120), (10, 135), (0, 150), (-10, 165), (-20, 180)],
        '品位': [(-15, 90), (-10, 110), (0, 150), (10, 190), (15, 210)],
    }
    generate_sensitivity_analysis(base_npv, sensitivity, output_dir / "sensitivity.png")

    print("\n所有图件生成完成！")
