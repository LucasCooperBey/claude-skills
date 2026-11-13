# adversarial-research

A Claude Code skill for checking contested claims. It splits a source into atomic claims and plans a verification pass in which skeptic agents try to refute each claim and label it `survives`, `cut` or `unconfirmed` with the link that settled it. That pass fans out many agents, so the skill stops after the claims list and the plan and waits for you to opt in; the example below covers that first phase only.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/adversarial-research ~/.claude/skills/
```

## Quick start

In Claude Code, with the text you want checked saved as `post.md`, type:

```
Use the adversarial-research skill on post.md. Do step 1 only: extract the atomic claims with their source to claims.md. Then write the step 2 verification plan, but do not run any agents or web searches.
```

You get `claims.md` with one testable claim per row and a plan for the verification step: how many skeptic agents, which claims get a three-verifier panel, and the verdict line each verifier must end with. Running step 2 is a separate, opted-in step.

## Example

The fixture was a made-up vendor launch post of two sentences (first model to score 100% on SWE-bench Verified, runs on any 8 GB laptop with no GPU, trained on 40 trillion tokens, 10x fewer bugs, MIT licensed, weights on Hugging Face), with a source URL on a reserved test domain. Only the first phase ran, as in the Quick start. The table is from the `claims.md` it wrote; the plan summary is from its reply, trimmed to that part.

```
| ID | Atomic claim | Type | Testable via | Stakes |
|----|--------------|------|--------------|--------|
| C1 | The model scores 100% on SWE-bench Verified. | Benchmark | Official SWE-bench leaderboard; submitted trajectories/logs | High |
| C2 | It is the first model ever to score 100% on SWE-bench Verified. | Priority / "first ever" | Leaderboard history; any earlier 100% submission | High |
| C3 | The model runs on any laptop with 8 GB of RAM. | Hardware requirement | Parameter count + quantization → memory footprint; user reports | Medium |
| C4 | The model runs with no GPU (CPU-only). | Hardware requirement | Model card; inference runtime support (e.g. llama.cpp/GGUF); user reports | Medium |
| C5 | The model was trained on 40 trillion tokens. | Training detail | Model card / tech report; plausibility check against the model's size | Low |
| C6 | Teams who switched to the model ship 10x fewer bugs. | Outcome / causal | Study methodology, sample, baseline, and who measured it | High |
| C7 | The model is MIT licensed. | License | LICENSE file in the weights repo; Hugging Face license metadata | Medium |
| C8 | The model weights are available on Hugging Face now. | Availability | Hugging Face search for the vendor's org/model | Medium |
```

```
- **Scale:** 15 agents. That's three skeptics each for the high-stakes claims (C1, C2, C6), one skeptic for each of the other five, plus the finder agent. This is above the usual guideline of fewer than 10 agents per run. Using one skeptic per claim brings it down to 9.
- **Verdict format:** each verifier ends with one plain-text line, `VERDICT: survives|cut|unconfirmed | url | reason`, which a regex then reads. The skill's own notes say forcing a fixed output format on these agents caused most results to come back empty. If a verifier's line can't be read, it counts as `unconfirmed` rather than being dropped.
- **Defaults:** if evidence is thin, the verdict is `unconfirmed`. Pages the vendor controls can show that the license and weights exist (C7, C8), but they don't count as proof of the benchmark score, hardware needs or bug-rate claims.

Running step 2 needs you to opt in to the Workflow tool, and to choose between 15 agents and 9.
```

It also noted that the post never names the model or the vendor and that the source URL cannot open, so the plan starts with one agent whose only job is to find them.

## Needs

- Claude Code.
- Claude Code's Workflow tool for step 2, the verifier agents.
- Web search for step 2: Claude Code's WebSearch and WebFetch work; web-search MCP tools such as Exa or Ref are optional.
- An X scraper, optional, if your claims come from X posts.

Source and credit: see the Source section of SKILL.md.
