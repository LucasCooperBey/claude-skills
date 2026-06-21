---
name: model-migration
description: Generate a personalized "how to use this new model" report by mining ALL your local Claude Code sessions, then comparing your actual usage patterns against the new model's documented behavior. Use when a new Claude/Codex/Gemini model ships (e.g. "how should I use Opus 5", "model migration", "what changes with the new model", "tailor my workflow to <model>"). Produces an evidence-backed report grounded in YOUR 1,000+ JSONL sessions, not a generic tutorial.
---

# Model Migration

Personalized upskilling for a new model, grounded in your real history. Inspired by Mark Kashef's "dynamic workflows" model-migration pattern (YT 9_ExDZFlaNc). The point: skip the generic "this model is INSANE" tutorial and generate advice tailored to how *you* actually prompt and which tools *you* actually use.

## When to run

A new model shipped and you want to know what to change. Run it **per model bump** (4.8 → 4.9 → 5 → ...). Not a daily tool — it burns tokens via agent fan-out. Re-run sporadically.

## The recipe

### 1. Deterministic full-corpus mine (zero LLM tokens)

Run the bundled miner — it processes EVERY `~/.claude/projects/**/*.jsonl` session with `jq`/`awk` and writes a digest. This is the "data analysis" layer; doing it deterministically keeps the 600MB+ of raw session noise out of agent context.

```bash
bash ~/.claude/skills/model-migration/mine_sessions.sh
```

Outputs to the directory set by `$MODEL_MIGRATION_OUT` (default: `~/model-migration-output/`):
- `01-models.txt` — model usage histogram (are you ignoring your own routing matrix?)
- `02-tools.txt` — tool-use histogram (your real workflow shape)
- `03-tokens.txt` — input/output/cache token totals
- `04-user-prompts.txt` — your full prompt corpus (the signal for prompting-pattern analysis)
- `05-session-dist.txt` — session length distribution

### 2. Fan-out analysis (Workflow tool)

Requires explicit opt-in (the user asking for this skill IS the opt-in). Author a Workflow that:

- **Qualitative prompt-pattern agents** — chunk `04-user-prompts.txt` (it's a few MB, NOT the full 600MB) across N agents; each extracts: recurring prompt shapes, verbosity, where the user over/under-specifies, retry/frustration signals, task archetypes.
- **`claude-code-guide` agent** (`agentType: 'claude-code-guide'`) — fetch the NEW model's release notes + Claude Code docs; produce a "what changed" brief grounded in Anthropic docs.
- **Synthesis agent** — merge the deterministic digest + qualitative findings + the docs brief into the report.

### 3. Report sections (match Mark's structure)

1. Executive summary / checklist
2. Usage profile analysis (from the digest)
3. Direct competency comparison (old model → new model, tied to your tasks)
4. Prompting patterns to change (be more literal with newer models; they handle direct prompts without hedging)
5. Skill & tool recommendations
6. Dynamic workflows you could build next
7. Advanced opportunities

Write the report as HTML to the output dir so it's shareable.

### 4. (Optional) Video

Mark converted the HTML to a 2-min explainer with Hyperframes (open-source, by Hay Jin). You have Remotion skills (`remotion-studio`, `remotion-kickstart`) — use those instead to render a walkthrough if you want the video artifact.

## Notes

- "All sessions" is honored by the deterministic pass (it genuinely reads all 1,014). The qualitative agents work the distilled prompt corpus — reading raw tool-call/thinking noise wastes tokens without adding signal.
- Scope agent count to the model's importance. A point release ≠ 60 agents.

## Workflow reliability (learned 2026-06-02)

Do NOT attach a `schema` to the prompt-pattern agents — they read a chunk and naturally end in prose, so StructuredOutput forcing fails (12/12 failed on the first run; synthesis compensated). Have pattern agents return MARKDOWN and let the synthesis agent read it, OR end their prompt with "Your FINAL action MUST be the StructuredOutput call; do not end with prose." Synthesis/writer agents with no schema are reliable. Pattern: have agents return MARKDOWN and let synthesis read it; schema forcing on prose-output agents fails reliably.
