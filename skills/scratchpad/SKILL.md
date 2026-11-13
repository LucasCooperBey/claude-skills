---
name: scratchpad
description: Compaction-resilient session notepad. Save working context that survives long conversations. Three tiers — pinned (always loaded), working (session), manual (permanent).
---

# Scratchpad — Compaction-Resilient Session Notes

Save important context to `.scratchpad.md` in the project root, a file that survives conversation compaction. Add `.scratchpad.md` to your `.gitignore` if you don't want it committed.

## Why This Exists

During long sessions, context compaction drops earlier messages. Critical working notes — debugging breadcrumbs, temporary findings, "tried X because Y" — vanish. This gives you a persistent notepad with three priority tiers.

**Different from memory:** Memory is cross-session knowledge about the user/project. Scratchpad is within-session working state that might become memory later.

## Commands

| Command | Action |
|---------|--------|
| `/scratchpad <content>` | Add to Working Memory with timestamp |
| `/scratchpad --pin <content>` | Add to Pinned Context (always loaded, 500 char limit) |
| `/scratchpad --save <content>` | Add to Manual section (never pruned) |
| `/scratchpad --show` | Display current scratchpad contents |
| `/scratchpad --prune` | Remove Working entries older than 7 days |
| `/scratchpad --clear` | Clear Working Memory (keep Pinned + Manual) |

## Sections

### Pinned Context (500 char limit)

- Read it when you are asked to read the scratchpad
- Use for critical session facts: "Project uses bun", "On branch feature/xyz", "Don't touch the legacy monolith"
- Keep SHORT — this eats into your context budget
- Overwrite semantics: new pin with same topic replaces old

### Working Memory

- Timestamped session notes
- Prune these entries when asked
- Good for: debugging breadcrumbs, temporary findings, "tried X, didn't work because Y"
- Newest entries at top

### Manual

- Never auto-pruned
- User-controlled permanent notes
- Good for: team contacts, deployment commands, recurring gotchas

## File Format

```markdown
# Scratchpad

## Pinned
Project uses bun. On branch claude/explore-feature-xyz. Legacy module is 9K lines — restyle only, don't refactor.

## Working
- [2026-04-01 20:30] Found auth bug in UserContext — missing useEffect dependency
- [2026-04-01 19:15] date-fns installed, date-range-picker.tsx created
- [2026-04-01 18:00] 4-team audit complete, ASCII atlas at docs/ASCII-SCREEN-ATLAS.md

## Manual
- Project dev server: bun dev (port 3000)
- Team contact: team@example.com
- DB studio: bun db:studio
```

## Behavior

1. Creates `.scratchpad.md` in the project root if it doesn't exist
2. Parses argument to determine section (--pin, --save, or default Working)
3. Appends with timestamp for Working entries
4. Warns if Pinned exceeds 500 chars
5. Confirms what was saved

## Integration

- Read, write, and prune the scratchpad file when asked
- When a Working note should be kept, write it into the Manual section when asked
- When a session ends, stale Working entries can be pruned with `/scratchpad --prune`

## Examples

```
/scratchpad The sidebar width transition bug is in client-pdf.ts:800-809, re-join step
/scratchpad --pin On branch feature/date-range-picker. Don't push to main.
/scratchpad --save Project uses 5-tier PDF fallback: Typst → Cloud → Puppeteer → HTML → JSON
/scratchpad --show
/scratchpad --prune
```
