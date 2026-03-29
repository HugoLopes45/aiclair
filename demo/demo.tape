Output demo/aiclair-demo.gif
Set FontSize 14
Set Width 900
Set Height 400
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 40ms
Set PlaybackSpeed 0.8

# --- danger-detector: block rm -rf ---
Type "# danger-detector — blocks destructive commands"
Enter
Sleep 600ms

Type `echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"rm -rf /"},"cwd":"/tmp","session_id":"x","transcript_path":""}' \`
Enter
Sleep 200ms
Type `  | python3 packages/hooks/danger-detector/hook.py | python3 -m json.tool`
Enter
Sleep 1500ms

# --- secret-guard: block AWS key ---
Type "# secret-guard — catches secrets before they land in files"
Enter
Sleep 600ms

Type `echo '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"config.py","content":"AWS_KEY=AKIAIOSFODNN7EXAMPLE"},"cwd":"/tmp","session_id":"x","transcript_path":""}' \`
Enter
Sleep 200ms
Type `  | python3 packages/hooks/secret-guard/hook.py | python3 -m json.tool`
Enter
Sleep 1500ms

# --- safe command passes ---
Type "# safe commands pass through untouched"
Enter
Sleep 600ms

Type `echo '{"hook_event_name":"PreToolUse","tool_name":"Bash","tool_input":{"command":"ls -la"},"cwd":"/tmp","session_id":"x","transcript_path":""}' \`
Enter
Sleep 200ms
Type `  | python3 packages/hooks/danger-detector/hook.py | python3 -m json.tool`
Enter
Sleep 2000ms
