"""Tests for <hook-name>."""
from conftest import run_script, HOOK_SCRIPT


def test_bypass_asterisk():
    output = run_script(HOOK_SCRIPT, "* just do it")
    assert output["hookSpecificOutput"]["additionalContext"] == "just do it"


def test_bypass_slash_command():
    output = run_script(HOOK_SCRIPT, "/commit")
    assert output["hookSpecificOutput"]["additionalContext"] == "/commit"


def test_evaluation_wrapper():
    output = run_script(HOOK_SCRIPT, "fix the bug")
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "PROMPT EVALUATION" in ctx


def test_null_prompt():
    output = run_script(HOOK_SCRIPT, None)
    assert "hookSpecificOutput" in output


def test_json_schema():
    output = run_script(HOOK_SCRIPT, "test")
    hook_out = output["hookSpecificOutput"]
    assert hook_out["hookEventName"] == "UserPromptSubmit"
    assert isinstance(hook_out["additionalContext"], str)
