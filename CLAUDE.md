# aiclair

> IMPORTANT: On first conversation message:
>
> - say "AI-Driven Development ON - Date: {current_date}, TZ: {current_timezone}." to User.
> - load all memory files in [aidd_docs/memory](aidd_docs/memory) directory.

## Project Overview

**aiclair** — Community framework for AI assistant hooks. Write hooks once in Python, run them across supported AI agents (Claude Code, Cursor, OpenCode, Codex).

- Python-first, stdlib only for hooks (zero install friction)
- Progressive disclosure: clear prompts pass through free, vague prompts trigger enrichment
- Adapter pattern: one hook logic, N agent adapters
- Community-driven: contributors add hooks as self-contained directories

## Behavior Guidelines

- Be anti-sycophantic — don't fold arguments just because I push back
- Challenge my reasoning, verify against actual codebase state
- If unsure, say "I don't know" — never fabricate

## Memory Management

List all files:

```shell
! ls -1tr aidd_docs/memory/
```

READ every file in `aidd_docs/memory/*` on load.

## Architecture

```
aiclair/
├── packages/
│   ├── core/                    # Shared stdlib-only utilities
│   ├── hooks/                   # Community hook implementations
│   └── adapter-claude-code/     # Claude Code adapter (MVP)
│       ├── hooks/               # Claude Code entrypoints
│       ├── skills/              # SKILL.md per hook
│       ├── plugin.json
│       └── hooks.json
├── .claude-plugin/              # Marketplace entry
├── aidd_docs/                   # AIDD memory bank + tasks
└── CONTRIBUTING.md
```

## Hook Contract

```
INPUT  (stdin): {"prompt": "user text"}
OUTPUT (stdout): {"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "..."}}
EXIT: 0 always
```

## Community Hook Structure

```
packages/hooks/<hook-name>/
├── hook.py           # Core logic (required, stdlib only)
├── SKILL.md          # Skill definition (optional)
├── metadata.json     # Hook metadata (required)
└── tests/
    └── test_hook.py  # pytest tests (required)
```

## Code Conventions

- Python 3.8+, stdlib only in hook scripts
- Hook scripts must stay < 80 lines
- No print() in production code, no hardcoded secrets
- Use `json.dumps()` for escaping — never manual `.replace()`
- Bypass prefixes: `* ` (skip), `/word` (slash cmd), `# ` (memorize)
- Tests: pytest, no emoji prints, conftest.py for shared helpers

## Commits

Format: `<type>: <description>` (feat|fix|refactor|docs|test|chore|perf|ci)
