# claude-skills

A small, curated set of [Claude Code](https://claude.com/claude-code) **skills** — reusable methodology packets that teach the agent *how* to do a class of work well. Each is a self-contained `SKILL.md` (plus optional `references/`); drop a folder into `~/.claude/skills/` and Claude auto-invokes it when the task matches.

These are the generic, no-secrets, no-personal-infra skills extracted from a larger private setup. They're methodology, not config — portable to any Claude Code install.

## The skills

| Skill | What it does |
|---|---|
| **prompt-grounding** | Audits a prompt against the actual codebase before sending — separates fact from invention, finds what's already built, rewrites grounded in reality. |
| **adversarial-research** | Deep research where verifier agents try to *refute* each claim instead of one agent confidently citing unread sources. Labels findings survives / cut / unconfirmed. |
| **critique** | Single-pass 3-agent critique for any work product — plans, code, designs, architecture. The general refinement tool. |
| **grill** | Adversarial code review — challenge code harshly, find what breaks in production. |
| **verification-before-completion** | Mandates fresh verification evidence before any "it's done / it passes" claim. Evidence before assertions. |
| **output-enforcement** | Overrides default truncation — bans placeholder/ellipsis patterns, enforces complete code output, handles token-limit splits cleanly. |
| **reverse-engineer-to-learn** | Strategic teardown of an app/package/repo to inform a new build — the 5 strategic questions, not a clone. |
| **package-research** | Researches packages/APIs against real source before integration, instead of guessing an API surface. |
| **coding-agents** | Core patterns for building AI coding agents — tool calling, agent loops, framework selection, production considerations. |
| **writing-plans** | Detailed implementation plans for multi-step tasks — exact files, code, test commands — before touching code. |
| **executing-plans** | Implements a written plan in batched phases with review checkpoints; stops on blockers instead of guessing. |
| **breakdown** | Multi-altitude explainer of a body of work — one-sentence → 100k/50k/30k/10k-ft, plus ASCII C4 diagrams. |
| **naming-the-machine** | Scans your systems to find and name emergent products / methodologies / IP hiding in what you've already built. |
| **deep-recon** | Multi-agent research swarm that finds existing solutions before you write a line of code. |
| **threat-model** | Repository-grounded threat modeling — trust boundaries, assets, abuse paths tied to real code, not a generic OWASP checklist. |
| **mcp-builder** | Builds MCP servers for API integration across the full dev lifecycle, research → evaluation. |

## Install

```bash
git clone https://github.com/Lucface/claude-skills.git
# copy the ones you want:
cp -R claude-skills/skills/grill ~/.claude/skills/
```

Restart Claude Code. The skill activates automatically when your task matches its description, or invoke it explicitly.

## License

MIT — see [LICENSE](./LICENSE). By [@Lucface](https://github.com/Lucface). More skills land here as they're scrubbed for public release.
