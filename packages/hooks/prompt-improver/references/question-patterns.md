# Question Patterns

## AskUserQuestion Format

```json
{
  "question": "Which component needs refactoring?",
  "header": "Target",
  "multiSelect": false,
  "options": [
    {"label": "Auth module", "description": "src/auth/ — 3 failing tests"},
    {"label": "API layer", "description": "src/api/ — deprecated methods"},
    {"label": "Database layer", "description": "src/db/ — N+1 queries found"}
  ]
}
```

Rules:
- `header` max 12 characters
- 2-4 options per question
- Each option label: 1-5 words
- Each description: one sentence with context from research

## Templates by Category

### Target identification
```json
{
  "question": "Which [file/function/module] are you referring to?",
  "header": "Target",
  "multiSelect": false,
  "options": [
    {"label": "[Name from codebase]", "description": "[Location and context]"},
    {"label": "[Name from codebase]", "description": "[Location and context]"}
  ]
}
```

### Approach selection
```json
{
  "question": "Which approach should be used?",
  "header": "Approach",
  "multiSelect": false,
  "options": [
    {"label": "[Approach A]", "description": "[Trade-off: faster but less robust]"},
    {"label": "[Approach B]", "description": "[Trade-off: more work but cleaner]"}
  ]
}
```

### Scope definition
```json
{
  "question": "What is the scope of this change?",
  "header": "Scope",
  "multiSelect": false,
  "options": [
    {"label": "This file only", "description": "Minimal change, low risk"},
    {"label": "This module", "description": "Broader refactor, medium risk"},
    {"label": "Full system", "description": "Complete overhaul, high impact"}
  ]
}
```

### Priority / urgency
```json
{
  "question": "What is the priority?",
  "header": "Priority",
  "multiSelect": false,
  "options": [
    {"label": "Fix now", "description": "Blocking issue, must resolve today"},
    {"label": "This sprint", "description": "Important but not blocking"},
    {"label": "Backlog", "description": "Nice to have, no deadline"}
  ]
}
```

### Validation criteria
```json
{
  "question": "How should success be validated?",
  "header": "Validation",
  "multiSelect": false,
  "options": [
    {"label": "Existing tests pass", "description": "No new tests needed"},
    {"label": "New unit tests", "description": "Write tests for changed logic"},
    {"label": "Manual testing", "description": "Verify in running app"}
  ]
}
```

## Common Pitfalls

- **Generic options**: "Option A / Option B" — always use names from research
- **Compound questions**: "What and how?" — split into two questions
- **Leading questions**: "Should we use the better approach?" — present options neutrally
- **Too many questions**: > 6 questions overwhelms — prioritize the most blocking ambiguity
