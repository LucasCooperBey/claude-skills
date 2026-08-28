---
name: pp3p
description: Performs three perfection passes plus polish for maximum code refinement with cleanup. Triggers on pp3p or three-pass polish requests.
---
# Perfection Pass x3 + Polish (/pp3p)

Three critique passes (3-5 agents each) + polish. Maximum refinement.

> **Scoring contract:** critique + verify with the same judge rubric as pp2p (BLOCKER / HIGH / MEDIUM / NIT, skeptical standalone stance, >=2-of-3 adversarial survival on contested high-stakes findings). Same contract as the cross-family review, so verdicts are comparable across passes and across AIs.

## Arguments

Parse `$ARGUMENTS` string:

| Arg | Effect |
|-----|--------|
| `--type TYPE` | Review type: `code`, `plan`, `design`, `architecture`, `strategy` (auto-detected if omitted) |
| `--agents "A,B,C"` | Custom agent perspectives (defaults are per-type — see Step 4) |
| `--security` | Preset: Solution-Fit, Security, Edge Cases |
| `--performance` | Preset: Solution-Fit, Performance, Elegance |
| `--api` | Preset: Solution-Fit, API Design, Edge Cases |
| `--stack-reality` | Stack-Reality critic on its own — fact-check a doc/plan against known stack state (solo mode, see Step 4) |
| `--sequential` | Agents see each other's findings (slower but more coherent) |
| `--no-early-exit` | Disable early exit on convergence |
| `--files "path1,path2"` | Explicit file targets (skip context detection) |

**Time budget:** 20 minutes for the critique passes. If elapsed time exceeds 15 min after ANY pass, skip the remaining critique passes and go to polish. Polish, the mutation gate, and the cross-family gate are EXEMPT from this budget — for pp3p they are non-negotiable and always run.

## Step 1: Verify Context

Identify what to refine. Check in order:
1. `--files` argument → Read those files
2. Recent code changes in conversation context
3. Uncommitted changes: `git diff --name-only` → if files exist, confirm with user
4. Nothing found → ask user:

> "Nothing to refine. Point me to files or paste code/plan to review."

Then STOP.

**Scope guard:** If target is >15 files, ask user to narrow scope.

## Step 2: Detect Review Type

If `--type` not specified, auto-detect from content:
- Contains code / function definitions → `code`
- Markdown with headers, no code → `plan`
- Discusses components, interfaces, modules → `architecture`
- UI/UX flows, wireframes → `design`
- Goals, priorities, sequencing → `strategy`
- Default: `code`

## Step 3: Gather Context

Read CLAUDE.md if present (extract code quality rules, patterns — max 50 lines).
Run `git log --oneline -5` for pattern awareness.

## Step 3.5: Create Run Marker

The marker lives at `.claude/perfection-pass.local.md` **in the project git root**. Skip it if cwd is outside a project.

Before creating:
1. **Stale-marker check:** if the file already exists, copy it to `.claude/perfection-passes/stale-{YYYYMMDD-HHMMSS}.md` and delete the original.
2. **Gitignore check:** append `.claude/*.local.md` to `.gitignore` if no existing pattern covers it.

Then create:

```markdown
---
iteration: 3
max_iterations: 3
include_polish: false
polish_done: true
review_type: <detected type from Step 2>
created_at: <ISO timestamp>
---

## Original Problem

[Problem statement]

## Current Solution

[The solution/files under review]
```

The pass loop runs INLINE (Step 5). The marker is a crash record, not a chaining mechanism. Append each pass's findings to the body as you go — but ONLY inside fenced code blocks. A bare `---` line or a column-0 `key:` line in the body corrupts YAML frontmatter parsers.

## Step 4: Select Agents

Choose base agents by type (unless `--agents` overrides):

**code:**
1. **Solution-Problem Fit** — Does it solve the stated problem correctly?
2. **Edge Cases & Gaps** — What inputs/states could break it?
3. **Elegance & Simplicity** — Can it be simpler without losing correctness?
4. **State-Integrity** (auto-add when the change touches persistence/state — DB schema/writes, migrations, caches, vector stores, agent memory, files-as-state): check append-only / supersede-never-overwrite / provenance-on-derived-values / atomic-HEAD-and-history / never-silently-lose-a-fact. For `pp3p` (used on data integrity), this critic is mandatory whenever data is touched.

**plan:**
1. **Completeness** — All steps defined? Missing prerequisites? Gaps?
2. **Feasibility** — Can each step be executed? Unrealistic assumptions?
3. **Risk & Edge Cases** — What could go wrong? Fallbacks?

**architecture:**
1. **Separation of Concerns** — Clean boundaries? Right abstractions?
2. **Scalability & Evolution** — Will this grow well?
3. **Integration Risk** — Dependencies, coupling, failure modes?

**design:**
1. **User Flow** — Happy path clear? Dead ends?
2. **Consistency** — Patterns reused? Naming coherent?
3. **Edge States** — Empty, error, loading, overflow?

**strategy:**
1. **Goal Alignment** — Actions connect to stated goals?
2. **Prioritization** — Sequencing justified?
3. **Blind Spots** — What's not being considered?

**Stack-Reality (MANDATORY for pp3p, EVERY type)** — append this critic to whatever set the type or preset selects. The anti-bullshit critic: cross-check every numeric/capability/version/pricing/repo-state claim against CLAUDE.md, stack notes, and current state. Any claim contradicting known ground truth is HIGH severity. Use the verbatim critic instructions in the **pp2p** skill ("Stack-Reality critic instructions") — they are canonical; do not paraphrase. pp3p guides high-stakes downstream work, so it needs this pass at least as much as pp2p does.

Presets (override type defaults; Stack-Reality is still appended):
- `--security`: Solution-Fit, Security, Edge Cases
- `--performance`: Solution-Fit, Performance, Elegance
- `--api`: Solution-Fit, API Design, Edge Cases
- `--stack-reality`: **solo mode** — run ONE pass of the lone Stack-Reality critic with the verify gate as usual, then report. Skip polish, the mutation gate, and the cross-family loop unless its findings triggered actual edits — this is a fact-check, not a refinement run.

## Step 5: Run Pass Loop (3 passes)

For each pass (1, 2, 3):

### 5a: Dispatch Critique Agents

Spawn one agent per selected critic — 4 for most types (base 3 + mandatory Stack-Reality), 5 when the persistence auto-add applies.

**Critic model — escalate for critical work.** pp3p is used on auth, payments, and data integrity; its critics are the last line before such code ships. Default to a fast/cheap tier for routine refinement; use the strongest available tier for the critic agents when the change touches auth/permissions, money movement, migrations, or destructive/irreversible operations (or when `--security`/`--performance` presets are active). The cheapest critic on the most critical pass is a false economy.

**Parallel** (default): Launch all simultaneously.
**Sequential** (`--sequential`): Launch one at a time, each sees prior findings.

Each agent prompt MUST include:
- The current solution (full text or file contents)
- The original problem statement
- Project context (CLAUDE.md excerpt)
- Their specific critique focus
- Instruction: "Return a numbered list of specific, actionable issues. If no issues found, return NONE."

### 5b: Verify, Then Apply

After all agents return:
1. Count raw issues across agents
2. **Adversarial verify gate.** Critic passes carry a measured false-positive rate (~20-30% Pass 1, ~5-10% Pass 3). Try to *refute* each HIGH/BLOCKER finding against the actual code — a finding survives only with an exact line + a concrete failure it causes; drop the rest with a one-line reason. On contested high-stakes findings (auth/payments/data), escalate to a pass@K consensus (sample the critic 3x, keep findings appearing in >=2 runs) rather than a single refute.
3. Print summary: `Pass N: X raw → Y surviving (per-agent: ...)`
4. If surviving issues == 0 AND early exit enabled (default): skip remaining critique passes and go to Step 6. Early exit skips CRITIQUE passes only — polish, the mutation gate, and the cross-family gate still run before the report.
5. Synthesize *surviving* findings into concrete improvements
6. Apply improvements (Edit files or revise solution); append findings + dropped-at-gate reasons to the run marker (inside fenced code blocks)
7. Continue to next pass with the UPDATED solution

### 5c: Error Handling

- If an agent returns empty/garbled: log it, continue with other agents' findings
- If ALL agents fail: STOP, report error, do not continue to next pass
- Never retry the same agent prompt — adjust focus if re-dispatching

## Step 6: Polish Pass

After all critique passes (or early exit), run ONE polish pass.

**For code:** Review modified files yourself (no subagent needed):
- Check for DRY violations introduced during fixes
- Verify naming consistency
- Remove dead code or commented-out lines
- Ensure CLAUDE.md conventions followed
- Apply non-controversial cleanups

**For plan:** Re-read full plan, check for:
- Ambiguous language introduced during revisions
- Missing details in newly added steps
- Consistent formatting

**For design/architecture:** Re-read full document, check for:
- Internal consistency after changes
- All components still well-defined
- No contradictions introduced

## Step 6.5: Mutation gate — "test the tests" (when the change adds/relies on a test suite)

A green test suite proves nothing until you prove it would go RED on a real bug. **Mandatory for pp3p** whenever the change includes or depends on automated tests. Skip only for pure-doc / config-only changes. On an early-exit run where no fixes were applied, mutate the pre-existing behaviors the suite guards, or mark N/A. pp3p is used on auth/payments/data integrity, so a green suite you haven't falsified is exactly the kind of false confidence this pass exists to kill.

1. For each behavior the suite claims to cover, **revert the fix / inject the bug in a throwaway copy** and run the matching test. Assert it **fails**. A mutation that *survives* (test stays green against broken code) is a test gap — fix the test, not the code. The classic survivor is a test that **reimplements the logic inline instead of calling the real function** — extract the function and call it.
2. Prefer a **committed mutation driver** (copy sources to a tempdir, revert one fix, run its selector, assert non-zero exit; flag STALE when the target string moved so it can't silently rot) over one-off manual mutation — it stays a regression asset.
3. Report `N/N mutations caught`. Anything less than 100% is a gap to close before the cross-family gate.

**Receipt:** "X tests · Y/Y mutations caught" belongs in the pp3p summary alongside the cross-family verdict.

## Step 7: Cross-family Adversarial Review

After polish, get an independent second opinion from a **different model family** than the one running this pass, framed adversarially — it challenges the chosen implementation, design tradeoffs, and assumptions (not just defect hunting). If the Codex plugin is available, use `/codex:adversarial-review`. Otherwise dispatch one adversarial review to GPT / Gemini / Grok / whatever isn't the session model. Do not hardcode a version.

**LOOP until convergence** (this is the non-negotiable final gate for pp3p):

```
  repeat (cap = 3 cross-family passes):
    run adversarial review on the LATEST state
    ├─ BLOCKER / HIGH → adjudicate each (fix it, OR refute on merit + document why), then LOOP
    ├─ only NITs      → apply inline / log as follow-up, then one more pass to
    │                   confirm (the confirming pass counts toward the cap)
    └─ no new blockers → CONVERGED → archive
  if still flagging at the cap → STOP, document residuals + escalate to the user
```

- Each pass reviews the newest state — no fix ships unreviewed.
- **Adjudicate, don't auto-accept.** Fixed, or refuted with a one-line reason. For data-integrity work, validate fixes against a real datastore where possible, not just types/tests.
- **Hold the scope line.** When a finding is real but a *different invariant / pre-existing / separate subsystem*, document it as a follow-up instead of ballooning the change. Convergence = "no new blockers in scope."

A different model family catches issues self-critique can miss. Mandatory for `pp3p` given its use on critical implementations (auth, payments, data integrity).

If no second model family is available, say so in the report and skip this gate rather than pretending a same-family re-read counts.

## Step 8: Report & Archive

1. Print final summary:

```
PP3P Complete
  Pass 1: X raw → X' surviving → applied
  Pass 2: Y raw → Y' surviving → applied (or: skipped — converged / time budget)
  Pass 3: Z raw → Z' surviving → applied (or: skipped — converged / time budget)
  Polish: N cleanups applied
  Mutation gate: Y/Y mutations caught (or: N/A — no test suite)
  Cross-family: converged in K pass(es) (or: skipped — no second family available)
  Total: X'+Y'+Z'+N pass/polish improvements (mutation + cross-family fixes counted on their own lines)
```

2. Archive report to `.claude/perfection-passes/pp3p_{topic}_{YYYYMMDD-HHMMSS}.md` (timestamped so same-day reruns never overwrite) containing:
   - Original problem
   - Issues found per pass (including findings dropped at the verify gate)
   - Final solution state

3. Delete `.claude/perfection-pass.local.md` BEFORE ending the turn.

## When to Use

- Critical implementations (auth, payments, data integrity)
- Complex architectural decisions
- Work guiding significant downstream effort
- When you want maximum confidence + clean code
- NOT for trivial changes — use `/critique` (single pass) instead

## Total Effort

- 3 passes x 4-5 agents = 12-15 agent critiques (base 3 per type + mandatory Stack-Reality, + State-Integrity when data is touched)
- 1 polish pass (self-review, no subagents)
- 1 mutation gate (falsify the tests — mandatory when a suite is in play)
- 1 cross-family adversarial review (looped to convergence)
- **Total: 12+ agent perspectives + polish + mutation gate + cross-family challenge**
