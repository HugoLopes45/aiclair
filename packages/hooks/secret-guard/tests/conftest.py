import sys
import json
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
from packages.core.tests.conftest import run_script  # noqa: F401

HOOK_SCRIPT = Path(__file__).parent.parent / "hook.py"


def run_pre_hook(tool_name: str, tool_input: dict, transcript_path: str = "") -> dict:
    stdin_data = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": "/tmp",
        "session_id": "test",
        "transcript_path": transcript_path,
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin_data, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def run_post_hook(stdout: str) -> dict:
    stdin_data = json.dumps({
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "cat secrets.txt"},
        "tool_response": {"stdout": stdout, "stderr": ""},
        "cwd": "/tmp",
        "session_id": "test",
        "transcript_path": "",
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin_data, capture_output=True, text=True
    )
    return json.loads(result.stdout)


def make_transcript_with_tag(tag: str) -> str:
    """Create a temp transcript file with a user message containing the tag."""
    import json as _json
    entry = _json.dumps({
        "role": "user",
        "content": [{"type": "text", "text": f"do the thing {tag}"}]
    })
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False)
    f.write(entry + "\n")
    f.close()
    return f.name
