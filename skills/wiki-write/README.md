# wiki-write

This folder is a public wiki writer: it files one dated markdown note for a decision, a synthesis, an incident, or a reflection. The writer checks the note, refuses a bad or duplicate entry, and an index script rebuilds a single INDEX.md from the files.

To use it as a Claude Code skill, copy this folder to `~/.claude/skills/wiki-write/`; SKILL.md tells the agent when to write and how. To try the scripts by hand, run the commands below from a copy of this folder: they write one entry and build the index. `WIKI_DIR` selects the wiki folder. Leave it unset to use `./wiki`.

```bash
export WIKI_DIR=./wiki
mkdir -p "$WIKI_DIR"
scripts/write-entry.sh decision picked-a-weekly-note <<'EOF'
actors: [me, claude]
tags: [example, workflow, memory]
summary: >
  Example only. A weekly note is filed when a real choice was made, so the
  reason can be read later without the original thread.
status: active
---

# Picked a weekly note

## What changed

Decisions that pass the three gates get one dated note.

## Why

A future reader can see the reason without replaying the work.

## Tradeoffs

A short note is easy to file and easy to miss detail in.
EOF
scripts/build-index.sh
```

The writer prints `WROTE:` and the file path. `scripts/build-index.sh` writes `$WIKI_DIR/INDEX.md`.

A decision or an incident is filed under `decisions/`. A synthesis is filed under `synthesis/`. A reflection is filed under `counterfactuals/`.

An agent that may have just made a durable choice reads `SKILL.md` before writing. The skill lists when to write, when not to write, and three gates for a decision: hard to reverse, surprising without context, and the result of a real trade-off. A decision that belongs with code goes in that repo's `docs/adr/` instead of this wiki. When the gates pass, the agent composes frontmatter and a body, runs `scripts/write-entry.sh`, then runs `scripts/build-index.sh`. The frontmatter contract is `SCHEMA.md`. Shapes for two made-up entries are under `examples/`.
