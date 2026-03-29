#!/usr/bin/env bash
# aiclair installer
# Usage:
#   bash install.sh                          # interactive: pick hooks
#   bash install.sh --all                    # install all hooks
#   bash install.sh --hooks prompt-improver  # install specific hooks
#   bash install.sh --hooks "danger-detector secret-guard"

set -e

INSTALL_DIR="${AICLAIR_DIR:-$HOME/.claude/plugins/aiclair}"
SETTINGS="$HOME/.claude/settings.json"

ALL_HOOKS=(prompt-improver danger-detector secret-guard)

# ── parse args ────────────────────────────────────────────────────────────────

SELECTED_HOOKS=()
INSTALL_ALL=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      INSTALL_ALL=true
      shift
      ;;
    --hooks)
      shift
      IFS=' ' read -r -a SELECTED_HOOKS <<< "$1"
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: bash install.sh [--all] [--hooks \"hook1 hook2\"]" >&2
      exit 1
      ;;
  esac
done

# ── clone ────────────────────────────────────────────────────────────────────

if [ -d "$INSTALL_DIR/.git" ]; then
  echo "aiclair already installed at $INSTALL_DIR — pulling latest..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "Installing aiclair to $INSTALL_DIR..."
  git clone https://github.com/HugoLopes45/aiclair "$INSTALL_DIR"
fi

# ── python check ─────────────────────────────────────────────────────────────

if command -v python3 &>/dev/null; then
  PYTHON="python3"
elif command -v python &>/dev/null; then
  PYTHON="python"
else
  echo "Error: python3 not found. Install Python 3.8+ and retry." >&2
  exit 1
fi

# ── interactive selection (if no flags given) ─────────────────────────────────

if [ "$INSTALL_ALL" = false ] && [ ${#SELECTED_HOOKS[@]} -eq 0 ]; then
  echo ""
  echo "Available hooks:"
  echo "  1) prompt-improver  — asks clarifying questions when prompts are vague"
  echo "  2) danger-detector  — blocks rm -rf, DROP TABLE, force push, shutdown"
  echo "  3) secret-guard     — blocks AWS keys, tokens, private keys from leaking"
  echo ""
  echo "Enter hook numbers to install (e.g. 1 2 3), or press Enter for all:"
  read -r selection

  if [ -z "$selection" ]; then
    INSTALL_ALL=true
  else
    for n in $selection; do
      case "$n" in
        1) SELECTED_HOOKS+=(prompt-improver) ;;
        2) SELECTED_HOOKS+=(danger-detector) ;;
        3) SELECTED_HOOKS+=(secret-guard) ;;
        *) echo "Unknown selection: $n — skipping" ;;
      esac
    done
  fi
fi

if [ "$INSTALL_ALL" = true ]; then
  SELECTED_HOOKS=("${ALL_HOOKS[@]}")
fi

if [ ${#SELECTED_HOOKS[@]} -eq 0 ]; then
  echo "No hooks selected. Exiting."
  exit 0
fi

# ── settings.json update ─────────────────────────────────────────────────────

mkdir -p "$(dirname "$SETTINGS")"
[ ! -f "$SETTINGS" ] && echo '{}' > "$SETTINGS"

HOOKS_ARG="${SELECTED_HOOKS[*]}"

$PYTHON - "$SETTINGS" "$INSTALL_DIR" "$HOOKS_ARG" <<'PYEOF'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
install_dir   = sys.argv[2]
selected      = sys.argv[3].split()

settings = json.loads(settings_path.read_text()) if settings_path.stat().st_size > 0 else {}
hooks = settings.setdefault("hooks", {})

def add_hook(event, entry):
    bucket = hooks.setdefault(event, [])
    new_cmd = entry["hooks"][0]["command"]
    for existing in bucket:
        for h in existing.get("hooks", []):
            if h.get("command") == new_cmd:
                return
    bucket.append(entry)

HOOK_DEFINITIONS = {
    "prompt-improver": [
        ("UserPromptSubmit", {
            "hooks": [{
                "type": "command",
                "command": f"python3 {install_dir}/packages/adapter_claude_code/hooks/improve-prompt.py || python {install_dir}/packages/adapter_claude_code/hooks/improve-prompt.py",
                "description": "aiclair: prompt-improver"
            }]
        }),
    ],
    "danger-detector": [
        ("PreToolUse", {
            "matcher": "Bash",
            "hooks": [{
                "type": "command",
                "command": f"python3 {install_dir}/packages/adapter_claude_code/hooks/danger-detector.py || python {install_dir}/packages/adapter_claude_code/hooks/danger-detector.py",
                "description": "aiclair: danger-detector"
            }]
        }),
    ],
    "secret-guard": [
        ("PreToolUse", {
            "matcher": "Bash|Write|Edit",
            "hooks": [{
                "type": "command",
                "command": f"python3 {install_dir}/packages/adapter_claude_code/hooks/secret-guard-pre.py || python {install_dir}/packages/adapter_claude_code/hooks/secret-guard-pre.py",
                "description": "aiclair: secret-guard (pre)"
            }]
        }),
        ("PostToolUse", {
            "matcher": "Bash",
            "hooks": [{
                "type": "command",
                "command": f"python3 {install_dir}/packages/adapter_claude_code/hooks/secret-guard-post.py || python {install_dir}/packages/adapter_claude_code/hooks/secret-guard-post.py",
                "description": "aiclair: secret-guard (post)"
            }]
        }),
    ],
}

installed = []
for hook_name in selected:
    if hook_name not in HOOK_DEFINITIONS:
        print(f"Unknown hook: {hook_name} — skipping")
        continue
    for event, entry in HOOK_DEFINITIONS[hook_name]:
        add_hook(event, entry)
    installed.append(hook_name)

settings_path.write_text(json.dumps(settings, indent=2) + "\n")
for name in installed:
    print(f"  + {name}")
PYEOF

echo ""
echo "aiclair installed. Hooks active:"
for hook in "${SELECTED_HOOKS[@]}"; do
  echo "  + $hook"
done
echo ""
echo "To uninstall: bash $INSTALL_DIR/uninstall.sh"
echo "To update:    git -C $INSTALL_DIR pull && bash $INSTALL_DIR/install.sh --all"
