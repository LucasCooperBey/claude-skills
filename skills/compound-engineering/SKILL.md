---
name: compound-engineering
description: Connected analyze-plan-execute-learn-repeat cycle with persistent memory. The human-in-the-loop version of Ralph for improving existing projects.
---
# Compound Engineering

A self-improving development loop that compounds knowledge across sessions.

## When to Use

- Improving an existing project iteratively
- After shipping v1 and entering optimization mode
- When you have error logs, user feedback, or analytics to act on
- When you want each fix to inform the next one
- For sustained improvement over multiple sessions

## When NOT to Use (Use Ralph Instead)

- Building from scratch with clear specs → Ralph
- Need autonomous overnight builds → Ralph
- Working in sandbox/VM → Ralph

## Quick Start

```
/compound                    # Full loop: analyze → plan → execute → learn → compound
/compound analyze            # Just run analysis phase
/compound plan               # Plan from existing analysis (requires prior analysis)
/compound execute            # Execute existing plan (requires prior plan)
/compound learn              # Run learning phase (requires prior execution)
/compound report             # Generate cycle report
```

## The 5-Phase Loop

**ANALYZE → PLAN → EXECUTE → LEARN → COMPOUND → (repeat)**

### Phase 1: ANALYZE — What needs fixing most?

**Inputs to consider:**
- Error logs (Sentry, console, server logs)
- User feedback (support tickets, reviews, direct messages)
- Analytics (PostHog, usage metrics)
- Test failures (CI/CD, local test runs)
- Performance data (load times, API response times)
- Previous learning log (`LEARNINGS.md`)
- Tech debt backlog

#### Pre-Computed Summary Stats

Gather stats directly — run test suite, check for type errors, scan logs:

```bash
# Run tests and capture counts
bun test 2>&1 | tail -5
# Check TypeScript errors (if applicable)
bunx tsc --noEmit 2>&1 | tail -5
# Recent errors in logs (if available)
tail -50 /var/log/app.log 2>/dev/null || echo "No log file found"
```

**Process:**
1. Generate `.compound-stats` (once)
2. Gather available signals (error rates, user complaints, test flakes)
3. Score each issue by impact: `severity x frequency x user-facing`
4. Pick the single highest-impact improvement
5. Document in analysis template

**If no clear priority emerges:** Don't force it. Report "no high-impact issues found" and recommend running `techdebt` scan or asking the user for specific pain points. A cycle with no action is better than a cycle that fixes nothing important.

**Output:** `~/.claude/artifacts/analysis/YYYY-MM-DD-compound/analysis.md`

```markdown
## Analysis: [Date]

### Signal Review
- Errors: [summary of error patterns]
- Feedback: [summary of user complaints]
- Tests: [flaky or failing tests]
- Performance: [bottlenecks identified]

### Priority: [The #1 Thing]
**Impact score:** [severity] x [frequency] x [user-facing] = [total]
**Why this first:** [justification]
**Scope:** [estimated size: small/medium/large]
```

### Phase 2: PLAN — How do we fix it?

1. **If non-trivial:** Invoke `deep-recon` first (has this been solved before?)
2. **Always:** Invoke `writing-plans` with:
   - Analysis output as context
   - Research brief (if recon was run)
   - Previous learnings (from `LEARNINGS.md`)
3. **Goal-driven:** Every task in the plan gets success criteria

**Output:** Implementation plan (standard `writing-plans` output)

### Phase 3: EXECUTE — Build it

1. **Choose executor:**
   - `executing-plans` — default for sequential, well-scoped plans (≤5 tasks)
   - `subagent-driven-development` — for plans with 3+ independent tasks that can parallelize
2. Quality gates between tasks (tests, types, lint)
3. Goal-driven execution: loop until success criteria met
4. Commit after each task

**If execution fails:** Don't retry the same approach more than twice. Escalate: check if the plan was wrong (return to Phase 2), or if the analysis missed something (return to Phase 1). Document what failed in the learning log either way.

**Output:** Working code with passing tests

### Phase 4: LEARN — What did we discover?

After execution, append to project `LEARNINGS.md`:

```markdown
## [Date] — [What was improved]

### What worked
- [thing that went well]

### What didn't
- [thing that was harder than expected]

### Patterns discovered
- [new pattern worth remembering]

### Avoid next time
- [anti-pattern encountered]

### Time spent
- Analysis: [X min]
- Planning: [X min]
- Execution: [X min]
- Total: [X min]
```

Also update project `CLAUDE.md` if a new project-specific pattern emerged.

### Phase 5: COMPOUND — Set up the next cycle

Generate a cycle report:

```markdown
## Compound Cycle Report — [Date]

### What improved
- [specific metric or behavior that got better]

### Verification
- [command output proving improvement]

### Next priority
Based on remaining signals:
1. [Next highest-priority issue]
2. [Runner-up]
3. [Third option]

### Recommendation
[Which to tackle next and why]
```

If user approves → loop back to Phase 1 with the next priority.

## Persistent Files

| File | Location | Purpose |
|------|----------|---------|
| `LEARNINGS.md` | Project root | Persistent learning log across all cycles |
| `analysis.md` | `~/.claude/artifacts/analysis/` | Current cycle analysis |
| `compound-report.md` | `~/.claude/artifacts/reports/` | Cycle completion reports |

## Comparison with Ralph

| Aspect | Compound | Ralph |
|--------|----------|-------|
| Context | Persistent learning log | Fresh per iteration |
| Human | In the loop (approves each phase) | AFK (autonomous) |
| Scope | Incremental improvement | Full build from spec |
| Safety | Normal dev environment | Sandbox required |
| Memory | Learns across sessions | No cross-session memory |
| Use when | Improving existing code | Building from scratch |

## Success Criteria

A compound cycle is complete when:
- [ ] One measurable improvement was shipped
- [ ] All tests pass
- [ ] Learning log was updated with insights
- [ ] Next priority was identified and documented
- [ ] Cycle report saved to artifacts

## Model Routing

- Analysis phase: `opus` (prioritization requires judgment)
- Planning phase: `opus` (architectural decisions)
- Execution phase: `sonnet` (implementing well-defined tasks)
- Learning phase: `sonnet` (documenting what happened)
- Report synthesis: `opus` (connecting improvement to metrics)

## Integration Points

| Skill | Role |
|-------|------|
| `deep-recon` | Research phase when problem is non-trivial |
| `writing-plans` | Creates implementation plan in Phase 2 |
| `executing-plans` | Runs plan in Phase 3 |
| `subagent-driven-development` | Alternative executor for Phase 3 |
| `verification-before-completion` | Ensures claims have evidence |
| `test-driven-development` | Execution follows TDD |

---

## Related Context

- [agent-guardrails.md](../../context/agent-guardrails.md) - Time budgets, retry limits
- [output-markers.md](../../context/output-markers.md) - Standard output format
- [validation-oracles.md](../../context/validation-oracles.md) - Baseline validation
