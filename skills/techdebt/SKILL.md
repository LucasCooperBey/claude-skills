---
name: techdebt
description: End-of-session tech debt cleanup. Scans for TODOs, dead code, unused imports, type issues, and quick wins before you log off.
---
# Tech Debt (/techdebt)

End-of-session codebase cleanup scan.

## When to Use

- End of a coding session
- Before creating a PR
- Periodic hygiene check
- After a big feature merge

## Instructions

When the user invokes `/techdebt`:

### Step 1: Identify Scope

Determine what to scan:

```bash
# Files modified this session (since last commit on main)
BASELINE=$(git merge-base HEAD main 2>/dev/null || echo "HEAD~10")
git diff --name-only $BASELINE HEAD
git diff --name-only  # Unstaged too
```

If no changes, scan the whole project's `src/` directory.

### Step 2: Run Parallel Scans

**Scan 1 — TODOs and FIXMEs** (grep for actionable items):
```bash
grep -rn "TODO\|FIXME\|HACK\|XXX\|WORKAROUND" src/ --include="*.ts" --include="*.tsx"
```

Categorize each:
- Stale (> 30 days, check git blame)
- Actionable now (< 5 min fix)
- Needs ticket (complex, track separately)

**Scan 2 — Dead Code** (Task tool, subagent_type: "general-purpose"):
```
Scan these files for dead code:
[file list]

Find:
- Unused exports (exported but never imported)
- Unused functions/variables
- Unreachable code paths
- Commented-out code blocks
- Unused imports

Return file:line for each finding.
```

**Scan 3 — Type Safety** (Task tool, subagent_type: "general-purpose"):
```
Scan these files for type safety issues:
[file list]

Find:
- `as` type assertions that could fail at runtime
- Missing null checks
- Implicit `any` from untyped dependencies
- Type guards that don't fully narrow
- Union types that aren't exhaustively handled

Return file:line and severity for each.
```

### Step 3: Quick Wins

Automatically fix items that are safe:
- Remove unused imports
- Delete commented-out code (if > 30 days old per git blame)
- Remove unused local variables
- Fix obvious type narrowing gaps

### Step 4: Report

```markdown
## Tech Debt Report

### Auto-Fixed
- Removed N unused imports
- Deleted N lines of dead code
- Fixed N type issues

### Needs Attention
| File | Issue | Effort |
|------|-------|--------|
| src/foo.ts:42 | Stale TODO from 2 months ago | 5 min |
| src/bar.ts:17 | Type assertion could fail | 15 min |

### TODOs Summary
- N stale (> 30 days)
- N actionable now
- N need tickets

### Health Score: X/10
```

### Step 4b: Research Artifact Index Sweep

Check for new files in `~/.claude/artifacts/research/` that aren't in `~/.claude/artifacts/research/INDEX.md`:

```bash
# Find files newer than INDEX.md
find ~/.claude/artifacts/research/ -name "*.md" -newer ~/.claude/artifacts/research/INDEX.md ! -name "INDEX.md" 2>/dev/null
```

If any unindexed files found, append them to the appropriate section in INDEX.md with channel tag. Report: "INDEX.md: added N new research artifacts."

### Step 5: Offer Next Steps

```
Would you like me to:
A) Fix the "Needs Attention" items now
B) Create GitHub issues for the complex ones
C) Just note it and move on
```

## Arguments

| Arg | Effect |
|-----|--------|
| `--fix-all` | Auto-fix everything safe, no prompt |
| `--report-only` | No fixes, just report |
| `--scope "dir"` | Scan specific directory |
