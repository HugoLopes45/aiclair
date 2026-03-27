"""
Base hook utilities for aiclair.

Handles stdin/stdout JSON contract for Claude Code UserPromptSubmit hooks.
"""
import functools
import json
import sys
import traceback


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

Request: {embedded}

EVALUATE: Score Clarity/Specificity/Context (1-10). Classify intent: CREATE|TRANSFORM|REASON|DEBUG|AGENTIC.

PROCEED if the prompt is specific enough to act on without ambiguity.

INVOKE {skill_name} skill only if genuinely vague:
1. State: "Prompt Improver flagged this as vague: [reason]."
2. Use skill to research, ask 1-6 targeted questions, suggest rewritten prompt.

Check conversation history before invoking."""


def read_tool_input() -> dict:
    """Read full stdin JSON for PreToolUse/PostToolUse hooks. Returns {} on any error."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        print(f"[aiclair] read_tool_input: malformed JSON on stdin: {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"[aiclair] read_tool_input: unexpected stdin error: {e}", file=sys.stderr)
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


def write_post_allow() -> None:
    """Print PostToolUse allow JSON to stdout."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "permissionDecision": "allow",
        }
    }
    print(json.dumps(output))


def write_post_warn(reason: str, context: str = "") -> None:
    """Print PostToolUse block JSON to stdout."""
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "permissionDecision": "block",
            "permissionDecisionReason": reason,
            "additionalContext": context,
        },
    }
    print(json.dumps(output))


def fail_closed(func):
    """Decorator: on any exception, emit deny and return. Never re-raises.

    Note: always emits hookEventName='PreToolUse' regardless of actual event.
    This is a known limitation — wrong event name in output is a minor schema
    issue but the deny still fires correctly.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"[aiclair] {func.__name__} crashed: {type(e).__name__}: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            write_deny("Internal error - fail closed")
            return None
    return wrapper
