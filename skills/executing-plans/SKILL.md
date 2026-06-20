---
name: executing-plans
description: Implements written plans through batched execution with review checkpoints. Stops on blockers and asks for clarification rather than guessing.
---
# Executing Implementation Plans

Systematic implementation of written plans through batched execution with review checkpoints.

## Process

### 1. Load and Review

```bash
# Read the plan
cat docs/plans/YYYY-MM-DD-feature-name.md
```

Before starting:
- Review the entire plan
- Raise concerns about unclear or risky steps
- Confirm understanding
- **Identify success criteria for each task** (see Goal-Driven Execution below)

### 2. Execute in Batches (Goal-Driven)

Default batch size: 3 tasks

For each task:
1. Mark as in-progress (TodoWrite)
2. **Define success criteria** — what proves this task is done?
3. Execute test-first (RED)
4. Implement (GREEN)
5. **Loop: verify ALL success criteria are met**
6. Only when ALL criteria pass → commit
7. Mark complete

### Goal-Driven Execution

Every task MUST have verifiable success criteria before execution starts.

**Template for each task:**
```markdown
## Task N: [description]
**Success criteria (ALL must pass):**
- [ ] `bun test [relevant test file]` passes
- [ ] `bun run typecheck` clean
- [ ] [Specific behavioral verification]
- [ ] No `any` types in new code

**Loop until ALL criteria are met.**
```

**The loop:**
```
while (not all criteria met) {
  attempt implementation/fix
  run ALL verification commands
  check each criterion
  if (all pass) → done
  if (3+ failed attempts on same criterion) → STOP, report blocker
}
```

**Key difference from step-based execution:**
- Step-based: "Do A, then B, then C" → done when steps complete
- Goal-driven: "Achieve state X" → done when state X is verified true

This prevents the "I did all the steps but it still doesn't work" problem.

### 3. Report After Each Batch

After completing a batch:
```
## Batch Complete

### Completed:
- Task 1: [status]
- Task 2: [status]
- Task 3: [status]

### Verification:
All tests passing: YES/NO

### Issues Encountered:
[Any problems or deviations]

Ready for feedback.
```

### 4. Wait for Review

Do not proceed to next batch until:
- User acknowledges completion
- User provides feedback
- User approves continuation

### 5. Complete

When all tasks done:
- Use finishing-development-branch skill
- Merge or create PR

## Stop Conditions

**STOP IMMEDIATELY when encountering:**

| Blocker | Action |
|---------|--------|
| Missing dependencies | Report and wait |
| Test failures | Report with error details |
| Plan gaps | Ask for clarification |
| Unclear instructions | Ask before guessing |
| Repeated verification failures | Stop after 3 attempts |

**Critical:** Ask for clarification rather than guessing.

## Batch Execution Example

```
## Starting Batch 1 (Tasks 1-3)

### Task 1: Add user validation
[in_progress]

Writing test...
```typescript
test('validates user email', () => {
  expect(() => validateUser({ email: 'invalid' })).toThrow();
});
```

Running test...
❌ FAIL (expected - no implementation)

Implementing...
[code]

Running test...
✅ PASS

Committing...
✅ Committed: abc123

[completed]

### Task 2: ...
```

## Handling Deviations

If plan requires modification:

1. **Stop execution**
2. **Document the issue**
   ```
   Plan deviation detected:
   - Task 4 assumes X exists
   - Actually, Y is the pattern here
   - Proposed adjustment: [change]
   ```
3. **Wait for approval**
4. **Continue with adjusted plan**

## Quality Checks

Before marking batch complete:
- All tests pass
- No linting errors
- No type errors
- Code matches plan intent

```bash
bun test
bun run lint
bun run typecheck
```

## Partial Failure & Typed Debt

When a task fails after 2+ attempts, don't just mark it BLOCKED. Classify the failure and record typed debt.

### Failure Classification

Pick exactly one before stopping or retrying:

- **RETRY_MODIFIED** — Relax acceptance criteria and retry. Record what was relaxed as debt.
- **RETRY_APPROACH** — Same success criteria, completely different implementation strategy. Never retry the exact same approach.
- **SPLIT** — Decompose the failing task into 2-4 smaller sub-tasks. Each must be independently verifiable. **Depth Limit:** Max 2 levels of decomposition. If a sub-task also needs splitting, ESCALATE_TO_REPLAN instead.
- **ACCEPT_WITH_DEBT** — Close the task but record a structured debt entry (see format below). Use when the gap is non-blocking and the cost of perfection exceeds the risk. **Debt Accumulation Threshold:** If a plan accumulates 3+ debts touching the same subsystem, pause and consider ESCALATE_TO_REPLAN. Localized debt compounds into systemic risk.
- **ESCALATE_TO_REPLAN** — The plan itself needs restructuring. Stop execution, surface findings, wait for approval before continuing.

### Debt Record Format

When using ACCEPT_WITH_DEBT, append to the plan file or batch report:

```
DEBT: {task name/number} — {severity: low | medium | high | critical}
Missing: {what specifically was not completed}
Impact: {which downstream tasks or systems are affected}
Accepted because: {justification — time, risk, scope, dependency}
Resolution: {what would fully fix it, estimated effort}
```

Example:
```
DEBT: Task 3 (Auth middleware) — medium
Missing: Rate limiting not implemented
Impact: Task 7 (API endpoints) will need to add it before ship
Accepted because: Rate limiting is out of scope for this plan; auth logic itself is correct
Resolution: Add express-rate-limit in a follow-up task, ~30 min
```

**Integration:** Before `/ship`, scan the plan file for open DEBT entries. Surface them in the pre-merge review. Debts that should persist across sessions should be promoted to the Runbook (`<your-runbook, e.g. docs/RUNBOOK.md>`).

### Cross-Task Convention Capture

When a task succeeds via a non-obvious approach, record the pattern so parallel or downstream tasks can reuse it without rediscovery:

```
CONVENTION: {pattern name}
Applied in: {task name/number}
Pattern: {what worked — be specific enough to copy}
Reuse when: {trigger condition}
```

Example:
```
CONVENTION: Drizzle insert with conflict ignore
Applied in: Task 2 (seed baseline data)
Pattern: db.insert(table).values(rows).onConflictDoNothing()
Reuse when: Any seeding or idempotent insert operation
```

Conventions accumulate in the batch report and are referenced at the start of each new batch.

### Hardness-Aware Routing

Before executing each task, classify it. This prevents wasting review cycles on trivial changes and ensures complex ones get proper scrutiny.

| Hardness | Criteria | Execution mode |
|----------|----------|----------------|
| Simple | < 5 min, single file, no architecture impact | Execute directly, no review gate |
| Medium | 5–30 min, multi-file, localized change | Execute with self-review before marking done |
| Complex | 30+ min, architecture change, cross-system impact | Execute with full review checkpoint — pause for user approval |

When in doubt, classify up, not down. A wrong complexity estimate on the low side is how "quick fixes" become 2-hour detours.

---

## Integration Points

| Skill | When |
|-------|------|
| test-driven-development | Each task implementation |
| verification-before-completion | After each verification step |
| finishing-development-branch | After all tasks complete |

---

## Guardrails

See [agent-guardrails.md](../../context/agent-guardrails.md) for time budgets, retry limits, and fast verification patterns.

## Related Context

- [agent-guardrails.md](../../context/agent-guardrails.md) - Time budgets, retry limits
- [validation-oracles.md](../../context/validation-oracles.md) - Baseline validation
- [output-markers.md](../../context/output-markers.md) - Standard output format
