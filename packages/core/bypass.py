"""
Bypass prefix detection for aiclair hooks.

Bypass patterns:
  "* "  — explicit skip (asterisk + space required)
  "/word" — slash command (letter after slash, no dots or slashes in first token)
  "# "  — memorize (hash + space required)
"""
import re


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
