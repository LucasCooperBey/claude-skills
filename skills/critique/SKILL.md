---
name: critique
description: Single-pass 3-agent critique for ANY work product — plans, code, designs, architecture. The general-purpose refinement tool.
---
# Critique (/critique)

Single-pass 3-agent critique that works on **any work product** — plans, code, designs, architecture, specs, strategies.

Unlike `/simplify` (code-only), this works on everything.

## Arguments

| Arg | Effect |
|-----|--------|
| `--type TYPE` | Force type: `code`, `plan`, `design`, `architecture`, `strategy` (auto-detected if omitted) |
| `--agents "A,B,C"` | Custom agent perspectives |
| `--security` | Preset: Solution-Fit, Security, Edge Cases |
| `--performance` | Preset: Solution-Fit, Performance, Elegance |
| `--apply` | Auto-apply improvements (default: present findings and ask) |

## Instructions

### Step 1: Identify the Work Product

Find what to critique from context:
- Plan file in conversation or referenced path
- Code in recent conversation or uncommitted changes
- Design/architecture document
- Any substantive work product

If nothing found:
> "Nothing to critique. Point me at a file, paste content, or describe what to review."
Then STOP.

### Step 2: Detect Type

If `--type` not specified, auto-detect:
- Has code blocks with implementation → `code`
- Markdown with ## headers, task lists, steps → `plan`
- Discusses components, interfaces, data flow → `architecture`
- UI/UX layouts, wireframes, component specs → `design`
- Business goals, roadmap, priorities → `strategy`
- Default: `plan`

**Key difference from /simplify: default is `plan`, not `code`.**

### Step 3: Select Agent Perspectives by Type

**For plans:**
1. **Completeness** — Are all steps defined? Missing prerequisites? Gaps between steps?
2. **Feasibility** — Can each step actually be executed? Unrealistic assumptions?
3. **Risk & Edge Cases** — What could go wrong? What's the fallback?

**For code:**
1. **Solution-Problem Fit** — Does it solve the stated problem?
2. **Edge Cases & Gaps** — What could break?
3. **Elegance & Simplicity** — Can it be simpler?

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

Custom agents override these defaults.

### Step 4: Dispatch 3 Agents in Parallel

Use the Agent tool (subagent_type: general-purpose) to spawn 3 critique agents.

Each agent prompt includes:
- The work product (full text)
- Their specific critique focus
- The detected type
- Project context (CLAUDE.md excerpt if available)
- Instruction: "Return a numbered list of specific, actionable findings. No fluff. Each finding must include: what's wrong, why it matters, and a concrete fix."

### Step 5: Synthesize & Present

Collect all agent findings. Deduplicate. Group by severity:

```
## Critique Results (TYPE)

### Critical (must fix)
1. [Finding] — [Fix]

### Important (should fix)
1. [Finding] — [Fix]

### Minor (nice to have)
1. [Finding] — [Fix]

### Verdict
X critical, Y important, Z minor findings across 3 perspectives.
```

### Step 6: Apply or Report

**If `--apply` flag or type is `code`:**
- Apply improvements directly
- Show diff summary

**If type is `plan`, `design`, `architecture`, `strategy`:**
- Present findings and ask: "Apply these improvements?"
- If yes, revise the work product inline

## When to Use

- After writing a plan (before executing)
- After drafting architecture or design docs
- Quick single-pass code review (lighter than /pp2p)
- Strategy documents and roadmaps
- Any time you want 3 perspectives on non-code work

## Comparison

| Skill | Passes | Works On | Polish Phase |
|-------|--------|----------|-------------|
| `/simplify` | 1 | Code only | No |
| `/critique` | 1 | Everything | No |
| `/pp2p` | 2 | Everything | Yes |
| `/pp3p` | 3 | Everything | Yes |
