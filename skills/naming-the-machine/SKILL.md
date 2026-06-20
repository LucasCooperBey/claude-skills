---
name: naming-the-machine
description: Scan skills, tools, workflows, and infrastructure to identify and name emergent expressions of value — products, methodologies, brands, or IP assets hidden in existing systems. Triggers on "what have I built," "find products in my systems," "audit for marketable expressions," or "name everything."
---

# Naming the Machine

## Invocation

`naming-the-machine [infrastructure|projects|workflows]`

Default: full audit. Unrecognized scopes fall back to full audit.

## Signal Levels

| Level | Definition | Test |
|-------|-----------|------|
| **Named** | Functioning system, unlabeled. 3+ active components producing output today | Could you demo it right now? |
| **Emergent** | Repeating pattern producing value across multiple sessions or projects | Would you notice if it disappeared? |
| **Nascent** | 1-2 components exist, others hypothetical | Can you describe the missing piece? |

## Execution

### Scan

Start from what exists, skip what doesn't, never error on missing paths.

**Sources** (check all that exist; scope narrows which to prioritize):
- **Always:** CLAUDE.md, skills index, context files, memory files
- **Projects:** Git repos or dirs with `CLAUDE.md`/`package.json` -- prefer diversity over recency, cap at 20, read READMEs/architecture docs only
- **Infrastructure:** Cron jobs (`crontab -l`), systemd services, MCP configs, tool registries
- **Workflows:** Slash command tables, agent dispatch patterns, session save/load patterns

Use subagents for parallel scanning. Read structure first; drill into files only when they show signals. First run: scan broadly. Subsequent runs: focus on changes since last run.

**Cross-scope stitching:** After scanning individual layers, look for patterns that span layers (e.g., a cron -> agent -> skill chain). Composite patterns are often the most valuable and least visible.

### Disqualify

A pattern must pass all three gates:

1. **3+ distinct components** — single tools or configs don't qualify; aliases for the same thing don't count as separate components
2. **Repeating** — used across multiple sessions, projects, or time periods (within-session recurrence alone is insufficient)
3. **Referenced or reused** — the user has invoked, described, or built on this pattern (not just theoretically valuable)

If it involves client work, annotate "verify IP ownership" but don't disqualify.

### Name

For each surviving pattern:

```
## [Working Title]
**Signal:** named | emergent | nascent
**Value lever:** One sentence — what outcome does this arrangement produce?
**Next action:** Ship it / name it publicly / add [specific missing piece] / watch it
```

For **named** items, add: **Linchpin** — the one component that, if pulled, the whole arrangement falls apart.

**Naming guidelines:** Name the value, not the mechanism. Two words preferred, three max. It should make someone ask "what's that?"

### Summary Matrix

```
| # | Working Title | Signal | Value Lever | Next Action |
|---|--------------|--------|-------------|-------------|
```

Sort: named → emergent → nascent.

### Persist and Diff

Save to `<your-output-dir>/naming-YYYY-MM-DD.md`. On first run, just save.

On subsequent runs, find the most recent prior file and diff:
- **New** — not in prior run
- **Promoted** — signal level increased
- **Retired** — in prior run, no longer present

Include delta in output.

## Output

```
NAMING COMPLETE: [count] expressions identified
named=[n] emergent=[n] nascent=[n]
DELTA: [n] new, [n] promoted, [n] retired (omit on first run)
```
