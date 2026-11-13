---
name: breakdown
description: Produce a multi-altitude explainer of a body of work (what it is, why it matters, where it sits, and how it was learned). Trigger when the user says "break it down", "explain what we did/built", "what was this", "give me the story", "zoom out", "explain at 100k/50k/30k/10k ft", "one-sentence version", "package this up", "what's the shape of this", or asks for ASCII C4 diagrams of work just completed. Defaults to explaining the CURRENT session's work; can target a named repo/feature/PR/commit-range. Also mines the session trace for the originating prompt and proposes an improved version of it. Composes as the optional final coda of /pp2p. Substantial explanations also render as a zoomable altitude HTML page (Step 7).
---

# /breakdown: the multi-altitude explainer

Turn a body of work into an explanation that a non-technical person *and* an engineer both find illuminating, and that is good enough to become seed documentation for a repo.

This skill exists because: **we often build something powerful that took a long, winding path to figure out, and then the wisdom of HOW and WHY evaporates.** This captures it while it's fresh, in a shape that's legible, attractive, and reusable.

## Step 0: Identify the subject + mine the prompt

**Bare invocation (`/breakdown` with no args): assume, don't ask.** Default to:
- **Audience = the person asking** (assume smart but not academic; plain language first, depth on demand).
- **Heavy ASCII** throughout: this is the house style for breakdowns.
- **Subject = the substantive work done in the current session.**
- **Skip the prompt-coaching** (Step 0.2's "improved variant"): don't append it to a normal breakdown.
Only deviate when the user names a different target, audience, or passes a flag. Never stall on a clarifying question: state any assumption in one line and proceed.

1. **Subject.** Default = the substantive work done in the *current session*. If the user names a target (a repo, a feature, a PR, a commit range, a file), use that instead. If ambiguous, state your assumption in one line and proceed (don't stall on a question).
2. **Mine the originating prompt (OPTIONAL, off by default).** Only when the user explicitly asks "how should I have asked?" or passes a `+prompt` flag: find the originating message, quote it, and write one improved variant. Otherwise skip this step entirely: the bare `/breakdown` should not lecture the user on how to prompt.

## Step 1: Lead with the one-sentence version

The first thing on screen is a single bolded sentence a layperson understands. No jargon. A metaphor is good. This is non-negotiable and goes first.

## Step 2: Descend the altitudes (lay-person BEFORE technical)

Produce four altitude sections, in this order, each headed by its altitude:

- **100,000 ft: for a non-technical person.** The point, in plain language, with a vivid analogy. Why a normal person would care. Use an ASCII before/after or simple diagram here: concrete beats abstract.
- **50,000 ft: strategic.** Where this fits in the bigger goal. What problem-class it solves. Any rollout/sequence/roadmap framing.
- **30,000 ft: the technical shape (C4 diagrams).** ASCII C4: a Context diagram (who/what uses it), a Container diagram (the systems/repos involved + status), and at least one before→after of the core idea. Label clearly.
- **10,000 ft: the engineering.** A Component (C3) ASCII diagram of the internals, plus the concrete decisions/bugs/tradeoffs. A small table of "issue found → why it mattered → fix" is ideal when there was a review process.

Rules for the altitudes:
- **ASCII art only, never images.** Monospace box-drawing. Keep diagrams under ~70 cols so they render in a terminal.
- Each altitude must be readable on its own; someone can stop at any level and have gotten value.
- Brief ≠ shallow. Depth is welcome here; this is the one place where long-form is correct. (Match length to the complexity of the work.)

## Step 3: Where it sits (the architecture placement)

Place the work inside the project's existing structure. If the project keeps these docs, read and cite them; if it does not, say so in one line and place the work from the code itself:
- A registry or list of its reusable parts: which part is this, or does it add a new one?
- An architecture overview: which layer(s) does it touch?

Show an ASCII placement (the relevant tier/layer slice with this work highlighted). Then state how it relates to the *adjacent* primitives (what it depends on, what depends on it, what it composes with).

## Step 4: The seed backstory (the "why it's whole and attractive" facets)

These eight facets make the explanation feel complete and make it directly reusable as a repo README. Cover each in 1-3 tight sentences:

1. **Ultimate solve:** not the mechanism, the *end state* it buys. ("Make the past queryable and trustworthy so the present can be built on without fear," not "it logs changes.")
2. **Why it matters:** the cost of NOT having it.
3. **Downstream effects:** what it unlocks elsewhere (autonomy, sellability, compounding, etc.).
4. **Best use cases:** where to reach for it; where NOT to.
5. **How we learned it:** the path: the research, the failures, the process that hardened it.
6. **What inspired it:** the intellectual lineage / prior art (name names).
7. **Source material:** specific docs, memos, transcribed videos, corpora used. If exact titles aren't to hand, name the corpus + how to pull them, and add a runbook TODO rather than inventing titles.
8. **Historical evolution:** how the idea evolved from inspiration → first instance → hardened standard.

## Step 5: Honest gaps

A short, plain list of what is NOT done / NOT in scope / known follow-ups. Never let the explainer read as "everything is perfect." If there are deferred items, name them and why they were deferred. Cross-check against the project's own status or ground-truth docs, when it has them, so no claim drifts from known reality.

## Step 6: Offer to crystallize

End by offering (one line, not a paragraph) to save the explanation as: a repo `README` / a seed doc / a `HOUSE-STANDARDS.md` entry / a wiki synthesis node. Don't auto-write unless the work clearly warrants a durable home and the user's pattern is "just do it."

## Step 7: Render the zoomable altitude page

1. When to render: the explanation is substantial (a system, a multi-part build, a nontrivial concept) or the user asks for an explainer, a zoomable page or HTML. Skip it for small conversational breakdowns.
2. Copy `template.html` from this skill's folder (`~/.claude/skills/breakdown/` for a personal install, `.claude/skills/breakdown/` inside a project) to `explainers/YYYY-MM-DD-<slug>.html` in the current project, creating `explainers/` if needed.
3. Fill every `⟪placeholder⟫`: the header (title, kick, one-liner, meta), the four altitude sections with the same content Steps 1 to 5 produced, and the `const ANATOMY = {...}` node object, where each node has `in`, `out`, the rule it enforces and its real paths, and `cls` is `"gate"`, `"human"` or `"guard"` where that applies. Every value comes from the work being explained; never invent a path, number or receipt.
4. Keep the CSS and the renderer script as they are. Every Mermaid diagram keeps its ASCII fallback in the `<details>` beside it. The page must work offline; the pinned Mermaid script from jsDelivr is its only network load, and without it the ASCII fallbacks open.
5. After saving, check that no `⟪` remains in the file (`grep -c '⟪' <file>` prints 0), then print the full path and tell the user how to open it.

## Quality bar (the taste this skill enforces)

- One-sentence version first. Always.
- Lay-person framing before any technical content.
- ASCII C4, not prose-only and not images.
- Cite `file:line` and commit SHAs for anything concrete: receipts, not assertions.
- Name the prior art and the source material: intellectual honesty is part of why it feels trustworthy.
- Surface gaps. A breakdown that hides what's unfinished is propaganda, not documentation.

## Composition

- Invoke standalone anytime ("break this down", "/breakdown").
- As a **pp2p coda**: after a perfection pass converges, run /breakdown on the hardened work so every major change ships *with* its own multi-altitude explanation. (This is the recommended default for substantial features.)
