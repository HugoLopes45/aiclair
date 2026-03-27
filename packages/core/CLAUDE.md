# packages/core

Shared stdlib-only utilities. No agent-specific logic allowed here.

## Rules
- Python 3.8+, stdlib only
- No Claude Code-specific imports or logic
- All JSON embedding via json.dumps() — never .replace()
- bypass.py is the single source of truth for prefix detection
