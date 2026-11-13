# context-budget

A Claude Code skill that estimates how much of the context window your setup uses before any work starts. It counts enabled plugins, installed skills, agents, hooks, CLAUDE.md and MEMORY.md, puts a token estimate on each, sorts them into always, sometimes and rarely used, and ends with a short list of what to cut. Figures it cannot read from the files, such as the MCP tools a plugin adds, it says it cannot measure.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/context-budget ~/.claude/skills/
```

## Quick start

In Claude Code, type:

```
Use the context-budget skill to audit my setup, and give the result in the skill's output format.
```

You get one `CONTEXT BUDGET AUDIT` block: the estimated overhead and what is left for work, the top consumers ranked, each component classified, and recommendations.

## Example

The fixture was a planted setup in a `setup/` folder, audited in place of `~/.claude`: a settings.json with two of its three plugins enabled and two hooks that do nothing (`true` and `echo done`), one reviewer agent, three skills with empty descriptions, a CLAUDE.md that repeats one rule 40 times, and a MEMORY.md whose only line links a `db.md` that does not exist. The output is trimmed: the reply's opening sentence, the block's header lines and its ranked TOP CONSUMERS list are left out (that list put CLAUDE.md first, at about 940 tokens), and the parts below are as the skill printed them.

```
Estimated infrastructure overhead: ~2k tokens (rule of thumb) / ~1.1k measured,
  plus the MCP tools from 2 enabled plugins, which the files can't show
Estimated available for work: ~198k tokens (~99% of 200k), before plugin MCP tools

CLASSIFICATION:
- Always:    CLAUDE.md, memory/MEMORY.md, reviewer agent
- Sometimes: github and postgres-tools plugins, release-notes skill
- Rarely:    old-demo skill (looks like a leftover), lint-fix skill (not written yet), both hooks (do nothing)

RECOMMENDATIONS:
- Cut CLAUDE.md's 40 identical rules down to one: saves ~850 tokens, about 90% of the file
- Delete old-demo. Write real descriptions and bodies for lint-fix and release-notes, or delete them.
  With an empty description, Claude can't tell when to use a skill.
- Remove the PreToolUse `true` hook (it runs on every Bash call for nothing) and the
  Stop `echo done` hook (it just adds output)
- Fix MEMORY.md: it links to db.md, but setup/memory/ only contains MEMORY.md
- Count the MCP tools that github and postgres-tools add (e.g. with /mcp) to get the real
  total. If they add many tools, disable postgres-tools outside database work.
  Target: under 10 MCP servers and under 80 tools.
- Keep the reviewer agent: it's small and clearly scoped
```

It closed with a note on its figures:

```
"Measured" means file size divided by about 4 characters per token. "Rule of thumb" uses the skill's per-item figures, which overstate the cost of this setup's tiny files. The one number the files can't give is the MCP tool cost of the two enabled plugins, so the overhead could be quite a bit higher than ~2k.
```

## Needs

- Claude Code.
- `python3` for the plugin count script in step 1.

Source and credit: see the Source section of SKILL.md.
