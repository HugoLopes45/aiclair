"""secret-guard hook — prevents API keys and secrets from leaking."""
import sys
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from packages.core.hook import (
    read_tool_input, write_deny, write_allow, write_post_allow, write_post_warn, fail_closed
)
from packages.core.bypass import check_universal_bypass

try:
    _spec = importlib.util.spec_from_file_location(
        "_patterns", Path(__file__).parent / "_patterns.py"
    )
    if _spec is None:
        raise ImportError("_patterns.py not found")
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    scan_for_secrets = _mod.scan_for_secrets
    scan_for_exfil = _mod.scan_for_exfil
    is_env_example = _mod.is_env_example
except Exception as e:
    import json as _json
    print(_json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"secret-guard failed to load patterns: {e}",
    }}))
    raise SystemExit(0)

@fail_closed
def main():
    data = read_tool_input()
    if not data:
        write_deny("Hook input error — fail closed")
        return
    event = data.get("hook_event_name", "PreToolUse")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    if check_universal_bypass(data.get("transcript_path", "")):
        write_post_allow() if event == "PostToolUse" else write_allow()
        return
    if event == "PostToolUse":
        tool_response = data.get("tool_response")
        stdout = (tool_response.get("stdout", "") if isinstance(tool_response, dict) else "") or ""
        found, msg = scan_for_secrets(stdout)
        if found:
            write_post_warn(msg, "Secret detected in command output — review before using this value")
        else:
            write_post_allow()
        return
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        found, msg = scan_for_exfil(command)
        if found:
            write_deny(msg)
            return
        found, msg = scan_for_secrets(command)
        if found:
            write_deny(msg)
            return
    elif tool_name in ("Write", "Edit"):
        file_path = tool_input.get("file_path", "")
        if is_env_example(file_path):
            write_allow()
            return
        content = tool_input.get("content", "") or tool_input.get("new_string", "") or ""
        found, msg = scan_for_secrets(content)
        if found:
            write_deny(msg)
            return
    write_allow()

if __name__ == "__main__":
    main()
