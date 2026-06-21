---
name: sprint-architect
description: Converts strategy documents, issue lists, or audits into dependency-aware agent-team execution boards. Produces wave-parallelized sprint boards with decision gates, capacity models, quality gates, and dispatcher protocols.
---

# Sprint Architect

Convert a strategy document or issue pile into a structurally sound agent-team execution board — dependency-validated, wave-parallelized, and ready for dispatch.

## When to Use

- Strategy doc or audit exists but no execution plan
- Issue backlog needs conversion to agent-dispatchable sprints
- Existing sprint board needs agent-team restructuring
- Team wants to parallelize work across AI agents with dependency safety

## When NOT to Use

- Single feature implementation (use `writing-plans`)
- Quick fix or bug patch (just code it)
- Exploratory research phase (use `deep-recon`)
- Plan already exists and just needs execution (use `executing-plans`)

## Relationship to Other Skills

```
writing-plans  →  sprint-architect  →  dispatching-parallel-agents
(single plan)     (execution board)     (wave dispatch)
                        ↓
                  executing-plans
                  (sequential fallback)
```

---

## Core Process

### Phase 1: Derive Strategy from Source

Read the source material and produce a master issues document with:

1. **Verified reality** — what actually exists, confirmed by reading code
2. **Workstreams** — grouped by concern (not by file or team)
3. **Decision gates** — human decisions that MUST resolve before implementation
4. **Dependency map** — hard vs soft dependencies between workstreams
5. **Acceptance criteria** — measurable per workstream

### Phase 2: Build the Execution Board

Convert the strategy into a YAML execution board with these required sections:

```
spec               → metadata, repo root, branch rules
capacity_model     → teams, SP budgets, utilization targets
operating_rules    → execution rules, handoff contracts, blocking rules
teams              → team definitions with owned paths
decision_gates     → human decisions with options + blocks arrays
sprints            → tickets grouped into waves within sprints
quality_gates      → named checks enforced at sprint boundaries
orchestrator       → now/next/later priority queue
agent_prompt       → dispatch template with capability auto-invokes
decision_protocol  → how human decisions get made and recorded
conflict_protocol  → how parallel agents avoid merge conflicts
capability_matrix  → which skills auto-invoke per ticket type
dispatcher         → how waves get dispatched and merged
```

### Phase 3: Validate

Run the validation checklist (see below) before declaring the board ready.

---

## Design Principles

### 1. Decision Gates Before Implementation

Human decisions that block implementation get their own ticket type (`DEC-*`). They are NOT implementation tickets — they require stakeholder judgment.

**Why:** Without locking decisions early, agents build on assumptions that get reversed. Every day a decision slips, its dependents cascade.

**Structure:**
```yaml
- id: "DEC-01"
  title: "Choose X vs Y"
  owner: "TEAM-PRODUCT"
  approver: "stakeholder name/role"
  deadline: "sprint-wave deadline"
  depends_on: []
  status: "pending"
  options:
    A: "Option A description"
    B: "Option B description"
  acceptance_criteria:
    - "Written policy documented with rationale"
    - "Impact on dependent tickets defined"
  blocks: ["TICKET-003", "TICKET-007"]  # forward reference
```

### 2. Bidirectional Dependency Tracking

Every `blocks` edge MUST have a reciprocal `depends_on` edge.

**Why:** One-directional tracking breaks silently. If DEC-01 says it blocks TICKET-003 but TICKET-003's `depends_on` doesn't list DEC-01, the dispatcher will schedule TICKET-003 prematurely.

**Validation rule:** For every ticket X in gate.blocks, ticket X.depends_on MUST contain gate.id. For every DEC-* in ticket.depends_on, that gate.blocks MUST contain ticket.id.

### 3. Wave-Parallel Execution

Sprints contain sequential waves. Within each wave, all tickets run in parallel.

**Why:** Pure parallelism causes merge conflicts. Pure sequential wastes capacity. Waves are the sweet spot — maximum parallelism within dependency-safe boundaries.

**Rules:**
- A ticket can only be in wave N if ALL its dependencies completed in wave N-1 or earlier
- No intra-wave dependencies (if A depends on B, they cannot share a wave)
- All agents in a wave merge to staging before next wave starts

**Template:**
```yaml
parallel_waves:
  - wave: "S1-W1"
    tickets: ["DEC-01", "DEC-02", "TICKET-004"]
    max_agents: 3
    rationale: "All dependency-free."
  - wave: "S1-W2"
    tickets: ["TICKET-001", "TICKET-006"]
    max_agents: 2
    rationale: "Unblocked by W1 decisions."
```

### 4. Capacity Modeling

Teams have agent counts and SP budgets with utilization targets.

**Why:** Without capacity modeling, sprints overcommit and everything slips. A 60% utilization target leaves room for blockers, reviews, and merge conflicts.

**Template:**
```yaml
capacity_model:
  team_sizes:
    TEAM-FE: { agents: 2, sp_per_sprint: 16, role: "UI/UX + state" }
    TEAM-BE: { agents: 2, sp_per_sprint: 16, role: "API + authz" }
  utilization_target: 0.6
  effective_sp_per_sprint: 38
  sprint_budget_summary:
    S1: { planned: 34, buffer: 4, headroom_pct: 12 }
  risk_note: "S2 is tight - if DEC-02 slips, downstream cascades."
```

### 5. File-Conflict Protocol

Identify hotspot files touched by multiple tickets and enforce merge discipline.

**Why:** `src/app/page.tsx` appearing in 10 tickets across 3 sprints will cause merge hell without protocol. Wave boundaries are merge checkpoints.

**Rules:**
- Identify files touched by 3+ tickets as hotspots
- Within a wave, if two tickets target the same hotspot, serialize them
- All agents rebase from staging before creating PR
- Wave merge sequence: merge in dependency order, run regression, advance

### 6. Quality Gates per Sprint

Named quality gates with specific checks enforced at sprint exit.

**Why:** Without exit criteria, sprints "finish" with regressions. Quality gates make sprint completion binary — either all checks pass or the sprint isn't done.

**Template:**
```yaml
quality_gates:
  - id: "QG-1"
    name: "Auth Safety"
    checks:
      - "No unauthorized access across roles"
    enforced_at: ["S2 exit", "S5 exit"]
```

### 7. Capability Auto-Invocation

Wire skills into the agent prompt template so agents invoke them automatically.

**Why:** Agents won't remember to run security reviews or TDD unless the prompt template mandates it. The template IS the quality enforcement.

**Matrix:**
```yaml
capability_auto_invoke:
  per_ticket_type:
    implementation:
      before_code: "test-driven-development"
      after_code: "verification-before-completion"
      before_pr: "pr-review-toolkit:code-reviewer"
    auth_changes:
      after_code: "security-sentinel"
    db_changes:
      after_code: "data-integrity-guardian"
```

### 8. Branch Strategy Alignment

The board's branch rules MUST match the repo's CLAUDE.md or branch protection rules.

**Why:** If the repo enforces `feature/ -> staging -> main` but the board says `codex/ -> main`, every agent PR will be rejected by GitHub.

**Validation:** Read the repo's CLAUDE.md FIRST. Extract the branch workflow. Set `branch_prefix` and `branch_workflow` to match exactly.

---

## Ticket Schema

```yaml
ticket_schema:
  required:
    - id           # unique identifier (PREFIX-NNN)
    - sp           # story points (fibonacci: 1,2,3,5,8,13)
    - days         # ideal engineer days (sp * 0.5)
    - owner        # team that owns execution
    - depends_on   # list of ticket/gate IDs that must be done first
    - status       # pending | in_progress | blocked | review | done
    - title        # what this ticket accomplishes
  optional:
    - support      # advisory teams
    - acceptance_criteria  # measurable DoD items
    - target_files         # files this ticket will modify
    - feature_flag         # flag name if behind toggle
    - branch      # branch name (filled on completion)
    - commit      # commit hash (filled on completion)
    - tests       # test results (filled on completion)
    - evidence    # DoD evidence (filled on completion)
```

## Agent Prompt Template

```yaml
agent_prompt_template:
  owner_prompt: |
    Ticket: {ticket_id}
    Role: {owner_team}
    Sprint: {sprint_id}
    Repo: {repo_root}
    Goal: Complete DoD for this ticket only.

    Constraints:
    - Respect dependencies: {depends_on}
    - Keep scope to files in owned paths unless justified.
    - Provide tests and evidence for each acceptance criterion.
    - Follow branch rules: {branch_workflow}
    - Create feature branch from staging: git checkout -b {branch_prefix}{ticket_id} staging
    - Use {package_manager} (NEVER {banned_package_managers})

    Capability auto-invokes (MANDATORY):
    - BEFORE writing code: write a failing test first (test-driven-development)
    - For any bug/error: use systematic-debugging
    - For any auth changes: invoke security-sentinel before marking done
    - For any DB schema changes: invoke data-integrity-guardian before marking done
    - BEFORE marking done: invoke verification-before-completion
    - BEFORE creating PR: invoke pr-review-toolkit:code-reviewer

    Required output:
    - Summary of change
    - Changed files
    - Test commands and results
    - Evidence per acceptance criterion
    - Risks/rollback notes
    - Handoff recommendation
    - Status update: {ticket_id} -> done | blocked (reason)
```

## Handoff Contract

Every completed ticket must output:
```yaml
handoff_contract:
  required_fields:
    - ticket_id
    - status          # done | blocked
    - changed_files   # list of files modified
    - tests_run       # test command + pass/fail count
    - evidence        # proof each AC is met
    - open_risks      # anything the next wave should know
    - next_ticket_recommendation  # what to dispatch next
```

---

## Validation Checklist

Run this BEFORE declaring the board ready:

### Dependency reciprocity
- [ ] For every DEC-* gate: each ticket in its `blocks` array has the gate in its `depends_on`
- [ ] For every ticket: each DEC-* in its `depends_on` lists the ticket in the gate's `blocks`
- [ ] DEC gates that depend on other DEC gates have reciprocal blocks/depends_on

### Wave scheduling
- [ ] Every ticket in wave N has ALL dependencies satisfied by wave N-1 or earlier
- [ ] No intra-wave dependencies (two tickets in the same wave where one depends on the other)

### Branch alignment
- [ ] `branch_prefix` matches repo's CLAUDE.md or branch protection rules
- [ ] `branch_workflow` matches repo's required PR flow (staging? direct to main?)
- [ ] Agent prompt template branch rule matches spec

### Capacity
- [ ] Sprint planned SP <= effective SP per sprint
- [ ] Risk notes identify tight sprints (< 5% headroom)

### Completeness
- [ ] All required sections present (spec through dispatcher)
- [ ] Every ticket has acceptance criteria
- [ ] Every sprint has exit criteria
- [ ] Quality gates have enforcement points

---

## Decision Gate Executor Protocol

Human decisions cannot be dispatched to code agents. Use this protocol:

1. **Prepare brief:** Agent generates `docs/decisions/{gate_id}-brief.md` with context, options, tradeoffs, recommendation, and impact analysis
2. **Present:** User takes brief to stakeholder (meeting, email, Slack)
3. **Record:** Persist decision in `docs/decisions/{gate_id}-record.md` with chosen option, rationale, date, approver
4. **Unblock:** Update gate status to `done`, dispatcher identifies newly unblocked tickets

---

## Output Format

```
SPRINT_ARCHITECT: Board generated for {project_name}
METRIC: sprints={count}
METRIC: tickets={count}
METRIC: decision_gates={count}
METRIC: quality_gates={count}
METRIC: dependency_edges={count}
VALIDATION: {pass_count}/{total_checks} checks passed
DETAILS: {path_to_board_file}
```

If validation fails:
```
VALIDATION_FAIL: {check_name} - {description of failure}
```

---

## Integration

**REQUIRED SUB-SKILLS:**
- `writing-plans` (for the strategy doc phase)
- `dispatching-parallel-agents` (for wave execution)
- `executing-plans` (sequential fallback)
- `test-driven-development` (wired into agent prompt)
- `verification-before-completion` (wired into agent prompt)
