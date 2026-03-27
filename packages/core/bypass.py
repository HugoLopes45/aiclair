"""
Bypass prefix detection for aiclair hooks.

Bypass patterns:
  "* "  — explicit skip (asterisk + space required)
  "/word" — slash command (letter after slash, no dots or slashes in first token)
  "# "  — memorize (hash + space required)

Universal bypass (transcript-based):
  check_universal_bypass(transcript_path) — True if the last user text message
  in the transcript starts with "* " (after strip).
"""
import json
import re
from pathlib import Path


def check_bypass(prompt: str):
    """
    Check if prompt matches a bypass pattern.

    Returns (is_bypass, clean_prompt) where clean_prompt is the
    prompt with the bypass prefix stripped (for "* " only).
    """
    if not isinstance(prompt, str):
        prompt = ""

    if prompt.startswith("* "):
        return True, prompt[2:].strip()

    if _is_slash_command(prompt):
        return True, prompt

    if prompt.startswith("# "):
        return True, prompt

    return False, prompt


def _is_slash_command(prompt: str) -> bool:
    """
    True only for slash commands like /commit, /review-pr.
    False for file paths like /Users/foo/bar.txt.
    """
    if not prompt.startswith("/") or len(prompt) < 2:
        return False
    first_token = prompt.split()[0] if prompt.strip() else ""
    return (
        first_token.startswith("/")
        and len(first_token) > 1
        and first_token[1].isalpha()
        and first_token.count("/") == 1
        and "." not in first_token
    )


def check_universal_bypass(transcript_path: str) -> bool:
    """Return True if the last user text message in the transcript starts with '* '.

    Reads the last 8KB of the JSONL transcript, iterates lines in reverse to
    find the last entry where role=user and content[0].type == "text", then
    checks if that text starts with "* " (after strip).

    Returns False on any error, empty path, or missing file (fail-safe).
    """
    # Every user turn starts with a text message before any tool_results.
    # The last text entry is therefore always from the current turn when PreToolUse fires.
    # No stale-bypass risk from previous turns.
    if not transcript_path:
        return False
    try:
        path = Path(transcript_path)
        if not path.exists():
            return False
        raw = path.read_bytes()[-8192:]
        lines = raw.decode("utf-8", errors="replace").splitlines()
        for line in reversed(lines):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            # Real transcript format: {"type": "user", "message": {"role": "user", "content": [...]}}
            message = entry.get("message", {})
            if message.get("role") != "user":
                continue
            content = message.get("content", [])
            if not content or not isinstance(content, list):
                continue
            first = content[0]
            if not isinstance(first, dict) or first.get("type") != "text":
                continue
            text = first.get("text", "")
            return text.strip().startswith("* ")
    except Exception:
        return False
    return False
