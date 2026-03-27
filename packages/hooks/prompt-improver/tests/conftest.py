"""
Shared test helpers for prompt-improver tests.
run_script() comes from packages.core.tests.conftest — import it here.
"""
import sys
from pathlib import Path

# Make packages importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from packages.core.tests.conftest import run_script  # noqa: F401

HOOK_SCRIPT = Path(__file__).parent.parent / "hook.py"
