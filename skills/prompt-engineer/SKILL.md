---
name: prompt-engineer
description: Turn a rough natural-language ask into a high-quality, Anthropic-spec prompt. Use when the user wants to write, engineer, improve, tighten, or harden a prompt — "write me a prompt for X", "make this prompt better", "rewrite my prompt to spec", "engineer this prompt", "prompt for <task>", or /prompt. ALWAYS reads references/anthropic-prompt-engineering.md (the codified current Anthropic guidance) before writing, instead of relying on memory of prompt-engineering folklore (now partly stale — e.g. prefill is deprecated, budget_tokens → adaptive thinking).
---

# Prompt Engineer

Rewrite the user's raw intent into a prompt that follows Anthropic's **current** best practices — grounded in the codified reference, not from memory.

## Why this exists
Claude "thinks it knows" how to write a prompt and skips the docs. The docs have also moved: **prefill is deprecated**, **adaptive thinking + `effort`** replaced `budget_tokens`, and newer models **over-trigger** on "CRITICAL: You MUST" language. So this skill makes referencing the doc non-optional.

## Workflow — do this every time

1. **Read the reference FIRST.** Open `references/anthropic-prompt-engineering.md` before writing anything. This is the entire point of the skill — do not skip it, do not work from memory.

2. **Capture intent.** Get the raw ask plus the few things that change the prompt. If any are unclear, ask as a SHORT multiple-choice (not free-text):
   - Target model / harness? (Opus 4.8 API · Claude Code agent · Fable 5 · other)
   - One-shot prompt · system prompt · agentic/long-horizon?
   - Output format? (prose · JSON/structured · code · HTML · a document)
   - Does it use tools / run autonomously?
   Default sensibly and proceed if the user said "just go."

3. **Engineer it** against the reference checklist:
   - Clarity & specificity; state the output + constraints; sequential steps as a numbered list.
   - Add context/motivation ("because …") — Claude generalizes from the why.
   - Examples: 3–5, relevant + diverse, in `<example>` / `<examples>` tags.
   - Structure with XML tags (`<instructions>`, `<context>`, `<input>`, `<documents>`).
   - Give a role (one system sentence).
   - Control output by saying what TO do (not "don't"); match prompt style to desired output.
   - Thinking: rely on adaptive thinking + `effort`; add a self-check line; avoid prescriptive CoT steps.
   - Tools: be explicit ("make these edits", not "could you suggest"); add the parallel-tools snippet if relevant.
   - Long context (20k+): longform data at the TOP, query at the bottom; ask it to quote first.
   - **Don't** over-prompt ("CRITICAL: You MUST" → "Use … when …"); **don't** add prefill; **don't** use `budget_tokens`.
   - Add the anti-overengineering / anti-hallucination / autonomy-safety snippets when the task warrants them (reference § snippet library).

4. **Deliver.** Output the engineered prompt in ONE clean fenced block, then a 2–4 line "what I changed & why." Keep it copy-paste ready — no placeholders.

5. **Offer to run it** (or run it if asked). For high-stakes prompts use generate → review-against-criteria → refine.

## Prompt skeleton (assemble only the parts you need, roughly this order)
1. Role (system) · 2. Task context / goal · 3. Tone & format rules · 4. Background data & documents (XML; at the TOP for long context) · 5. Detailed rules & steps · 6. Examples (`<examples>`) · 7. Conversation history · 8. The immediate task/question · 9. "Think / self-check" · 10. Output-format spec.

## Keep the reference fresh
The Anthropic guidance evolves (prefill got deprecated; adaptive thinking arrived). When models change, re-sync `references/anthropic-prompt-engineering.md` from:
https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices

## Not this skill
- Auditing a prompt's *factual claims* against your codebase/strategy → `prompt-grounding`.
- Generating a Ralph autonomous-loop prompt → `ralph-prompt-generator`.
