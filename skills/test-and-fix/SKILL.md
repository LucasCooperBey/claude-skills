---
name: test-and-fix
description: Run tests and auto-fix failures. Standalone test runner that diagnoses and repairs failing tests without manual intervention.
---
# Test and Fix (/test-and-fix)

Run the test suite and automatically fix any failures.

## When to Use

- After making code changes
- Before committing
- When tests are red and you want them green fast
- As a standalone alternative to the fix loop in `/ship`

## Arguments

Parse `$ARGUMENTS` for these flags:

| Arg | Effect |
|-----|--------|
| `--file "path"` | Run only specific test file |
| `--no-fix` | Report failures without fixing |
| (bare path) | Treat as `--file` |

## Time Budget

- Total: 10 minutes max
- Per-failure fix: 2 minutes max
- If approaching budget, stop fixing and report what remains

## Step 1: Detect Test Runner

Check the project root to determine the test command. Do NOT assume `bun test`.

| Signal | Runner |
|--------|--------|
| `bun.lockb` or `bunfig.toml` | `bun test` |
| `package.json` with `"test"` script | `bun run test` (or `npm test` if no bun lockfile) |
| `pytest.ini`, `pyproject.toml` [tool.pytest], or `conftest.py` | `python -m pytest` |
| `Gemfile` with rspec | `bundle exec rspec` |
| `Makefile` with `test` target | `make test` |
| None found | Ask user for test command, then proceed |

Store the detected command as `$TEST_CMD` for all subsequent steps.

## Step 2: Run Tests

```bash
$TEST_CMD 2>&1
```

If `--file` was provided: `$TEST_CMD [file] 2>&1`

Capture: pass/fail counts, error messages, stack traces, file locations.

**If tests hang (no output for 60s):** Kill the process, report timeout, ask user.

## Step 3: Triage Failures

All pass? Report `SUCCESS: All tests passing` and exit.

Categorize each failure:

| Category | Example | Action |
|----------|---------|--------|
| Type error | Property missing, wrong arg | Fix the type |
| Logic error | Wrong assertion value | Fix the implementation |
| Test drift | Test expectations outdated | Update the test |
| Missing mock | Unresolved dependency | Add mock/stub |
| Env/config | Missing env var, wrong DB URL | Fix config, don't touch code |

## Step 4: Fix Loop

If `--no-fix`: skip to Step 6.

For each failing test (max 5 fix iterations total, max 2 attempts per failure):

1. Read the failing test file AND the source file it tests
2. Determine fix location: source code, test code, or mock/fixture
3. Apply the fix using Edit tool
4. Re-run just that test file: `$TEST_CMD [file]`
5. If still failing, try ONE different approach
6. If still failing after 2 attempts, flag for manual review and move to next failure

**Never retry the exact same fix.** Change approach or escalate.

## Step 5: Full Suite Verification

After all individual fixes, run the full suite: `$TEST_CMD`

If fixes introduced NEW failures:
1. Identify which fix caused it (check git diff)
2. Revert that specific fix: `git checkout -- [file]`
3. Report the conflict — don't attempt to resolve cascading failures

## Step 6: Report

```
## Test Results

### Fixed
- `file:line` -- description of fix

### Still Failing (needs manual review)
- `file:line` -- why auto-fix didn't work

### Summary
- N tests total, N passing, N fixed this run, N need manual attention
```

## Safety Rails

- Never delete tests to make them pass
- Prefer fixing source over changing test expectations (unless the test is genuinely wrong)
- If a fix changes public API behavior, warn the user before applying
- Max 5 fix iterations total, max 2 attempts per individual failure
- If no test runner detected and user doesn't provide one, exit with `BLOCKED: No test runner found`
