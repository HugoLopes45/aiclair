#!/usr/bin/env python3
"""Claude Code entrypoint for secret-guard hook (PostToolUse)."""
import importlib.util
import os
import sys
from pathlib import Path

plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", str(Path(__file__).parent.parent.parent.parent))
hook_path = Path(plugin_root) / "packages" / "hooks" / "secret-guard" / "hook.py"

try:
    spec = importlib.util.spec_from_file_location("hook", hook_path)
    if spec is None:
        raise ImportError(f"hook not found: {hook_path}")
    hook_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hook_module)
    hook_module.main()
except Exception as e:
    import json
    print(f"[aiclair] secret-guard-post failed to load: {e}", file=sys.stderr)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "permissionDecision": "block", "permissionDecisionReason": "aiclair internal error — fail closed"}}))
    sys.exit(0)
