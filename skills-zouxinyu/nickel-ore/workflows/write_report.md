# Workflow B：镍矿报告撰写

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

**红土型镍矿特别章节**：
- 风化剖面分层（腐殖土层 / 褐铁矿层 / 过渡层 / 蛇纹石层 / 基岩）
- Ni-Co-Fe-Mg-Si 垂向分布曲线
- HPAL / RKEF / Ferronickel 工艺适配性分析
- 剥采比与经济性

**岩浆型镍矿特别章节**：
- 岩浆分异序列（橄榄岩 / 辉石岩 / 辉长岩）
- 硫化物矿物组合（磁黄铁矿 / 镍黄铁矿 / 黄铜矿 / 紫硫镍矿）
- Ni-Cu-PGE 共生关系
- 与 Norilsk / Voisey's Bay / Jinchuan / Sudbury 对比

### Step 4：图件清单
按章节列出图件，对每张图说明：
- 图名、用途
- 来源（用户已有 / 需新绘制 / AI 概念示意）
- 数据可信度

**红土型必备图件**：
- 风化剖面柱状图
- Ni-Co 品位等值线图
- 剥采比分区图

**岩浆型必备图件**：
- 岩浆侵入体平面图
- 典型勘探线剖面（显示岩浆分异）
- Ni-Cu-PGE 品位等值线图

### Step 5：参考文献
- 优先用用户文件夹内已有 PDF 作为引用
- 中文用 GB/T 7714 格式，英文用 SEG / GeoScienceWorld 格式
- 调用 `ref-verify` skill 用 CrossRef / OpenAlex 验证（避免 AI 幻觉）

### Step 6：输出
- 调用 `anthropic-skills:docx` 生成 .docx
- 中文文档遵循 `cjk-docx` 编码规则
- 文件名 `Nickel_Report_<���型>_<对象>_<YYYYMMDD>.docx`
- 保存至桌面

## 与 paper skill 的衔接

如果用户最终目的是发表期刊论文（而非内部技术报告），转入 `paper` skill：本 skill 的输出可作为 paper skill 的输入素材。
