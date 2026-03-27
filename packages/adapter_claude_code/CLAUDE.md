# packages/adapter-claude-code

Claude Code adapter. Thin wrappers connecting core hooks to Claude Code's plugin system.

## Rules
- Entrypoints in hooks/ are thin wrappers only — logic lives in packages/hooks/
- plugin.json must have "skills" field, must NOT have "hooks" field
- hooks.json is auto-discovered — do not reference it in plugin.json
- Skills are sourced from packages/hooks/<name>/ — no duplication
- python3 ... || python ... fallback in all hook commands (Windows compatibility)
