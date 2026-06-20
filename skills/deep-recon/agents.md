# Deep Recon Agent Definitions

## Phase 2: Parallel Agents (launch all 3 simultaneously)

### Solution Scout
```
Task({
  description: "Solution Scout for [topic]",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Research existing solutions for: [PROBLEM]

    Search strategy:
    1. WebSearch: "[problem] library [framework]"
    2. WebSearch: "[problem] open source github"
    3. WebSearch: "[problem] SaaS API service"
    4. WebSearch: "[problem] library comparison [year]"
    5. WebFetch top 3-5 results for details

    For each solution, report:
    - Name and URL
    - Stars/downloads (popularity signal)
    - What it solves (1-2 sentences)
    - Pros and cons
    - Last updated / actively maintained?
    - License

    Rank by: relevance x maintenance health x adoption.
    Return at least 3 solutions, ideally 5-8.
    If searches return nothing, broaden terms and retry once.
  `
})
```

### Community Intel
```
Task({
  description: "Community Intel for [topic]",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Find what real developers say about: [PROBLEM]

    Search strategy:
    1. WebSearch: "site:reddit.com [problem terms]"
    2. WebSearch: "[problem] site:news.ycombinator.com"
    3. WebSearch: "[problem] [framework] stackoverflow"
    4. WebSearch: "[problem] blog substack dev.to [year]"
    5. WebFetch top 3-5 most relevant threads

    Synthesize into:
    - Community consensus: what most people recommend
    - Contrarian views: valid dissenting opinions
    - Common pitfalls: what trips people up
    - Key quotes: most insightful comments (verbatim with source)

    If no discussions found, note "no community signal" and move on.
  `
})
```

### Doc Collector
```
Task({
  description: "Doc Collector for [topic]",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Find docs, tutorials, and guides for: [PROBLEM]

    Search strategy:
    1. WebSearch: "[top solution] documentation getting started"
    2. WebSearch: "[problem] tutorial [framework] [year]"
    3. WebSearch: "[problem] best practices [year]"
    4. WebFetch top 5 documentation pages for summaries

    Organize results as:
    1. Must-read (directly solves our problem)
    2. Useful context (background knowledge)
    3. Deep dives (for later reference)

    Each entry: title, URL, type (docs/tutorial/blog/video), 1-2 sentence summary.
  `
})
```

## Phase 3: Sequential Agent (runs AFTER Phase 2)

### Code Analyzer
```
Task({
  description: "Code Analyzer for [topic]",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: `
    Analyze how these solutions implement: [PROBLEM]

    Solutions to analyze: [TOP 2-3 FROM SOLUTION SCOUT]

    For each:
    1. WebFetch the GitHub README for architecture overview
    2. WebSearch: "[package] architecture" or "[package] internals"
    3. WebFetch key source files if accessible

    Report for each solution:
    - Architecture pattern (monolith, plugin, middleware, etc.)
    - Key abstractions (main types/interfaces)
    - How they handle [CORE CHALLENGE]
    - What we can directly adopt

    Focus on PATTERNS, not API surface.
  `
})
```

## Lead Agent Synthesis Prompt

```
Synthesize 4 agent outputs into a research brief for: [PROBLEM]

Agent outputs:
- Solution Scout: [paste]
- Community Intel: [paste]
- Doc Collector: [paste]
- Code Analyzer: [paste]

Use the template at templates/research-brief.md.
Be opinionated — recommend ONE approach and defend it with evidence.
Save to: <your-output-dir>/research/YYYY-MM-DD-[topic]/research-brief.md
```
