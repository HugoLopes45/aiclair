"""Tests for prompt-improver hook."""
import json
import re
import sys
from pathlib import Path

# Make the local conftest importable regardless of pytest rootdir
sys.path.insert(0, str(Path(__file__).parent))

from conftest import run_script, HOOK_SCRIPT


def test_bypass_asterisk_space():
    output = run_script(HOOK_SCRIPT, "* just do it")
    assert output["hookSpecificOutput"]["additionalContext"] == "just do it"


def test_bypass_slash_command():
    output = run_script(HOOK_SCRIPT, "/commit")
    assert output["hookSpecificOutput"]["additionalContext"] == "/commit"


def test_bypass_hash_space():
    output = run_script(HOOK_SCRIPT, "# remember TypeScript")
    assert output["hookSpecificOutput"]["additionalContext"] == "# remember TypeScript"


def test_bold_markdown_not_bypassed():
    output = run_script(HOOK_SCRIPT, "**bold** fix this")
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "PROMPT EVALUATION" in ctx


def test_file_path_not_bypassed():
    output = run_script(HOOK_SCRIPT, "/Users/hugo/file.txt fix this")
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "PROMPT EVALUATION" in ctx


def test_hashtag_not_bypassed():
    output = run_script(HOOK_SCRIPT, "#trending fix this")
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "PROMPT EVALUATION" in ctx


def test_evaluation_wrapper_structure():
    output = run_script(HOOK_SCRIPT, "fix the bug")
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "PROMPT EVALUATION" in ctx
    assert "EVALUATE" in ctx
    assert "prompt-improver" in ctx


def test_null_prompt_no_crash():
    output = run_script(HOOK_SCRIPT, None)
    assert "hookSpecificOutput" in output


def test_special_characters_json_safe():
    prompt = 'fix the "bug" & handle newline\nin code'
    output = run_script(HOOK_SCRIPT, prompt)
    ctx = output["hookSpecificOutput"]["additionalContext"]
    assert "bug" in ctx
    assert "&" in ctx


def test_token_overhead():
    output = run_script(HOOK_SCRIPT, "test")
    ctx = output["hookSpecificOutput"]["additionalContext"]
    estimated_tokens = len(ctx) // 4
    assert estimated_tokens < 250


def test_json_output_schema():
    output = run_script(HOOK_SCRIPT, "test")
    assert "hookSpecificOutput" in output
    hook_out = output["hookSpecificOutput"]
    assert hook_out["hookEventName"] == "UserPromptSubmit"
    assert isinstance(hook_out["additionalContext"], str)
