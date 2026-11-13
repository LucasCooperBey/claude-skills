# visual-verdict

A Claude Code skill that compares a screenshot of what you built against a reference image and returns a JSON verdict: a score from 0 to 100, `pass`, `revise` or `fail`, the concrete differences, and suggested edits tied to them. The skill's method is to apply the edits, take a new screenshot and compare again until the score reaches 90.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/visual-verdict ~/.claude/skills/
```

## Quick start

In Claude Code, with your screenshot and the reference saved in the project, type:

```
Use the visual-verdict skill to compare built.png against reference.png, category dashboard, and return the skill's JSON verdict.
```

You get one JSON object in the skill's shape: score, verdict, whether the category matches, the differences, the suggestions and a short reasoning.

## Example

The fixture was two 600 by 400 PNGs drawn with ImageMagick: a reference dashboard (blue header, 28 point title, two equal white cards) and a built version with three planted changes (green header, 18 point title, the right card smaller and moved down and in). This is the full reply, untrimmed; the run was told not to save the verdict to a file.

````
I compared built.png against reference.png and didn't save the verdict to a file. The Revenue card and page background match; the header colour, title size and Orders card do not.

```json
{
  "score": 63,
  "verdict": "revise",
  "category_match": true,
  "differences": [
    "Header bar is green (~#16A34A) in the build; the reference is blue (~#1D4ED8)",
    "The 'Sales dashboard' title is noticeably smaller in the build (~18px vs ~26px in the reference)",
    "Orders card is smaller in the build (~210x220px vs 260x260px in the reference)",
    "Orders card is offset: it starts at roughly x=336, y=140 instead of x=316, y=100, so its top no longer lines up with the Revenue card",
    "Gap between cards is ~52px in the build vs ~32px in the reference, and the right margin is wider (~54px vs ~24px)",
    "The 'Orders' label is shifted down along with its card, so it no longer lines up with the 'Revenue' label"
  ],
  "suggestions": [
    "Change the header background to the reference blue (e.g. #1D4ED8 / Tailwind blue-700)",
    "Increase the header title font size to ~26px (e.g. text-2xl/text-[26px])",
    "Make the Orders card the same size as Revenue (260x260px), ideally with a shared card class or equal-width grid columns",
    "Remove the extra top offset/margin on the Orders card so both cards share y=100 (align-items: start in a 2-column grid)",
    "Use a two-column grid with a 32px gap and 24px outer padding so the card positions match the reference"
  ],
  "reasoning": "The overall dashboard structure and the Revenue card match, but the header colour and title size are wrong and the Orders card is the wrong size and position, which breaks the two-column alignment. Fixing the header styles and making the two cards a uniform grid should bring this to pass."
}
```
````

## Needs

- Claude Code, which reads PNG and JPEG images directly.
- A screenshot of your build and a reference image. Any screenshot works; a browser tool such as the Playwright MCP server is optional.
- `npx pixelmatch`, optional, for a pixel diff when a mismatch is hard to find.

Source and credit: see the Source section of SKILL.md.
