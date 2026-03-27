# aiclair

![CI](https://github.com/aiclair-community/aiclair/actions/workflows/validate.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.1.0-blue)

Community framework for Claude Code hooks — Python Claude Code plugins for UserPromptSubmit and PreToolUse events.

## What it does

- **prompt-improver**: Evaluates prompt clarity on every UserPromptSubmit; asks 1-6 targeted questions when a prompt is vague.
- **danger-detector**: Blocks destructive Bash commands (`rm -rf`, `DROP TABLE`, force push, shutdown, iptables flush) on PreToolUse; unwraps `bash -c` and `python -c` before checking.
- **secret-guard**: Blocks AWS keys, GitHub tokens, private keys, and Stripe keys from appearing in Bash, Write, and Edit operations; uses entropy filtering; supports `[allow-secret]` tag override.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/aiclair-community/aiclair/main/install.sh | bash
```

The script prompts you to pick which hooks to install, then wires them into `~/.claude/settings.json`. No pip install, no build step.

**Install all hooks without prompts:**

```bash
curl -fsSL https://raw.githubusercontent.com/aiclair-community/aiclair/main/install.sh | bash -s -- --all
```

**Install specific hooks:**

```bash
curl -fsSL https://raw.githubusercontent.com/aiclair-community/aiclair/main/install.sh | bash -s -- --hooks "danger-detector secret-guard"
```

**Uninstall:**

```bash
bash ~/.claude/plugins/aiclair/uninstall.sh
```

## Hooks

| Hook | Event | What it does |
|---|---|---|
| [prompt-improver](packages/hooks/prompt-improver/) | UserPromptSubmit | Evaluates prompt clarity; asks 1-6 targeted questions for vague prompts |
| [danger-detector](packages/hooks/danger-detector/) | PreToolUse (Bash) | Blocks `rm -rf`, `DROP TABLE`, force push, shutdown, iptables flush; unwraps `bash -c`/`python -c` |
| [secret-guard](packages/hooks/secret-guard/) | PreToolUse (Bash/Write/Edit) + PostToolUse (Bash) | Blocks AWS keys, GitHub tokens, private keys, Stripe keys; entropy filtering; `[allow-secret]` tag override |

## Bypass prefixes

Applies to prompt-improver only.

| Prefix | Behavior |
|---|---|
| `* ` | Skip evaluation entirely |
| `/command` | Slash commands pass through automatically |
| `# ` | Memorize commands pass through automatically |

## Per-project config

danger-detector reads `.aiclair.json` at the project root to allow patterns that would otherwise be blocked.

```json
{
  "danger_detector": {
    "allow_patterns": [
      "rm -rf dist/",
      "DROP TABLE test_"
    ]
  }
}
```

## Contributing

1. Copy `packages/hooks/_template` to `packages/hooks/<your-hook-name>/`.
2. Implement `hook.py` — under 80 lines, standard library only.
3. Add `metadata.json` with hook name, event, and description.
4. Write tests in `tests/`.
5. Run `python3 scripts/validate-hook.py` to check structure and style.

## License

MIT
