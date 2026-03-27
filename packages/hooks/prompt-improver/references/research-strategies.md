# Research Strategies

## Decision Tree

```
What needs clarification?
├── Which file/function → grep for function names, git log for recent changes
├── Which bug → search failing tests, errors in conversation history
├── Which approach → check existing patterns in codebase, look for precedents
├── What scope → explore module boundaries, check what imports what
└── Unclear intent → re-read conversation history, ask directly
```

## Strategy 1: Conversation History First

Before any codebase exploration, check if the conversation already has:
- Recent error messages or stack traces
- File paths mentioned in prior turns
- Previous attempts at the same task
- User corrections or clarifications

If history provides sufficient context: skip to Phase 2 (questions).

## Strategy 2: Codebase Exploration

Use when history is insufficient:

**For "fix the bug" type prompts:**
- Search for failing tests: `Grep("FAILED\|Error\|assert")`
- Check recent changes: `git log --oneline -10`
- Look for TODO/FIXME: `Grep("TODO\|FIXME\|HACK")`

**For "add feature" type prompts:**
- Find existing similar features as reference
- Check module structure to identify insertion point
- Look for related tests to understand expected behavior

**For "refactor" type prompts:**
- Identify the current pattern (grep for it)
- Find all usages to understand scope
- Check for existing tests that define expected behavior

## Strategy 3: Documentation Lookup

Use when the task involves external libraries or APIs:
- Fetch official docs before asking about approach
- Check README/CHANGELOG for version-specific behavior
- Look for existing integration patterns in codebase

## Research Plan Template

Before asking questions, create a minimal research plan:

```
1. [ ] Check conversation history for context
2. [ ] [Specific search based on prompt type]
3. [ ] [One more targeted lookup if needed]
```

Stop as soon as you have enough grounding for specific questions. Over-research wastes context.
