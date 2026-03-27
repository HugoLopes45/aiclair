"""Shared helpers for adapter-claude-code tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from packages.core.tests.conftest import run_script  # noqa: F401

ADAPTER_DIR = Path(__file__).parent.parent
ENTRYPOINT = ADAPTER_DIR / "hooks" / "improve-prompt.py"
