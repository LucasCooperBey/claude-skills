---
name: deep-recon
description: Multi-agent research swarm that finds existing solutions before you write a single line of code. Prevents reinventing the wheel.
---
# Deep Recon

Research swarm that scours the internet for existing solutions before you build anything.

**Time budget:** 10 min total. Abort if no useful results after 5 min of searching.

## When to Use

- Before building anything non-trivial
- When `brainstorming` identifies a hard problem
- When you suspect the problem has been solved before
- Before writing an implementation plan
- When evaluating build vs buy decisions

## Quick Start

```
/deep-recon [problem description]

Examples:
/deep-recon real-time collaborative editing for a web app
/deep-recon email deliverability monitoring system
/deep-recon AI agent orchestration with tool use
```

The problem description is passed as `$ARGUMENTS`. If empty, ask the user what to research.

## The Process

### Phase 1: Decompose (Lead Agent)

Parse `$ARGUMENTS` into 3-5 searchable questions. Also identify:
- **Domain:** What field is this in?
- **Frameworks:** What tech stack constraints exist?
- **Core challenge:** What's the hard part?

### Phase 2: Dispatch Research Agents (parallel)

Launch 3 agents in parallel using the Task tool with `subagent_type: "general-purpose"` and `model: "sonnet"`.

**Agent 1 — Solution Scout:** Find packages, repos, and services.
- `WebSearch` for "[problem] library [framework]", "[problem] open source github", "[problem] SaaS API"
- `WebFetch` top results for details (stars, last commit, license)
- Output: Ranked list with name, URL, pros/cons, maintenance status

**Agent 2 — Community Intel:** Find real developer discussions.
- `WebSearch` targeting reddit.com, news.ycombinator.com, stackoverflow
- `WebFetch` top 3-5 threads for detailed reading
- Output: Community consensus, pitfalls, "I wish I'd known" quotes

**Agent 3 — Doc Collector:** Find docs, tutorials, educational content.
- `WebSearch` for "[solution] docs", "[problem] tutorial [year]", "[problem] best practices"
- `WebFetch` top doc pages for summaries
- Output: Curated links ranked as must-read / useful / deep-dive

### Phase 3: Code Analyzer (sequential, after Phase 2)

This runs AFTER Phase 2 because it needs Solution Scout results as input.

Launch one agent (`sonnet`) to analyze the top 2-3 solutions found:
- Use `WebFetch` on GitHub repos to read READMEs and key source files
- Use `WebSearch` for "[package] architecture" or "[package] how it works"
- Report: Architecture pattern, key abstractions, how they handle the core challenge, adoptable patterns

### Phase 4: Synthesize (Lead Agent)

Merge all agent outputs into a research brief using the template at `templates/research-brief.md`.

Save to: `<your-output-dir>/research/YYYY-MM-DD-[topic]/research-brief.md`

Be opinionated — recommend ONE approach and defend it with evidence.

### Phase 5: Feed into Planning

The research brief becomes input for `writing-plans`:
- Package solves 80%+ → recommend using it
- No good solution → plan includes key patterns from research
- Open questions → items to resolve during planning

## Error Handling

- **No search results:** Broaden terms, drop framework constraint, try synonym. After 2 empty rounds, note gap and move on.
- **Agent returns garbage:** Discard, note in brief as "insufficient data for [area]".
- **Problem too broad:** Split into sub-problems, recon each separately (max 2 splits).
- **All solutions are bad:** That's a valid finding. Brief should say "build from scratch" with rationale.

## Success Criteria

- [ ] At least 3 existing solutions evaluated (or documented why fewer exist)
- [ ] Community sentiment captured
- [ ] Recommended approach with justification
- [ ] Research brief saved to artifacts
- [ ] Open questions identified

## Integration Points

| Skill | Relationship |
|-------|-------------|
| `brainstorming`, if you have it | Triggers recon for non-trivial problems |
| the `writing-plans` skill in this repo | Receives research brief as input |
| `app-teardown`, if you have it | Code Analyzer can use teardown methods for deep analysis |
| the `package-research` skill in this repo | Solution Scout can delegate to this for npm/pypi specifics |
| the `compound-engineering` skill in this repo | Analysis phase triggers recon when needed |

## Model Routing

- Lead agent (decompose + synthesize): `opus`
- Solution Scout / Community Intel / Doc Collector: `sonnet`
- Code Analyzer: `sonnet`
