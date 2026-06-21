# claude-skills

A curated, **no-secrets** library of [Claude Code](https://claude.com/claude-code) **skills** — reusable methodology packets that teach the agent *how* to do a class of work well. Each is a self-contained `SKILL.md` (plus optional `references/`); drop a folder into `~/.claude/skills/` and Claude auto-invokes it when your task matches its description.

These are the generic skills extracted from a larger private Claude Code setup — every one scrubbed of personal paths, project names, and infrastructure, and gated (gitleaks + trufflehog + marker scan) before release. Methodology, not config.

## The skills (50)

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
git clone https://github.com/Lucface/claude-skills.git
cp -R claude-skills/skills/grill ~/.claude/skills/    # copy any you want
```

Restart Claude Code; the skill activates automatically when your task matches its description, or invoke it explicitly. Placeholders like `<your-output-dir>` mark spots to point at your own paths.

## License

MIT — see [LICENSE](./LICENSE). By [@Lucface](https://github.com/Lucface). Extracted clean from a private setup; more land here as they're scrubbed.
