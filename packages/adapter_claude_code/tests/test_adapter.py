"""Tests for Claude Code adapter."""
import json
import re
import sys
from pathlib import Path

# Make the local conftest importable regardless of pytest rootdir
sys.path.insert(0, str(Path(__file__).parent))

from conftest import run_script, ENTRYPOINT, ADAPTER_DIR


PLUGIN_JSON = ADAPTER_DIR / "plugin.json"
HOOKS_JSON = ADAPTER_DIR / "hooks.json"
SKILLS_DIR = ADAPTER_DIR / "skills" / "prompt-improver"


def test_plugin_json_exists():
    assert PLUGIN_JSON.exists()


def test_plugin_json_has_skills():
    config = json.loads(PLUGIN_JSON.read_text())
    assert "skills" in config
    assert isinstance(config["skills"], list)
    assert len(config["skills"]) > 0


def test_plugin_json_no_hooks_field():
    config = json.loads(PLUGIN_JSON.read_text())
    assert "hooks" not in config


def test_plugin_json_version_is_semver():
    config = json.loads(PLUGIN_JSON.read_text())
    assert re.match(r"^\d+\.\d+\.\d+$", config["version"])


def test_hooks_json_exists():
    assert HOOKS_JSON.exists()


def test_hooks_json_structure():
    config = json.loads(HOOKS_JSON.read_text())
    assert "hooks" in config
    assert "UserPromptSubmit" in config["hooks"]


def test_skill_files_present():
    assert (SKILLS_DIR / "SKILL.md").exists()
    assert (SKILLS_DIR / "references").is_dir()


def test_entrypoint_invocable():
    output = run_script(ENTRYPOINT, "fix the bug")
    assert "hookSpecificOutput" in output
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "PROMPT EVALUATION" in ctx


def test_entrypoint_bypass():
    output = run_script(ENTRYPOINT, "* just do it")
    assert output["hookSpecificOutput"]["additionalContext"] == "just do it"


def test_entrypoint_null_prompt():
    output = run_script(ENTRYPOINT, None)
    assert "hookSpecificOutput" in output


def test_danger_detector_entrypoint_exists():
    assert (ADAPTER_DIR / "hooks" / "danger-detector.py").exists()


def test_secret_guard_pre_entrypoint_exists():
    assert (ADAPTER_DIR / "hooks" / "secret-guard-pre.py").exists()


def test_secret_guard_post_entrypoint_exists():
    assert (ADAPTER_DIR / "hooks" / "secret-guard-post.py").exists()


def test_hooks_json_has_pretooluse():
    hooks_json = json.loads((ADAPTER_DIR / "hooks.json").read_text())
    assert "PreToolUse" in hooks_json["hooks"]


def test_hooks_json_has_posttooluse():
    hooks_json = json.loads((ADAPTER_DIR / "hooks.json").read_text())
    assert "PostToolUse" in hooks_json["hooks"]


def test_hooks_json_danger_detector_matcher():
    hooks_json = json.loads((ADAPTER_DIR / "hooks.json").read_text())
    pre_hooks = hooks_json["hooks"]["PreToolUse"]
    matchers = [h.get("matcher", "") for h in pre_hooks]
    assert "Bash" in matchers


def test_hooks_json_secret_guard_matcher():
    hooks_json = json.loads((ADAPTER_DIR / "hooks.json").read_text())
    pre_hooks = hooks_json["hooks"]["PreToolUse"]
    matchers = [h.get("matcher", "") for h in pre_hooks]
    assert any("Write" in m and "Edit" in m for m in matchers)


def test_danger_detector_end_to_end():
    """Entrypoint subprocess call with destructive command -> deny."""
    import subprocess, sys, json as _json
    stdin_data = _json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "rm -rf /"},
        "cwd": "/tmp",
        "session_id": "test",
        "transcript_path": ""
    })
    result = subprocess.run(
        [sys.executable, str(ADAPTER_DIR / "hooks" / "danger-detector.py")],
        input=stdin_data, capture_output=True, text=True
    )
    output = _json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_secret_guard_end_to_end():
    """Entrypoint subprocess call with AWS key in Write -> deny."""
    import subprocess, sys, json as _json
    stdin_data = _json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "config.py", "content": "key = 'AKIAIOSFODNN7EXAMPLE'"},
        "cwd": "/tmp",
        "session_id": "test",
        "transcript_path": ""
    })
    result = subprocess.run(
        [sys.executable, str(ADAPTER_DIR / "hooks" / "secret-guard-pre.py")],
        input=stdin_data, capture_output=True, text=True
    )
    output = _json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


# C1–C4: spec=None dereference — adapters must fail-closed when hook path is invalid


def _run_adapter_with_bad_root(hook_filename: str, stdin_data: str) -> "subprocess.CompletedProcess":
    import subprocess, sys
    return subprocess.run(
        [sys.executable, str(ADAPTER_DIR / "hooks" / hook_filename)],
        input=stdin_data,
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "CLAUDE_PLUGIN_ROOT": "/nonexistent/path/that/does/not/exist"},
    )


def test_fix_c1_improve_prompt_bad_root_emits_valid_json():
    """C1: improve-prompt.py must emit valid JSON (not crash) when hook path is invalid."""
    import json as _json
    result = _run_adapter_with_bad_root("improve-prompt.py", _json.dumps({"prompt": "hello"}))
    assert result.stdout.strip(), "expected JSON output, got empty stdout (crash)"
    output = _json.loads(result.stdout)
    assert "hookSpecificOutput" in output


def test_fix_c2_danger_detector_bad_root_denies():
    """C2: danger-detector.py must deny (not fail open) when hook path is invalid."""
    import json as _json
    stdin_data = _json.dumps({
        "hook_event_name": "PreToolUse", "tool_name": "Bash",
        "tool_input": {"command": "echo hi"}, "cwd": "/tmp",
        "session_id": "test", "transcript_path": ""
    })
    result = _run_adapter_with_bad_root("danger-detector.py", stdin_data)
    assert result.stdout.strip(), "expected JSON output, got empty stdout (crash)"
    output = _json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_fix_c3_secret_guard_pre_bad_root_denies():
    """C3: secret-guard-pre.py must deny when hook path is invalid."""
    import json as _json
    stdin_data = _json.dumps({
        "hook_event_name": "PreToolUse", "tool_name": "Write",
        "tool_input": {"file_path": "x.py", "content": "x=1"}, "cwd": "/tmp",
        "session_id": "test", "transcript_path": ""
    })
    result = _run_adapter_with_bad_root("secret-guard-pre.py", stdin_data)
    assert result.stdout.strip(), "expected JSON output, got empty stdout (crash)"
    output = _json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_fix_c4_secret_guard_post_bad_root_denies():
    """C4: secret-guard-post.py must deny when hook path is invalid."""
    import json as _json
    stdin_data = _json.dumps({
        "hook_event_name": "PostToolUse", "tool_name": "Bash",
        "tool_input": {}, "tool_response": {"stdout": ""},
        "cwd": "/tmp", "session_id": "test", "transcript_path": ""
    })
    result = _run_adapter_with_bad_root("secret-guard-post.py", stdin_data)
    assert result.stdout.strip(), "expected JSON output, got empty stdout (crash)"
    output = _json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] in ("deny", "block")
