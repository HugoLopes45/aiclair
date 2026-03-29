#!/usr/bin/env python3
"""Claude Code entrypoint for danger-detector hook."""
import importlib.util
import os
import sys
from pathlib import Path

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).parent.parent.parent.parent))
hook_path = Path(plugin_root) / "packages" / "hooks" / "danger-detector" / "hook.py"

try:
    spec = importlib.util.spec_from_file_location("hook", hook_path)
    if spec is None:
        raise ImportError(f"hook not found: {hook_path}")
    hook_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook_module)
    hook_module.main()
except Exception as e:
    import json
    print(f"[aiclair] danger-detector failed to load: {e}", file=sys.stderr)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "aiclair internal error — fail closed"}}))
    sys.exit(0)
