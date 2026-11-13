---
name: writing-plans
description: Creates detailed implementation plans for multi-step tasks with exact file paths, code examples, and test commands.
---
# Writing Implementation Plans

Create comprehensive plans for multi-step tasks, designed for engineers with limited codebase familiarity.

## Plan Structure

```markdown
# Implementation Plan: [Feature Name]

## Goal
[One sentence describing the outcome]

## Architecture Context
[Relevant tech stack and patterns]

## Prerequisites
- [ ] Dependency installed
- [ ] Config in place

---

## Task 1: [Descriptive Name]
**Files:** `src/path/to/file.ts`
**Time:** 2-5 minutes

### Test First
```typescript
// src/path/to/file.test.ts
test('description of expected behavior', () => {
  // Test code
});
```

**Verify failure:**
```bash
bun test src/path/to/file.test.ts
# Expected: FAIL - function not implemented
```

### Implementation
```typescript
// src/path/to/file.ts
export function featureName() {
  // Implementation
}
```

**Verify success:**
```bash
bun test src/path/to/file.test.ts
# Expected: PASS
```

### Commit
```bash
git add src/path/to/file.ts src/path/to/file.test.ts
git commit -m "Add [feature] with tests"
```

---

## Task 2: ...
```

## Core Principles

| Principle | Application |
|-----------|-------------|
| DRY | Don't repeat logic; extract helpers |
| YAGNI | Only build what's needed now |
| TDD | Write test → verify fail → implement → verify pass |
| Frequent commits | Commit after each task |

## Task Granularity

Each task should:
- Take 2-5 minutes to complete
- Have a clear, verifiable outcome
- Be completable by someone unfamiliar with codebase
- Include exact file paths
- Include complete code examples
- Include verification commands with expected output

## Output Location

Save plans to:
```
docs/plans/YYYY-MM-DD-feature-name.md
```

## Execution Handoff

After plan completion, offer two paths:

### Option 1: Subagent-Driven (Same Session)
Fresh subagent per task, maintains plan context.
```
"Would you like me to execute this plan using subagent-driven development?"
```

### Option 2: Parallel Session (Worktree)
Separate worktree for isolated development.
```
"Would you like to execute this in a separate worktree session?"
```

## Plan Components Checklist

- [ ] Clear goal statement
- [ ] Architecture/tech stack context
- [ ] Prerequisites listed
- [ ] Tasks with exact file paths
- [ ] Test code for each task
- [ ] Verification commands with expected output
- [ ] Commit messages for each task
- [ ] No ambiguous instructions

## Code Example Requirements

Every code block must be:
- Complete (not pseudocode)
- Copy-pasteable
- Include imports
- Include types (for TypeScript)

Bad:
```typescript
// Add validation logic here
```

Good:
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1),
});

export function validateUser(input: unknown) {
  return UserSchema.parse(input);
}
```

---

## Deliberation Mode (RALPLAN-DR)

Activates automatically when the plan touches high-risk areas, or when the user requests "deliberate" or "consensus" planning.

### Auto-triggers

| Trigger | Why |
|---------|-----|
| Auth/security changes | Mistakes are hard to reverse |
| Database migrations | Data loss risk |
| Destructive/irreversible operations | No undo |
| Production deployment changes | User-facing impact |
| Compliance/PII handling | Legal risk |
| Public API changes | Breaking changes for consumers |

### What Deliberation Adds

Every plan in deliberation mode includes these additional sections BEFORE the task list:

#### 1. Principles (3-5)

Guiding principles specific to THIS plan, not generic platitudes.

```markdown
## Principles
1. **Zero-downtime migration** — users must not experience service interruption
2. **Rollback within 5 minutes** — every step must be reversible
3. **Data integrity over speed** — validate before and after each migration step
```

#### 2. Decision Drivers (top 3)

The factors that most influence the architecture choice.

```markdown
## Decision Drivers
1. **Existing Drizzle ORM patterns** — must stay consistent with schema.ts conventions
2. **Neon's branching capability** — can test migrations on branch before prod
3. **Vercel's 60s function timeout** — constrains migration batch sizes
```

#### 3. Viable Options (>= 2)

At least two options with bounded pros/cons. If only one option is viable, explain why alternatives were rejected.

```markdown
## Options

### Option A: Incremental migration with dual-write
**Pros:** Zero downtime, reversible, proven pattern
**Cons:** Temporary code complexity, 2-week dual-write period

### Option B: Blue-green schema swap
**Pros:** Clean cutover, no dual-write
**Cons:** Requires Neon branch, brief read-only window (~30s)

### Rejected: Big-bang migration
**Why rejected:** 60s Vercel timeout makes single-shot migration impossible for 50K+ rows
```

#### 4. ADR (Architecture Decision Record)

```markdown
## ADR
**Decision:** Option A — incremental migration with dual-write
**Drivers:** Neon timeout limits, zero-downtime requirement, team familiarity
**Alternatives considered:** Blue-green swap (viable but higher operational risk), big-bang (rejected — timeout)
**Why chosen:** Lowest risk, most reversible, matches existing patterns in drizzle/migrations/
**Consequences:** 2-week dual-write period, temporary ~15% write latency increase
**Follow-ups:** Remove dual-write code after migration verified (deadline: 2 weeks post-deploy)
```

#### 5. Pre-mortem (high-risk only, 3 scenarios)

```markdown
## Pre-mortem
1. **Migration times out mid-batch** → Mitigation: batch size < 1000 rows, idempotent batches, checkpoint table
2. **Dual-write divergence** → Mitigation: reconciliation query runs hourly, alerts on mismatch > 0
3. **Rollback needed after partial migration** → Mitigation: old column retained for 2 weeks, reads still work from either
```

#### 6. Expanded Test Plan (high-risk only)

```markdown
## Test Plan
- **Unit:** Schema validation, migration function logic, batch size handling
- **Integration:** Full migration on Neon branch with production-like data
- **E2E:** User workflow before/during/after migration
- **Observability:** Migration progress dashboard, error rate alerts, latency monitoring
```

### Quality Gates

Every plan (deliberation or not) must meet:

| Gate | Standard |
|------|----------|
| Evidence grounding | 80%+ claims cite file:line |
| Testability | 90%+ acceptance criteria are concrete (no "fast" — use "p99 < 200ms") |
| Risk coverage | All identified risks have mitigations |
| Specificity | No vague terms without metrics |
| Step sizing | Steps sized to actual scope (not always exactly 5) |

## Source

Adapted from https://github.com/obra/superpowers (MIT, Copyright (c) 2025 Jesse Vincent). Changed for this repo by Lucas Cooper-Bey in 2026: wording rewritten, keeping the same plan premise, task size, and output path.
