"""danger-detector — blocks destructive Bash commands before execution."""
import sys
import json
import importlib.util
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from packages.core.hook import read_tool_input, write_deny, write_allow, fail_closed
from packages.core.bypass import check_universal_bypass

try:
    _spec = importlib.util.spec_from_file_location(
        "_helpers", Path(__file__).parent / "_helpers.py"
    )
    if _spec is None:
        raise ImportError("_helpers.py not found")
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    BLOCK_PATTERNS = _mod.BLOCK_PATTERNS
    unwrap = _mod.unwrap
    extract_subshells = _mod.extract_subshells
except Exception as e:
    import json as _json
    print(_json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": f"danger-detector failed to load helpers: {e}",
    }}))
    raise SystemExit(0)

def load_allow_patterns(cwd: str) -> list:
    config_path = Path(cwd, ".aiclair.json")
    try:
        text = config_path.read_text()
        return json.loads(text).get("danger_detector", {}).get("allow_patterns", [])
    except FileNotFoundError:
        return []
    except (PermissionError, OSError) as e:
        print(f"[aiclair] cannot read .aiclair.json: {e}", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"[aiclair] malformed .aiclair.json: {e}", file=sys.stderr)
        return []

def detect(command: str, cwd: str) -> tuple:
    # Strip each allow-pattern from the command rather than allowing the whole command.
    # This prevents bypassing detection by prefixing a destructive command with an allowed substring.
    effective = command
    for pattern in load_allow_patterns(cwd):
        effective = effective.replace(pattern, "")
    if not effective.strip():
        return (False, "")
    targets = list(dict.fromkeys([effective, unwrap(effective)] + extract_subshells(effective)))
    # Guard against ReDoS: skip targets that are empty or excessively long
    targets = [t for t in targets if t and len(t) <= 4096]
    for target in targets:
        for bp in BLOCK_PATTERNS:
            if bp["regex"].search(target):
                return (True, bp["message"])
    return (False, "")

@fail_closed
def main():
    data = read_tool_input()
    if not data:
        write_deny("Hook input error — fail closed")
        return
    if check_universal_bypass(data.get("transcript_path", "")):
        write_allow()
        return
    if data.get("tool_name", "") != "Bash":
        write_allow()
        return
    command = data.get("tool_input", {}).get("command", "")
    is_dangerous, reason = detect(command, data.get("cwd", ""))
    if is_dangerous:
        write_deny(reason)
    else:
        write_allow()

if __name__ == "__main__":
    main()
