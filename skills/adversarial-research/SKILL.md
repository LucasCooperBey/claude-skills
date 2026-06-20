---
name: adversarial-research
description: Deep research where agents adversarially fact-check each other's findings instead of one agent confidently citing sources it never verified. Scrapes claims from X/web/GitHub, then spins up independent verifier agents that try to REFUTE each claim, labeling them survives / cut / unconfirmed with source links. Use for "fact-check these claims", "what holds up vs hype", "peer-review this research", "adversarial research on X". Overlaps deep-recon — prefer this when the goal is verifying contested claims, not discovering prior art.
---

# Adversarial Research

Peer-review-by-agent. Inspired by Mark Kashef's second dynamic-workflow use case (YT 9_ExDZFlaNc): a single deep-research agent claims "checked 300 sources" but never plays devil's advocate against itself. This spins up a separate verification swarm whose job is to break each claim.

## When to run

You have a body of contested claims (a new feature's capabilities, a vendor's marketing, a hyped technique) and want signal separated from hype. Token-heavy — Mark's run was ~200 agents / 20 min. Scope the depth.

Relationship to your existing skills: `deep-recon` finds existing solutions (prior-art search); `deep-research` synthesizes a cited report. This one is specifically the **adversarial verification layer** — use it on top of, or instead of, those when claims are disputed.

## The recipe

### 1. Gather claims

Pull raw claims from the relevant surface:

- **X/Twitter** — Apify X scraper actor (search `apify` MCP: `search-actors` → `tweet scraper`). You already use Apify for YouTube analytics. Alternatively the native X API toolkit (`~/Developer/personal/x-tools/`).
- **Web/GitHub** — `mcp__exa__web_search_advanced_exa`, `mcp__exa__crawling_exa`, `mcp__ref__*`.

Extract atomic claims (one assertion each) with their source URL. Write to a claims file.

### 2. Adversarial verification (Workflow tool, explicit opt-in)

Pipeline each claim through independent skeptic agents:

```
pipeline(claims,
  claim => agent(`Try to REFUTE this claim. Default to refuted=true if you cannot find
                  primary evidence. Claim: ${claim.text}  Source: ${claim.url}`,
                 {schema: VERDICT}),
  ...
)
```

For high-stakes claims use a **perspective-diverse panel** (3 verifiers, distinct lenses: primary-source / reproducibility / counter-example) and require majority to survive.

### 3. Label + report

Each claim → `survives` (independently verified) / `cut` (refuted) / `unconfirmed` (no primary evidence either way), with the link that settled it. Write an HTML report grouping by verdict so disputed claims are scannable with "a second set of eyes."

## Guardrails

- Verifiers must cite the source that confirmed/refuted — no unsourced verdicts.
- Bias toward `unconfirmed` over `survives` when evidence is thin. Hype masquerades as confirmed.
- Route web fetches through the sandboxed research proxy where appropriate (`research-proxy` / `link-preview-subagent`) to avoid indirect prompt injection from scraped content.

## Workflow reliability (learned 2026-06-02)

CRITICAL: the verify agents do web research and end in prose, so forcing a `schema` on them failed catastrophically (~190/239 dropped to null on the first run). Two safe fixes: (1) have each verifier return a one-line verdict in plain text like `VERDICT: survives | url | reason` and parse with a regex/jq pass, or (2) end the prompt with "Your FINAL action MUST be the StructuredOutput call; do not end your turn with prose." Also cap extraction — 80 tweets produced 239 fragmentary "claims"; instruct extractors to emit only distinct, substantive, testable claims (target ≤ ~5/tweet). See [[feedback_workflow_structured_output_failure]].
