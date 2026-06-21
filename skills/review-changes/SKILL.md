---
name: review-changes
description: Analyze uncommitted changes before committing. Quick pre-commit review of what you're about to ship.
---
# Review Changes (/review-changes)

Analyze all uncommitted changes in the working directory before committing.

## When to Use

- Before `git commit` — quick sanity check
- Before `/ship` — preview what's going out
- When you've been coding for a while and lost track of changes
- Before creating a PR

## Instructions

When the user invokes `/review-changes`:

### Step 1: Gather Changes

```bash
# Staged changes
git diff --cached --stat
git diff --cached

# Unstaged changes
git diff --stat
git diff

# Untracked files
git status --short | grep "^??"
```

If no changes found: "Working directory is clean. Nothing to review."

### Step 2: Summarize

Produce a structured summary:

```markdown
## Changes Overview

**Staged (ready to commit):**
- `src/auth.ts` — +42 -12 (added token refresh logic)
- `test/auth.test.ts` — +28 -0 (new tests for refresh)

**Unstaged:**
- `src/utils.ts` — +3 -1 (minor fix, probably should stage)

**Untracked:**
- `src/new-feature.ts` — New file (should this be committed?)

**Total: N files changed, +X -Y lines**
```

### Step 3: Quick Analysis

For each changed file, check:

1. **Accidental changes** — Debug logs, console.log, commented code left in
2. **Missing files** — New imports that reference untracked files
3. **Secrets check** — Any `.env` values, API keys, tokens in the diff
4. **Convention compliance** — Quick check against CLAUDE.md rules
5. **Test coverage** — Did source files change without corresponding test changes?
6. **Proof of thoughtfulness** — Were decisions intentional or just model defaults? Flag any architectural choice that looks like it was accepted without review (e.g., new abstractions, dependency additions, structural patterns that don't match existing conventions).
7. **Cut check** — Flag any addition without a linked issue, user request, or explicit decision. If it can't be explained in one sentence to a beta user, it doesn't ship in V1.

### Step 4: Report Issues

```markdown
## Issues Found

### Must Fix
- `src/auth.ts:15` — `console.log("debug")` left in
- `src/config.ts:8` — Hardcoded API key (NEVER commit this)

### Should Fix
- `src/utils.ts` — Changed but no test updates
- `src/new-feature.ts` — Not staged, but imported by staged files

### Looks Good
- Token refresh logic is clean
- Tests cover the happy path and error cases
```

### Step 5: Suggest Commit

If everything looks good (or after fixes):

```markdown
## Suggested Commit

**Message:** `add token refresh with automatic retry`

**Stage these:**
```bash
git add src/auth.ts test/auth.test.ts src/utils.ts
```

**Don't stage:**
- `src/scratch.ts` — Looks like scratch work

Proceed with commit? Or fix issues first?
```

## Arguments

| Arg | Effect |
|-----|--------|
| `--staged-only` | Only review staged changes |
| `--quick` | Skip analysis, just show summary |
| `--fix` | Auto-fix issues found (remove debug logs, etc.) |
