---
name: reverse-engineer-to-learn
description: Studies how existing apps solve problems to inform new builds. Performs strategic teardowns for learning, scoping features, and finding packages. Reverse-engineers macOS app bundles, npm/pypi packages, GitHub repos, and web apps (via browser), then applies the strategic questions. Triggers — "teardown", "reverse engineer", "how does X work", "study this app/package".
---
# Reverse Engineer to Learn

Absorbed `app-teardown`: this skill now performs the raw teardown itself — macOS app
bundles, npm/pypi packages, GitHub repos, and web apps via browser — AND the strategic
layer on top, transforming raw teardowns into actionable intelligence (Yash Poojary's
methodology). It is the single canonical teardown skill (`/teardown`, `/re-learn`).

**REQUIRED SUB-SKILL:** app-teardown

## Quick Start

```
/re-learn [AppName]
```

## The 5 Strategic Questions

After running `/teardown [AppName] macos`, ask these questions — they're the core value:

1. **Build vs. Buy?** — Which parts are custom code vs. third-party packages? Reveals where they invested effort.

2. **What did they prioritize?** — Where's the complexity budget? What's native vs. web vs. off-the-shelf?

3. **What's the 80/20?** — Which 20% of tech choices deliver 80% of value? (Spotify: web everywhere except audio)

4. **What packages can I adopt?** — Solved problems I'd otherwise build. Finding the right package = 3 days → 3 hours.

5. **What scope does this reveal?** — Permissions, APIs, storage patterns. Define realistic scope before building.

## The Workflow

### 1. Target Selection

Pick apps by **feature**, not category. Building audio? Tear down Spotify. Building auto-update? Tear down any app using Sparkle.framework. The target doesn't need to be a competitor.

### 2. Run Technical Teardown

```
/teardown [AppName] macos
```

### 3. Apply the 5 Questions

Transform raw output into strategic intelligence. Save to your project:

```
./teardowns/[app-name]-macos.md
```

See `references/templates.md` for report format.

### 4. Reference During Builds

Point Claude at your teardown library when building:

```
Before implementing [feature], check ./teardowns/spotify-macos.md
for packages and patterns. Apply the same approach if relevant.
```

## Kevin Chen Prompt Template

For deep analysis, feed the [Rewind teardown blog](https://kevinchen.co/blog/rewind-ai-app-teardown/) as methodology context — the LLM learns the method and applies it systematically. See `references/kevin-chen-method.md`.

## Anti-Patterns

- **Don't scan and move on.** Value is in the 5 questions, not raw data.
- **Don't only tear down competitors.** Any app with your needed feature is valid.
- **Don't rebuild solved problems.** If a $100B company uses a package, you should too.

## Integration

| Skill | Role |
|-------|------|
| `app-teardown` | Technical methods (plutil, otool, strings) |
| `deep-recon` | Code Analyzer uses teardown library |
| `writing-plans` | Teardowns inform scope |

## Source

Inspired by Kevin Chen (https://kevinchen.co/blog/rewind-ai-app-teardown/). The skill also names Yash Poojary's methodology; that source was not located.
