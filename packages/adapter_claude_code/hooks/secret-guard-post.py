#!/usr/bin/env python3
"""Claude Code entrypoint for secret-guard hook (PostToolUse)."""
import importlib.util
import os
import sys
from pathlib import Path

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).parent.parent.parent.parent))
hook_path = Path(plugin_root) / "packages" / "hooks" / "secret-guard" / "hook.py"

spec = importlib.util.spec_from_file_location("hook", hook_path)
hook_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook_module)

hook_module.main()
