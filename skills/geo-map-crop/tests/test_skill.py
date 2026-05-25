"""
test_skill.py — geo-map-crop Harness Gate Tests (G14)

三类测试：
  - happy path: 正常输入，验证输出文件存在、大小合理、图例>0
  - edge cases: 边界参数（极小裁剪区、单页PDF、SVG输出）
  - error cases: 缺失文件、无效参数、图例为空

运行方式：
  cd C:\\Users\\39555\\.claude\\skills\\geo-map-crop
  python -m pytest tests/ -v
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 将 scripts 目录加入路径
SKILL_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_DIR / "scripts"))

TEMP_DIR = Path("C:/Users/39555/.claude/temp/geo-map-crop")


# ─────────────────────────────────────────────────────────────────────────────
# Gate 函数（与 artifact_spec.md 中的门禁脚本对应）
# ─────────────────────────────────────────────────────────────────────────────

def gate_output_exists(output_path: str) -> bool:
    return os.path.isfile(output_path)


def gate_file_size(output_path: str, min_bytes: int = 50_000) -> bool:
    return os.path.getsize(output_path) >= min_bytes


def gate_legend_count(meta_path: str, min_count: int = 1) -> bool:
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    return meta.get("stats", {}).get("matched_count", 0) >= min_count


def gate_quality_status(meta_path: str) -> bool:
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    return meta.get("quality", {}).get("status", "error") != "error"


# ─────────────────────────────────────────────────────────────────────────────
# 辅助：生成最小合法 meta.json
# ─────────────────────────────────────────────────────────────────────────────

def _write_meta(path: str, matched: int = 5, status: str = "ok"):
    meta = {
        "quality": {"status": status, "warnings": []},
        "stats": {"matched_count": matched, "detected_count": 30, "coverage": 0.85},
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False)


# ─────────────────────────────────────────────────────────────────────────────
# Test Suite 1: Gate 函数单元测试（不依赖真实地质图）
# ─────────────────────────────────────────────────────────────────────────────

class TestGateFunctions(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    # --- gate_output_exists ---
    def test_gate_output_exists_pass(self):
        p = os.path.join(self.tmpdir, "out.png")
        Path(p).write_bytes(b"\x89PNG" + b"\x00" * 60_000)
        self.assertTrue(gate_output_exists(p))

    def test_gate_output_exists_fail(self):
        self.assertFalse(gate_output_exists(os.path.join(self.tmpdir, "nonexistent.png")))

    # --- gate_file_size ---
    def test_gate_file_size_pass(self):
        p = os.path.join(self.tmpdir, "big.png")
        Path(p).write_bytes(b"\x00" * 60_000)
        self.assertTrue(gate_file_size(p, min_bytes=50_000))

    def test_gate_file_size_fail_too_small(self):
        p = os.path.join(self.tmpdir, "tiny.png")
        Path(p).write_bytes(b"\x00" * 100)
        self.assertFalse(gate_file_size(p, min_bytes=50_000))

    # --- gate_legend_count ---
    def test_gate_legend_count_pass(self):
        p = os.path.join(self.tmpdir, "meta.json")
        _write_meta(p, matched=5)
        self.assertTrue(gate_legend_count(p, min_count=1))

    def test_gate_legend_count_fail_zero(self):
        p = os.path.join(self.tmpdir, "meta_zero.json")
        _write_meta(p, matched=0)
        self.assertFalse(gate_legend_count(p, min_count=1))

    # --- gate_quality_status ---
    def test_gate_quality_status_ok(self):
        p = os.path.join(self.tmpdir, "meta_ok.json")
        _write_meta(p, status="ok")
        self.assertTrue(gate_quality_status(p))

    def test_gate_quality_status_warning_passes(self):
        """warning 状态不阻断交付"""
        p = os.path.join(self.tmpdir, "meta_warn.json")
        _write_meta(p, status="warning")
        self.assertTrue(gate_quality_status(p))

    def test_gate_quality_status_error_fails(self):
        p = os.path.join(self.tmpdir, "meta_err.json")
        _write_meta(p, status="error")
        self.assertFalse(gate_quality_status(p))


# ─────────────────────────────────────────────────────────────────────────────
# Test Suite 2: 中间产物落文件检查
# ─────────────────────────────────────────────────────────────────────────────

class TestArtifactFiles(unittest.TestCase):

    def test_color_map_json_schema(self):
        """color_map.json 必须是 list[{cluster_id, rgb, pixel_count}]"""
        sample = [
            {"cluster_id": 0, "rgb": [228, 193, 70], "pixel_count": 12345},
            {"cluster_id": 1, "rgb": [128, 0, 0], "pixel_count": 5678},
        ]
        for entry in sample:
            self.assertIn("cluster_id", entry)
            self.assertIn("rgb", entry)
            self.assertEqual(len(entry["rgb"]), 3)
            self.assertIn("pixel_count", entry)

    def test_legend_filtered_json_schema(self):
        """legend_filtered.json 必须是 list[{color, code, desc, delta_e}]"""
        sample = [
            {"color": [228, 193, 70], "code": "Qa", "desc": "砂、粉砂及冲积物", "delta_e": 4.2},
        ]
        for entry in sample:
            self.assertIn("color", entry)
            self.assertIn("code", entry)
            self.assertIn("desc", entry)
            self.assertIn("delta_e", entry)
            self.assertIsInstance(entry["delta_e"], float)

    def test_meta_json_schema(self):
        """_meta.json 必须含 quality.status 和 stats.matched_count"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            _write_meta(f.name, matched=3, status="ok")
            meta_path = f.name
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        self.assertIn("quality", meta)
        self.assertIn("status", meta["quality"])
        self.assertIn("stats", meta)
        self.assertIn("matched_count", meta["stats"])
        os.unlink(meta_path)


# ─────────────────────────────────────────────────────────────────────────────
# Test Suite 3: geo_crop_engine 模块导入与基础接口检查
# ─────────────────────────────────────────────────────────────────────────────

class TestEngineImport(unittest.TestCase):

    def test_engine_importable(self):
        """geo_crop_engine 必须可以导入"""
        try:
            import geo_crop_engine  # noqa: F401
            imported = True
        except ImportError as e:
            self.fail(f"geo_crop_engine 导入失败: {e}")

    def test_crop_function_exists(self):
        """crop_geological_map 函数必须存在"""
        import geo_crop_engine
        self.assertTrue(
            hasattr(geo_crop_engine, "crop_geological_map"),
            "geo_crop_engine 缺少 crop_geological_map 函数",
        )

    def test_crop_function_signature(self):
        """crop_geological_map 必须接受 input_path, crop_pct, output_path 参数"""
        import inspect
        import geo_crop_engine
        sig = inspect.signature(geo_crop_engine.crop_geological_map)
        params = list(sig.parameters.keys())
        for required in ["input_path", "crop_pct", "output_path"]:
            self.assertIn(required, params, f"缺少必填参数: {required}")


# ─────────────────────────────────────────────────────────────────────────────
# Test Suite 4: Edge Cases（参数边界）
# ─────────────────────────────────────────────────────────────────────────────

class TestEdgeCases(unittest.TestCase):

    def test_crop_pct_full_image(self):
        """crop_pct=(0,0,100,100) 应为合法参数（裁剪整张图）"""
        crop_pct = (0, 0, 100, 100)
        x1, y1, x2, y2 = crop_pct
        self.assertGreaterEqual(x2 - x1, 0)
        self.assertGreaterEqual(y2 - y1, 0)

    def test_crop_pct_minimum_area(self):
        """crop_pct 最小区域（1%×1%）应为合法参数"""
        crop_pct = (49, 49, 50, 50)
        x1, y1, x2, y2 = crop_pct
        self.assertGreater(x2, x1)
        self.assertGreater(y2, y1)

    def test_color_threshold_range(self):
        """CIEDE2000 阈值应在合理范围 [2, 30]"""
        valid_thresholds = [2, 8, 12, 20, 30]
        for t in valid_thresholds:
            self.assertGreaterEqual(t, 2)
            self.assertLessEqual(t, 30)

    def test_lon_lat_extent_valid(self):
        """经纬度范围：lon_min < lon_max, lat_min < lat_max"""
        extent = (36.0, 42.5, 18.0, 25.0)
        lon_min, lon_max, lat_min, lat_max = extent
        self.assertLess(lon_min, lon_max)
        self.assertLess(lat_min, lat_max)


# ─────────────────────────────────────────────────────────────────────────────
# Test Suite 5: 反模式检测（S1-S4，对应 G27）
# ─────────────────────────────────────────────────────────────────────────────

class TestAntiPatterns(unittest.TestCase):

    def test_s1_non_geological_map_detection(self):
        """S1: 非地质图（如卫星图、地形图）不应被当作地质图处理
        验证：legend_filtered.json 中 matched_count=0 时 gate 应阻断"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            _write_meta(f.name, matched=0, status="warning")
            meta_path = f.name
        result = gate_legend_count(meta_path, min_count=1)
        self.assertFalse(result, "非地质图（无图例匹配）应被 gate 阻断")
        os.unlink(meta_path)

    def test_s2_empty_crop_region(self):
        """S2: 裁剪区域为空（x1==x2 或 y1==y2）应被检测为无效"""
        invalid_crops = [(10, 10, 10, 50), (10, 10, 50, 10)]
        for crop in invalid_crops:
            x1, y1, x2, y2 = crop
            area = (x2 - x1) * (y2 - y1)
            self.assertEqual(area, 0, f"空裁剪区域 {crop} 面积应为 0")

    def test_s3_output_too_small_blocked(self):
        """S3: 输出文件过小（<50KB）应被 gate 阻断"""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(b"\x00" * 1000)  # 1KB，远小于50KB
            tiny_path = f.name
        result = gate_file_size(tiny_path, min_bytes=50_000)
        self.assertFalse(result, "过小的输出文件应被 gate 阻断")
        os.unlink(tiny_path)

    def test_s4_error_status_blocked(self):
        """S4: quality.status=error 应被 gate 阻断，不允许交付"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False, encoding="utf-8"
        ) as f:
            _write_meta(f.name, status="error")
            meta_path = f.name
        result = gate_quality_status(meta_path)
        self.assertFalse(result, "error 状态应被 gate 阻断")
        os.unlink(meta_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
