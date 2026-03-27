"""
danger-detector — blocks destructive Bash commands before execution.

Supports per-project allow lists via .aiclair.json.
"""
import sys
import json
import re
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from packages.core.hook import read_tool_input, write_deny, write_allow, fail_closed
from packages.core.bypass import check_universal_bypass

BLOCK_PATTERNS = [
    {"id": "rm-recursive",   "regex": re.compile(r'\brm\s+-[^\s]*r[^\s]*\s'), "message": "Recursive file deletion blocked"},
    {"id": "drop-database",  "regex": re.compile(r'\b(DROP|TRUNCATE)\s+(TABLE|DATABASE|SCHEMA)\b', re.IGNORECASE), "message": "Destructive SQL operation blocked"},
    {"id": "force-push",     "regex": re.compile(r'\bgit\s+push\b.*(-f\b|--force\b)'), "message": "Force push blocked"},
    {"id": "kill-all",       "regex": re.compile(r'\b(killall\s+-9|kill\s+-9\s+-1|pkill\s+-9)\b'), "message": "Kill-all process signal blocked"},
    {"id": "shutdown",       "regex": re.compile(r'\b(shutdown|reboot|halt|poweroff)\b'), "message": "System shutdown command blocked"},
    {"id": "iptables-flush", "regex": re.compile(r'\biptables\s+-F\b'), "message": "Firewall flush blocked"},
    {"id": "reverse-shell-tcp",  "regex": re.compile(r'bash\s+-i\s+>&?\s*/dev/tcp/'), "message": "Reverse shell (TCP) blocked"},
    {"id": "reverse-shell-nc",   "regex": re.compile(r'\bnc\b.*-[ec]\s+/bin/(bash|sh)\b'), "message": "Reverse shell (netcat) blocked"},
    {"id": "fork-bomb",          "regex": re.compile(r':\(\)\s*\{.*:\s*\|.*:'), "message": "Fork bomb blocked"},
    {"id": "anti-forensics",     "regex": re.compile(r'\b(history\s+-c|unset\s+HISTFILE|shred\s+-u)\b'), "message": "Anti-forensics command blocked"},
]


def unwrap(command: str) -> str:
    """Extract inner command from bash -c '...' / python3 -c '...' / eval '...'"""
    # Match double-quoted or single-quoted argument, not crossing the same quote type
    m = re.search(r'''(?:bash|sh|python3?|eval)\s+-?c\s+(?:"([^"]+)"|'([^']+)')''', command)
    if m:
        return m.group(1) if m.group(1) is not None else m.group(2)
    return command


def load_allow_patterns(cwd: str) -> list:
    try:
        cfg = json.loads(Path(cwd, ".aiclair.json").read_text())
        return cfg.get("danger_detector", {}).get("allow_patterns", [])
    except Exception:
        return []


def detect(command: str, cwd: str) -> tuple:
    allow_patterns = load_allow_patterns(cwd)
    for pattern in allow_patterns:
        if pattern in command:
            return (False, "")
    inner = unwrap(command)
    for bp in BLOCK_PATTERNS:
        if bp["regex"].search(inner):
            return (True, bp["message"])
    return (False, "")


@fail_closed
def main():
    data = read_tool_input()
    transcript_path = data.get("transcript_path", "")
    if check_universal_bypass(transcript_path):
        write_allow()
        return
    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        write_allow()
        return
    command = data.get("tool_input", {}).get("command", "")
    cwd = data.get("cwd", "")
    is_dangerous, reason = detect(command, cwd)
    if is_dangerous:
        write_deny(reason)
    else:
        write_allow()


if __name__ == "__main__":
    main()
