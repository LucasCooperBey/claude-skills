---
name: ship
description: Fix-until-clean loop then commit and push. Use when ready to ship code — runs tests, lint, typecheck, fixes any issues, commits, and pushes.
---
# Ship — Fix Until Clean, Then Push

Automated loop that ensures code is clean before shipping.

## When to Use

- Done coding and ready to commit + push
- Want to make sure everything passes before pushing
- Replace manual "run tests, fix, run again" cycle

## Arguments

```
/ship [optional commit message]

Examples:
/ship add user validation endpoint
/ship fix dashboard performance regression
/ship                              # auto-generates commit message from diff
```

Parse `$ARGUMENTS` as the commit message. If empty, auto-generate from `git diff --staged`.

## Time Budget

- Quality checks: 2 min max per suite run
- Fix loop: 3 min max per fix attempt, 10 min total
- Hard stop: 15 min total. If not shipped by then → STOP, report status

## Step 0: Detect Project Type

Before running anything, detect what's available:

```bash
# Check for package.json scripts
# Node/Bun project: use bun test, bun run lint, bun run typecheck
# Python project (pyproject.toml or setup.py): use uv run pytest, uv run ruff check
# Ruby project (Gemfile): use bundle exec rake test, bundle exec rubocop
# If no recognizable project → warn and skip quality checks, just commit
```

Only run checks that exist. If `package.json` has no `lint` script, skip lint. Don't fail on missing scripts.

## Step 1: Detect Branch Context

```bash
# Check current branch
BRANCH=$(git branch --show-current)

# Branch detection: check your project's CLAUDE.md for branch conventions
# If your project uses a staging/dev branch instead of main, warn before pushing to main
```

## Step 2: Quality Check Loop

Run all available checks. Max 5 fix iterations (hard stop: same error 3 times).

For each failure:
1. Read the error output
2. Identify root cause
3. Fix it (max 2 attempts same approach, then try alternative)
4. Re-run the failing check
5. If fixed → continue to next check
6. If still failing after 3 attempts on same issue → STOP and report

## Step 3: Commit + Push

Once all checks pass:

```bash
# Stage changes — use specific files, NOT git add -A
# Review what changed with git status first
# NEVER stage .env, credentials, or secrets files
git add [specific files]

# Commit with message (from $ARGUMENTS or auto-generated from diff)
git commit -m "$(cat <<'EOF'
[commit message]

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"

# Push
git push
```

## Step 4: Handle Push Failures

If push is rejected (remote has new commits):

```bash
git pull --rebase
# Re-run quality suite (rebase might introduce conflicts)
# If clean → push again
git push
# If merge conflicts → STOP, ask user
```

## Step 5: Post-Ship

After successful push:
- Run `/sv` to save session state
- Update changelog if applicable
- Report: `SUCCESS: Shipped. [N] files changed, all checks passing.`

## Safety Rails

| Condition | Action |
|-----------|--------|
| 5+ fix iterations | STOP, report remaining issues |
| Same error 3 times | STOP, needs different approach |
| Merge conflicts | STOP, ask for help |
| No changes to commit | Skip, notify user |
| .env or secrets in diff | WARN, exclude from staging |
| On wrong branch (per project convention) | WARN before pushing |
