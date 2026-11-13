# claude-skills

A curated, **no-secrets** library of [Claude Code](https://claude.com/claude-code) **skills** — reusable methodology packets that teach the agent *how* to do a class of work well. Each is a self-contained `SKILL.md` (plus optional `references/`); drop a folder into `~/.claude/skills/` and Claude auto-invokes it when your task matches its description.

These are generic skills for Claude Code, some extracted from a private setup and some adapted or inspired by other people's public work (see Credits), every one scrubbed of personal paths, project names, and infrastructure, and gated (gitleaks + trufflehog + marker scan) before release. Methodology, not config.

## The skills (52)

| Skill | What it does |
|---|---|
| **adversarial-research** | Deep research where agents adversarially fact-check each other's findings instead of one agent confidently… |
| **algorithmic-art** | Creates generative and computational art using p5.js with seeded randomness, particle systems, and interact… |
| **api-integration** | Integrates with external APIs including REST, GraphQL, and webhooks. |
| **breakdown** | Produce a multi-altitude explainer of a body of work — what it is, why it matters, where it sits, and how i… |
| **c4-architect** | Generates and maintains C4 architecture diagrams (Context, Container, Component) as Mermaid in docs/archite… |
| **canvas-design** | Creates visual art in PDF and PNG formats covering design philosophies, aesthetic movements, and museum-qua… |
| **coding-agents** | Core patterns for building AI coding agents with tool calling, agent loops, and autonomous code execution —… |
| **compound-engineering** | Connected analyze-plan-execute-learn-repeat cycle with persistent memory. |
| **context-budget** | Audit token consumption across all loaded components — skills, agents, MCP tools, rules, hooks |
| **counterfactual** | Generate structured alternate timelines for a past decision log entry and write them as a `reflection` entr… |
| **critique** | Single-pass 3-agent critique for ANY work product — plans, code, designs, architecture. |
| **d3js-visualization** | Creates data visualizations with D3.js including custom charts, network diagrams, geographic maps, and publ… |
| **data-analyst-agent** | Build AI agents that analyze datasets, create visualizations, and extract insights through autonomous code… |
| **database-migrations** | Modifies database schemas safely with migration strategies, rollback procedures, and zero-downtime deployme… |
| **deep-recon** | Multi-agent research swarm that finds existing solutions before you write a single line of code. |
| **design-taste** | Senior UI/UX Engineer. |
| **doc-coauthoring** | Guide users through a structured workflow for co-authoring documentation. |
| **e2b-sandbox** | Secure cloud sandbox execution for AI coding agents using E2B. |
| **ecosystem-audit** | Audit your entire .claude ecosystem (skills, agents, slash commands, hooks, rules, memory) for duplicates,… |
| **excalidraw-diagram** | Create Excalidraw diagram JSON files that make visual arguments. |
| **executing-plans** | Implements written plans through batched execution with review checkpoints. |
| **frontend-design** | Builds web components, pages, applications, landing pages, and styled web UIs. |
| **fullstack-agent** | Enables AI agents to create complete web applications with file system operations, code execution, template… |
| **grill** | Adversarial code review — challenge your code harshly, find what will break in production. |
| **kickoff** | Full workflow orchestrator. |
| **mcp-builder** | Builds MCP (Model Context Protocol) servers for API integration. |
| **model-migration** | Generate a personalized "how to use this new model" report by mining ALL your local Claude Code sessions, t… |
| **naming-the-machine** | Scan skills, tools, workflows, and infrastructure to identify and name emergent expressions of value — prod… |
| **output-enforcement** | Overrides default LLM truncation behavior. |
| **package-research** | Researches packages, dependencies, and APIs before integration. |
| **pdf-generation** | Generates PDFs using Typst templates, handles print layouts, and processes images with Sharp. |
| **pp2p** | Two critique passes + polish + mutation-test-the-tests + a different-model-family review looped until clean. Default for real features. |
| **pp3p** | Three critique passes + polish + mutation gate + adversarial cross-family loop. For auth, payments, data integrity. |
| **prompt-engineer** | Turn a rough natural-language ask into a high-quality, Anthropic-spec prompt. |
| **prompt-grounding** | Audits a prompt against the actual codebase, docs, and strategy files — separates fact from invention, find… |
| **redesign** | Upgrades existing websites and apps to premium quality. |
| **requesting-code-review** | Structures code review requests with context, commit hashes, and requirements. |
| **reverse-engineer-to-learn** | Studies how existing apps solve problems to inform new builds. |
| **review-changes** | Analyze uncommitted changes before committing. |
| **scratchpad** | Compaction-resilient session notepad. |
| **ship** | Fix-until-clean loop then commit and push. |
| **slack-gif-creator** | Creates animated GIFs optimized for Slack including emoji animations and message GIFs with proper sizing an… |
| **sprint-architect** | Converts strategy documents, issue lists, or audits into dependency-aware agent-team execution boards. |
| **techdebt** | End-of-session tech debt cleanup. |
| **test-and-fix** | Run tests and auto-fix failures. |
| **threat-model** | Repository-grounded threat modeling. |
| **verification-before-completion** | Mandates fresh verification evidence before any completion claims. |
| **visual-verdict** | Structured visual QA verdict for screenshot-to-reference comparisons. |
| **web-asset-generator** | Creates web assets including favicons, app icons, Open Graph images, social media cards, and other web grap… |
| **webapp-testing** | Provides Playwright patterns and best practices for web application testing. |
| **whatdidimiss** | After a chunk of work is done, surfaces what the model noticed but was never asked to do — adjacent tasks,… |
| **writing-plans** | Creates detailed implementation plans for multi-step tasks with exact file paths, code examples, and test c… |

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/pp2p ~/.claude/skills/
cp -R claude-skills/skills/pp3p ~/.claude/skills/
cp -R claude-skills/skills/grill ~/.claude/skills/    # or any other folder
```

Restart Claude Code; the skill activates automatically when your task matches its description, or invoke it explicitly. Placeholders like `<your-output-dir>` mark spots to point at your own paths.

## Credits

Many of these skills started from other people's public work. Each one below names its source; the license notices are in THIRD_PARTY_NOTICES.md.

**Adapted or copied**

- algorithmic-art, canvas-design, mcp-builder, slack-gif-creator, and webapp-testing are adapted from Anthropic (https://github.com/anthropics/skills, Apache-2.0, Copyright 2026 Anthropic, PBC.).
- frontend-design is adapted from Anthropic (https://github.com/anthropics/skills, Apache-2.0); its LICENSE.txt names no copyright holder.
- threat-model is adapted from OpenAI (https://github.com/openai/skills, Apache-2.0, OpenAI, github.com/openai/skills).
- executing-plans, writing-plans, requesting-code-review, and verification-before-completion are adapted from Jesse Vincent (https://github.com/obra/superpowers, MIT, Copyright (c) 2025 Jesse Vincent).
- design-taste (copied with modifications) and output-enforcement (copied) come from Leonxlnx (https://github.com/Leonxlnx/taste-skill, MIT, Copyright (c) 2026 Leonxlnx), and redesign is adapted from that same repo.
- visual-verdict is adapted from Yeachan Heo (https://github.com/Yeachan-Heo/oh-my-claudecode, MIT, Copyright (c) 2025 Yeachan Heo) and first appeared in https://github.com/Yeachan-Heo/oh-my-codex (MIT, Copyright (c) 2026 Yeachan-Heo).
- prompt-engineer is adapted from Anthropic's prompting best practices (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices); no open license and no holder were found on that page.

**Inspired by**

- adversarial-research, ecosystem-audit, and model-migration are inspired by Mark Kashef's Dynamic Workflows Prompt Pack (https://markkashef.gumroad.com/l/dynamic-workflows-prompt-pack-claude); no license is stated.
- coding-agents, data-analyst-agent, fullstack-agent, and e2b-sandbox are inspired by the DeepLearning.AI short course Building Coding Agents with Tool Execution (E2B); no canonical public repo was found, and a student copy is at https://github.com/jose-deblas/building-coding-agents. Owner and license for the course are unverified.
- e2b-sandbox is also inspired by https://e2b.dev/docs.
- compound-engineering is inspired by Every's compound-engineering-plugin (https://github.com/EveryInc/compound-engineering-plugin, MIT, Copyright (c) 2025 Every); only the name and the analyze-plan-execute-learn idea match.
- context-budget is inspired by Affaan Mustafa's everything-claude-code (https://github.com/affaan-m/everything-claude-code, MIT, Copyright (c) 2026 Affaan Mustafa).
- d3js-visualization is inspired by https://github.com/chrisvoncsefalvay/claude-d3js-skill, which has no license file.
- grill and techdebt are inspired by Boris Cherny's Claude Code tips (https://x.com/bcherny/status/2017742741636321619); the post states no license.
- reverse-engineer-to-learn is inspired by Kevin Chen (https://kevinchen.co/blog/rewind-ai-app-teardown/), and the skill also names Yash Poojary's methodology, whose source was not located.
- web-asset-generator is inspired by https://github.com/alonw0/web-asset-generator (MIT, Copyright (c) 2025 Web Asset Generator Contributors).

**Copies whose upstream carries no license**

- excalidraw-diagram is copied from Cole Medin's coleam00/excalidraw-diagram-skill (https://github.com/coleam00/excalidraw-diagram-skill), which has no license file.
- doc-coauthoring is copied from anthropics/skills (https://github.com/anthropics/skills), whose folder has no license file.

These two are credited here and are not covered by this repo's MIT license.

## License

My own skills are MIT, see LICENSE. Skills adapted from other projects keep their upstream licenses: each Apache-2.0 skill carries its LICENSE.txt in its folder, and THIRD_PARTY_NOTICES.md holds the MIT notices.

By [@LucasCooperBey](https://github.com/LucasCooperBey).
