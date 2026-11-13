---
name: whatdidimiss
description: After a chunk of work is done, surfaces what the model noticed but was never asked to do — adjacent tasks, unraised risks, natural follow-ups, and contradictions with the original plan. Opt-in only; the model reviews the work it just completed and the context it gathered, then returns a tight ranked list, each item with a one-line "worth doing? (y/n)". Triggers on "/whatdidimiss", "what did I miss", "what did you uncover", "anything else worth doing", "did we miss anything", "what else came up". NOT a fresh audit and NOT always-on — it only reports genuine findings from the work just done, and says "nothing notable" when there are none.
user-invocable: true
---

# What Did I Miss

Review the work you JUST completed in this session and surface the things you noticed but were never explicitly asked to handle. This is the "while you were in there, what else did you see?" pass.

## Why this exists

Doing a task generates side-knowledge — an adjacent bug, a risky edge case, an obvious next step, a fact that quietly contradicts the original plan. That knowledge normally evaporates when the turn ends. This skill makes you spend it before it's gone. It is **opt-in** (you invoke it deliberately) precisely so it never nags — do not propose wiring it into a hook, Stop event, or settings.json.

## What to do

1. **Look back at the actual work, not the whole repo.** Ground this in what you did and read THIS session: files touched, commands run, errors seen, code/context examined, the original ask. Do not go spelunking for new problems — this is reflection on work done, not a fresh audit.

2. **Surface only genuine findings**, sorted best-first, across these four buckets (omit any bucket that's empty — don't pad to fill it):
   - **(a) Adjacent** — things you noticed but didn't do (a nearby bug, a stale comment, a sibling file with the same issue).
   - **(b) Risks / edge cases** — failure modes or edge cases you saw but didn't raise (empty input, race, missing auth check, unhandled error path).
   - **(c) Follow-ups** — the natural next step the work sets up (a test to add, a migration to run, a doc to update, a caller to update).
   - **(d) Contradictions** — anything you found that conflicts with the original plan, a stated assumption, or memory/ground-truth (the request assumed X but the code does Y).

3. **Format — one line per item**, ranked, with a label and a verdict:
   ```
   1. [a] Three other call-sites use the old signature — they'll break at runtime. — worth doing? y
   2. [b] New endpoint has no rate-limit; trivial to abuse. — worth doing? y
   3. [c] CHANGELOG not updated for this change. — worth doing? y
   4. [d] Ask assumed Qdrant, but this path writes to pgvector. — worth doing? y/n (flag — confirm intent)
   ```
   Keep each item to a single line. No sub-bullets, no code blocks, no re-explaining what you built. Total output stays short — aim for the few that matter, not an exhaustive list. If you have more than ~6, keep the top 6 and drop the rest.

4. **The hard rule: do not manufacture work.** If nothing genuinely surfaced, reply exactly `Nothing notable.` and stop. A short honest answer beats a padded one — inventing busywork is the failure mode this skill exists to avoid. Findings must trace to something you actually saw, not generic best-practice you could append to any task.

5. **End with the offer, one line:** "Want me to take any of these? (numbers, or n)" — then wait. Don't start on them unprompted.

## Failure modes

- **Invoked after a trivial or no-op turn** (a one-line answer, a single read) → almost always `Nothing notable.` Don't strain to produce items.
- **Tempted to re-audit the codebase** → out of scope. Only report what THIS session surfaced. For a real audit use `/critique`, `/grill`, or `/pp2p`.
- **Padding** → the moment an item is "you could also add tests/docs/types in general" with no specific trigger from the work, cut it.

## Not this skill

- Adversarial review of code you wrote → `/critique` or `/grill`.
- Polish / hardening passes → `/pp2p`, `/pp3p`.
- End-of-session tech-debt scan across the project → `techdebt`.
