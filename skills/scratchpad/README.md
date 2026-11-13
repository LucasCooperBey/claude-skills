# scratchpad

A Claude Code skill that keeps working notes in one file, `.scratchpad.md` in your project root, so they survive when a long conversation is compacted. Notes go into three sections: Pinned (short facts for the whole session), Working (timestamped notes, newest first, which you can prune) and Manual (kept until you remove them).

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/scratchpad ~/.claude/skills/
```

Add `.scratchpad.md` to your project's `.gitignore` if you don't want it committed.

## Quick start

In Claude Code, type:

```
/scratchpad --pin This project uses uv, never pip.
```

The skill creates `.scratchpad.md` if it is missing, writes the note under Pinned, and tells you how many of the 500 Pinned characters you have used. `/scratchpad <note>` adds a timestamped Working note, `/scratchpad --save <note>` adds a Manual note, and `/scratchpad --show` prints the file.

## Example

Four commands, each its own Claude Code session, in an empty project, and each full reply:

`/scratchpad --pin This project uses uv, never pip.` replied:

```
I pinned **"This project uses uv, never pip."** in a new `.scratchpad.md` in the project root. The Pinned section is now 31 of its 500 characters. I'll use `uv` for any Python package commands this session.
```

`/scratchpad Tried pytest -x; test_parse fails only when TZ is unset.` replied:

```
I added your note to the Working Memory section of `.scratchpad.md`:

- [2026-11-12 18:51] Tried pytest -x; test_parse fails only when TZ is unset.

The Pinned section still says "This project uses uv, never pip."
```

`/scratchpad --save Release: uv build && uv publish` replied:

````
I added this line to the Manual section of `.scratchpad.md`:

```
- Release: uv build && uv publish
```

The Manual section is never pruned automatically, so this stays until you remove it. The Pinned and Working sections weren't changed.
````

`/scratchpad --show` replied:

```
Here's what's in `.scratchpad.md` right now:

**Pinned**
- This project uses uv, never pip.

**Working**
- [2026-11-12 18:51] Tried `pytest -x`; `test_parse` fails only when TZ is unset.

**Manual**
- Release: `uv build && uv publish`
```

The file it left in the project root:

```
# Scratchpad

## Pinned
This project uses uv, never pip.

## Working
- [2026-11-12 18:51] Tried pytest -x; test_parse fails only when TZ is unset.

## Manual
- Release: uv build && uv publish
```

## Needs

- Claude Code.
