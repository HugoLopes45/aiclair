import sys
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

from packages.core.tests.conftest import run_script  # noqa: F401

HOOK_SCRIPT = Path(__file__).parent.parent / "hook.py"


def run_hook(command: str, cwd: str = "/tmp", aiclair_config: dict = None):
    """Run danger-detector hook with a Bash command."""
    import tempfile
    stdin_data = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "cwd": cwd,
        "session_id": "test",
        "transcript_path": ""
    })
    if aiclair_config:
        tmpdir = Path(tempfile.mkdtemp())
        (tmpdir / ".aiclair.json").write_text(json.dumps(aiclair_config))
        stdin_data = json.dumps({
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": command},
            "cwd": str(tmpdir),
            "session_id": "test",
            "transcript_path": ""
        })
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin_data, capture_output=True, text=True
    )
    return json.loads(result.stdout)
