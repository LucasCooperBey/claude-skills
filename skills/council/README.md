# council

A Claude Code skill: a method Claude Code follows to run a council of real models on a decision. Each seat writes an independent position first, each seat's model is read from the harness's own record, the seats cross-examine one another under neutral labels, dissent is kept by name, and a separate reviewer checks the recommendation. It is for someone facing an important, uncertain choice who wants several models' independent views and not one model's answer.

## Install

```
git clone https://github.com/LucasCooperBey/claude-skills.git
mkdir -p ~/.claude/skills
cp -R claude-skills/skills/council ~/.claude/skills/
```

This puts the skill in your skills folder, and creates that folder if it is not there yet.

## Quick start

The skill ships with a three-seat roster in `roster.md`: opus, sonnet and haiku, each asked for high effort and each run as its own `claude -p` call. A row is one seat: the model as the harness names it, the effort to request, the command that runs it, and where its model id is read to check identity. Keep the default, or edit `roster.md` to choose who sits on the council. Then ask Claude Code for a council on a question, for example:

```
Run a council on this question: should a small team rewrite a slow internal tool or keep patching it? Use the council skill. Keep the run folder in ./council-run.
```

## Example

This is a real run with the default three-seat roster.

The prompt:

```
Run a council on this question, using the default roster: should a three-person team that ships a web app several times a week squash or merge pull requests into main? Use the council skill. Keep the run folder in ./council-run.
```

The command:

```
claude -p --setting-sources project --strict-mcp-config --no-session-persistence \
  --output-format json --permission-mode acceptEdits \
  --allowedTools "Bash(claude:*)" "Bash(jq:*)" Read < prompt.txt > stdout.json
```

The allow list permits seat calls through `claude`, `jq` to read each call's JSON, and Read. `--permission-mode acceptEdits` lets the session write the run folder's files.

The run was started in an empty folder that held the skill as a project skill, in `.claude/skills/council/`, which is why the command reads project settings only. To repeat the run, save the prompt as `prompt.txt` in that folder first. In everyday use you ask Claude Code in a normal session, as in the Quick start, and no such command is needed.

The result opens with the decision and the next action:

> **Decision: squash merge by default.** All three seats chose it independently and kept it after cross-examination, each at medium confidence. It rests on general engineering experience, because the question gave no facts about the team beyond its size, product and cadence.

The disagreement section keeps the minority views by name:

> ## Disagreement kept
>
> - **haiku (minority point):** squash makes the PR the only rollback unit, whereas merge commits let you revert one sub-change. The others treat this as a PR-size problem, and it stays open because PR size is unknown.
> - **Trial criterion:** sonnet and haiku wanted a "no diagnosis delayed more than 30 minutes" test. opus wanted it dropped as unmeasurable, and I sided with opus.
> - **If the trial fails:** opus would keep squash and add a size-based exception; sonnet would switch to merge commits.

The roster section shows which model sat in each seat, as the harness reported it (its synthesis, cost and limits bullets are left out here):

> ## Roster
>
> | Seat | Model reported by harness | Effort requested | Harness | Completed | Specialists |
> |---|---|---|---|---|---|
> | 1 | `claude-opus-5-5` | high | `claude -p --model opus` | position and cross-examination | none |
> | 2 | `claude-sonnet-5-5` | high | `claude -p --model sonnet` | position and cross-examination | none |
> | 3 | `claude-haiku-5-5` | high | `claude -p --model haiku` | position and cross-examination | none |
>
> - **Identity:** model ids were read from the `modelUsage` key of each call's JSON output. Effort is as requested; the harness record does not report the effort used.
> - **Final review:** a fresh `claude-opus-5-5` call. It is not independent, because every roster model held a seat and opus was reused. Its verdict was "accept with the listed corrections", and I applied them. The post-review revisions have not themselves been reviewed.

The recommendation, the strongest case against it, the acceptance test and the rest of the result are left out above; the full output is in [examples/sample-run.md](examples/sample-run.md).

Four tool calls were refused by the allow list during the run, and the session redid those steps with permitted calls.

## Needs

- Claude Code, signed in on a plan.
- `jq`, which reads each seat's model id from its JSON output.
- Other command line tools only if you add seats that use them.
- No metered API key for the default roster.

## Limits

- Seats from one vendor share training and blind spots, so their agreement is weak evidence.
- Neutral labels reduce brand cues in cross-examination. They do not make the seats blind.
- A council spends several model calls of plan usage. The example made ten seat calls, plus the session that ran them.
- With the default roster every model holds a seat, so the final review reuses one of them, and the result says it is not independent. The example shows this.
- The council advises. It does not decide.

## Related

[blind-council](https://github.com/LucasCooperBey/blind-council) is a separate harness in which five models from five vendors debate and a sixth model judges. Three of its five debaters run through a metered API key; this skill needs no API key.
