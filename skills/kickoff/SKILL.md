---
name: kickoff
description: Full workflow orchestrator. Use when starting substantial work that benefits from research, planning, and structured execution. Chains recon → teardown → compound → execute → learn.
---
# Kickoff — Full Workflow Orchestrator

Single command to run the complete Research → Analyze → Plan → Code → Review → Learn → Compound pipeline.

## When to Use

- Starting a non-trivial feature or project
- Facing a hard problem where existing solutions might exist
- Want the full power of the research + compound workflow
- Any time you'd normally jump straight to coding on something complex

## Invocation

```
/kickoff [problem or feature description]

Examples:
/kickoff add real-time collaborative editing to the app
/kickoff build a PDF invoice generator with custom templates
/kickoff implement OAuth2 with Google and GitHub providers
/kickoff fix the performance bottleneck in the dashboard API
```

## The Pipeline

```
CLARITY → RECON → TEARDOWN? → ANALYZE → PLAN → EXECUTE → LEARN → COMPOUND
 ambiguity  research  study refs  prioritize  write plan  TDD build  log findings  next cycle?
  gate
```

**Time budget:** Target 60–90 min total. If any phase exceeds 20 min, checkpoint with user.

**Abort:** User can say "stop" or "skip to [phase]" at any gate. Respect immediately.

### Phase 0: CLARITY GATE (ambiguity scoring)

Before any execution, score how well-defined the request is. This prevents the #1 waste: executing on vague requirements.

**Skip if:** Request already has specific file paths, clear acceptance criteria, and obvious scope (score would be < 0.20).

**Ambiguity dimensions** (scored 0.0 = unknown → 1.0 = crystal clear):

| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Intent | 30% | WHY the user wants this |
| Outcome | 25% | WHAT end state they want |
| Scope | 20% | HOW FAR the change should go |
| Constraints | 15% | Technical or business limits |
| Success Criteria | 10% | HOW completion will be judged |

**Formula:** `ambiguity = 1 - (intent × 0.30 + outcome × 0.25 + scope × 0.20 + constraints × 0.15 + success × 0.10)`

**Threshold:** `<= 0.20` before proceeding to Phase 1.

**Rules:**
- Ask ONE question per round, targeting the weakest dimension
- Max 8 rounds (then proceed with explicit risk warning)
- Gather codebase facts via Glob/Grep/Read BEFORE asking user about them
- Show score after each answer so user sees progress
- Intent and scope questions come FIRST, implementation detail LAST

**Example round:**
```
Round 3 | Target: Scope | Ambiguity: 42%

I see the project has 5 document types but only field_report has the full
editing pipeline. Should this change cover all 5 types, or just field reports?
```

**Pre-context snapshot:** Save brief context to `~/.claude/artifacts/context/{slug}-{timestamp}.md` before starting. This enables resuming kickoff across sessions.

**Gate:** When ambiguity <= 0.20, announce score breakdown and proceed to Phase 1.

### Phase 1: RECON (automatic)

Dispatch the deep-recon research swarm:

```
Invoke the deep-recon skill with: [problem description]

4 parallel agents search for:
- Existing packages/solutions
- Community discussions (Reddit, HN, SO, Substack)
- Documentation and tutorials
- Source code analysis of top solutions
```

**Output:** Research brief saved to `~/.claude/artifacts/research/`

**Gate:** Present research findings to user. Ask:
- Should we use an existing solution?
- Should we study any of these solutions deeper? (→ teardown)
- Should we build from scratch with patterns from research?

**If recon finds nothing useful:** Skip teardown, proceed to Analyze with what you know from the codebase.

### Phase 2: TEARDOWN (conditional)

Only if research found apps/packages worth studying deeper:

```
Invoke: /teardown [solution found in recon]

Methods available:
- macOS app bundle analysis
- NPM/PyPI package source code analysis
- GitHub repo architecture analysis
- Web app browser analysis
```

**Output:** Teardown report saved to `~/.claude/artifacts/research/teardowns/`

**If teardown fails** (private repo, binary-only, paywalled): Note what was inaccessible and proceed to Analyze with available information.

**Gate:** Present teardown findings. Confirm approach before planning.

### Phase 3: ANALYZE

Score the problem and select priority:

```
Use the compound-engineering skill's analyze phase.

Inputs:
- Research brief from Phase 1
- Teardown findings from Phase 2 (if any)
- Current project state (errors, tests, feedback)
- Previous LEARNINGS.md entries
```

**Output:** Analysis with priority matrix and selected approach.

### Phase 4: PLAN

Write implementation plan with research context:

```
Invoke: writing-plans skill

Inputs:
- Analysis output
- Research brief (patterns to adopt)
- Teardown findings (architecture to reference)

Every task gets:
- Specific success criteria
- Verification commands
- Reference to research findings
```

**Output:** Implementation plan with goal-driven success criteria per task.

**Gate:** Present plan to user for approval before execution.

### Phase 5: EXECUTE

Build it using goal-driven execution:

```
Invoke: executing-plans or subagent-driven-development

For each task:
1. Define success criteria
2. Write test first (TDD)
3. Implement
4. Loop until ALL criteria pass
5. Commit
```

**Quality hooks fire automatically:**
- Type check after every edit
- No `any` types enforcement
- Auto-format
- Quality gate blocks commits until clean

### Phase 6: LEARN

Update persistent learning log:

```
Use compound-engineering's learn phase.

Append to project LEARNINGS.md:
- What worked
- What didn't
- Patterns discovered
- Time spent per phase
```

### Phase 7: COMPOUND

Generate cycle report and suggest next improvement:

```
Use compound-engineering's report phase.

Output:
- What improved (with verification evidence)
- Next priority recommendation
- Cycle metrics
```

**If more work to do:** Loop back to Phase 3 (Analyze) with user approval.

## Adaptive Shortcuts

Not every problem needs every phase. The kickoff auto-adapts:

| Problem Type | Phases Used |
|-------------|------------|
| Complex new feature | All 7 phases |
| Known problem, unclear solution | Recon → Plan → Execute → Learn |
| Improvement to existing feature | Analyze → Plan → Execute → Learn |
| Bug fix with research needed | Recon → Execute → Learn |
| Simple bug fix | Skip kickoff, just fix it |

**Detection criteria for skipping phases:**
- **Skip recon:** You already know the solution space (internal bug fix, well-understood library)
- **Skip teardown:** Recon found no comparable implementations worth studying
- **Skip entirely:** Problem touches ≤3 files, solution is obvious, no architectural decision needed — just fix it directly

## User Checkpoints

The pipeline pauses for user input at these gates:

1. **After RECON** — "Build, buy, or study deeper?"
2. **After PLAN** — "Does this plan look right?"
3. **After EXECUTE** — "Everything working?"
4. **After COMPOUND** — "Continue to next improvement?"

## Model Routing

| Phase | Model | Why |
|-------|-------|-----|
| Recon lead | opus | Synthesizing research |
| Recon agents | sonnet | Fast parallel search |
| Teardown scanning | sonnet | Pattern matching |
| Teardown synthesis | opus | Architecture analysis |
| Analyze | opus | Priority judgment |
| Plan | opus | Architectural decisions |
| Execute (implementers) | sonnet | Well-defined tasks |
| Learn | sonnet | Documentation |
| Compound report | opus | Connecting metrics |

## Integration

This skill orchestrates all other skills:

```
kickoff
├── deep-recon (Phase 1)
│   ├── package-research
│   └── dispatching-parallel-agents
├── app-teardown (Phase 2)
├── compound-engineering (Phases 3, 6, 7)
│   ├── writing-plans (Phase 4)
│   └── executing-plans / subagent-driven-development (Phase 5)
│       ├── test-driven-development
│       ├── verification-before-completion
│       └── goal-driven execution
└── finishing-development-branch (when done)
```
