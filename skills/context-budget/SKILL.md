---
name: context-budget
description: Audit token consumption across all loaded components — skills, agents, MCP tools, rules, hooks
---

# Context Budget Audit

Estimate how much of your context window is consumed by the agent harness infrastructure vs actual work.

## When to Use
- Context feels heavy or compacting frequently
- Adding new skills/MCPs and want to know the cost
- Optimizing which components stay loaded

## Process

### 1. Inventory All Loaded Components

Run these in parallel:

**Enabled plugins (each can add MCP tools):**
```bash
# Count enabled plugins; each MCP tool a plugin adds costs ≈ 500 tokens of schema
cat ~/.claude/settings.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
# Count enabled plugins
plugins = {k:v for k,v in d.get('enabledPlugins',{}).items() if v}
print(f'Enabled plugins (MCP tools not counted): {len(plugins)}')
for p in plugins: print(f'  - {p}')
"
```

**Installed skills:**
Count `~/.claude/skills/*/SKILL.md` plus the project's `.claude/skills/*/SKILL.md`:
```bash
find -L ~/.claude/skills .claude/skills -mindepth 2 -maxdepth 2 -name SKILL.md 2>/dev/null | wc -l
```
Each skill listing in the system prompt ≈ 100-200 tokens.

**Agent definitions:**
Each agent defined in `~/.claude/agents/` ≈ 300-800 tokens when loaded.

**Hook definitions:**
Each hook in settings.json ≈ 50-100 tokens.

### 2. Estimate Token Budget

| Component | Per-Unit Estimate | Count | Total |
|-----------|------------------|-------|-------|
| MCP tool schema | ~500 tokens | ? | ? |
| Skill listing (system prompt) | ~150 tokens | ? | ? |
| Agent definition | ~500 tokens | ? | ? |
| Hook definition | ~75 tokens | ? | ? |
| CLAUDE.md | measure directly | 1 | ? |
| MEMORY.md | measure directly | 1 | ? |

**Key insight from [everything-claude-code](https://github.com/affaan-m/everything-claude-code) (Affaan Mustafa):** "Your 200k context window before compacting might only be 70k with too many tools enabled."

### 3. Classify Components

For each component, classify:
- **Always:** Core workflow, used every session
- **Sometimes:** Domain-specific, used in certain projects
- **Rarely:** Niche, could be loaded on-demand

### 4. Recommendations

- Keep MCP servers under 10 enabled / under 80 total tools
- Move "Rarely" skills to on-demand invocation
- Consider disabling MCP servers you use < once/week
- Check if any plugins overlap in functionality

## Output Format

```
CONTEXT BUDGET AUDIT: {date}
═══════════════════════════════
Estimated infrastructure overhead: ~{N}k tokens
Estimated available for work: ~{M}k tokens ({P}% of 200k)

TOP CONSUMERS:
1. {component}: ~{N} tokens
2. {component}: ~{N} tokens
...

RECOMMENDATIONS:
- {action}
```

## Source

Inspired by Affaan Mustafa's everything-claude-code (https://github.com/affaan-m/everything-claude-code).
