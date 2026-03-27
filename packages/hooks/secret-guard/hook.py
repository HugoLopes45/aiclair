"""secret-guard hook — prevents API keys and secrets from leaking."""
import sys
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.core.hook import (
    read_tool_input, write_deny, write_allow, write_post_warn, fail_closed
)
from packages.core.bypass import check_universal_bypass

# Load sibling _patterns module via importlib to stay stdlib-only in hook.py
_spec = importlib.util.spec_from_file_location(
    "_patterns", Path(__file__).parent / "_patterns.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
scan_for_secrets = _mod.scan_for_secrets
scan_for_exfil = _mod.scan_for_exfil
is_env_example = _mod.is_env_example


@fail_closed
def main():
    data = read_tool_input()
    event = data.get("hook_event_name", "PreToolUse")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    transcript_path = data.get("transcript_path", "")

    # Universal bypass gates ALL events
    if check_universal_bypass(transcript_path):
        write_allow(event)
        return

    if event == "PostToolUse":
        stdout = data.get("tool_response", {}).get("stdout", "") or ""
        found, msg = scan_for_secrets(stdout)
        if found:
            write_post_warn(msg, "Secret detected in command output — review before using this value")
        else:
            write_allow("PostToolUse")
        return

    # PreToolUse logic follows...

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
