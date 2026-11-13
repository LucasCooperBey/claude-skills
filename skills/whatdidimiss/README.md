# whatdidimiss

A Claude Code skill you run after finishing a piece of work, to have Claude list what it noticed along the way and was never asked to handle: a nearby bug, a risk it did not raise, the obvious next step, or something that contradicts the original request. It is a reflection pass over what the session already touched, not a search: it does not open new files to look for problems, and when nothing came up it answers `Nothing notable.`

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/whatdidimiss ~/.claude/skills/
```

## Quick start

Do a task in Claude Code, then type:

```
/whatdidimiss
```

You can also ask "what did I miss" or "anything else worth doing". You get up to six one-line items, ranked, each labeled [a] adjacent, [b] risk, [c] follow-up or [d] contradiction and ending in `worth doing? y` or `n`, then one line asking which to take. It starts none of them on its own.

## Example

The fixture was a small project: `src/prices.py`, whose `to_cents` truncates (`int(dollars * 100)`) and whose `apply_discount` returns a float; `src/report.py`, whose `refund` repeats the same truncation; and a README line describing the old `int()` behavior. The request was:

```
Fix to_cents in src/prices.py: int(dollars * 100) truncates, so to_cents(19.99) returns 1998. Make it round to the nearest cent. Change only that function. When you are done, run /whatdidimiss.
```

The whole reply:

```
I fixed `to_cents` in `src/prices.py:2`. It now uses `return round(dollars * 100)` instead of `int(dollars * 100)`, and that was the only change. A quick check returned 1999, 29, 115, 435, 0 and 1000 for 19.99, 0.29, 1.15, 4.35, 0 and 10.

Here's what came up while I was in there (/whatdidimiss):

1. [a] `apply_discount` in the same file returns a float (`cents - cents * pct / 100`), so a "cents" value can come out fractional, like 1999 × 10% → 1799.1. | worth doing? y
2. [b] `round()` rounds exact half-cents to the nearest even number, and float error makes some of them land either way. If prices can have three or more decimal places, money usually needs `Decimal` with half-up rounding. | worth doing? y/n (only matters if inputs can be fractional cents)
3. [c] There's no test for `to_cents`. A small test with 19.99, 0.29, 1.15 and 4.35 would catch this coming back. | worth doing? y

Want me to take any of these? (numbers, or n)
```

All three items trace to the one file the session read. The session's tool log shows it read `src/prices.py`, changed that one line, ran two Python checks that load only `prices.py`, then loaded the skill. It never opened `src/report.py` or the README, so it did not mention the copy of the bug in `refund` or the stale README line. That is the skill working as written; to find those, ask for a search or an audit instead.

## Needs

- Claude Code, and some work done earlier in the same session for it to look back on.

## Limits

- It only knows what the session saw. Files it did not open, and problems elsewhere in the repo, are out of its reach by design.
- For a review of the code itself, SKILL.md points to `/critique`, `/grill`, `/pp2p`, `/pp3p` and `techdebt`. Those are other skills in this repo; copy their folders from `claude-skills/skills/` too if you want them.
- Opt-in only: the skill tells Claude not to wire it into a hook or run it on every turn.
