# Copper-Ore Skill 质量审查流程

> 本文档定义 copper-ore skill 的质量闭环机制，遵循 memory/skill-quality-loop.md 标准。

## 适用范围

- 模式 A（项目分析）：输出项目评价报告前必须执行
- 模式 B（报告撰写）：输出技术报告前必须执行
- 模式 C（潜力预测）：输出潜力评价报告前必须执行
- 模式 D（知识查询）：无需审查，直接回答

## 质量闭环配置

copper-ore 采用 **A + F** 组合（最低配置）：
- **模式 A**：多视角并行审查（2 个 Reviewer）
- **模式 F**：问题 severity 分级

如果项目为 Tier 1 级别（>5 Mt Cu）或用户明确要求高质量，升级为 **A + C + F**：
- 增加 **模式 C**：迭代修复循环（MAX_ROUNDS = 2）

---

## 审查流程

### Step 1：双 Reviewer 并行审查

**Reviewer-1：地质技术准确性**
- 矿床类型判定是否正确（对照 deposit_types.md 诊断特征）
- 构造背景定位是否合理（对照 global_belts.md）
- 品位-吨位评估是否符合该类型曲线（对照 grade_tonnage.md）
- 成矿要素打分是否有数据支撑
- 参考文献引用是否准确

**Reviewer-2：逻辑与风险平衡**
- 结论是否存在"一边倒"乐观倾向（CLAUDE.md 防一边倒规则）
- 风险分析是否充分（必须包含主要风险和不确定因素）
- 数据来源是否标注清晰
- 假设条件是否明确
- 建议是否可操作

### Step 2：问题 Severity 分级（模式 F）

| Severity | 定义 | 示例 | 处理 |
|----------|------|------|------|
| Critical | 致命错误，会导致误判 | 矿床类型判错、品位数量级错误、构造背景完全不符 | 必须修复 |
| High | 重大问题，影响可信度 | 缺少风险分析、数据无来源、关键假设未说明 | 必须修复 |
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

## 审查输出格式

每次审查后生成审查记录（嵌入报告末尾或单独文件）：

```markdown
## 质量审查记录

**审查时间**：2026-04-27 12:30
**项目名称**：XXX 铜矿
**Tier 级别**：Tier 2（2.5 Mt Cu @ 0.65%）

### Reviewer-1（地质技术）
- ✅ 矿床类型判定正确（Porphyry Cu-Mo）
- ✅ 构造定位合理（安第斯弧后伸展）
- ⚠️ Medium：品位-吨位图缺少数据来源标注
- ❌ High：成矿要素打分第 7 项（蚀变强度）无数据支撑

### Reviewer-2（逻辑与风险）
- ✅ 风险分析充分（列出 5 项主要风险）
- ❌ Critical：结论过于乐观，未考虑剥蚀深度不确定性
- ⚠️ Medium：建议部分缺少优先级排序

### 统计
- Critical: 1
- High: 1
- Medium: 2
- Low: 0

### 处置
→ 执行修复（Critical + High）
→ 修复后增量审查通过
→ 最终输出报告
```

---

## 与 mineral-system-eval 的协作

当用户任务同时涉及 copper-ore 和 mineral-system-eval 时：
1. mineral-system-eval 负责通用五要素框架评分
2. copper-ore 提供铜矿专项知识库（deposit_types, global_belts, grade_tonnage）
3. 质量审查由 copper-ore 的 Reviewer-1 + mineral-system-eval 的 Reviewer 共同完成

---

## 版本记录

- v1.0 (2026-04-27)：初始版本，采用 A + F 最低配置
- 后续根据实际使用反馈升级为 A + C + F 或更高配置
