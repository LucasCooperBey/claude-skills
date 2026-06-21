# Anthropic prompt-engineering — codified reference

> The "one reference file." Read this every time before writing or improving a prompt.
> **Source:** https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/claude-prompting-best-practices
> **Synced:** 2026-06-19 (current models: Fable 5, Mythos 5, Opus 4.8/4.7/4.6, Sonnet 4.6, Haiku 4.5). Re-sync when models change — this guidance moves.

## Before you write a prompt
Prompt engineering assumes you have: (1) clear success criteria, (2) a way to test against them, (3) a first-draft prompt to improve. If a failing eval is really about latency/cost, switch models instead — don't prompt-engineer it.

---

## Part 1 — General principles (all current models)

### Be clear and direct
Treat Claude as a brilliant new employee with no context on your norms. Be specific about the desired output + constraints. If you want "above and beyond," ask for it explicitly — don't rely on inference. Give steps as a numbered list when order/completeness matters.
**Golden rule:** if a colleague with minimal context would be confused by your prompt, so will Claude.
- Weak: `Create an analytics dashboard`
- Strong: `Create an analytics dashboard. Include as many relevant features and interactions as possible. Go beyond the basics to create a fully-featured implementation.`

### Add context / motivation
Explain *why* — Claude generalizes from the reason.
- Weak: `NEVER use ellipses`
- Strong: `Your response will be read aloud by a text-to-speech engine, so never use ellipses since it won't know how to pronounce them.`

### Use examples (multishot)
The most reliable way to steer format, tone, structure. Make examples **relevant** (mirror the real case), **diverse** (cover edge cases; vary so Claude doesn't latch onto an unintended pattern), and **structured** (wrap each in `<example>`, the set in `<examples>`). **3–5 examples** is the sweet spot. You can ask Claude to critique your examples' relevance/diversity or generate more.

### Structure with XML tags
XML tags let Claude unambiguously parse a prompt that mixes instructions, context, examples, and inputs. Wrap each content type in its own tag (`<instructions>`, `<context>`, `<input>`). Use consistent, descriptive names; nest when there's a hierarchy (`<documents>` → `<document index="n">`).

### Give Claude a role
One sentence in the `system` prompt focuses tone + behavior, e.g. `system="You are a helpful coding assistant specializing in Python."`

### Long-context prompting (20k+ tokens)
- **Longform data at the TOP**, above the query/instructions/examples. Queries at the *end* can improve quality up to ~30% on complex multi-doc inputs.
- Wrap each doc in `<document index="n">` with `<source>` + `<document_content>` subtags.
- **Ground in quotes:** ask Claude to first pull relevant quotes into `<quotes>` tags, then do the task — cuts through noise.

### Model self-knowledge
To make Claude identify itself / pick a model string:
`The assistant is Claude, created by Anthropic. The current model is Claude Opus 4.8.`
`When an LLM is needed, default to Claude Opus 4.8 unless the user requests otherwise. The exact model string is claude-opus-4-8.`

---

## Part 2 — Output & formatting

- **Newer models are terser** (more direct, conversational, less verbose; may skip post-tool summaries). If you want summaries: `After completing a task that involves tool use, provide a quick summary of the work you've done.`
- **Say what TO do, not what NOT to do.** Instead of "Do not use markdown" → "Write in smoothly flowing prose paragraphs," or "Write the prose in `<smoothly_flowing_prose_paragraphs>` tags."
- **Match prompt style to desired output.** Markdown in → markdown out; remove it from the prompt to reduce it in the response.
- **LaTeX:** newer models default to LaTeX for math. For plain text, explicitly forbid LaTeX/MathJax/`\( \)`/`$`/`\frac{}` and ask for `/ * ^` notation.

### ⚠️ Prefill is DEPRECATED (major change)
Starting with 4.6 models + Mythos Preview, **prefilling the last assistant turn returns a 400 error.** Migrate:
- **Force a format (JSON/YAML/classification):** use **Structured Outputs** (schema-constrained) or a tool with an enum field. Or just ask — newer models match complex schemas reliably.
- **Kill preambles:** `Respond directly without preamble. Do not start with 'Here is...', 'Based on...', etc.` (or output inside XML tags / use structured outputs; strip stragglers in post).
- **Avoid bad refusals:** no longer needed — clear user-message prompting suffices.
- **Continuations:** put it in the user turn: `Your previous response was interrupted and ended with `[text]`. Continue from where you left off.`

---

## Part 3 — Tool use

- **Be explicit to make Claude ACT.** "Can you suggest changes" → Claude suggests. "Change this function to improve performance" / "Make these edits" → Claude acts.
- **`<default_to_action>`** snippet to make it proactive; **`<do_not_act_before_instructions>`** to make it conservative (see snippet library).
- **Don't over-prompt tool use.** 4.5/4.6 are more responsive to the system prompt and may *over*-trigger. "CRITICAL: You MUST use this tool when…" → "Use this tool when…".
- **Parallel tool calls:** newer models do this well; the `<use_parallel_tool_calls>` snippet pushes it to ~100% (independent calls in parallel; dependent calls sequential; never guess missing params).

---

## Part 4 — Thinking & reasoning

- **Adaptive thinking** (`thinking: {type: "adaptive"}`) replaces extended-thinking-with-`budget_tokens`. Claude decides when/how much to think based on the **`effort`** parameter (`low|medium|high|xhigh|max`) + query complexity. Prefer it for agentic/multi-step/coding work. `budget_tokens` still works on 4.6/Sonnet 4.6 but is deprecated — control depth via `effort` (or `max_tokens` as a hard cap).
- **Don't hand-write CoT steps** — "think thoroughly" usually beats a prescriptive plan. Reserve manual `<thinking>`/`<answer>` tags for when thinking is OFF.
- **Multishot + thinking:** put `<thinking>` tags inside few-shot examples to teach a reasoning style.
- **Self-check:** append `Before you finish, verify your answer against [criteria].` — catches errors, especially code/math.
- **Over-thinking:** 4.6 explores a lot at high effort. To rein in: lower `effort`, or `When deciding how to approach a problem, choose an approach and commit… avoid revisiting unless new info contradicts it.`
- **Word sensitivity:** with thinking OFF, Opus 4.5 is sensitive to "think" — use "consider/evaluate/reason through."

---

## Part 5 — Agentic systems

- **Long-horizon / state:** newer models track state well across context windows. Use structured files for state (`tests.json`), freeform notes for progress (`progress.txt`), and **git** for checkpoints. Emphasize incremental progress.
- **Context awareness / compaction:** if your harness compacts or saves to files, tell Claude so it won't wrap up early — see the `Your context window will be automatically compacted…` snippet.
- **Multi-window:** different prompt for the first window (set up tests/scripts), then iterate a todo-list; have it write tests first ("It is unacceptable to remove or edit tests"); create `init.sh`; on a fresh window be prescriptive ("call pwd; review progress.txt, tests.json, git logs").
- **Autonomy vs. safety:** without guidance 4.6 may do irreversible things. Use the reversibility snippet to require confirmation for destructive/hard-to-reverse/visible-to-others actions, and to ban destructive shortcuts (`--no-verify`).
- **Research:** give clear success criteria, ask for multi-source verification, and use the structured hypothesis-tree snippet for complex research.
- **Subagents:** 4.6 orchestrates natively (and may *over*-spawn — e.g. a subagent for a job a `grep` would do). Steer with the subagent-usage snippet.
- **Chain prompts** when you need to inspect intermediates: the common pattern is **self-correction** (draft → review against criteria → refine), each a separate call.
- **Overeagerness / overengineering:** 4.5/4.6 over-build (extra files, abstractions, unrequested flexibility). Use the anti-overengineering snippet (scope/docs/defensive-coding/abstractions limits).
- **Anti-hardcoding:** ask for a general solution, not test-passing hacks (snippet).
- **Anti-hallucination:** the `<investigate_before_answering>` snippet — never speculate about unopened code; read referenced files first.
- **Reduce file creation:** ask it to clean up temp scratch files at the end.

---

## Part 6 — Capability tips
- **Vision (4.5/4.6):** better multi-image extraction; giving a crop/"zoom" tool/skill consistently boosts image-eval performance; analyze video by splitting into frames.
- **Frontend:** without guidance, models default to "AI slop" (Inter/Roboto, purple-on-white gradients, cookie-cutter layouts). Use the `<frontend_aesthetics>` snippet to force distinctive typography/color/motion/backgrounds.

---

## Part 7 — What CHANGED (don't ship stale advice)
1. **Prefill (last assistant turn) is gone** → Structured Outputs / direct instructions.
2. **Adaptive thinking + `effort`** replace manual `budget_tokens`.
3. **Stop over-prompting.** Aggressive "CRITICAL/MUST/ALWAYS" + "if in doubt use [tool]" now cause *over*-triggering. Use normal phrasing; dial back anti-laziness language.
4. **Models are more proactive + terser** — request summaries/animations/thoroughness explicitly if you want them.
5. **Be specific & use quality modifiers** when migrating ("…go beyond the basics to create a fully-featured implementation").

---

## Snippet library (copy-paste building blocks)

**Proactive action**
```
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's intent is
unclear, infer the most useful likely action and proceed, using tools to discover any
missing details instead of guessing.
</default_to_action>
```

**Conservative action**
```
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed. When intent is
ambiguous, default to information, research, and recommendations rather than action. Only
edit/modify/implement when the user explicitly requests it.
</do_not_act_before_instructions>
```

**Parallel tool calls**
```
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between them, make all
independent calls in parallel rather than sequentially. If some calls depend on previous
results, call those sequentially. Never use placeholders or guess missing parameters.
</use_parallel_tool_calls>
```

**Context-window awareness (agent harness)**
```
Your context window will be automatically compacted as it approaches its limit, allowing
you to continue working indefinitely. Do not stop early due to token-budget concerns. As
you approach the limit, save progress and state to memory before the context refreshes.
Be as persistent and autonomous as possible; never artificially stop a task early.
```

**Autonomy vs. safety**
```
Consider the reversibility and impact of your actions. Take local, reversible actions
(editing files, running tests) freely, but for actions that are hard to reverse, affect
shared systems, or could be destructive, ask the user first. Examples warranting
confirmation: deleting files/branches, dropping tables, rm -rf, git push --force, git
reset --hard, pushing code, commenting on PRs, sending messages. Never use destructive
actions (e.g. --no-verify) as a shortcut.
```

**Anti-overengineering**
```
Avoid over-engineering. Only make changes directly requested or clearly necessary.
- Scope: don't add features/refactors/"improvements" beyond the ask.
- Documentation: don't add docstrings/comments/types to code you didn't change.
- Defensive coding: only validate at system boundaries (user input, external APIs).
- Abstractions: no helpers/utilities for one-time ops; no designing for hypothetical futures.
```

**Anti-hallucination (coding)**
```
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific file,
read it before answering. Investigate relevant files BEFORE answering questions about the
codebase. Never make claims about code before investigating unless you are certain.
</investigate_before_answering>
```

**Complex research**
```
Search in a structured way. As you gather data, develop several competing hypotheses.
Track confidence levels in your progress notes. Regularly self-critique your approach.
Update a hypothesis tree / research-notes file to persist information. Break the task down
systematically.
```

**Subagent usage**
```
Use subagents when tasks run in parallel, need isolated context, or are independent
workstreams that don't share state. For simple tasks, sequential steps, single-file edits,
or work needing shared context, work directly rather than delegating.
```

**Minimize markdown (prose output)** and **frontend aesthetics** snippets: see the source page — pull verbatim when needed.
