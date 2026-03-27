"""Tests for bypass prefix detection."""
import json
import tempfile
from pathlib import Path

import pytest
from packages.core.bypass import check_bypass, _is_slash_command, check_universal_bypass


# --- Helpers ---

def _make_transcript(*entries) -> str:
    """Write JSONL entries to a temp file, return the path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False)
    for entry in entries:
        f.write(json.dumps(entry) + "\n")
    f.close()
    return f.name


def _user_text_entry(text: str) -> dict:
    return {
        "type": "user",
        "message": {
            "role": "user",
            "content": [{"type": "text", "text": text}],
        },
    }


def _user_tool_result_entry() -> dict:
    return {
        "type": "user",
        "message": {
            "role": "user",
            "content": [{"type": "tool_result", "tool_use_id": "abc", "content": "done"}],
        },
    }


# --- Positive bypass cases ---

def test_asterisk_space_bypasses():
    is_bypass, clean = check_bypass("* fix the bug")
    assert is_bypass
    assert clean == "fix the bug"


def test_asterisk_space_strips_prefix():
    _, clean = check_bypass("*   extra spaces  ")
    assert clean == "extra spaces"


def test_slash_command_bypasses():
    is_bypass, clean = check_bypass("/commit")
    assert is_bypass
    assert clean == "/commit"


def test_hash_space_bypasses():
    is_bypass, clean = check_bypass("# remember this")
    assert is_bypass
    assert clean == "# remember this"


# --- Negative bypass cases (must NOT bypass) ---

def test_markdown_bold_does_not_bypass():
    is_bypass, _ = check_bypass("**bold text** fix this")
    assert not is_bypass


def test_file_path_does_not_bypass():
    is_bypass, _ = check_bypass("/Users/hugo/file.txt fix this")
    assert not is_bypass


def test_hashtag_does_not_bypass():
    is_bypass, _ = check_bypass("#hashtag trending")
    assert not is_bypass


def test_asterisk_without_space_does_not_bypass():
    is_bypass, _ = check_bypass("*fix the bug")
    assert not is_bypass


def test_hash_without_space_does_not_bypass():
    is_bypass, _ = check_bypass("#fix the bug")
    assert not is_bypass


def test_shebang_does_not_bypass():
    is_bypass, _ = check_bypass("#!/usr/bin/env python")
    assert not is_bypass


# --- Edge cases ---

def test_null_prompt_does_not_crash():
    is_bypass, clean = check_bypass(None)
    assert not is_bypass
    assert clean == ""


def test_empty_prompt_does_not_bypass():
    is_bypass, _ = check_bypass("")
    assert not is_bypass


def test_slash_command_with_hyphen():
    # /review-pr: first_token = "/review-pr", count("/") == 1, no dot, [1].isalpha() = True
    # Valid slash command — hyphens are allowed after the initial alpha char
    assert _is_slash_command("/review-pr") is True


def test_slash_with_dot_does_not_bypass():
    assert _is_slash_command("/.bashrc") is False


def test_slash_with_multiple_slashes_does_not_bypass():
    assert _is_slash_command("/usr/bin/python") is False


# --- check_universal_bypass tests ---

def test_universal_bypass_with_star_prefix():
    transcript = _make_transcript(_user_text_entry("* fix it"))
    assert check_universal_bypass(transcript) is True


def test_universal_bypass_no_star():
    transcript = _make_transcript(_user_text_entry("fix it"))
    assert check_universal_bypass(transcript) is False


def test_universal_bypass_empty_path():
    assert check_universal_bypass("") is False


def test_universal_bypass_missing_file():
    assert check_universal_bypass("/tmp/does_not_exist_aiclair_xyz.jsonl") is False


def test_universal_bypass_checks_last_message_only():
    # Old message has "* ", new one does not — must return False
    transcript = _make_transcript(
        _user_text_entry("* do something"),
        _user_text_entry("now do something else"),
    )
    assert check_universal_bypass(transcript) is False


def test_universal_bypass_skips_tool_result_entries():
    # Last user entry is tool_result; the entry before is "* text" — must return True
    transcript = _make_transcript(
        _user_text_entry("* fix it"),
        _user_tool_result_entry(),
    )
    assert check_universal_bypass(transcript) is True


def test_universal_bypass_multi_turn_no_stale():
    # Turn 1: "* bypass" + tool_result
    # Turn 2: "normal prompt" + tool_result
    # Last text entry = "normal prompt" (no * ) → must return False
    transcript = _make_transcript(
        _user_text_entry("* do something"),
        _user_tool_result_entry(),
        _user_text_entry("now do something else"),
        _user_tool_result_entry(),
    )
    assert check_universal_bypass(transcript) is False


def test_truncation_guard_exact_8192_file_not_discarded():
    """Transcript exactly 8192 bytes — bypass entry is last line, must be found."""
    import os
    # Build a bypass entry as the last line
    entry = json.dumps(_user_text_entry("* go")) + "\n"
    entry_b = entry.encode("utf-8")
    # Pad preceding content to reach exactly 8192 bytes total
    pad_prefix = b'{"p":"'
    pad_suffix = b'"}\n'
    pad_content = b"x" * (8192 - len(entry_b) - len(pad_prefix) - len(pad_suffix))
    pad_line = pad_prefix + pad_content + pad_suffix

    import tempfile
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.jsonl', delete=False) as f:
        f.write(pad_line)
        f.write(entry_b)
        path = f.name

    assert os.path.getsize(path) == 8192
    # File is exactly 8192 bytes — old code would discard the bypass entry (off-by-one bug),
    # fixed code uses file_size > 8192 so nothing is discarded.
    assert check_universal_bypass(path) is True
