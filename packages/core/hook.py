"""
Base hook utilities for aiclair.

Handles stdin/stdout JSON contract for Claude Code UserPromptSubmit hooks.
"""
import functools
import json
import sys


def read_prompt() -> str:
    """Read and parse prompt from stdin JSON. Returns empty string on null/missing."""
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    return data.get("prompt") or ""


def write_output(text: str) -> None:
    """Write hook output to stdout in Claude Code format."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }
    }
    print(json.dumps(output))


def build_evaluation_wrapper(prompt: str, skill_name: str) -> str:
    """
    Build evaluation wrapper for a prompt.
    Uses json.dumps() for safe prompt embedding — handles all special chars.
    Keeps wrapper under 250 tokens.
    """
    embedded = json.dumps(prompt, ensure_ascii=False)
    return f"""PROMPT EVALUATION

Original user request: {embedded}

EVALUATE: Is this prompt clear enough to execute, or does it need enrichment?

PROCEED IMMEDIATELY if:
- Detailed/specific OR you have sufficient context OR can infer intent

ONLY USE SKILL if genuinely vague (e.g., "fix the bug" with no context):
- If vague:
  1. Preface with: "Hey! Prompt Improver flagged your prompt as vague because [specific reason]."
  2. Then use the {skill_name} skill to research and generate clarifying questions
- Check conversation history before invoking the skill.

If clear, proceed. If vague, invoke the skill."""


def read_tool_input() -> dict:
    """Read full stdin JSON for PreToolUse/PostToolUse hooks. Returns {} on any error."""
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def write_deny(reason: str, event_name: str = "PreToolUse") -> None:
    """Print PreToolUse deny JSON to stdout."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))


def write_allow(event_name: str = "PreToolUse") -> None:
    """Print PreToolUse allow JSON to stdout."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "permissionDecision": "allow",
        }
    }
    print(json.dumps(output))


def write_post_warn(reason: str, context: str = "") -> None:
    """Print PostToolUse block JSON to stdout."""
    output = {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": context,
        },
    }
    print(json.dumps(output))


def fail_closed(func):
    """Decorator: on any exception, emit deny and return. Never re-raises."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            write_deny("Internal error - fail closed")
            return None
    return wrapper
