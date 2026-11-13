# Wiki frontmatter schema

Every wiki entry is a markdown file with YAML frontmatter. `scripts/build-index.sh` rebuilds `INDEX.md` from that frontmatter. A reader uses the index to choose which files to open. The body is not indexed. Make the frontmatter dense.

## Fields the writer injects

`scripts/write-entry.sh` adds these three fields. Do not pass them on stdin. Also omit the opening `---` fence. Include a closing `---` line before the body.

- `id`: `<date>-<slug>`. The date is `YYYY-MM-DD`. The slug is the second argument, kebab-case, with no date prefix.
- `type`: `decision`, `synthesis`, `incident`, or `reflection`.
- `date`: the day the entry was written.

Set `WIKI_ENTRY_DATE` to `YYYY-MM-DD` when a caller needs to pin the date. When it is unset, the writer uses today's date.

## Fields you must pass

```yaml
actors: [me, claude]
tags: [workflow, memory]
summary: >
  One to three sentences. A reader uses this, plus tags and actors, to decide
  whether to open the file.
```

`actors`, `tags`, and `summary` are required for every type. Use 2 to 6 kebab-case tags. More than 6 means the entry is too broad.

## Optional fields

```yaml
status: active
domain: workflow
confidence: high
supersedes: [2026-11-01-older-note]
sources:
  - ./decisions/2026-11-01-older-note.md
links:
  - ./synthesis/2026-11-01-older-note.md
alternatives_considered:
  - id: leave-it-unwritten
    one_liner: Keep the choice in the conversation only
  - id: file-a-note
    one_liner: File one dated note
    chosen: true
```

`status` may be `active`, `archived`, or `superseded`. The index skips `status: superseded` and leaves the file on disk.

`supersedes` names older ids this entry replaces. The writer does not edit those files. To drop an older entry from the index, set `status: superseded` on that file.

`confidence` and `alternatives_considered` are optional. When the type is `decision` and they are present, the index prints them on that entry's line. Mark the chosen alternative with `chosen: true`.

## Body by type

- decision: `## What changed`, `## Why`, `## Tradeoffs`
- synthesis: numbered findings with one-line headers
- incident: `## What happened`, `## Root cause`, `## Fix`, `## Prevention`
- reflection: the pattern, then the events that support it

## Where a type is filed

| Type | Folder |
| --- | --- |
| decision | `decisions/` |
| incident | `decisions/` |
| synthesis | `synthesis/` |
| reflection | `counterfactuals/` |

The path is `$WIKI_DIR/<folder>/<id>.md`. `$WIKI_DIR` defaults to `./wiki`.

## Id format

`YYYY-MM-DD-kebab-slug`. The date prefix supports time-window queries. The slug is descriptive enough to read in a directory listing. You pass the slug without the date. The writer adds the date. A second write of the same id is refused.

## What does not go in the wiki

- In-progress plans and working drafts stay in project folders.
- Raw tool output stays in the project's logs.
- A decision that lives with the code belongs in that repo's `docs/adr/`.
- Conversation context that nobody will open again is not written.

If you would look the note up months from now, it belongs here.

## On-disk shape

```yaml
---
id: 2026-11-12-example-decision
type: decision
date: 2026-11-12
actors: [me, claude]
tags: [example, decisions, workflow]
summary: >
  Example only. One dated note records a choice a later reader would otherwise
  have to reconstruct from a chat.
status: active
---
```

The body follows the closing fence. Two made-up files in `examples/` show a decision and a synthesis.
