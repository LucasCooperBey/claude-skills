---
name: verification-before-completion
description: Mandates fresh verification evidence before any completion claims. Prevents assumptions by requiring proof that work is actually complete and correct.
---
# Verification Before Completion

**Central Rule:** NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

## Proactive Verification (During, Not After)

Verification is NOT a post-hoc check. It runs **during** execution, at every step.

### When to verify:
- **After every code change** — not just at the end
- **After every test write** — confirm it fails before implementing
- **After every implementation** — confirm tests pass now
- **Before every commit** — full suite, not just changed tests
- **Before any completion claim** — fresh evidence required

### The Verification Loop

```
for each change:
  1. Make the change
  2. Run relevant verification immediately
  3. If fails → fix now (don't accumulate)
  4. If passes → proceed to next change
  5. After all changes → run full verification suite
```

This catches issues at the moment they're introduced, not 10 steps later.

## The Five-Step Verification Gate

Before claiming work is done:

### 1. Identify
What command/test proves your claim?

### 2. Run
Execute the complete verification command fresh.

### 3. Read
Check the full output AND the exit code.

### 4. Verify
Does the output actually support your assertion?

### 5. Claim
Only then make the claim, with evidence cited.

## Red Flags - Language That Signals Skipped Verification

| Phrase | Problem |
|--------|---------|
| "Should work" | No verification done |
| "Probably fixed" | Assumption, not evidence |
| "Seems correct" | Impression, not verification |
| "Done!" | Premature declaration |
| "Perfect!" | Satisfaction without proof |

## Verification Examples

### Code Changes
```bash
# Don't say "the bug is fixed"
# Do: run the test and show output
bun test src/feature.test.ts
# Then: "Test passes: [actual output]"
```

### Build/Compile
```bash
# Don't say "it compiles"
# Do: actually compile and check
bun run build
echo $?  # Check exit code
# Then: "Build succeeded with exit code 0"
```

### File Creation
```bash
# Don't say "file was created"
# Do: verify it exists with expected content
ls -la path/to/file
head -20 path/to/file
# Then: "File exists at [path] with content: [preview]"
```

## Why This Matters

Historical failures from skipped verification:
- Broken code shipped to production
- Lost user trust from "fixed" bugs that weren't
- Wasted hours debugging issues that "should work"

## The Spirit of This Rule

This isn't about exact wording. It's about honesty.

Any statement that implies success without evidence violates the principle:
- "I updated the config" → Did you verify the change took effect?
- "The API now returns X" → Did you call it and check?
- "Tests are passing" → Did you run them just now?

## Verification Workflow

```
1. Make change
2. Identify verification method
3. Run verification
4. Read full output
5. Check exit code
6. Only then report success/failure with evidence
```

## Skipping Any Step = Lying, Not Verifying

Partial verification is not verification:
- Running command but not reading output
- Reading output but ignoring exit code
- Checking one thing but claiming another

## Evidence Format

Good: "Build completed successfully (exit code 0). Output shows 47 tests passed, 0 failed."

Bad: "Build works now."

## Ship Discipline — the four gates between "green" and "done"

When a code change is ready to call done (deployed / fixed / shipped), pass four gates —
green tests are necessary, never sufficient. (Harvested from Dan Mercede's `ship` skill.)

1. **Tests RED→GREEN** — the relevant test failed before the fix, passes after. No declared
   suite RAISES rigor (hand-roll a failing default-deny check on any authz path); it never
   licenses skipping.
2. **PR on the post-edit diff** — re-detect the base branch (never assume `main`); a prior or
   verbal LGTM is permission, not approval of the *current* diff. Never force-push.
3. **Adversarial self-review** — attack your own change: where does it fail OPEN instead of
   closed? what mutation/decision goes unaudited? what state is asserted but never verified?
   Prefer ELIMINATING a fail-open path over making it "safe". Grade BLOCKING / WARNING / INFO;
   fix BLOCKING first.
4. **Live-verify runtime** — confirm via the declared path (health endpoint, container/systemd
   status, connectivity). A green deploy/CI is NOT runtime proof. If you can't verify, say
   "unverifiable / not done" — never substitute a forward-promise ("will verify").

### Rationalizations that mean STOP (you're about to ship on faith)

| Rationalization | Reality |
|---|---|
| "I'm confident the fix is correct." | Confidence is not evidence. Live-verify. |
| "`deploy.sh` exited 0, so it works." | A clean deploy proves the script ran, not that the handler serves traffic. |
| "CI was green, round it up to done." | CI green is necessary-not-sufficient; only an independent runtime check closes it. |
| "Senior already said LGTM, ship it." | A stale/verbal LGTM isn't approval of the post-edit diff. |
| "Flag me if any delta wants re-review." | Re-review is opt-IN, not opt-out. |
| "No test suite here, so move fast." | No suite RAISES rigor; hand-roll RED→GREEN, especially on authz. |
| "I'll make the bypass safe." | First ask whether the bypass should exist at all; prefer elimination. |

---

## Guardrails

See [agent-guardrails.md](../../context/agent-guardrails.md) for retry budgets, escalation ladder, and blocked state template.

## Related Context

- [agent-guardrails.md](../../context/agent-guardrails.md) - Retry budgets, escalation ladder
- [output-markers.md](../../context/output-markers.md) - Standard markers
- [validation-oracles.md](../../context/validation-oracles.md) - Baseline comparison

## Source

Adapted from https://github.com/obra/superpowers (MIT, Copyright (c) 2025 Jesse Vincent). Changed for this repo by Lucas Cooper-Bey in 2026: a proactive-verification loop added.
