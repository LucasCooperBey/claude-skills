# pp2p

A Claude Code skill that refines code you name in two critique passes. Each pass sends three or four critic agents at the work (for code: solution fit, edge cases, simplicity), drops any finding it cannot tie to a line and a real failure, and applies the rest. Then it runs one polish pass, a mutation gate that breaks the code on purpose to prove the tests catch it, and a review by a different model family when one is available. It is the middle rung between a single critique pass and the heavier `pp3p`.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/pp2p ~/.claude/skills/
```

## Quick start

In Claude Code, inside a git repo, type:

```
/pp2p --type code --files "src/parser.py,tests/test_parser.py" The problem: <what the code should do>
```

The flags, from SKILL.md:

- `--files "a,b"` names the files. Without it the skill looks at recent changes in the conversation, then at uncommitted changes, which it asks you to confirm.
- `--type` is `code`, `plan`, `design`, `architecture` or `strategy`; it is detected when you leave it out.
- `--security`, `--performance` and `--api` pick preset critics; `--agents "A,B,C"` names your own.
- `--stack-reality` runs one fact-check critic on its own; `--sequential` lets each critic see the earlier ones' findings; `--no-early-exit` keeps the second pass even when the first finds nothing.

It keeps a run record at `.claude/perfection-pass.local.md` and archives its report under `.claude/perfection-passes/`, and it adds `.claude/*.local.md` to `.gitignore` so the record stays out of commits.

## Example

The fixture was a new git repo with one commit: `textstats.py`, whose `word_count` and `top_words` split text on a single space, and `test_textstats.py` with two passing tests. The request was:

```
/pp2p --type code --files "textstats.py,test_textstats.py" The problem: word_count and top_words should treat any run of whitespace as one separator and ignore punctuation around words, and the tests should prove it.
```

It ran for about four minutes and ended with this summary:

```
PP2P Complete
  Pass 1: 22 raw → 9 surviving → applied
  Pass 2: 9 raw → 4 surviving → applied
  Polish: 0 cleanups (nothing left to tidy)
  Mutation gate: 16 tests · 11/11 mutations caught
  Cross-family: skipped (no other model family available)
  Total: 13 improvements
```

Both functions now share one `_words()` helper that splits on any whitespace and trims punctuation and symbol characters from each end of a word, so `don't` and `e-mail` stay whole and a token such as `--` is not a word. The suite grew from 2 tests to 16, and 10 of them fail against the original code. Among the findings the critics raised and the run fixed:

```
- Accented words were being damaged. My first version cut off accent marks stored as separate characters: decomposed `café` came back as `cafe`, and `नमस्ते` lost its last vowel sign. Now only punctuation and symbol characters are trimmed, and a test covers it.
- Several tests proved nothing. Some passed even on the old buggy code.
```

It left one choice to the user: symbols at the edge of a word are trimmed too, so `C++` counts as `C`, and it named the one-character change that keeps them. It committed nothing.

Two steps were skipped in that run, and the report said so. No second model family was installed, so the cross-family review did not run. The session was `claude -p`, where Claude Code refuses writes under `.claude/`, so the run record and the archived report were not written; in an interactive session Claude Code asks you to approve those writes instead.

## Needs

- Claude Code, with subagents (the critics run as agents).
- A git repo for the run record.
- For the cross-family gate, a second model family the session can reach, such as the Codex plugin or a Codex or Gemini CLI. Without one the gate is skipped and the report says so.

## Limits

- SKILL.md sets a 15 minute budget for the critique passes and skips the second pass when the first runs past 10 minutes. Polish, the mutation gate and the cross-family gate always run.
- It asks you to narrow the scope when more than 15 files are named.
- For auth, payments or data integrity work, SKILL.md points you to `pp3p`.
