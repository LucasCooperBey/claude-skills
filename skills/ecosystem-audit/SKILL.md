---
name: ecosystem-audit
description: Audit your entire .claude ecosystem (skills, agents, slash commands, hooks, rules, memory) for duplicates, overlapping capabilities, stale one-off demos, contradictory rules, and context bloat. Use ~monthly or when things feel cluttered — "audit my .claude", "find duplicate skills", "what's stale", "ecosystem audit", "clean up my agents", "find contradictory rules". Returns a low/medium/high prioritized fix list with reasons and exact paths.
---

# Ecosystem Audit

This fans out many agents and needs the Workflow tool with explicit opt-in.

Periodic hygiene for a sprawling agentic OS. Inspired by Mark Kashef's third dynamic-workflow use case (YT 9_ExDZFlaNc): as you keep adding skills/agents/rules, things go stale and contradictory, and you never have time to revisit. Fan out agents to find the rot.

## When to run

Sporadically — every couple weeks to monthly. NOT daily. It burns tokens via fan-out. Differs from `capabilities` (which counts/indexes what exists) and `agent-enlightenment` (which designs new agents): this one finds what to **delete, merge, or fix**.

## The recipe

### 1. Deterministic inventory (zero LLM tokens)

```bash
# Skills
find ~/.claude/skills -maxdepth 2 -name 'SKILL.md' | wc -l
# Slash command name collisions (the foo-bar vs foo:bar pattern)
ls ~/.claude/commands | sed -E 's/[-:]/ /' | awk '{print $1}' | sort | uniq -d
# Agents (active vs dormant)
ls ~/.claude/agents/*.md ~/.claude/agents/dormant/*.md
# Memory files
find ~/.claude/projects/*/memory -name '*.md' | wc -l
# Hook surface
jq '.hooks' ~/.claude/settings.json
```

### 2. Fan-out finders (Workflow tool, explicit opt-in)

Run finders in parallel, each scoped to one rot type:

- **duplicate-skill-finder** — same capability under different names; stock Anthropic skills copied multiple times; plugin variants shadowing local skills (your CLAUDE.md may already flag certain skills as existing multiple times).
- **stale-demo-finder** — skills/agents created for one demo/video and never used again. Cross-reference names against the tool-use histogram from a session mine — a `Skill` invocation count of 0 for a skill = never fired.
- **command-collision-finder** — duplicate slash commands (e.g., `dev-<project>` vs `dev:<project>`, `db-reset-*` vs `db:reset-*`, aliased save commands like `sv`/`save`/`svg`/`svgg`).
- **rule-contradiction-finder** — contradictory or superseded rules across CLAUDE.md + context files + memory files (e.g., a rule that says "never push to main" vs a per-project exception; superseded branching guidance).
- **dormant-bloat-finder** — dormant agents that will never wake; orphaned hooks pointing at deleted scripts.

### 3. Synthesis → prioritized fix list

One synthesis agent merges findings into:

- **HIGH** — actively costs context/tokens every session, or causes wrong behavior (duplicated always-on skills, contradictory load-bearing rules).
- **MEDIUM** — clutter that degrades discoverability (duplicate commands, stale demos).
- **LOW** — cosmetic / nice-to-have.

Each item: what, where (exact path), why it's a problem, recommended action (delete / merge / rename / fix), and rollback note for anything destructive.

## Guardrails

- **Read before recommending deletion.** A skill/agent that looks stale may be load-bearing for a hook or cron. Cross-check against `settings.json` hooks, launchd, and cron before flagging for delete.
- Output is a report, not auto-deletion. Destructive cleanup is a separate, narrated step.
- Enumerate matches and sniff size before any `rm` — never bulk-delete blind.

## Workflow reliability (learned in practice)

The finder agents do heavy investigation (Read/Grep/Bash) — forcing a `schema` on them is fragile (some fail the first run). Prefer: finders return MARKDOWN findings, a synthesis agent structures them; OR end each finder prompt with "Your FINAL action MUST be the StructuredOutput call." Also: the orphaned-hook + memory-contradiction dimensions are cheaper done deterministically (jq over settings.json hooks + test -f each script; grep MEMORY.md links vs files) than via agents.

## Source

Inspired by Mark Kashef's Dynamic Workflows Prompt Pack (https://markkashef.gumroad.com/l/dynamic-workflows-prompt-pack-claude), use case 3, "The Setup Audit".
