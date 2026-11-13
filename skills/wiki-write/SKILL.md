---
name: wiki-write
description: Use when a real decision was made, multiple inputs were synthesized, something broke, or a pattern emerged across events, to append a dated wiki entry under $WIKI_DIR (default ./wiki). Append-only, frontmatter-indexed, queryable by a later reader.
---

# wiki-write

Write an append-only entry to the wiki.

The scripts live in this skill's `scripts/` folder (`~/.claude/skills/wiki-write/scripts/` when installed for your user). Run them by that full path from the folder that should hold the wiki, usually your project root. The wiki root is `$WIKI_DIR`. When that variable is unset, the scripts use `./wiki` under the folder you run them from, so set `WIKI_DIR` to an absolute path to keep one wiki across projects.

## When to invoke this skill

- A choice was made that a future reader would benefit from re-reading: `decision`
- Multiple inputs (transcripts, research, meetings) distilled into findings: `synthesis`
- Something broke or surprised: production bug, agent failure, mistake: `incident`
- A pattern emerged across multiple events worth naming: `reflection`

## When NOT to invoke

- In-progress plans, working drafts: project folders
- Raw tool-call traces: project logs, not the wiki
- Conversation context that will not be referenced again: do not write
- Trivial actions (renamed a variable, fixed a typo): do not write

If you would reference the entry 6 months from now, write it. Otherwise skip.

## Decision-worthiness gate (3 gates)

Before writing a `decision` (or an ADR-style entry), confirm ALL THREE hold. If any is missing, skip it. This stops the wiki filling with non-decisions.

1. **Hard to reverse**: there is real cost to changing your mind later
2. **Surprising without context**: a future reader will wonder why it was done this way
3. **The result of a real trade-off**: genuine alternatives existed and one was chosen for specific reasons

A reversible, obvious, no-alternative call is not a decision. Do not record it.

### Where the decision lives (routing fork)

- A decision that lives with the code belongs in that repo's `docs/adr/`.
- This wiki is for cross-project and strategic decisions and syntheses.
- Do not copy a code-local ADR into the wiki. Reference it in `links` or `sources`.

## How to write

1. **Pick the type:** decision | synthesis | incident | reflection
2. **Pick a slug:** kebab-case, descriptive, no date prefix (the helper adds today's date). Example: `pick-a-weekly-review-day`, `rename-the-cache-key`
3. **Compose frontmatter + body**, omitting `id`, `type`, `date`: the helper injects those. Required fields:
   - `actors:`, `[me, claude]`
   - `tags:`, 2 to 6 kebab-case tags (for example `[weekly-review, cache, naming]`)
   - `summary:`, one to three sentences as a YAML block scalar. A reader uses this, plus tags and actors, to decide whether to open the file.
4. **Optional fields:** `domain`, `status`, `supersedes`, `sources`, `links`
   - **Linking:** populate `links` (related entries) and `supersedes` (the entry this one replaces) so a later reader can traverse the notes. An unlinked entry is an island: when this entry relates to, replaces, or builds on another, wire the relation.
5. **Body sections** depend on type: see SCHEMA.md. Typical patterns:
   - decision: `## What changed`, `## Why`, `## Tradeoffs`
   - synthesis: numbered findings with one-line headers
   - incident: `## What happened`, `## Root cause`, `## Fix`, `## Prevention`

## Invocation

```bash
~/.claude/skills/wiki-write/scripts/write-entry.sh <type> <slug> <<'EOF'
actors: [me, claude]
tags: [tag-one, tag-two, tag-three]
summary: >
  One to three sentences describing the entry. A reader uses this
  plus tags and actors to decide whether to open the file.
domain: meta
status: active
---

# Entry title

## What changed

Body text.
EOF
```

The script reads `$WIKI_DIR` (default `./wiki`).

The script:

- Validates required fields (`actors`, `tags`, `summary`), the type, and a kebab-case slug
- Refuses a duplicate id
- Injects `id`, `type`, and `date`
- Files `decision` and `incident` under `$WIKI_DIR/decisions/`, `synthesis` under `$WIKI_DIR/synthesis/`, and `reflection` under `$WIKI_DIR/counterfactuals/`
- Prints `WROTE: <path>` on success
- On any refusal, exits non-zero and prints one error line

## After writing

Run `~/.claude/skills/wiki-write/scripts/build-index.sh` from the same folder to refresh `$WIKI_DIR/INDEX.md`.

## Read first

- `SCHEMA.md`, full frontmatter contract
- `README.md`, what this folder is and how to run it
- `examples/decisions/2026-11-12-example-decision.md`, example decision shape
- `examples/synthesis/2026-11-12-example-synthesis.md`, example synthesis shape

## Source

The append-only wiki follows the LLM wiki pattern Andrej Karpathy described. The scripts, the schema and the tests are original to this repo.
