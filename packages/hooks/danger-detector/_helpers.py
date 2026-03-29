"""Block patterns and command-unwrapping helpers for danger-detector."""
import re

BLOCK_PATTERNS = [
    {"id": "rm-recursive",   "regex": re.compile(r'\brm\s+-[^\s]*r[^\s]*(\s|$)'), "message": "Recursive file deletion blocked"},
    {"id": "drop-database",  "regex": re.compile(r'\b(DROP|TRUNCATE)\s+(TABLE|DATABASE|SCHEMA)\b', re.IGNORECASE), "message": "Destructive SQL operation blocked"},
    {"id": "force-push",     "regex": re.compile(r'\bgit\s+push\b.*(-f\b|--force\b)'), "message": "Force push blocked"},
    {"id": "kill-all",       "regex": re.compile(r'\b(killall\s+-9|kill\s+-9\s+-1|pkill\s+-9)\b'), "message": "Kill-all process signal blocked"},
    {"id": "shutdown",       "regex": re.compile(r'\b(shutdown|reboot|halt|poweroff)\b'), "message": "System shutdown command blocked"},
    {"id": "iptables-flush", "regex": re.compile(r'\biptables\s+-F\b'), "message": "Firewall flush blocked"},
    {"id": "reverse-shell-tcp",  "regex": re.compile(r'bash\s+-i\s+>&?\s*/dev/tcp/'), "message": "Reverse shell (TCP) blocked"},
    {"id": "reverse-shell-nc",   "regex": re.compile(r'\bnc\b[^;|&\n]*-[ec]\s+/bin/(bash|sh)\b'), "message": "Reverse shell (netcat) blocked"},
    {"id": "fork-bomb",          "regex": re.compile(r':\(\)\s*\{[^;]*:\s*\|[^;]*:'), "message": "Fork bomb blocked"},
    {"id": "anti-forensics",     "regex": re.compile(r'\b(history\s+-c|unset\s+HISTFILE|shred\s+-u)\b'), "message": "Anti-forensics command blocked"},
]


def unwrap(command: str) -> str:
    """Extract inner command from bash -c '...' / python3 -c '...' / eval '...'"""
    # Allow \\" inside double-quoted and \\' inside single-quoted arguments
    m = re.search(r'''(?:bash|sh|python3?|eval)\s+-?c\s+(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)')''', command)
    if m:
        return m.group(1) if m.group(1) is not None else m.group(2)
    return command


def extract_subshells(command: str) -> list:
    """Extract contents of $(...) and backtick subshell substitutions, iteratively.

    Handles nested subshells by rescanning each extracted content for inner $() patterns.
    """
    results = []
    queue = [command]
    seen = {command}
    while queue:
        current = queue.pop()
        # $(...) form — single-level extraction per pass
        for match in re.findall(r'\$\(([^)]+)\)', current):
            if match not in seen:
                results.append(match)
                seen.add(match)
                queue.append(match)
        # Detect truncated nested $(...) left by outer ) consumption: scan for $( in extracted strings
        for m in re.finditer(r'\$\((.+)', current):
            inner = m.group(1).rstrip(')')
            if inner and inner not in seen:
                results.append(inner)
                seen.add(inner)
                queue.append(inner)
        # backtick form
        for match in re.findall(r'`([^`]+)`', current):
            if match not in seen:
                results.append(match)
                seen.add(match)
                queue.append(match)
    return results
