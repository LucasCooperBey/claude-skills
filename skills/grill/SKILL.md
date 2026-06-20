---
name: grill
description: Adversarial code review — challenge your code harshly, find what will break in production. Inspired by Boris Cherny's setup.
---
# Grill (/grill)

Adversarial code review that actively tries to break your code.

**Time budget:** 10 min total (agents ~5 min, synthesis + fixes ~5 min). Abort at 10 min with partial report.

## Arguments

Parse `$ARGUMENTS` string:
- `--security` → Security-only mode (just Agent 2)
- `--perf` → Add performance stress-test agent (Agent 4)
- `--files "a.ts,b.ts"` → Target specific files instead of git diff
- `--report-only` → No auto-fixes, just report
- No args → Full 3-agent review of changed files

## Instructions

### Step 1: Identify Target

```bash
git diff --name-only HEAD~1   # committed changes
git diff --name-only          # unstaged changes
git diff --name-only --cached # staged changes
```

Merge all three lists, deduplicate. If `--files` was passed, use those instead.

If no files found: ask what to review and stop.

Filter out non-code files (images, lockfiles, .env). If >20 files, ask user to narrow scope.

### Step 2: Dispatch Adversarial Reviewers

Launch agents in parallel (Task tool, subagent_type: "general-purpose", model: "sonnet"). Each agent prompt MUST include: "Read each file using the Read tool before analyzing."

**Agent 1 — The Breaker:**
```
You are a hostile QA engineer. Your job is to BREAK this code. Read each file listed below using the Read tool, then find:
- Edge cases that will crash in production
- Race conditions and concurrency issues
- Input combinations that cause unexpected behavior
- State transitions that lead to corruption
- Error paths that swallow failures silently

Files to read and review: [list with full paths]

Be specific. Show the exact input/scenario that breaks it.
Do NOT suggest improvements — only find what's broken.
Rate each: Critical / High / Medium / Low.
If nothing is broken, say "No issues found" — don't invent problems.
```

**Agent 2 — The Security Auditor:**
```
You are a penetration tester reviewing this code. Read each file listed below using the Read tool, then find:
- Injection vulnerabilities (SQL, XSS, command)
- Authentication/authorization bypasses
- Data exposure through error messages or logs
- Missing input validation at trust boundaries
- Secrets or credentials in code
- OWASP Top 10 violations

Files to read and review: [list with full paths]

Rate each finding: Critical / High / Medium / Low.
Show the attack vector for each.
If the code has no security surface (e.g. pure utility), say "No security issues found."
```

**Agent 3 — The Skeptic:**
```
You are a senior engineer who thinks this code is wrong. Read each file listed below using the Read tool, then challenge:
- Does this actually solve the stated problem?
- Are the types correct or just making the compiler happy?
- Will this scale to 10x/100x current load?
- Are error messages helpful or misleading?
- Is the abstraction level right or over/under-engineered?

Files to read and review: [list with full paths]

For each concern, explain the concrete consequence of not fixing it.
Rate each: Critical / High / Medium / Low.
If the code is solid, say so — don't manufacture concerns.
```

**Agent 4 — The Stress Tester** (only if `--perf` flag):
```
You are a performance engineer. Read each file listed below using the Read tool, then find:
- O(n^2) or worse algorithms on unbounded input
- Missing pagination/limits on queries
- N+1 query patterns
- Unbounded memory growth (accumulating arrays, missing cleanup)
- Blocking operations in async paths

Files to read and review: [list with full paths]

Rate each: Critical / High / Medium / Low.
```

Skip Agent 1 and 3 if `--security` flag is set.

### Step 3: Synthesize Findings

Deduplicate across agents. Merge into severity-sorted report:

```
## Grill Report — [date]
Files reviewed: [list]
Agents: [which ran]

### Critical (fix before shipping)
- [finding] — [file:line] — [agent]

### High (fix soon)
- [finding] — [file:line] — [agent]

### Medium (track for later)
- [finding] — [file:line] — [agent]

### Low (nice to fix)
- [finding] — [file:line] — [agent]

### Clean
- [things that passed all reviews]

### Verdict: SHIP / HOLD / BLOCK
```

Verdict rules: any Critical → BLOCK. 3+ High → HOLD. Otherwise → SHIP.

### Step 4: Fix (unless --report-only)

- **Critical items**: Present each fix to user for confirmation before applying. Never auto-fix security code silently.
- **High items**: List with recommended fixes, let user choose which to apply.
- **Medium/Low**: Note in report only.

### Step 5: Re-verify

Detect project type and run tests:
- `package.json` with bun.lockb → `bun test`
- `package.json` without bun.lockb → `npm test`
- `pytest.ini` / `pyproject.toml` / `tests/` with .py → `pytest`
- `Gemfile` → `bundle exec rspec`
- `Makefile` with test target → `make test`

If tests fail after fixes, revert the failing fix (`git checkout -- <file>`) and note in report.
