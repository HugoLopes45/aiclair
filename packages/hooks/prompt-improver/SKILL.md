---
name: prompt-improver
description: Enriches vague prompts with targeted research and clarification. Invoked when hook determines a prompt needs enrichment.
---

# Prompt Improver Skill

## When Invoked

- Hook has already determined the prompt is vague
- Proceed directly to research and clarification

## Core Workflow

### Phase 1: Research

Check conversation history first — if it already provides sufficient context, skip codebase exploration.

If history is insufficient:
1. Review codebase (Task/Explore for structure, Grep/Glob for patterns, git log for recent changes)
2. Search for errors, failing tests, TODO/FIXME comments
3. Document findings to ground questions in actual context

### Phase 2: Generate Questions

Based on research, formulate 1-6 questions:
- **Grounded**: every option comes from research findings
- **Specific**: concrete options (2-4 per question), no "Other approach" vagueness
- **Focused**: one decision point per question

Number of questions:
- 1-2: simple ambiguity (which file? which approach?)
- 3-4: moderate complexity (scope + approach + validation)
- 5-6: complex scenarios with multiple unknowns

### Phase 3: Clarify

Use `AskUserQuestion` tool:
- `question`: clear, specific, ends with `?`
- `header`: max 12 chars
- `multiSelect`: false unless choices are non-exclusive
- `options`: 2-4 concrete choices from research

### Phase 4: Execute

Proceed with original intent using clarification answers and research findings.

## References

Load only when needed:
- [Question patterns](references/question-patterns.md)
- [Research strategies](references/research-strategies.md)
- [Examples](references/examples.md)
