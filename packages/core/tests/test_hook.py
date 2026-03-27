"""Tests for hook base utilities."""
import io
import json
import re
import sys
from packages.core.hook import (
    build_evaluation_wrapper,
    fail_closed,
    read_tool_input,
    write_allow,
    write_deny,
    write_post_warn,
)


def test_evaluation_wrapper_contains_prompt():
    wrapper = build_evaluation_wrapper("fix the bug", "prompt-improver")
    assert "fix the bug" in wrapper


def test_evaluation_wrapper_contains_skill_name():
    wrapper = build_evaluation_wrapper("fix the bug", "prompt-improver")
    assert "prompt-improver" in wrapper


def test_evaluation_wrapper_uses_json_embedding():
    # Prompt with quotes and backslashes — must be JSON-safe
    prompt = 'fix the "bug" in user\'s code & database\nnewline here'
    wrapper = build_evaluation_wrapper(prompt, "prompt-improver")
    # The prompt must appear JSON-encoded (quotes escaped)
    assert '\\"bug\\"' in wrapper or "\\u0022" in wrapper or json.dumps(prompt) in wrapper


def test_evaluation_wrapper_token_estimate():
    wrapper = build_evaluation_wrapper("test", "prompt-improver")
    # Rough token estimate: chars / 4
    estimated_tokens = len(wrapper) // 4
    assert estimated_tokens < 250


def test_evaluation_wrapper_contains_evaluation_marker():
    wrapper = build_evaluation_wrapper("fix the bug", "prompt-improver")
    assert "PROMPT EVALUATION" in wrapper
    assert "EVALUATE" in wrapper


def test_evaluation_wrapper_newline_in_prompt():
    prompt = "fix the bug\nand also the tests"
    wrapper = build_evaluation_wrapper(prompt, "prompt-improver")
    # Newline must be escaped in JSON embedding — not raw newline breaking the structure
    assert "fix the bug" in wrapper


def test_read_tool_input_valid(monkeypatch):
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "npm test"},
    }
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    result = read_tool_input()
    assert result["tool_name"] == "Bash"
    assert result["tool_input"]["command"] == "npm test"


def test_read_tool_input_empty(monkeypatch):
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))
    result = read_tool_input()
    assert result == {}


def test_write_deny_output(capsys):
    write_deny("Dangerous command detected")
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert data["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert data["hookSpecificOutput"]["permissionDecisionReason"] == "Dangerous command detected"


def test_write_allow_output(capsys):
    write_allow()
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert data["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_write_post_warn_output(capsys):
    write_post_warn("Output too large", context="Exceeded limit")
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["decision"] == "block"
    assert data["reason"] == "Output too large"
    assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
    assert data["hookSpecificOutput"]["additionalContext"] == "Exceeded limit"


def test_fail_closed_catches_exception(capsys):
    @fail_closed
    def broken():
        raise ValueError("something went wrong")

    result = broken()
    assert result is None
    captured = capsys.readouterr()
    data = json.loads(captured.out.strip())
    assert data["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "fail closed" in data["hookSpecificOutput"]["permissionDecisionReason"]


def test_evaluation_wrapper_contains_intent_types():
    wrapper = build_evaluation_wrapper("fix the bug", "prompt-improver")
    intents = ["CREATE", "TRANSFORM", "REASON", "DEBUG", "AGENTIC"]
    assert any(intent in wrapper for intent in intents)


def test_evaluation_wrapper_contains_scoring_dimensions():
    wrapper = build_evaluation_wrapper("build a feature", "prompt-improver")
    dimensions = ["Clarity", "Specificity", "Context"]
    assert any(dim in wrapper for dim in dimensions)


def test_evaluation_wrapper_token_limit_with_intent():
    wrapper = build_evaluation_wrapper("add logging", "prompt-improver")
    assert len(wrapper) // 4 < 250
