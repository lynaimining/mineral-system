#!/usr/bin/env python3
"""
Skill Specify - 规格驱动的 Skill 开发工具
基于 Specification-Driven Development (SDD) 方法论

用法:
    python skill_specify.py <描述>
    python skill_specify.py "沙特矿权区块快速评估工具"
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime

# 配置
SKILLS_DIR = Path.home() / ".superpowers" / "skills"
TEMPLATES_DIR = Path(__file__).parent / "templates"
REPO_DIR = Path.home() / "Desktop" / "07-平台开发" / "mineral-system"

def slugify(text):
    """将中英文描述转为 slug"""
    # 移除特殊字符，保留中英文、数字、空格
    text = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', text)
    # 转小写，空格转连字符
    text = text.lower().strip()
    text = re.sub(r'[\s_]+', '-', text)
    return text

def get_next_skill_number():
    """扫描现有 skills，返回下一个编号"""
    if not SKILLS_DIR.exists():
        return 1

    max_num = 0
    for skill_dir in SKILLS_DIR.iterdir():
        if skill_dir.is_dir():
            # 尝试从目录名提取编号（如果有的话）
            match = re.match(r'^(\d+)-', skill_dir.name)
            if match:
                num = int(match.group(1))
                max_num = max(max_num, num)

    return max_num + 1

def create_skill_spec(description):
    """创建 skill 规格文档"""
    skill_num = get_next_skill_number()
    skill_slug = slugify(description)
    skill_name = f"{skill_num:03d}-{skill_slug}"

    # 创建目录
    skill_dir = SKILLS_DIR / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    # 生成文件
    files_created = []

    # 1. skill.md
    skill_md = skill_dir / "skill.md"
    with open(skill_md, 'w', encoding='utf-8') as f:
        f.write(generate_skill_template(description, skill_slug))
    files_created.append(skill_md)

    # 2. constitution.md
    constitution_md = skill_dir / "constitution.md"
    with open(constitution_md, 'w', encoding='utf-8') as f:
        f.write(generate_constitution_template())
    files_created.append(constitution_md)

    # 3. checklist.md
    checklist_md = skill_dir / "checklist.md"
    with open(checklist_md, 'w', encoding='utf-8') as f:
        f.write(generate_checklist_template())
    files_created.append(checklist_md)

    # 4. examples.md
    examples_md = skill_dir / "examples.md"
    with open(examples_md, 'w', encoding='utf-8') as f:
        f.write(generate_examples_template(description))
    files_created.append(examples_md)

    return {
        'skill_name': skill_name,
        'skill_dir': skill_dir,
        'files': files_created,
        'clarifications': extract_clarifications(skill_dir)
    }

def generate_skill_template(description, slug):
    """生成 skill.md 模板"""
    return f"""---
name: {slug}
description: {description}
trigger_keywords:
  - {description}
  - [NEEDS CLARIFICATION: 补充中文触发词]
  - [NEEDS CLARIFICATION: 补充英文触发词]
  - [NEEDS CLARIFICATION: 补充口语变体]
execution_model: [NEEDS CLARIFICATION: haiku/sonnet/opus?]
quality_baseline: 8.5
created: {datetime.now().isoformat()}
---

# {description}

## WHAT（功能定义）

**核心能力**：
- [NEEDS CLARIFICATION: 输入是什么？]
- [NEEDS CLARIFICATION: 输出是什么？]
- [NEEDS CLARIFICATION: 核心处理逻辑是什么？]

**用户故事**：
1. 作为 [角色]，我需要 [功能]，以便 [价值]
2. [NEEDS CLARIFICATION: 补充更多用户故事]

**验收标准**：
- [ ] [NEEDS CLARIFICATION: 如何判断成功？]
- [ ] [NEEDS CLARIFICATION: 输出格式要求？]
- [ ] [NEEDS CLARIFICATION: 性能要求？]

## WHY（需求背景）

**问题陈述**：
[NEEDS CLARIFICATION: 当前痛点是什么？为什么需要这个 skill？]

**价值主张**：
[NEEDS CLARIFICATION: 解决后带来什么价值？节省多少时间？提升多少质量？]

## 约束条件

**必须遵守**：
- [NEEDS CLARIFICATION: 有哪些硬性约束？]
- 编码完整性验证（如涉及中文输出）
- 数据来源可追溯

**禁止**：
- [NEEDS CLARIFICATION: 有哪些反模式？]
- 不验证就交付
- 主观判断无数据支撑

## 质量标准

- L1 完整性：所有必需步骤执行 ✅
- L2 准确性：数据来源可验证 ✅
- L3 收敛性：输出格式规范 ✅
- 综合评分：≥8.5/10

## 依赖

**Python 包**：
- [NEEDS CLARIFICATION: 需要哪些 Python 包？]

**外部服务**：
- [NEEDS CLARIFICATION: 需要调用哪些 API？]

**数据源**：
- [NEEDS CLARIFICATION: 需要哪些数据文件？]
"""

def generate_constitution_template():
    """生成 constitution.md 模板"""
    return """# Skill 宪法（不可变原则）

## Article I: Library-First
本 skill 必须作为独立模块，可被其他 skill 调用。

**验证标准**：
- [ ] 无硬编码路径依赖
- [ ] 输入输出接口清晰
- [ ] 可独立测试

## Article II: CLI Interface
所有功能必须可通过文本输入/输出验证。

**验证标准**：
- [ ] 接受文本输入（stdin/args/files）
- [ ] 产生文本输出（stdout/files）
- [ ] 支持 JSON 格式（如需结构化数据）

## Article III: Test-First
先定义验证标准，再生成内容。

**验证标准**：
- [ ] 输入：[NEEDS CLARIFICATION: 测试输入是什么？]
- [ ] 预期输出：[NEEDS CLARIFICATION: 预期输出是什么？]
- [ ] 失败案例：[NEEDS CLARIFICATION: 哪些情况应该失败？]

## Article IV: Simplicity
初始实现最多 3 个主要步骤。

**步骤分解**：
1. [NEEDS CLARIFICATION: 第一步做什么？]
2. [NEEDS CLARIFICATION: 第二步做什么？]
3. [NEEDS CLARIFICATION: 第三步做什么？]

如果超过 3 步，必须重新设计或拆分为多个 skill。

## Article V: Anti-Abstraction
直接解决问题，不包装抽象层。

**反模式**：
- ❌ 创建"通用框架"
- ❌ 过度参数化
- ❌ 为未来需求预留接口

**正确做法**：
- ✅ 直接调用库函数
- ✅ 硬编码合理默认值
- ✅ 只解决当前问题

## Article VI: Integration-First
用真实数据测试，不用 mock。

**测试数据源**：
- [NEEDS CLARIFICATION: 从哪里获取测试数据？]
- [NEEDS CLARIFICATION: 测试数据是否需要脱敏？]
"""

def generate_checklist_template():
    """生成 checklist.md 模板"""
    return """# 质量检查清单

## Phase 0: 前置检查（容错处理）
- [ ] 输入文件存在且可读
- [ ] 依赖包已安装
- [ ] 输出目录可写
- [ ] [NEEDS CLARIFICATION: 其他前置条件？]

## Phase 1: 数据提取/输入处理
- [ ] [NEEDS CLARIFICATION: 提取什么数据？]
- [ ] 数据完整性验证
- [ ] 异常值处理
- [ ] 编码检测（如涉及文本）

## Phase 2: 核心处理
- [ ] [NEEDS CLARIFICATION: 核心逻辑是什么？]
- [ ] 中间结果保存（如任务>5分钟）
- [ ] 进度追踪
- [ ] 错误处理

## Phase 3: 输出生成
- [ ] 格式符合规范
- [ ] 编码完整性验证（中文报告必检）
- [ ] 文件大小合理
- [ ] [NEEDS CLARIFICATION: 其他输出要求？]

## L1 验证（工具调用完整性）
- [ ] 所有必需步骤已执行
- [ ] 无跳过步骤
- [ ] 中间产物已生成

## L2 验证（实体准确性）
- [ ] 数据来源可追溯
- [ ] 数值计算正确
- [ ] 引用真实存在
- [ ] [NEEDS CLARIFICATION: 其他准确性要求？]

## L3 验证（状态收敛）
- [ ] 无孤立引用
- [ ] 无乱码（U+FFFD）
- [ ] 格式合规
- [ ] 文件可正常打开

## 自检报告格式

执行完成后输出：

```
✅ [Skill名称] 执行完整性自检
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
流程完整性: ✅ 全部执行 / ⚠️ 部分跳过 / ❌ 关键步骤缺失
关键产物: [列出关键指标]
质量评估: [PASS / WARN / FAIL]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
"""

def generate_examples_template(description):
    """生成 examples.md 模板"""
    return f"""# 触发词库和用例

## 触发词（≥10个）

### 中文触发词
1. {description}
2. [NEEDS CLARIFICATION: 补充同义词]
3. [NEEDS CLARIFICATION: 补充口语表达]
4. [NEEDS CLARIFICATION: 补充简称]
5. [NEEDS CLARIFICATION: 补充动词变体]

### 英文触发词
1. [NEEDS CLARIFICATION: 英文表达]
2. [NEEDS CLARIFICATION: 英文同义词]
3. [NEEDS CLARIFICATION: 英文口语]
4. [NEEDS CLARIFICATION: 英文缩写]
5. [NEEDS CLARIFICATION: 英文动词变体]

### 混合表达
1. [NEEDS CLARIFICATION: 中英混合]
2. [NEEDS CLARIFICATION: 口语化混合]

## 应触发用例（至少5个）

1. **用例1**：[NEEDS CLARIFICATION: 描述典型使用场景]
   - 用户输入：[NEEDS CLARIFICATION]
   - 预期行为：[NEEDS CLARIFICATION]

2. **用例2**：[NEEDS CLARIFICATION]
   - 用户输入：[NEEDS CLARIFICATION]
   - 预期行为：[NEEDS CLARIFICATION]

3. **用例3**：[NEEDS CLARIFICATION]
   - 用户输入：[NEEDS CLARIFICATION]
   - 预期行为：[NEEDS CLARIFICATION]

4. **用例4**：[NEEDS CLARIFICATION]
   - 用户输入：[NEEDS CLARIFICATION]
   - 预期行为：[NEEDS CLARIFICATION]

5. **用例5**：[NEEDS CLARIFICATION]
   - ���户输入：[NEEDS CLARIFICATION]
   - 预期行为：[NEEDS CLARIFICATION]

## 不应触发用例（至少3个）

1. **反例1**：[NEEDS CLARIFICATION: 相似但不同的任务]
   - 用户输入：[NEEDS CLARIFICATION]
   - 正确行为：不触发本 skill，应触发 [其他 skill]

2. **反例2**：[NEEDS CLARIFICATION]
   - 用户输入：[NEEDS CLARIFICATION]
   - 正确行为：[NEEDS CLARIFICATION]

3. **反例3**：[NEEDS CLARIFICATION]
   - 用户输入：[NEEDS CLARIFICATION]
   - 正确行为：[NEEDS CLARIFICATION]
"""

def extract_clarifications(skill_dir):
    """提取所有 [NEEDS CLARIFICATION] 项"""
    clarifications = []

    for md_file in skill_dir.glob("*.md"):
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            matches = re.findall(r'\[NEEDS CLARIFICATION:([^\]]+)\]', content)
            for match in matches:
                clarifications.append({
                    'file': md_file.name,
                    'question': match.strip()
                })

    return clarifications

def main():
    if len(sys.argv) < 2:
        print("Usage: python skill_specify.py <description>")
        print('Example: python skill_specify.py "Saudi block rapid assessment tool"')
        sys.exit(1)

    description = ' '.join(sys.argv[1:])

    print(f"[*] Creating Skill Spec: {description}")
    print()

    result = create_skill_spec(description)

    print(f"[OK] Skill spec created: {result['skill_name']}")
    print(f"[DIR] {result['skill_dir']}")
    print()
    print("[FILES] Generated:")
    for f in result['files']:
        print(f"  - {f.name}")
    print()

    if result['clarifications']:
        print(f"[WARN] Needs clarification ({len(result['clarifications'])} items):")
        print()
        for i, item in enumerate(result['clarifications'], 1):
            print(f"{i}. [{item['file']}] {item['question']}")
        print()
        print("[NEXT] Steps:")
        print(f"   1. Edit files to fill [NEEDS CLARIFICATION] items")
        print(f"   2. Run /skill.implement {result['skill_name']}")

    # Output JSON for other tools
    output = {
        'skill_name': result['skill_name'],
        'skill_dir': str(result['skill_dir']),
        'files': [str(f) for f in result['files']],
        'clarifications_count': len(result['clarifications'])
    }

    output_file = result['skill_dir'] / 'spec-metadata.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n[META] Metadata saved: {output_file}")

if __name__ == '__main__':
    main()
