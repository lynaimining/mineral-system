# Nickel-Ore Skill 质量审查流程

> 本文档定义 nickel-ore skill 的质量闭环机制，遵循 memory/skill-quality-loop.md 标准。

## 适用范围

- 模式 A（项目分析）：输出项目评价报告前必须执行
- 模式 B（报告撰写）：输出技术报告前必须执行
- 模式 C（潜力预测）：输出潜力评价报告前必须执行
- 模式 D（知识查询）：无需审查，直接回答

## 质量闭环配置

nickel-ore 采用 **A + F** 组合（最低配置）：
- **模式 A**：多视角并行审查（2 个 Reviewer）
- **模式 F**：问题 severity 分级

如果项目为 Tier 1 级别（>1 Mt Ni）或用户明确要求高质量，升级为 **A + C + F**：
- 增加 **模式 C**：迭代修复循环（MAX_ROUNDS = 2）

---

## 审查流程

### Step 1：双 Reviewer 并行审查

**Reviewer-1：地质技术准确性**
- 矿床类型判定是否正确（红土型 vs 岩浆型，对照 deposit_types.md 诊断特征）
- 冶炼工艺适配是否合理（HPAL/RKEF/Ferronickel，对照 processing_routes.md）
- 品位-吨位评估是否符合该类型曲线（对照 grade_tonnage.md）
- 成矿要素打分是否有数据支撑
- 参考文献引用是否准确

**Reviewer-2：逻辑与风险平衡**
- 结论是否存在"一边倒"乐观倾向（CLAUDE.md 防一边倒规则）
- 风险分析是否充分（必须包含主要风险和不确定因素）
- 冶炼工艺选择的经济性分析是否合理（Class 1 vs Class 2 产品价差）
- 数据来源是否标注清晰
- 假设条件是否明确
- 建议是否可操作

### Step 2：问题 Severity 分级（模式 F）

| Severity | 定义 | 示例 | 处理 |
|----------|------|------|------|
| Critical | 致命错误，会导致误判 | 矿床类型判错（红土误判为岩浆）、工艺路线完全不适配、品位数量级错误 | 必须修复 |
| High | 重大问题，影响可信度 | 缺少风险分析、数据无来源、关键假设未说明、工艺经济性分析缺失 | 必须修复 |
| Medium | 中等问题，影响专业性 | 术语不准确、参考文献格式错误、图表标注不清 | 建议修复 |
| Low | 轻微问题，不影响结论 | 措辞优化、排版细节 | 可忽略 |

### Step 3：修复决策

```
IF (Critical + High) == 0:
  → PASS，输出最终报告
ELSE IF 项目为 Tier 1 或用户要求高质量:
  → 启动迭代修复循环（模式 C，MAX_ROUNDS = 2）
  → 修复 Critical + High 问题
  → 增量审查修复部分
  → 若仍有 Critical/High 且超过 2 轮，标记 NEEDS_HUMAN
ELSE:
  → 修复 Critical 问题（High 问题列入报告附录"待完善事项"）
  → 输出报告
```

---

## 镍矿特有的审查要点

### 红土型镍矿
- **垂向分带识别**：褐铁矿层 vs 腐泥土层是否正确判定
- **工艺适配**：Ni/Fe 比、Mg/Fe 比是否支持所选工艺路线
- **气候条件**：是否位于热带-亚热带气候带
- **风化深度**：是否满足经济开采要求（>10 m）

### 岩浆型镍矿
- **硫化物类型**：块状 vs 浸染状 vs 网脉状识别是否准确
- **地壳混染证据**：是否有同位素/捕虏体等证据支持
- **岩浆通道**：是否识别出岩浆管道系统
- **PGE 共生**：是否评估 PGE 副产价值

### 工艺经济性
- **产品等级**：Class 1（电池级）vs Class 2（不锈钢级）价差是否考虑
- **工艺成本**：HPAL（高 CAPEX）vs RKEF（高 OPEX）差异是否分析
- **环境风险**：HPAL 尾渣处理、红土矿开采环境影响是否提及

---

## 与 copper-ore / mineral-system-eval 的协作

当用户任务同时涉及 nickel-ore 和其他 skill 时：
1. **Ni-Cu-PGE 共生矿床**（Magmatic Ni-Cu-PGE）：调用 copper-ore 的知识库（Norilsk、Voisey's Bay、Jinchuan、Sudbury）
2. **通用框架**：mineral-system-eval 负责五要素框架评分
3. **质量审查**：nickel-ore 的 Reviewer-1 + mineral-system-eval 的 Reviewer 共同完成

---

## 版本记录

- v1.0 (2026-04-27)：初始版本，采用 A + F 最低配置
