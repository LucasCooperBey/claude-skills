# ecosystem-audit

A Claude Code skill that audits your `.claude` setup (skills, slash commands, agents, hooks, memory files and CLAUDE.md rules) for duplicates, name collisions, hooks that point at missing scripts and rules that contradict each other. It returns a fix list ranked HIGH, MEDIUM and LOW, with the path, the reason, a recommended action and a rollback note for each item. It reports and changes no file.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/ecosystem-audit ~/.claude/skills/
```

## Quick start

In Claude Code, type:

```
Use the ecosystem-audit skill. Run step 1, the deterministic inventory, name the step 2 finders without running them, and give the step 3 fix list.
```

You get an inventory table of your setup, the step 2 finders it would run, and a ranked fix list. Step 2 fans out many agents and costs tokens, so it waits for you to opt in.

## Example

The fixture was a scratch project whose `.claude` folder held two skills that do the same job, two slash commands named `deploy-staging` and `deploy:staging`, and a Stop hook calling a script that does not exist, plus a CLAUDE.md with "Always commit straight to main." next to "Never push to main; open a pull request." The prompt asked the skill to audit that project's `.claude` in place of `~/.claude`, and only the first phase ran (step 1, the step 2 names, the step 3 list). The output below is trimmed to three parts and its section headings are left out.

Step 1, the inventory:

```
| Surface | Result |
|---|---|
| Skills | 3: `ecosystem-audit`, `summarize-notes`, `note-summary` |
| Slash commands | 2: `deploy-staging.md`, `deploy:staging.md`. These are the same name, one with `-` and one with `:` |
| Agents | none (`.claude/agents/` doesn't exist, and there's no `dormant/` folder) |
| Memory files | 0 under `.claude/` |
| Hooks (`.claude/settings.json`) | 1 Stop hook, which runs `bash .claude/hooks/notify-done.sh`. **That script doesn't exist** (there's no `.claude/hooks/` folder) |
| `CLAUDE.md` | 2 rules: "Always commit straight to main" and "Never push to main; open a pull request" |
| Other | `./deploy.sh`, which `deploy-staging.md` points to, **doesn't exist** at the project root |
```

Step 2, named and not run:

```
These need the Workflow tool and your explicit opt-in:
- **duplicate-skill-finder**
- **stale-demo-finder**
- **command-collision-finder**
- **rule-contradiction-finder**
- **dormant-bloat-finder**
```

Step 3, the HIGH items (the same run listed the duplicate commands and the duplicate skills as MEDIUM):

```
1. **The two `CLAUDE.md` rules point opposite ways.** Path: `CLAUDE.md`.
   - **Why:** "Commit straight to main" pushes work onto main. "Never push to main; open a PR" requires a branch. Following both leaves commits stuck on local main that can't be pushed.
   - **Action:** Pick one workflow. If you want PRs, a likely fix is: "Never commit or push to main. Work on a feature branch and open a pull request."
   - **Rollback:** It's a text edit, so keep the old lines in your history.
2. **The Stop hook runs a script that doesn't exist.** Path: `.claude/settings.json` → `hooks.Stop`, which calls `.claude/hooks/notify-done.sh`.
   - **Why:** It fails at the end of every turn, which is noise or an error every session.
   - **Action:** Either restore `notify-done.sh` or delete the Stop hook entry.
   - **Rollback:** Save a copy of `settings.json` before editing.
```

## Needs

- Claude Code.
- Claude Code's Workflow tool for step 2, the fan-out finders. Steps 1 and 3 run without it.
- `jq`, optional, for the hook surface in step 1.

Source and credit: see the Source section of SKILL.md.
