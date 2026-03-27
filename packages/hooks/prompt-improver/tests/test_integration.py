"""Integration tests for prompt-improver."""
import json
import re
import sys
from pathlib import Path

# Make the local conftest importable regardless of pytest rootdir
sys.path.insert(0, str(Path(__file__).parent))

from conftest import run_script, HOOK_SCRIPT

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
METADATA_JSON = Path(__file__).parent.parent / "metadata.json"


def test_metadata_exists():
    assert METADATA_JSON.exists()


def test_metadata_valid_json():
    data = json.loads(METADATA_JSON.read_text())
    assert "name" in data
    assert "version" in data
    assert "events" in data
    assert isinstance(data["events"], list)


def test_metadata_version_is_semver():
    data = json.loads(METADATA_JSON.read_text())
    assert re.match(r"^\d+\.\d+\.\d+$", data["version"])


def test_bypass_flow():
    for prompt, expected in [
        ("* just do it", "just do it"),
        ("/commit", "/commit"),
        ("# note", "# note"),
    ]:
        output = run_script(HOOK_SCRIPT, prompt)
        assert output["hookSpecificOutput"]["additionalContext"] == expected


def test_evaluation_flow():
    for prompt in ["fix the bug", "add tests", "refactor code"]:
        output = run_script(HOOK_SCRIPT, prompt)
        ctx = output["hookSpecificOutput"]["additionalContext"]
        assert "EVALUATE" in ctx
        assert prompt in ctx


def test_hook_output_consistent_structure():
    for prompt in ["fix the bug", "* bypass", "/commit"]:
        output = run_script(HOOK_SCRIPT, prompt)
        assert "hookSpecificOutput" in output
        assert "hookEventName" in output["hookSpecificOutput"]
        assert "additionalContext" in output["hookSpecificOutput"]
