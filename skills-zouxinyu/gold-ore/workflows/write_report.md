# Workflow B：金矿报告撰写

## 步骤

### Step 1：与用户确认报告类型
四选一（如不明确则提问）：
1. 专题地质报告（成矿规律 / 矿床综合研究）
2. 中国规范勘查报告（DZ/T 0033）
3. NI 43-101 / JORC 海外技术报告
4. 年报市场+地质综合章节

### Step 2：材料整合
- 扫描用户工作目录所有相关文件
- 列出可用图、表、数据
- 对照报告章节需求识别"已有"vs"缺失"——缺失项明确告知用户

### Step 3：按对应模板撰写
读取 `templates/technical_report.md` 中对应子格式章节。逐节生成内容。

**金矿特色章节**：
- 成矿时代与构造背景（造山型强调变质—变形时代关系）
- 蚀变矿物组合（Orogenic: 碳酸盐—绢云母—黄铁矿；Epithermal: 硅化—明矾石—高岭土）
- 金赋存状态（自然金粒度、载金矿物、不可见金）
- 选冶性能（重选—浮选—氰化—生物氧化适用性）

### Step 4：图件清单
按章节列出图件，对每张图说明：
- 图名、用途
- 来源（用户已有 / 需新绘制 / AI 概念示意）
- 数据可信度

**金矿必备图件**：
- 区域构造—成矿带分布图
- 矿床地质平面图（含蚀变分带）
- 典型勘探线剖面（含品位等值线）
- 金品位—吨位累积曲线对比图
- 蚀变矿物组合柱状图

### Step 5：参考文献
- 优先用用户文件夹内已有 PDF 作为引用
- 中文用 GB/T 7714 格式，英文用 SEG / Economic Geology 格式
- 调用 `ref-verify` skill 用 CrossRef / OpenAlex 验证（避免 AI 幻觉）
- **金矿权威文献**：Groves et al. (Orogenic), Cline et al. (Carlin), Hedenquist et al. (Epithermal)

### Step 6：输出
- 调用 `anthropic-skills:docx` 生成 .docx
- 中文文档遵循 `cjk-docx` 编码规则
- 文件名 `Gold_Report_<类型>_<对象>_<YYYYMMDD>.docx`
- 保存至 `Desktop/02-矿业评估/<项目名>/` 或 `Desktop/04-调研报告/`

## 与 paper skill 的衔接

如果用户最终目的是发表期刊论文（而非内部技术报告），转入 `chinese-paper` skill：本 skill 的输出可作为 paper skill 的输入素材。
