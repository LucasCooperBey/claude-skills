---
name: visual-verdict
description: Structured visual QA verdict for screenshot-to-reference comparisons. Returns JSON scores driving edit iterations. Use after any UI implementation to verify visual fidelity.
---

# Visual Verdict — Structured Visual QA

Compare generated UI screenshots against reference images and return a strict JSON verdict that drives the next edit iteration.

## When to Use

- After implementing any UI component, page, or design change
- When verifying visual fidelity against Figma, ASCII mockups, or design specs
- As a gate before marking frontend work complete
- Inside design-taste and frontend-design workflows as verification step

## When NOT to Use

- Pure backend/API work with no visual output
- When no reference image exists (use design-taste for initial design instead)

## Inputs

| Input | Required | Source |
|-------|----------|--------|
| Reference image(s) | Yes | Figma screenshot, design mockup, ASCII art render, or prior approved screenshot |
| Generated screenshot | Yes | a screenshot skill if you have one, Playwright MCP `browser_take_screenshot`, or manual screenshot |
| Category hint | Optional | e.g. `dashboard`, `form`, `table`, `marketing`, `mobile` |

## Output Contract

Return **JSON only** with this exact shape:

```json
{
  "score": 0,
  "verdict": "revise",
  "category_match": false,
  "differences": ["..."],
  "suggestions": ["..."],
  "reasoning": "short explanation"
}
```

### Field Rules

| Field | Type | Description |
|-------|------|-------------|
| `score` | int 0-100 | Overall visual fidelity score |
| `verdict` | string | `pass` (90+), `revise` (50-89), `fail` (<50) |
| `category_match` | bool | Does it match the intended UI category/style? |
| `differences[]` | string[] | Concrete visual mismatches (layout, spacing, typography, colors, hierarchy) |
| `suggestions[]` | string[] | Actionable next edits tied to differences |
| `reasoning` | string | 1-2 sentence summary |

## Pass Threshold

- **Target: 90+** to pass
- If `score < 90`, continue editing and re-run visual-verdict before any further code changes
- Track iteration count — if 3+ iterations without reaching 90, flag for human review

## Workflow

### Step 1: Capture Current State

```
# Option A: a screenshot skill, if your setup has one

# Option B: Use Playwright MCP
browser_take_screenshot → saved to /tmp/screenshot-{timestamp}.png

# Option C: Manual
User provides screenshot path
```

### Step 2: Load Reference

Read reference image(s) — can be:
- Figma export screenshot
- ASCII mockup rendered to image
- Prior approved screenshot from `visual-verdicts/` in the project
- Design spec image

### Step 3: Compare and Score

Evaluate across these dimensions (weighted):

| Dimension | Weight | What to Check |
|-----------|--------|---------------|
| Layout | 30% | Element positioning, grid alignment, spacing ratios |
| Typography | 20% | Font sizes, weights, line heights, hierarchy |
| Color | 20% | Palette adherence, contrast, semantic color usage |
| Components | 15% | Button styles, input fields, cards, icons match |
| Spacing | 15% | Padding, margins, gaps between elements |

### Step 4: Generate Verdict

```json
{
  "score": 87,
  "verdict": "revise",
  "category_match": true,
  "differences": [
    "Top nav spacing is 12px tighter than reference",
    "Primary button uses font-weight 500, reference shows 600",
    "Card border-radius is 8px, reference shows 6px"
  ],
  "suggestions": [
    "Increase nav item horizontal padding by 12px (px-4 → px-7)",
    "Set primary button font-weight to 600 (font-semibold)",
    "Reduce card border-radius to 6px (rounded-md)"
  ],
  "reasoning": "Core layout matches well. Typography weight and micro-spacing details need one more pass."
}
```

### Step 5: Save Verdict

Save to `visual-verdicts/{component}-{timestamp}.json` in the project root (add `visual-verdicts/` to `.gitignore` if you don't want it committed)

This creates an improvement trail:
```
visual-verdicts/
  home-page-20260401T1430.json    # score: 72
  home-page-20260401T1445.json    # score: 87
  home-page-20260401T1502.json    # score: 94 ← passed
```

### Step 6: Loop or Pass

- If `score >= 90`: verdict is `pass`, mark complete
- If `score < 90`: apply suggestions, re-screenshot, re-run visual-verdict
- If 3+ iterations without passing: escalate to user with full diff history

## Debug Visualization

When mismatch diagnosis is hard:

1. Keep visual-verdict as the **authoritative decision**
2. Use pixel-level diff as a **secondary debug aid** to localize hotspots
3. Convert hotspots into concrete `differences[]` and `suggestions[]`

```bash
# If pixelmatch is available:
npx pixelmatch reference.png generated.png diff.png 0.1
```

## Integration Points

| Skill | How Visual Verdict Fits |
|-------|------------------------|
| `design-taste` | Run visual-verdict after design-taste generates initial UI |
| `frontend-design` | Verification gate before marking implementation done |
| `redesign` | Before/after comparison for upgrade quality |
| a screenshot skill (if you have one) | Input capture for generated screenshots |
| `review-changes` | Add visual-verdict as pre-commit check for UI changes |

## Example: Full Loop

```
1. User: "Implement the home page from the ASCII mockup"
2. → frontend-design builds the page
3. → take a screenshot of the result
4. → visual-verdict compares against ASCII mockup render
5. → Score: 78, verdict: revise
6.    Differences: sidebar width, heading size, card padding
7. → Apply 3 suggestions
8. → take a screenshot of the updated result
9. → visual-verdict re-scores
10. → Score: 93, verdict: pass
11. → Done, commit
```

## Source

Adapted from https://github.com/Yeachan-Heo/oh-my-claudecode (MIT, Copyright (c) 2025 Yeachan Heo); the skill first appeared in https://github.com/Yeachan-Heo/oh-my-codex (MIT, Copyright (c) 2026 Yeachan-Heo). Changed for this repo by Lucas Cooper-Bey in 2026: the file is expanded.
