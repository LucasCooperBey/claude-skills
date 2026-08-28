---
name: pp2p
description: Performs two perfection passes plus polish for moderate code refinement with cleanup. Triggers on pp2p or two-pass polish requests.
---
# Perfection Pass x2 + Polish (/pp2p)

Two critique passes (3-4 agents each) + polish + a **cross-family** review gate. Thorough refinement for moderate-complexity work — the middle rung between `/critique` (single pass) and `/pp3p` (mega-hardening for auth/payments/data integrity).

> **Scoring contract:** critics score + verify with a consistent judge rubric. Discrete labels (BLOCKER / HIGH / MEDIUM / NIT), skeptical standalone stance, >=2-of-3 adversarial survival on contested high-stakes findings, stop after 2 flat cycles. Don't invent a per-pass rubric.

## Arguments

Parse `$ARGUMENTS` string:

| Arg | Effect |
|-----|--------|
| `--type TYPE` | Set review type: `code`, `plan`, `design`, `architecture`, `strategy` (auto-detected if omitted) |
| `--agents "A,B,C"` | Custom agent perspectives (defaults are per-type — see Step 5) |
| `--security` | Preset: Solution-Fit, Security, Edge Cases |
| `--performance` | Preset: Solution-Fit, Performance, Elegance |
| `--api` | Preset: Solution-Fit, API Design, Edge Cases |
| `--stack-reality` | Stack-Reality critic on its own — fact-check a doc/plan against known stack state (solo mode, see Step 5) |
| `--sequential` | Agents see each other's findings (slower but more coherent) |
| `--no-early-exit` | Disable early exit on convergence |
| `--files "path1,path2"` | Explicit file targets (skip context detection) |

**Time budget:** 15 minutes for the critique passes. If Pass 1 exceeds 10 min elapsed, apply its surviving findings and skip Pass 2. Polish, the mutation gate, and the cross-family gate are EXEMPT from this budget — they always run.

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

## Step 4: Create Run Marker

The marker lives at `.claude/perfection-pass.local.md` **in the project git root**. Skip it if cwd is outside a project.

Before creating:
1. **Stale-marker check:** if the file already exists, copy it to `.claude/perfection-passes/stale-{YYYYMMDD-HHMMSS}.md` (create the dir if needed) and delete the original.
2. **Gitignore check:** append `.claude/*.local.md` to `.gitignore` if no existing pattern covers it. The marker carries the full problem + findings and must not ride a `git add -A` into a repo.

Then create:

```markdown
---
iteration: 2
max_iterations: 2
include_polish: false
polish_done: true
review_type: <detected type from Step 2>
created_at: <ISO timestamp>
---

## Original Problem

[Problem statement from conversation]

## Current Solution

[The solution/files under review]
```

The pass loop runs INLINE (Step 6). The marker is a crash record, not a chaining mechanism. Append each pass's findings to the body as you go — but ONLY inside fenced code blocks. A bare `---` line or a column-0 `key:` line in the body corrupts YAML frontmatter parsers.

## Step 5: Select Agent Perspectives

Choose agents by detected type (unless `--agents` overrides):

**For plans (run all 4):**
1. **Completeness** — Are all steps defined? Missing prerequisites? Gaps between steps?
2. **Feasibility** — Can each step actually be executed? Unrealistic assumptions?
3. **Risk & Edge Cases** — What could go wrong? What's the fallback?
4. **Stack-Reality** — Every numeric claim, every "X requires Y GB", every "won't fit / can't run / needs X" must be cross-checked against the user's actual stack (CLAUDE.md, hardware/docs notes, what's already running). **If the claim contradicts what's already running, flag it.** See "Stack-Reality critic instructions" below.

**For code:**
1. **Solution-Problem Fit** — Does it solve the stated problem?
2. **Edge Cases & Gaps** — What could break?
3. **Elegance & Simplicity** — Can it be simpler?

**Auto-add when the change touches PERSISTENCE / STATE** (DB schema or writes, migrations, caches, vector stores, agent memory, or files-used-as-state): add a 4th critic (preferred), or replace **Elegance** with it only when under the time budget.
4. **State-Integrity** — Does it follow append-only / supersede-never-overwrite (no lossy in-place updates of data that should be historical), provenance on every derived value (no naked numbers), typed history not blurry chunks, HEAD-and-history move atomically, and never silently lose a fact? If the change overwrites state that someone would later ask "what was this before, and why did it change?" about — that's a finding.

**For architecture:**
1. **Separation of Concerns** — Clean boundaries? Right abstractions?
2. **Scalability & Evolution** — Will this grow well? Paint into corners?
3. **Integration Risk** — Dependencies, coupling, failure modes?

**For design:**
1. **User Flow** — Is the happy path clear? Dead ends?
2. **Consistency** — Patterns reused? Naming coherent?
3. **Edge States** — Empty, error, loading, overflow handled?

**For strategy:**
1. **Goal Alignment** — Do actions connect to stated goals?
2. **Prioritization** — Is sequencing justified? Dependencies right?
3. **Blind Spots** — What's not being considered?

Presets (override type-based defaults):
- `--security`: Solution-Fit, Security, Edge Cases
- `--performance`: Solution-Fit, Performance, Elegance
- `--api`: Solution-Fit, API Design, Edge Cases
- `--stack-reality`: **solo mode** — run ONE pass of the lone Stack-Reality critic with the verify gate as usual, then report. Skip polish, the mutation gate, and the cross-family loop unless its findings triggered actual edits — this is a fact-check, not a refinement run.

**Critic model — escalate for critical work.** Default to a fast/cheap tier for routine refinement; use the strongest available tier for critic agents when the change touches auth/permissions, money movement, migrations, or destructive/irreversible operations (or when `--security`/`--performance` presets are active). If the work is squarely in that territory, consider whether it should be a `/pp3p` run instead.

### Stack-Reality critic instructions (use verbatim in agent prompts when this critic fires)

You are the anti-bullshit critic. Your single job: **cross-check every numeric and capability claim in the work product against the user's actual stack.** Hardware sizing claims, model availability claims, "this requires X", "won't fit", "needs Y to run", repo-state claims, runtime version claims, pricing claims, project-URL claims — all subject.

**Process:**
1. Read CLAUDE.md, any `*ground*truth*` / hardware / stack notes in the repo, and whatever the user has already said is running. These exist specifically because models keep getting stack facts wrong.
2. Skim the work product. Highlight every:
   - Number (GB, MB, $, %, count, version)
   - "Won't fit" / "can't run" / "needs X" / "requires Y"
   - Model/repo/tool name asserted as available or unavailable
   - Architecture claim about the user's machines
   - Pricing / project URL / vendor state assertion
3. For each, verify against those notes + current state (`which`, package versions, `nvidia-smi` / `sysctl` / `uname` as relevant). If the notes or live state say the model/tool is already running, ANY "won't fit / can't run" claim is wrong — the correct framing is "fits at quant Y; speed Z is the real ceiling" or similar.
4. If you don't have enough info to verify (e.g., the doc claims a runtime version and nothing records it), say "needs verification via $command" rather than letting the claim stand.

**Output:** for each problem found, give:
- Quote (exact text from the work product)
- What's wrong (what reality contradicts the claim)
- Source of the contradiction (which file, which line, or which command output)
- Corrected framing (what the doc should say instead)

**Severity:** any claim that contradicts known ground truth is HIGH severity, even if cosmetic — these are exactly the errors that propagate into downstream decisions.

## Step 6: Run Pass Loop (2 passes)

For each pass (1, 2):

### 6a: Dispatch Critique Agents

Spawn one agent per selected critic — 3 for most types, 4 when the plan set or a persistence auto-add applies.

**Parallel** (default): Launch all simultaneously.
**Sequential** (`--sequential`): Launch one at a time, each sees prior findings.

Each agent prompt MUST include:
- The current solution (full text or file contents)
- The original problem statement
- Project context (CLAUDE.md excerpt)
- Their specific critique focus
- Instruction: "Return a numbered list of specific, actionable issues. If no issues found, return NONE."

### 6b: Verify, Then Apply

After all agents return:
1. Count raw issues across agents
2. **Adversarial verify gate.** Critic passes carry a measured ~20-30% false-positive rate at Pass 1. Take each HIGH/BLOCKER finding and try to *refute* it: re-read the actual code/diff, and for anything non-obvious, default to "not a real issue unless proven." A finding survives only if you can point to the exact line + a concrete failure it causes. Drop the rest with a one-line reason. On contested high-stakes findings (auth/payments/data), escalate to a pass@K consensus (sample the critic 3x, keep findings appearing in >=2 runs) rather than a single refute.
3. Print summary: `Pass N: X raw → Y surviving (per-agent: ...)`
4. If surviving issues == 0 AND early exit enabled (default): skip remaining critique passes and go to Step 7. Early exit skips CRITIQUE passes only — polish, the mutation gate, and the cross-family gate still run before the report.
5. Synthesize *surviving* findings into concrete improvements
6. Apply improvements (Edit files or revise solution); append findings + dropped-at-gate reasons to the run marker (inside fenced code blocks)
7. Continue to next pass with the UPDATED solution

### 6c: Error Handling

- If an agent returns empty/garbled: log it, continue with other agents' findings
- If ALL agents fail: STOP, report error, do not continue to next pass
- Never retry the same agent prompt — adjust focus if re-dispatching

## Step 7: Polish Pass

After both critique passes (or early exit), run ONE polish pass.

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

## Step 7.5: Mutation gate — "test the tests" (when the change adds/relies on a test suite)

A green test suite proves nothing until you prove it would go RED on a real bug.

**When it fires:** the change includes or depends on automated tests (a new suite, new test cases, or a behavior guarded only by tests). Skip for pure-doc / config-only changes. On an early-exit run where no fixes were applied, mutate the pre-existing behaviors the suite guards, or mark N/A.

**What to do:**
1. For each behavior the suite claims to cover, **revert the fix / inject the bug in a throwaway copy** and run the matching test. Assert it **fails**. A mutation that *survives* (test stays green against broken code) is a test gap — fix the test, not the code. The classic survivor is a test that **reimplements the logic inline instead of calling the real function** — extract the function and call it.
2. Prefer a **committed mutation driver** (copy sources to a tempdir, revert one fix, run its selector, assert non-zero exit; flag STALE when the target string moved so it can't silently rot) over one-off manual mutation — it stays a regression asset.
3. Report `N/N mutations caught`. Anything less than 100% is a gap to close before the cross-family gate.

**Receipt:** "X tests · Y/Y mutations caught" belongs in the pp2p summary alongside the cross-family verdict.

## Step 8: Cross-family Final Gate — LOOP until convergence

After polish completes, get an independent second opinion from a **different model family** than the one running this pass. If the Codex plugin is available, use `/codex:review`. Otherwise dispatch one review to GPT / Gemini / Grok / whatever isn't the session model. Do not hardcode a version — it rots.

**This is a LOOP, not a single shot.** A cross-family reviewer's first pass routinely surfaces the *next* layer once the first is fixed — keep combing until it comes back clean:

```
  repeat (cap = 3 cross-family passes):
    run the reviewer on the LATEST committed/working state
    ├─ BLOCKER / HIGH returned → adjudicate each (fix it, OR refute it on merit
    │                            and document why), then LOOP (run again)
    ├─ only NITs → apply inline or log as follow-up, then one more pass to
    │             confirm (the confirming pass counts toward the cap)
    └─ no new blockers → CONVERGED → proceed to report
  if still flagging blockers at the cap → STOP, document residuals + escalate to the user
```

Rules for the loop:
- **Each pass reviews the newest state**, so fixes from pass N are themselves reviewed in pass N+1 (no fix ships unreviewed).
- **Adjudicate, don't auto-accept.** A finding is either *fixed* or *refuted on merit with a one-line reason*. Disagreeing with the reviewer is allowed and expected.
- **Hold the scope line.** Adversarial review widens its net each pass; when a finding is real but a *different invariant / pre-existing / separate subsystem*, document it as a follow-up rather than letting it balloon the change. Convergence means "no new blockers *in scope*," not "the reviewer ran out of opinions."
- A different model family catches what self-critique misses — that's the whole point of looping it.

If no second model family is available, say so in the report and skip this gate rather than pretending a same-family re-read counts.

## Step 9: Report & Archive

1. Print final summary:

```
PP2P Complete
  Pass 1: X raw → X' surviving → applied
  Pass 2: Y raw → Y' surviving → applied (or: skipped — converged / time budget)
  Polish: N cleanups applied
  Mutation gate: Y/Y mutations caught (or: N/A — no test suite)
  Cross-family: converged in K pass(es) (or: skipped — no second family available)
  Total: X'+Y'+N pass/polish improvements (mutation + cross-family fixes counted on their own lines)
```

2. Archive report to `.claude/perfection-passes/pp2p_{topic}_{YYYYMMDD-HHMMSS}.md` (timestamped so same-day reruns never overwrite) containing:
   - Original problem
   - Issues found per pass (including findings dropped at the verify gate)
   - Final solution state

3. Delete `.claude/perfection-pass.local.md` BEFORE ending the turn.

## When to Use

- Moderate complexity features
- When you want thorough refinement AND clean code
- Balance between speed and quality
- NOT for auth/payments/data-integrity-critical work — use `/pp3p`
- NOT for trivial changes — use `/critique` (single pass)
