# packages/hooks

Community hook implementations. Agent-agnostic logic only.

## Rules
- Each hook is a self-contained directory
- hook.py < 80 lines, stdlib only
- Import from packages/core/ for shared utilities
- conftest.py in tests/ is the ONLY place run_hook() is defined
- No hardcoded agent names or agent-specific tool calls
