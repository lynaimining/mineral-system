---
name: geo-map-crop
execution_model: haiku
harness:
  preferred_model:
    phase1_render: haiku
    phase2_boundary: sonnet
    phase3_legend_ocr: sonnet
    phase4_tuning: sonnet
    phase5_qa_gate: opus
  context_mode: fresh
  human_gate_required: true
  human_gate_owner: "地质师（邹心宇 / 王选策）"
  artifact_spec: workflows/artifact_spec.md
  tests: tests/test_skill.py
description: >
  地质图裁剪工具 — 从大幅面地质图（PDF/图片）中裁剪任意区域，用 CIEDE2000 自动筛选图例，
  输出含坐标轴+矢量图例的专业小地质图（PNG/SVG），中间产物落文件，交付前四项 gate 全通过。
  触发词：裁剪地质图、地质图裁剪、截取地质图、crop geological map、裁剪地图区域、
  提取地质图的一部分、从地质图上截一块、地质图选区、geological map subset。
---

# Geological Map Crop — 地质图智能裁剪

将一张大地质图中的任意区域裁剪出来，并自动筛选出该区域内出现的地质单元图例，
组合生成一张专业的裁剪地质图，包含：
- **颜色量化**的干净地图面（去除扫描噪声）
- **经纬度坐标轴**（从原图网格线读取）
- **紧凑的矢量化图例**（底部3列排列，中文/英文标注）
- **SVG矢量输出**（可选，适合论文编辑）

## v2 更新摘要

| 功能 | 旧版 | 新版 |
|------|------|------|
| 色差算法 | CIE76 | **CIEDE2000**（工业标准，地质色更准） |
| 默认阈值 | 30 (CIE76) | **12** (CIEDE2000) |
| PDF 页数 | 仅第1页 | **任意页** (`page_num` 参数) |
| 输出格式 | PNG only | **PNG + SVG** |
| 质量验证 | 无 | **自动 QA 报告**（元数据含 warnings） |

## 工作流概览

```
用户提供地质图 (PDF/PNG/JPG)
        |
  1. 渲染为高分辨率图像 (300 DPI, 支持指定页码)
        |
  2. 识别主地图边界 + 图例区域
        |
  3. 从原图边缘读取经纬度坐标
        |
  4. 用户指定裁剪区域
        |
  5. 检测图例色块 + K-Means聚类裁剪区颜色
        |
  6. CIEDE2000 颜色匹配（比CIE76更准确）
        |
  7. Claude 视觉识别图例文字 -> 编写中文图例条目
        |
  8. 颜色量化地图 + 坐标轴 + 紧凑图例 -> 输出 (PNG/SVG)
        |
  9. 自动质量验证 -> 元数据报告
```

## 详细步骤

### Phase 1：读取与分析地质图

1. **渲染地质图**：运行 Python 代码将 PDF 渲染为高分辨率 PNG：
   ```python
   import fitz
   from PIL import Image
   doc = fitz.open("地质图.pdf")
   page = doc[0]  # 或 doc[page_num] 用于多页PDF
   pix = page.get_pixmap(dpi=300)
   img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
   img.save("rendered.png")
   ```

2. **查看渲染图像**：用 `Read` 工具查看 PNG，识别：
   - **主地图区域** `map_frame`: `(x_left, y_top, x_right, y_bottom)` 像素坐标
   - **图例色块列** `legend_swatch_x`: `(x_start, x_end)` — 图例中颜色方块的窄列
   - **图例垂直范围** `legend_y_range`: `(y_start, y_end)`

3. **读取经纬度坐标**：裁剪地图边缘（上/下/左/右各一条窄带）查看坐标标注，
   确定地图的 `lon_lat_extent`: `(lon_min, lon_max, lat_min, lat_max)` 十进制度数。

### Phase 2：确定裁剪区域

4. **用户指定裁剪区域**。可通过：
   - **百分比坐标** `crop_pct=(x1%, y1%, x2%, y2%)`，(0,0) 为左上角，(100,100) 为右下角
   - **地名描述** — Claude 在地图上找到位置后转换为百分比
   - **参考截图** — Claude 对比参考图在原图上定位

### Phase 3：视觉识别图例

5. **Claude 读取原图图例面板**，为每个匹配到的地质单元编写图例条目：
   ```python
   legend_entries = [
       {'color': (228,193,70), 'code': 'Qa/Qw', 'desc': '砂、粉砂及冲积物'},
       {'color': (128,0,0),    'code': 'Agn',   'desc': '伟晶岩'},
   ]
   ```

### Phase 4：执行裁剪（Pro 模式）

6. **调用 `crop_geological_map`**，传入 `legend_entries` 和 `lon_lat_extent` 启用 Pro 模式：

   ```python
   import sys
   sys.path.insert(0, r"<skill目录>/scripts")
   from geo_crop_engine import crop_geological_map

   crop_geological_map(
       input_path=r"<地质图路径>",
       crop_pct=(x1, y1, x2, y2),
       output_path=r"C:\Users\39555\Desktop\<输出文件名>.png",
       dpi=300,
       map_frame=(mx1, my1, mx2, my2),
       legend_swatch_x=(sx1, sx2),
       legend_y_range=(ly1, ly2),
       color_threshold=12,       # CIEDE2000 阈值（旧版CIE76用30）
       n_clusters=30,
       title="地图标题",
       page_num=0,               # 多页PDF页码（0-indexed）
       output_format='png',      # 'png' 或 'svg'
       # --- Pro 模式参数 ---
       legend_entries=legend_entries,
       lon_lat_extent=(lon_min, lon_max, lat_min, lat_max),
       quantize=True,
       map_scale=1.8,
   )
   ```

   **Pro 模式输出特点**：
   - 地图颜色量化为图例色板（干净平面色块，去除扫描噪声）
   - 地图放大 1.8x 作为画面主体
   - 四边经纬度坐标轴（15分钟间隔刻度线 + 标签）
   - 底部紧凑3列图例（完整边框，居中"图 例"标题）

   **SVG 输出**：设 `output_format='svg'`，生成可编辑矢量文件 + PNG 伴随文件。
   SVG 中地图嵌入为 base64 PNG，图例和坐标轴为矢量元素，可在 Inkscape/Illustrator 中编辑。

### Phase 5：检查与调整

7. **查看输出和质量报告**。元数据 `_meta.json` 中包含 `quality` 字段：
   - `status`: "ok" / "info" / "warning" / "error"
   - `warnings`: 具体问题列表（如 NO_MATCHES, FEW_MATCHES, OVER_MATCHING 等）
   - `stats`: 统计数据（检测/匹配数量、颜色覆盖率等）

8. **调优参数**：

   | 问题 | 解决方案 |
   |------|----------|
   | 漏掉地质单元 | 增大 `color_threshold`（12→15-20） |
   | 匹配了无关图例 | 减小 `color_threshold`（12→8-10） |
   | 坐标不对 | 检查 `lon_lat_extent` 参数 |
   | 地图太小/太大 | 调整 `map_scale`（1.5-2.5） |
   | 不需要颜色量化 | 设 `quantize=False` 保留原始光栅 |
   | 需要 SVG 矢量 | 设 `output_format='svg'` |
   | 多页 PDF | 设 `page_num=N`（0-indexed） |

### Phase 6：交付

9. **最终文件保存到桌面** `C:\Users\39555\Desktop`。

## 关键算法

### CIEDE2000 颜色匹配（v2 新增）
取代旧版 CIE76，在 CIELAB 色彩空间中计算感知色差。对地质图常见的绿色系、棕色系、
蓝灰色系的区分能力显著优于 CIE76。阈值参考：<2 不可察觉, 2-5 可察觉, 5-12 明显不同。

### 颜色量化
将裁剪区每个像素归类到最近的图例颜色（RGB 欧氏距离），白色/黑色/灰色像素单独保留，
高斯模糊平滑锯齿边缘。

### 坐标轴绘制
根据 `lon_lat_extent` 和裁剪区在地图中的像素位置，线性插值计算经纬度范围，
每 15 分钟绘制一个刻度线。

## 依赖

```
PyMuPDF (fitz)   — PDF 渲染
Pillow           — 图像处理
numpy            — 数组运算
scikit-learn     — K-Means 聚类
opencv-python    — 颜色量化与图像平滑（可选，无则跳过量化）
```

缺失用 `pip install PyMuPDF Pillow numpy scikit-learn opencv-python` 安装。

---

## 背景与定位（Thesis）

**geo-map-crop 解决的核心问题**：地质报告和论文中经常需要从 1:200000 或更大幅面的区域地质图中截取局部区域，手动截图会丢失图例、坐标信息，且图例条目无法自动筛选。本 skill 通过 CIEDE2000 色差算法自动识别裁剪区内出现的地质单元，生成含坐标轴和筛选图例的专业小地质图，直接可用于论文插图和勘探报告。

**适用场景**：矿业评估报告插图、学术论文区域地质图、找矿靶区位置图、项目区地质背景图。

**不适用场景**：卫星遥感图裁剪（无地质图例）、地形图裁剪（无地质单元）、非地质专业图件。

---

## Harness 执行流程（中间产物落文件）

每个阶段完成后必须将产物保存到文件，下一阶段读文件而非依赖 context：

```
Phase 1 (haiku)  → rendered.png          → ~/.claude/temp/geo-map-crop/
Phase 2 (sonnet) → color_map.json        → ~/.claude/temp/geo-map-crop/
Phase 3 (sonnet) → legend_filtered.json  → ~/.claude/temp/geo-map-crop/
Phase 4 (sonnet) → <output>.png/.svg     → 用户指定路径
Phase 5 (opus)   → <output>_meta.json    → 与输出文件同目录
                   ↓ 四项 gate 全通过
                   Human Gate（地质师确认）
                   ↓
                   交付
```

**⚠️ 不可跳过的步骤**：
- Phase 1：rendered.png 必须保存，Phase 2 读取它
- Phase 3：legend_filtered.json 必须保存，Phase 4 读取它
- Phase 5：四项 gate 脚本必须全部运行，任一 exit 1 则阻断

---

## 执行完整性自检清单

执行完成后输出自检报告：

```
✅ geo-map-crop 执行完整性自检
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 1 rendered.png:     ✅ 存在 / ❌ 缺失
Phase 2 color_map.json:   ✅ 存在 / ❌ 缺失
Phase 3 legend_filtered:  ✅ N 条 / ❌ 0 条
Phase 4 输出文件:          ✅ X KB / ❌ 过小
Phase 5 gate 全通过:       ✅ PASS / ❌ FAIL
Human Gate 确认:           ✅ 已确认 / ⏳ 待确认
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 10.0 Skill 误用反模式

### S1 — 将非地质图传入本 skill

**错误**：把卫星图、地形图、DEM 渲染图、遥感影像传入 geo-map-crop。
**后果**：无地质图例可识别，legend_filtered.json 为空，gate_legend_count 阻断，输出无意义。
**正确做法**：非地质图裁剪直接用图像编辑工具；地质解译需先用 geological-targeting skill。

### S2 — 跳过 Phase 1 直接传原始 PDF 给 Phase 3

**错误**：不渲染 PDF，直接让 Claude 视觉识别 PDF 中的图例颜色。
**后果**：PDF 颜色与渲染后 PNG 颜色存在色差，CIEDE2000 匹配结果不准确，图例条目错误。
**正确做法**：必须先用 fitz 渲染为 300 DPI PNG，再进行颜色识别。

### S3 — 依赖 context 传递中间产物（违反原则二）

**错误**：Phase 3 识别的 legend_entries 只存在 context 中，Phase 4 直接引用，不落文件。
**后果**：session 中断后无法恢复；多 Agent 模式下 Phase 4 Agent 看不到 Phase 3 的结果。
**正确做法**：legend_filtered.json 必须写入 `~/.claude/temp/geo-map-crop/`，Phase 4 读文件。

### S4 — 跳过 gate 直接交付（违反原则三）

**错误**：输出文件生成后直接告诉用户"已完成"，不运行四项 gate 脚本。
**后果**：可能交付空图例、过小文件、error 状态的低质量结果，地质师引用后发现问题。
**正确做法**：四项 gate 全部 exit 0 后，再触发 Human Gate 确认，最后交付。
