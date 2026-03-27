#!/usr/bin/env python3
"""
validate-hook.py — Validates an aiclair hook directory.

Usage: python3 scripts/validate-hook.py packages/hooks/my-hook/

Exit 0 = valid, Exit 1 = invalid with error messages.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = ["hook.py", "metadata.json"]
REQUIRED_METADATA_FIELDS = ["name", "version", "description", "author", "events", "agents"]
MAX_HOOK_LINES = 80
MAX_SKILL_LINES = 100
MAX_REFERENCE_LINES = 300
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
STDLIB_ONLY_PATTERN = re.compile(r"^import (\w+)|^from (\w+)", re.MULTILINE)
ALLOWED_MODULES = {
    "json", "sys", "os", "re", "pathlib", "subprocess", "importlib",
    "functools", "itertools", "collections", "typing", "abc", "io",
    "hashlib", "base64", "urllib", "http", "email", "html", "xml",
    "math", "random", "time", "datetime", "calendar", "locale",
    "string", "textwrap", "difflib", "enum", "dataclasses",
    "packages",  # aiclair internal
    "__future__",
}

errors = []


def error(msg):
    errors.append(f"  ✗ {msg}")


def check(condition, msg):
    if not condition:
        error(msg)
    return condition


def validate(hook_dir: Path):
    if not hook_dir.exists():
        print(f"Error: directory not found: {hook_dir}")
        sys.exit(1)

    print(f"Validating: {hook_dir}")

    # Required files
    for fname in REQUIRED_FILES:
        check((hook_dir / fname).exists(), f"Missing required file: {fname}")

    # hook.py line count
    hook_py = hook_dir / "hook.py"
    if hook_py.exists():
        lines = hook_py.read_text().splitlines()
        check(
            len(lines) <= MAX_HOOK_LINES,
            f"hook.py is {len(lines)} lines (max {MAX_HOOK_LINES})",
        )
        # Check stdlib only
        content = hook_py.read_text()
        for match in STDLIB_ONLY_PATTERN.finditer(content):
            module = match.group(1) or match.group(2)
            if module and module not in ALLOWED_MODULES:
                error(f"hook.py imports non-stdlib module: {module}")

    # metadata.json validation
    metadata_path = hook_dir / "metadata.json"
    if metadata_path.exists():
        try:
            metadata = json.loads(metadata_path.read_text())
            for field in REQUIRED_METADATA_FIELDS:
                check(field in metadata, f"metadata.json missing field: {field}")
            if "version" in metadata:
                check(
                    bool(SEMVER_PATTERN.match(metadata["version"])),
                    f"metadata.json version is not semver: {metadata.get('version')}",
                )
        except json.JSONDecodeError as e:
            error(f"metadata.json is invalid JSON: {e}")

    # SKILL.md optional but size-limited if present
    skill_md = hook_dir / "SKILL.md"
    if skill_md.exists():
        lines = skill_md.read_text().splitlines()
        check(
            len(lines) <= MAX_SKILL_LINES,
            f"SKILL.md is {len(lines)} lines (max {MAX_SKILL_LINES})",
        )

    # References optional but size-limited if present
    references_dir = hook_dir / "references"
    if references_dir.exists():
        for ref_file in references_dir.glob("*.md"):
            lines = ref_file.read_text().splitlines()
            check(
                len(lines) <= MAX_REFERENCE_LINES,
                f"{ref_file.name} is {len(lines)} lines (max {MAX_REFERENCE_LINES})",
            )

    # Tests must exist
    tests_dir = hook_dir / "tests"
    check(tests_dir.exists(), "Missing tests/ directory")
    if tests_dir.exists():
        test_files = list(tests_dir.glob("test_*.py"))
        check(len(test_files) > 0, "No test files found in tests/")

    # Report
    if errors:
        print(f"\nFAILED — {len(errors)} error(s):")
        for e in errors:
            print(e)
        sys.exit(1)
    else:
        print(f"  PASSED — all checks OK")
        sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate-hook.py <hook-directory>")
        sys.exit(1)
    validate(Path(sys.argv[1]))
