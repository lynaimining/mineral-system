"""tests/test_skill.py — gold-ore skill quality gate (G14)"""
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
SKILL_MD = SKILL_ROOT / "SKILL.md"

REQUIRED_SECTIONS = [
    "Step 0",
    "反模式",
    "置信度",
    "知识库索引",
    "背景与定位",
]

REQUIRED_FILES = [
    "SKILL.md",
    "knowledge/deposit_types.md",
    "knowledge/grade_tonnage.md",
    "knowledge/global_belts.md",
    "workflows/quality_review.md",
]


def test_skill_md_exists():
    assert SKILL_MD.exists(), "SKILL.md not found"


def test_no_encoding_errors():
    raw = SKILL_MD.read_bytes()
    assert b"\xef\xbf\xbd" not in raw, "SKILL.md contains Unicode replacement chars (\uFFFD)"


def test_required_sections_present():
    text = SKILL_MD.read_text(encoding="utf-8")
    for section in REQUIRED_SECTIONS:
        assert section in text, "Missing required section: " + section


def test_thesis_section_present():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "背景与定位" in text, "Missing 背景与定位 (Thesis) section — G24 violation"


def test_required_files_exist():
    for rel in REQUIRED_FILES:
        assert (SKILL_ROOT / rel).exists(), "Missing required file: " + rel


def test_validate_script_passes():
    validate = SKILL_ROOT / "scripts" / "validate.py"
    if not validate.exists():
        return  # skip if no validate script
    result = subprocess.run(
        [sys.executable, str(validate), "--check-skill"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "validate.py failed: " + result.stdout + result.stderr


def test_anti_patterns_present():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "反模式" in text, "Missing anti-patterns section — G27 violation"


def test_skill_misuse_anti_patterns_present():
    text = SKILL_MD.read_text(encoding="utf-8")
    assert "Skill 误用反模式" in text or "S1" in text, "Missing skill-level misuse anti-patterns — G27 violation"


def test_frontmatter_has_thesis():
    """G24: frontmatter description should be <=5 lines (compressed thesis, not 25-line keyword list)"""
    text = SKILL_MD.read_text(encoding="utf-8")
    lines = text.split('\n')
    in_desc = False
    desc_lines = 0
    for line in lines:
        if line.strip().startswith("description:"):
            in_desc = True
            continue
        if in_desc:
            if line.startswith("  ") or line.startswith('\t'):
                desc_lines += 1
            else:
                break
    assert desc_lines <= 5, "Frontmatter description too long (" + str(desc_lines) + " lines) — G24 violation, compress to <=5 lines"
