"""Shared test helpers for <hook-name> tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from packages.core.tests.conftest import run_script  # noqa: F401

HOOK_SCRIPT = Path(__file__).parent.parent / "hook.py"
