"""Shared test helpers for aiclair core tests."""
import json
import subprocess
import sys
from pathlib import Path


def run_script(script_path: Path, prompt) -> dict:
    """Run a hook script with given prompt value and return parsed output."""
    input_data = json.dumps({"prompt": prompt})
    result = subprocess.run(
        [sys.executable, str(script_path)],
        input=input_data,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Script failed: {result.stderr}")
    return json.loads(result.stdout)
