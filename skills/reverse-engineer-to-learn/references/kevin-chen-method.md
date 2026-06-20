# Kevin Chen Prompt Template Method

**Source:** https://kevinchen.co/blog/rewind-ai-app-teardown/

## Why It Works

When you feed this blog URL to an LLM alongside an app path, the LLM:

1. **Learns the method** — not Rewind-specific findings, but the systematic approach
2. **Applies all 6 analysis areas** — bundle, binary, database, filesystem, runtime, permissions
3. **Produces exhaustive output** — ~15 minutes of autonomous agent work
4. **Generates strategic insights** — not just "what's in this app" but "what decisions did they make"

The technical commands are covered in `app-teardown/methods/macos-app.md`. This blog adds the **analytical framework** that transforms raw data into learning.

## The 6 Analysis Areas (from Chen's method)

| Area | Strategic Question |
|------|-------------------|
| Frameworks | What third-party tech did they buy? |
| Storage | What performance/quality tradeoffs? |
| Permissions | What's the feature scope surface? |
| Dependencies | What infrastructure did they outsource? |
| Database | Local-first? Cloud-sync? ML pipeline? |
| Resources | On-device inference? Privacy approach? |

## When to Use This vs. `/teardown`

- **`/teardown [App] macos`** — Quick structural scan, outputs raw findings
- **Kevin Chen prompt** — Deep autonomous analysis with strategic interpretation baked in

Use the prompt template when you want the LLM to do the strategic thinking for you, not just report findings.
