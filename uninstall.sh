#!/usr/bin/env bash
# aiclair uninstaller
# Removes aiclair hooks from ~/.claude/settings.json and optionally deletes the install directory

set -e

INSTALL_DIR="${AICLAIR_DIR:-$HOME/.claude/plugins/aiclair}"
SETTINGS="$HOME/.claude/settings.json"

# ── remove hooks from settings.json ──────────────────────────────────────────

if [ ! -f "$SETTINGS" ]; then
  echo "No settings.json found — nothing to remove."
else
  python3 - "$SETTINGS" "$INSTALL_DIR" <<'PYEOF'
import json, sys
from pathlib import Path

settings_path = Path(sys.argv[1])
install_dir   = sys.argv[2]

settings = json.loads(settings_path.read_text())
hooks = settings.get("hooks", {})
removed = 0

for event in list(hooks.keys()):
    cleaned = []
    for entry in hooks[event]:
        aiclair_cmds = [
            h for h in entry.get("hooks", [])
            if install_dir in h.get("command", "")
        ]
        if not aiclair_cmds:
            cleaned.append(entry)
        else:
            removed += len(aiclair_cmds)
    if cleaned:
        hooks[event] = cleaned
    else:
        del hooks[event]

settings_path.write_text(json.dumps(settings, indent=2) + "\n")
print(f"Removed {removed} aiclair hook(s) from settings.json.")
PYEOF
fi

# ── optionally remove install directory ──────────────────────────────────────

if [ -d "$INSTALL_DIR" ]; then
  read -r -p "Delete $INSTALL_DIR? [y/N] " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    rm -rf "$INSTALL_DIR"
    echo "Deleted $INSTALL_DIR."
  else
    echo "Kept $INSTALL_DIR."
  fi
fi

echo "aiclair uninstalled."
