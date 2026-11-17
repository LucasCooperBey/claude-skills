# Sample run

This is the full output of the README's example, a real run with the default roster.

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

The dollar figure near the end is the `total_cost_usd` field the harness printed for each of the ten seat calls, added up. The run was made signed in to a subscription plan.

Everything below the rule is the `result` field of the run's JSON output, unedited. The run folder and the files it names near the end were the run's own working files; they are not included here.

---

**Decision: squash merge by default.** All three seats chose it independently and kept it after cross-examination, each at medium confidence. It rests on general engineering experience, because the question gave no facts about the team beyond its size, product and cadence.

**Next action:** before changing any setting, look back at your last 20 merged PRs and check three things:
- **PR size:** lines changed per PR, looking at the largest tenth and not only the median.
- **Rollback unit:** whether recent rollbacks undid a whole PR or only part of one.
- **Curated commits:** how many PRs have two or more commits that each look meaningful and independently buildable.

If about a quarter or fewer PRs are curated and rollbacks were whole-PR, squash stands. If about half or more are curated, or you needed partial-PR rollbacks, use merge commits instead. Those cut-offs are one seat's judgment, not evidence.

## The recommendation

- **Default:** squash, with the commit message set to the PR title plus description.
- **Exceptions:** use a true merge commit for stacked PRs and for PRs whose commits each build and pass tests. The author declares the exception in the PR description.
- **Main reason:** one PR equals one commit on `main`, so a rollback is a single `git revert <sha>`. Reverting a merge commit has a trap: re-merging the same branch brings nothing back until you revert the revert.
- **Why merge commits gain little:** finer `git bisect` only helps if the commits inside a branch build and pass tests, and CI usually tests only the PR head.

## Strongest case against it

Squash is the lossy choice. A team on merge commits can switch to squash later and lose nothing; a team on squash cannot get the detail back from `main`. The recommendation fails if any of these is true of your team:
- PRs are routinely large and cannot be split.
- Commits inside branches are routinely green and meaningful.
- Stacked PRs are a normal workflow.
- You need to backport parts of PRs to release branches.

## Disagreement kept

- **haiku (minority point):** squash makes the PR the only rollback unit, whereas merge commits let you revert one sub-change. The others treat this as a PR-size problem, and it stays open because PR size is unknown.
- **Trial criterion:** sonnet and haiku wanted a "no diagnosis delayed more than 30 minutes" test. opus wanted it dropped as unmeasurable, and I sided with opus.
- **If the trial fails:** opus would keep squash and add a size-based exception; sonnet would switch to merge commits.

## Acceptance test and revision trigger

Run squash until 20 PRs have merged and for at least 4 weeks, logging every revert, every "which change broke this?" investigation and every use of an exception.

| Outcome | Condition |
|---|---|
| Fail | A squashed PR had to be taken apart to diagnose or roll back, or exceptions were used on more than 2 of 20 PRs |
| Inconclusive | No failure, but no revert or investigation occurred; keep squash |
| Pass | No failure, and at least one real revert or investigation occurred |

Revisit the default on a failed trial, on adopting stacked PRs, on needing partial-PR backports, or if the look-back shows about half or more PRs are curated.

## Roster

| Seat | Model reported by harness | Effort requested | Harness | Completed | Specialists |
|---|---|---|---|---|---|
| 1 | `claude-opus-5-5` | high | `claude -p --model opus` | position and cross-examination | none |
| 2 | `claude-sonnet-5-5` | high | `claude -p --model sonnet` | position and cross-examination | none |
| 3 | `claude-haiku-5-5` | high | `claude -p --model haiku` | position and cross-examination | none |

- **Identity:** model ids were read from the `modelUsage` key of each call's JSON output. Effort is as requested; the harness record does not report the effort used.
- **Final review:** a fresh `claude-opus-5-5` call. It is not independent, because every roster model held a seat and opus was reused. Its verdict was "accept with the listed corrections", and I applied them. The post-review revisions have not themselves been reviewed.
- **Synthesis:** written by this session (`claude-fable-5-2`), which held no seat.
- **Cost:** $0.57 measured across 10 calls, from the harness's own cost field.
- **Limits:** all seats are from one vendor, so their agreement is weak evidence. No seat call failed.

Everything is in `./council-run`; open `recommendation.md` first. The folder also holds the packet, the raw seat outputs in `positions/` and `cross/`, and the review in `review/`. A leftover unused `run-seats.sh` is also in there and can be deleted.
