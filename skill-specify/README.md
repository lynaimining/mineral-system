# Skill Specify - 规格驱动的 Skill 开发工具

基于 Specification-Driven Development (SDD) 方法论，帮助你创建高质量、结构化的 Skill 规格文档。

## 核心理念

**规格先行**：Skill 不是"代码生成器"，而是"规格执行引擎"。维护 Skill = 演进规格文档。

## 快速开始

### 1. 创建 Skill 规格

```bash
python skill_specify.py "沙特矿权区块快速评估工具"
```

**输出**：
```
[*] Creating Skill Spec: 沙特矿权区块快速评估工具
[OK] Skill spec created: 001-沙特矿权区块快速评估工具
[DIR] C:\Users\39555\.superpowers\skills\001-沙特矿权区块快速评估工具

[FILES] Generated:
  - skill.md           # 主规格（WHAT/WHY）
  - constitution.md    # 6条不可变原则
  - checklist.md       # L1/L2/L3 验证清单
  - examples.md        # 触发词库（≥10个）

[WARN] Needs clarification (44 items)
[NEXT] Steps:
   1. Edit files to fill [NEEDS CLARIFICATION] items
   2. Run /skill.implement 001-沙特矿权区块快速评估工具
```

### 2. 填写规格文档

编辑生成的 4 个文件，填写所有 `[NEEDS CLARIFICATION]` 标记项：

- **skill.md** - 定义 WHAT（功能）和 WHY（需求背景）
- **constitution.md** - 定义 6 条不可变原则
- **checklist.md** - 定义质量检查清单
- **examples.md** - 定义触发词和用例

### 3. 实现 Skill

```bash
# 方式1：手动实现
# 根据规格文档编写 skill 实现代码

# 方式2：AI 辅助实现（未来功能）
# python skill_implement.py 001-沙特矿权区块快速评估工具
```

## 生成的文件结构

```
~/.superpowers/skills/001-沙特矿权区块快速评估工具/
├── skill.md                    # 主规格文档
│   ├── WHAT（功能定义）
│   ├── WHY（需求背景）
│   ├── 约束条件
│   ├── 质量标准（L1/L2/L3）
│   └── 依赖
├── constitution.md             # Skill 宪法（6条不可变原则）
│   ├── Article I: Library-First
│   ├── Article II: CLI Interface
│   ├── Article III: Test-First
│   ├── Article IV: Simplicity
│   ├── Article V: Anti-Abstraction
│   └── Article VI: Integration-First
├── checklist.md                # 质量检查清单
│   ├── Phase 0: 前置检查
│   ├── Phase 1: 数据提取
│   ├── Phase 2: 核心处理
│   ├── Phase 3: 输出生成
│   ├── L1 验证（完整性）
│   ├── L2 验证（准确性）
│   └── L3 验证（收敛性）
├── examples.md                 # 触发词库和用例
│   ├── 触发词（≥10个）
│   ├── 应触发用例（≥5个）
│   └── 不应触发用例（≥3个）
└── spec-metadata.json          # 元数据（供工具使用）
```

## Skill 宪法（6条不可变原则）

### Article I: Library-First
每个 Skill 必须是独立可复用的模块。

### Article II: CLI Interface
所有功能必须可通过文本输入/输出验证。

### Article III: Test-First
先定义质量标准和验证方法，再执行。

### Article IV: Simplicity
初始实现最多 3 个主要步骤，禁止过度设计。

### Article V: Anti-Abstraction
直接解决问题，不要再包一层抽象。

### Article VI: Integration-First
用真实数据/环境测试，不用 mock。

## 三层验证标准

- **L1 工具调用完整性** — 所有必需步骤是否执行
- **L2 实体准确性** — 数据、引用、数值是否正确
- **L3 状态收敛** — 最终交付物是否干净完整

## 模板驱动质量（7种约束机制）

1. **防止过早实现细节** — Skill 描述写 WHAT/WHY，不写 HOW
2. **强制不确定性标记** — 模糊点必须用 `[NEEDS CLARIFICATION]` 标注
3. **结构化检查清单** — 每个 Skill 必须有自检清单
4. **宪法合规门控** — 核心规则必须是决策树，覆盖所有分支
5. **层级化细节管理** — 主文档保持高层可读，细节提取到独立文件
6. **测试优先顺序** — 先定义验证标准，再生成内容
7. **防止投机性功能** — 每个功能必须追溯到具体用户需求

## 示例：完整工作流

```bash
# 1. 创建规格
python skill_specify.py "从地质图自动提取成矿要素"

# 2. 编辑规格文档
# 填写 skill.md 中的 [NEEDS CLARIFICATION] 项
# 填写 constitution.md 中的验证标准
# 填写 checklist.md 中的检查项
# 填写 examples.md 中的触发词和用例

# 3. 验证规格完整性
python skill_validate.py 002-从地质图自动提取成矿要素

# 4. 实现 Skill
# 根据规格文档编写实现代码

# 5. 质量检查
# 对照 checklist.md 逐项验证
# 确保达到 8.5/10 质量基线
```

## 与现有工具集成

### skill-creator
`skill.specify` 生成规格文档，`skill-creator` 根据规格生成实现。

### skill-evolution-advisor
规格文档作为演进分析的输入，提供结构化的改进建议。

### skill-metrics
三层验证标准（L1/L2/L3）直接映射到 skill-metrics 的记录格式。

## 常见问题

### Q: 为什么要先写规格？
A: 规格驱动开发确保 Skill 设计清晰、可追溯、可维护。修改规格比修改代码成本低得多。

### Q: [NEEDS CLARIFICATION] 必须全部填写吗？
A: 是的。未填写的项会导致实现时的歧义和质量问题。

### Q: 控制台显示乱码怎么办？
A: 这是 Windows GBK 编码问题，不影响文件内容。生成的文件是正确的 UTF-8 编码。

### Q: 如何判断规格是否完整？
A: 检查以下几点：
- 无 `[NEEDS CLARIFICATION]` 标记
- 触发词 ≥10 个
- 应触发用例 ≥5 个
- 不应触发用例 ≥3 个
- 质量检查清单覆盖所有阶段

## 参考资料

- [Specification-Driven Development (SDD)](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- [CLAUDE.md - Skill 设计方法论](../../CLAUDE.md#skill-设计方法论)
- [skill-quality-loop.md](../../../.claude/projects/C--Users-39555/memory/skill-quality-loop.md)

## 版本历史

- **v1.0** (2026-05-20) - 初始版本，基于 SDD 方法论
