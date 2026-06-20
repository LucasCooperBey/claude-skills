# Templates

## Teardown Report Format

Save to `./teardowns/[app-name]-macos.md`:

```markdown
# Teardown: [App Name]
**Date:** YYYY-MM-DD
**Purpose:** [What I wanted to learn]

## Build vs Buy
| Component | Built | Bought (Package) |
|-----------|-------|-------------------|
| [component] | x | — |
| [component] | — | [package name] |

## Priority Map
- **Native/High effort:** [list]
- **Off-the-shelf:** [list]
- **Web-wrapped:** [list]

## Packages Worth Adopting
- `[package]` — [what it does, why they use it]

## Architecture Patterns
- [pattern]: [how they implement it]

## Scope Implications
- [what this tells me about building my feature]

## Key Takeaway
[One sentence: the most important thing I learned]
```

## Deep Analysis Prompt Template

For autonomous teardown + strategic analysis in one pass:

```
Reverse engineer [App Name] using the methodology from:
https://kevinchen.co/blog/rewind-ai-app-teardown/

Analyze /Applications/[AppName].app

Then answer the 5 strategic questions:
1. What did they build vs buy?
2. What did they prioritize?
3. What's the 80/20?
4. What solved problems can I adopt?
5. What scope does this reveal for my project?

Save to ./teardowns/[app-name]-macos.md using the standard format.
```

## Build-Time Reference Prompts

When implementing a feature:

```
I'm building [feature]. Reference ./teardowns/ to see how other apps
solved this. Apply relevant patterns and packages.
```

For a specific question:

```
What packages does [App] use for [capability]?
Check ./teardowns/[app]-macos.md and recommend if we should use the same.
```
