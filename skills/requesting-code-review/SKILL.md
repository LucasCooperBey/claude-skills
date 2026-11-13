---
name: requesting-code-review
description: Structures code review requests with context, commit hashes, and requirements. Facilitates early and frequent review cycles.
---
# Requesting Code Review

Structure code review requests for effective feedback.

## Core Principle

**Review early, review often.** Prevents issues from compounding.

## When Reviews Are Required

| Scenario | Priority |
|----------|----------|
| After each task in subagent workflow | Required |
| Upon finishing major features | Required |
| Before merging to main | Required |
| When stuck | Optional |
| Before refactoring | Optional |
| After fixing complex bugs | Optional |

## Request Process

### 1. Gather Context

```bash
# Get commit range
BASELINE=$(git merge-base HEAD main)
CURRENT=$(git rev-parse HEAD)

echo "Baseline: $BASELINE"
echo "Current: $CURRENT"

# Show what changed
git log $BASELINE..$CURRENT --oneline
git diff $BASELINE..$CURRENT --stat
```

### 2. Dispatch Review Request

```
Task({
  prompt: `
    Code review request.

    ## What Was Built
    [Brief description of feature/fix]

    ## Requirements
    [Original requirements or task description]

    ## Commits
    - Baseline: ${BASELINE}
    - Current: ${CURRENT}

    ## Description
    [What changed and why]

    ## Areas of Concern
    [Specific things to look at closely]

    Please review for:
    - Spec compliance
    - Code quality
    - Test coverage
    - Potential issues
  `,
  subagent_type: "general-purpose"
})
```

### 3. Act on Findings

| Severity | Action |
|----------|--------|
| Critical | Fix immediately |
| Important | Fix before proceeding |
| Minor | Document for later |

## Request Template

```markdown
## Code Review Request

### Summary
[One sentence describing what this code does]

### Requirements Fulfilled
- [x] Requirement 1
- [x] Requirement 2

### Changes
**Files modified:**
- `src/feature.ts` - Added validation logic
- `src/feature.test.ts` - Added tests

**Commits:**
```
abc123 - Add user validation
def456 - Add error handling
```

### How to Test
```bash
bun test src/feature.test.ts
```

### Concerns
- Performance of X might be an issue with large data
- Not sure if Y pattern is idiomatic

### Questions
- Should we also handle edge case Z?
```

## Reviewer Categories

Reviewers will categorize feedback:

| Category | Meaning | Your Action |
|----------|---------|-------------|
| Critical | Blocks merge | Fix now |
| Important | Should fix | Fix before continuing |
| Minor | Nice to have | Schedule for later |
| Question | Clarification | Answer promptly |

## Handling Disagreement

If feedback seems incorrect:

1. Don't dismiss it immediately
2. Provide technical evidence
3. Explain your reasoning
4. Be open to being wrong

```
I hear your concern about X. Here's why I chose this approach:

1. [Technical reason]
2. [Evidence from testing]
3. [Alternative considered and why rejected]

If you still think Y is better, I'm happy to change it.
```

## Post-Review

After receiving feedback:

```bash
# Fix issues
# ...

# Verify fixes
bun test

# Commit fixes
git commit -m "Address review feedback: [summary]"

# Re-request if changes were significant
```

## Source

Adapted from https://github.com/obra/superpowers (MIT, Copyright (c) 2025 Jesse Vincent). Changed for this repo by Lucas Cooper-Bey in 2026: wording rewritten into tables.
