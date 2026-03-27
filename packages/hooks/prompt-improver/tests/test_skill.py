"""Tests for SKILL.md and reference files structure."""
import re
from pathlib import Path

HOOK_DIR = Path(__file__).parent.parent
# SKILL.md lives in the adapter package; the hooks copy was an orphan and has been removed.
_PROJECT_ROOT = Path(__file__).parents[4]
SKILL_MD = _PROJECT_ROOT / "packages" / "adapter_claude_code" / "skills" / "prompt-improver" / "SKILL.md"
REFERENCES_DIR = SKILL_MD.parent / "references"


def test_skill_md_exists():
    assert SKILL_MD.exists()


def test_skill_md_has_frontmatter():
    content = SKILL_MD.read_text()
    assert content.startswith("---\n")
    assert "name: prompt-improver" in content


def test_skill_md_under_100_lines():
    lines = SKILL_MD.read_text().splitlines()
    assert len(lines) < 100, f"SKILL.md is {len(lines)} lines (max 100)"


def test_skill_md_has_phases():
    content = SKILL_MD.read_text()
    assert "Phase 1" in content
    assert "Phase 2" in content
    assert "Phase 3" in content


def test_skill_md_no_absolute_never():
    content = SKILL_MD.read_text()
    assert "NEVER skip research" not in content


def test_references_exist():
    assert (REFERENCES_DIR / "question-patterns.md").exists()
    assert (REFERENCES_DIR / "research-strategies.md").exists()
    assert (REFERENCES_DIR / "examples.md").exists()


def test_references_under_300_lines():
    for ref_file in REFERENCES_DIR.glob("*.md"):
        lines = ref_file.read_text().splitlines()
        assert len(lines) < 300, f"{ref_file.name} is {len(lines)} lines (max 300)"
