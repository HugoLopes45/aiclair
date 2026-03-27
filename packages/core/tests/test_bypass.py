"""Tests for bypass prefix detection."""
import pytest
from packages.core.bypass import check_bypass, _is_slash_command


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
