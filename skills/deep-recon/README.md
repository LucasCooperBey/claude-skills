# deep-recon

A Claude Code skill that researches a problem before you build anything: has it been solved, what do people who tried it say, and what do the docs warn about. It sends research agents out in parallel (Solution Scout, Community Intel, Doc Collector, then a Code Analyzer on the top picks) and writes one research brief with a recommendation, the drawbacks of each alternative, open questions and sources.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/deep-recon ~/.claude/skills/
```

## Quick start

In Claude Code, type `/deep-recon` and the problem in one line, plus where the brief should go:

```
/deep-recon a command-line tool that checks a folder of Markdown files for broken relative links. Use ./out as <your-output-dir>, and keep each research agent to one search round.
```

You get a short answer in the chat and a full brief at `./out/research/<date>-<topic>/research-brief.md`. Without the "one search round" limit the agents search longer and cost more.

## Example

The prompt was the Quick start line above, run in an empty project. It took about three minutes, and the brief it saved has 240 lines with these sections: Problem Statement, Existing Solutions, Community Consensus, Recommended Approach, Key Patterns to Adopt, Open Questions, Sources. The reply in the chat, trimmed to its answer, the tools it compared and its gaps:

```
The research is finished: **don't build this. Use lychee in offline mode** (`lychee --offline --include-fragments --root-dir . docs/`) as a CI check that fails the build on a broken link. One thing is unconfirmed: no source said `--offline` and `--include-fragments` work together, so test that before relying on it.

The brief is at `out/research/2026-11-12-markdown-relative-link-checker/research-brief.md`. All four agents ran, each limited to one search round.

**Tools compared:**
1. **lychee** (Rust, ~4.1k stars, actively maintained, GitLab's docs repo uses it). It checks local files without network access, handles links that start with `/`, URL-encoded paths and folder links, and can check `#anchor` links. It has an official GitHub Action.
2. **remark-validate-links** (JavaScript). The best fallback if lychee's anchor handling turns out too loose. It uses `github-slugger`, the library that reproduces GitHub's rules for turning headings into anchors, including repeated headings, and it checks anchors in other files. The cost is a Node/remark setup.
3. **mlc** (Rust). Checks that linked files exist but doesn't check anchors.
4. **markdown-link-check**. Mostly aimed at web links, with weak anchor support.
5. **markdownlint MD051**. Checks anchors within the same file only, so it's an add-on rather than a replacement.
```

```
**Gaps:**
- Reddit and Hacker News turned up nothing, so the community view comes from GitHub issues.
- A few source files returned 404. Because of that, lychee's handling of repeated headings and mlc's internals weren't checked.
- The brief also lists five design patterns, in case you ever do need to build your own.
```

## Needs

- Claude Code, with its built-in subagents (Task or Agent), WebSearch and WebFetch.
- Nothing else; `agents.md` and `templates/research-brief.md` are in this folder.
