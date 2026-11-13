# prompt-grounding

A Claude Code skill that checks a prompt against your project before anyone acts on it. It reads the docs, code and archived decisions, then sorts each claim in the prompt as ACCURATE, INVENTED, CONFLATED or MISFRAMED with the file and line that shows it, names the real gap, and rewrites the prompt so it matches what the project says.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/prompt-grounding ~/.claude/skills/
```

## Quick start

In Claude Code, with the prompt you want checked saved as `prompt.txt` in your project, type:

```
Use the prompt-grounding skill on the prompt in prompt.txt against this project, and give the result in the skill's output format.
```

You get the claim audit, the real gap in a few sentences, and a grounded prompt you can hand on in place of the original.

## Example

The fixture was a small invoicing project: a README with Pro at $29 a month and a 14-day trial, an archived decision "No free tier", and a working `export_invoices_csv` in `src/export.py`. The prompt said Pro is $19, claimed a free tier, said there is no export yet, and asked for a "Momentum Score" dashboard. The reply, with its first line left out:

```
## Claim Audit

### ACCURATE (1 claim)
- **A Pro plan exists.** Confirmed in `README.md:7`: "Pro: $29 a month, with a 14-day trial." The plan is real but the price in the prompt is wrong (see CONFLATED).

### INVENTED (2 terms/concepts)
- **"Momentum Score"**: appears nowhere in the project. No doc defines it, no code calculates it, and nothing says what goes into it or what it's for.
- **"dashboard"**: appears nowhere in the project. The only code is a CSV writer, with no UI, web layer or reporting surface.

### CONFLATED (1 claim)
- **The prompt says Pro is $19 a month. The docs say $29 a month, with a 14-day trial.** Source: `README.md:7`. The prompt also leaves out the Team plan at $79 a month (`README.md:8`).

### MISFRAMED (2 gaps)
- **The prompt says "we have a free tier."** This was decided against and archived: `docs/archive/decisions-2026-03.md:3` says "No free tier. The 14-day trial on Pro replaces it." The README also lists no free plan. Any work built around a free tier goes against that decision.
- **The prompt says "there is no export feature yet" and asks for a CSV export of invoices.** That export already exists: `src/export.py:3`, `export_invoices_csv(invoices, path)`, writes `id`, `customer`, `total` to a CSV. What's missing could be a way to call it (no CLI, endpoint or UI uses it in this project), more columns (date, status, line items) or tests. "Add a CSV export" isn't the gap.

## The Real Gap
The CSV invoice export already exists. The only open questions are whether it needs more fields or a way for users to trigger it. The "Momentum Score" dashboard is a brand-new idea with no definition, so someone has to decide what the score measures before anything can be built.

## Grounded Prompt
> Ledgerly is a small-business invoicing product with two paid plans: Pro at $29 a month with a 14-day trial, and Team at $79 a month (`README.md`). There is no free tier; the March 2026 decision replaced it with the Pro trial (`docs/archive/decisions-2026-03.md`).
>
> **1. Extend the existing invoice CSV export.** `src/export.py` already has `export_invoices_csv(invoices, path)`, which writes `id`, `customer` and `total`. Don't rewrite it. Instead:
> - suggest which extra columns are worth adding (for example invoice date, due date, status, currency), keeping the current column order so existing files still work;
> - suggest how users should trigger the export (CLI command, endpoint or UI button), since nothing calls it today;
> - add tests for the function.
>
> **2. Customer "Momentum Score" (new idea, not in any doc yet).** Nothing in the project defines this score, and there is no dashboard or UI layer. Before building anything, propose:
> - a definition of the score from invoice data we already have (for example invoice frequency, change in total billed, on-time payment rate), with the formula and the reasoning behind it;
> - whether it should be limited to a plan (Pro or Team);
> - the smallest useful way to show it (for example a CSV column or report first, a dashboard only if a UI layer is added later).
>
> Don't assume a free tier or a $19 price anywhere.
```

## Needs

- Claude Code. The skill uses only its read and search tools.
