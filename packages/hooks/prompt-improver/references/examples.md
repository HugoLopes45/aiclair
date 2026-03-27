# Examples

## Example 1: Vague Bug Fix

**Prompt:** "fix the bug"

**Research findings:**
- Conversation history: user mentioned login errors 2 turns ago
- `grep "FAILED" tests/` → `test_auth.py::test_login` failing
- `src/auth.py:145` → bare `except:` swallowing errors

**Questions generated:**
```json
{
  "question": "Which bug are you referring to?",
  "header": "Bug target",
  "multiSelect": false,
  "options": [
    {"label": "Login failure", "description": "auth.py:145 — exception swallowed silently"},
    {"label": "Session timeout", "description": "session.py:89 — timeout not reset on activity"}
  ]
}
```

**After answer:** Fix `auth.py:145` with proper error handling and add reproducer test.

---

## Example 2: Clear Prompt (Skill Not Invoked)

**Prompt:** "Refactor getUserById in src/api/users.ts to use async/await instead of promises"

**Hook evaluation:** Clear — specific target, specific action, clear success criteria.

**Result:** Hook passes through immediately. Skill not invoked.

---

## Example 3: Ambiguous Feature Request

**Prompt:** "add authentication"

**Research findings:**
- No auth system exists in codebase
- `package.json` has no auth dependencies
- Existing API routes have no middleware

**Questions generated (2):**
```json
[
  {
    "question": "Which authentication approach?",
    "header": "Auth type",
    "multiSelect": false,
    "options": [
      {"label": "JWT tokens", "description": "Stateless, good for APIs"},
      {"label": "Session-based", "description": "Stateful, simpler for web apps"},
      {"label": "OAuth2", "description": "Third-party login (Google, GitHub)"}
    ]
  },
  {
    "question": "Which routes need protection?",
    "header": "Route scope",
    "multiSelect": false,
    "options": [
      {"label": "All routes", "description": "Full protection"},
      {"label": "Admin only", "description": "Only /admin/* routes"},
      {"label": "Custom selection", "description": "Define per-route"}
    ]
  }
]
```
