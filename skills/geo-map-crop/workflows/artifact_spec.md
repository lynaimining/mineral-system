# geo-map-crop — Artifact Specification (Harness)

## Inputs

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `input_path` | file path | ✅ | 原始地质图（PDF / PNG / JPG / TIFF） |
| `crop_pct` | tuple (x1,y1,x2,y2) | ✅ | 裁剪区域百分比坐标，(0,0)=左上，(100,100)=右下 |
| `output_path` | file path | ✅ | 输出文件路径（.png 或 .svg） |
| `map_frame` | tuple (x1,y1,x2,y2) | ⬜ | 主地图边界像素坐标（不传则自动检测） |
| `legend_swatch_x` | tuple (x1,x2) | ⬜ | 图例色块列像素范围 |
| `legend_y_range` | tuple (y1,y2) | ⬜ | 图例垂直像素范围 |
| `legend_entries` | list[dict] | ⬜ | Pro模式：手动提供图例条目（含color/code/desc） |
| `lon_lat_extent` | tuple (lon_min,lon_max,lat_min,lat_max) | ⬜ | Pro模式：经纬度范围（十进制度） |
| `color_threshold` | float | ⬜ | CIEDE2000 色差阈值，默认 12 |
| `n_clusters` | int | ⬜ | K-Means 聚类数，默认 30 |
| `page_num` | int | ⬜ | PDF 页码（0-indexed），默认 0 |
| `output_format` | str | ⬜ | 'png' 或 'svg'，默认 'png' |
| `quantize` | bool | ⬜ | 是否颜色量化，默认 True |
| `map_scale` | float | ⬜ | 地图放大倍数，默认 1.8 |
| `dpi` | int | ⬜ | 渲染分辨率，默认 300 |

---

## 中间产物（必须落文件，不得活在 context）

| 文件名 | 保存路径 | 内容 | 生成时机 |
|--------|----------|------|----------|
| `rendered.png` | `~/.claude/temp/geo-map-crop/` | PDF 渲染结果（300 DPI） | Phase 1 完成后 |
| `color_map.json` | `~/.claude/temp/geo-map-crop/` | 颜色聚类结果：`[{"cluster_id": 0, "rgb": [228,193,70], "pixel_count": 12345}]` | Phase 3 完成后 |
| `legend_filtered.json` | `~/.claude/temp/geo-map-crop/` | 匹配到的图例条目：`[{"color": [228,193,70], "code": "Qa", "desc": "砂、粉砂及冲积物", "delta_e": 4.2}]` | Phase 3 完成后 |
| `<output_name>_meta.json` | 与输出文件同目录 | 质量报告（status/warnings/stats） | Phase 5 完成后 |

**规则**：下一阶段必须读文件，不得依赖 context 记忆上一阶段结果。

---

## Outputs

| 文件 | 格式 | 质量要求 |
|------|------|----------|
| 裁剪地质图 | PNG（主输出） | 文件大小 > 50 KB；宽度 ≥ 800px |
| 裁剪地质图（矢量） | SVG（可选） | 文件大小 > 10 KB；含 `<image>` 和 `<rect>` 元素 |
| 质量报告 | `_meta.json` | status 字段存在；warnings 为 list |

---

## 质量门禁（Gate Scripts）

> 所有门禁必须是确定性脚本，exit 1 则阻断交付，不依赖 LLM 自判。

### Gate 1：输出文件存在性检查

```bash
# gate_output_exists.sh
OUTPUT_PATH="$1"
if [ ! -f "$OUTPUT_PATH" ]; then
    echo "GATE FAIL: 输出文件不存在: $OUTPUT_PATH"
    exit 1
fi
echo "GATE PASS: 输出文件存在"
```

### Gate 2：文件大小检查

```python
# gate_file_size.py
import sys, os
path = sys.argv[1]
size = os.path.getsize(path)
if size < 50_000:  # 50 KB
    print(f"GATE FAIL: 文件过小 ({size} bytes)，可能裁剪失败或图例为空")
    sys.exit(1)
print(f"GATE PASS: 文件大小 {size/1024:.1f} KB")
```

### Gate 3：图例条目数检查

```python
# gate_legend_count.py
import sys, json
meta_path = sys.argv[1]
with open(meta_path, encoding='utf-8') as f:
    meta = json.load(f)
matched = meta.get('stats', {}).get('matched_count', 0)
if matched == 0:
    print(f"GATE FAIL: 图例匹配数为 0，裁剪区可能无有效地质单元")
    sys.exit(1)
print(f"GATE PASS: 图例匹配 {matched} 个条目")
```

### Gate 4：质量状态检查

```python
# gate_quality_status.py
import sys, json
meta_path = sys.argv[1]
with open(meta_path, encoding='utf-8') as f:
    meta = json.load(f)
status = meta.get('quality', {}).get('status', 'unknown')
if status == 'error':
    warnings = meta.get('quality', {}).get('warnings', [])
    print(f"GATE FAIL: 质量状态 error，warnings: {warnings}")
    sys.exit(1)
print(f"GATE PASS: 质量状态 {status}")
```

### 完整门禁执行顺序

```bash
python gate_file_size.py "$OUTPUT_PATH"       || exit 1
python gate_legend_count.py "$META_PATH"      || exit 1
python gate_quality_status.py "$META_PATH"    || exit 1
echo "ALL GATES PASSED — 可以交付"
```

---

## 模型分级

| 阶段 | 任务 | 推荐模型 |
|------|------|----------|
| Phase 1 | PDF 渲染、格式判断 | haiku |
| Phase 2 | 地图边界识别、坐标读取 | sonnet |
| Phase 3 | 图例文字视觉识别、中文图例编写 | sonnet |
| Phase 4 | 参数调优决策 | sonnet |
| Phase 5 | 质量审查、交付确认 | opus（human_gate） |

目标端到端成本：单次裁剪 < $0.5

---

## Human Gate

```yaml
human_gate_required: true
gate_trigger: "图例筛选结果 + 裁剪范围确认"
gate_owner: "地质师（邹心宇 / 王选策）"
gate_description: >
  裁剪范围和图例筛选结果需要地质师目视确认，
  确保裁剪区域正确、图例条目无遗漏或误匹配，
  再进行最终输出和报告引用。
```
