# Contributing to aiclair

## Adding a Hook

### 1. Create your hook directory
```bash
cp -r packages/hooks/_template packages/hooks/my-hook
```

### 2. Implement the hook
Edit `packages/hooks/my-hook/hook.py`. Requirements:
- Python 3.8+, stdlib only (no pip imports)
- < 80 lines
- Use `json.dumps()` for string embedding — never `.replace()`
- Import shared utilities from `packages/core/`

### 3. Fill in metadata
Edit `packages/hooks/my-hook/metadata.json`:
```json
{
  "name": "my-hook",
  "version": "1.0.0",
  "description": "What your hook does",
  "author": "your-github-username",
  "events": ["UserPromptSubmit"],
  "agents": ["claude-code"]
}
```

### 4. Write tests
Tests live in `packages/hooks/my-hook/tests/`. Use `conftest.py` for the shared `run_hook()` helper — never redefine it locally.

### 5. Validate
```bash
python3 scripts/validate-hook.py packages/hooks/my-hook/
pytest packages/hooks/my-hook/
```

### 6. Open a PR

## PR Checklist

- [ ] `hook.py` < 80 lines
- [ ] stdlib only (no external imports)
- [ ] `metadata.json` present with all required fields
- [ ] Tests pass: `pytest packages/hooks/my-hook/`
- [ ] Validation passes: `python3 scripts/validate-hook.py packages/hooks/my-hook/`
- [ ] If SKILL.md present: < 100 lines
- [ ] If references/ present: each file < 300 lines

## Code Conventions

- `json.dumps()` for all string embedding in prompts
- Bypass patterns: `"* "` (space required), `"/word"` (alpha + no dots/slashes), `"# "` (space required)
- Tests: pytest functions only, no classes, no emoji prints
- conftest.py is the single source of `run_hook()` — never duplicate it
