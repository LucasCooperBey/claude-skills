---
name: threat-model
description: Repository-grounded threat modeling. Enumerates trust boundaries, assets, attacker capabilities, and abuse paths tied to actual code. Not generic OWASP checklists — evidence-backed claims with file/line references.
---

# Threat Model (/threat-model)

Systematic threat modeling rooted in the actual codebase. Every claim references real code — no generic category dumps.

**Time budget:** 20 min total. Scope + recon ~5 min, analysis ~10 min, synthesis + questions ~5 min. Abort at 20 min with partial report.

## When to Use

- Before deploying a new service or API to production
- When adding auth, payments, file uploads, or other security-sensitive features
- Before external API integrations, or multi-tenant features
- When explicitly asked to threat model a codebase

## When NOT to Use

- General code review (use `/grill` instead, the grill skill in the same repo as this one)
- Architecture summaries without security focus

## Arguments

Parse `$ARGUMENTS` string:
- `--scope "api,auth,db"` → Limit to named components/directories
- `--attacker "external"` → Limit attacker model to external-only (skip insider/supply chain)
- `--report-only` → Skip validation questions, emit report immediately
- `--save` → Save output to `<your-output-dir>/security/{project}-threat-model.md`
- No args → Full model of entire repo

## Instructions

### Step 1: Scope — Map the System from Code

Use Glob and Grep to enumerate actual components. Do NOT invent components.

```
Glob: **/*.{ts,tsx,js,py,go,rb,rs}  (entrypoints, routers, handlers)
Glob: **/{schema,migration,model,entity}*
Glob: **/{auth,middleware,guard,policy}*
Glob: **/.env.example, **/docker-compose*, **/Dockerfile*
Grep: pattern="process\.env\." — find all env var refs
Grep: pattern="(fetch|axios|got|request)\(" — external HTTP calls
Grep: pattern="(sql|query|db\.|prisma\.|drizzle)" — DB access
```

Build a component inventory:
- **Entrypoints:** HTTP routes, CLI commands, background jobs, webhooks, event listeners
- **Data stores:** databases, file storage, caches, queues
- **External integrations:** third-party APIs, OAuth providers, payment processors
- **Configuration:** env vars, secrets, feature flags

Note which are **runtime** vs **CI/build/dev tooling only** — threats differ.

### Step 2: Trust Boundaries

For each boundary crossing, document:
- Protocol (HTTP/S, gRPC, WS, IPC)
- Authentication mechanism (JWT, session cookie, API key, mTLS, none)
- Encryption in transit (TLS version, self-signed, none)
- Input validation (schema validation, sanitization, none observed)
- Authorization model (RBAC, ABAC, owner-check, none observed)

Format each boundary as:
```
[Caller] → [Callee] | Protocol | Auth | Encrypted | Validated
```

Reference the file:line where auth/validation is (or is absent).

### Step 3: Assets

List what drives risk. For each asset:
- **Type:** credentials/secrets, PII, financial data, integrity-critical state, IP/source code
- **Location:** where stored, how accessed (file:line)
- **Sensitivity:** what's the blast radius if compromised?

Only list assets with evidence in the codebase. Skip hypothetical assets.

### Step 4: Attacker Model

Define realistic attacker capabilities based on actual exposure:

**Assess exposure first:**
- Is there a public API? (unauthenticated surface)
- Are there multi-tenant data boundaries?
- Does the app handle webhooks from external parties?
- Are there admin/privileged roles?
- Are there third-party dependencies with broad permissions?

**Attacker tiers (include only relevant ones):**

| Tier | Capabilities | Include if... |
|------|-------------|---------------|
| External unauthenticated | HTTP requests, no credentials | Any public endpoint exists |
| External authenticated | Valid account, standard permissions | Multi-user app |
| Malicious insider/tenant | Cross-tenant API access, valid JWT for own org | Multi-tenant data model |
| Supply chain | Compromised dependency, CI environment | npm/pip deps, GitHub Actions |
| Infrastructure | Cloud misconfiguration, leaked env vars | Deployed app with cloud resources |

**Explicitly state non-capabilities** — what the attacker cannot do (e.g., "cannot execute arbitrary code on host", "cannot read DB directly"). This prevents scope creep.

### Step 5: Threats — Abuse Paths

Map attacker capabilities to assets via trust boundary weaknesses. Each threat must:
1. Name the abuse path (not a category name — a specific action)
2. Reference the vulnerable code location (file:line)
3. Map to an asset and boundary
4. Note any existing controls that partially mitigate

Format:
```
T-{n}: {Attacker tier} can {specific action} via {entry point / boundary}
       affecting {asset} because {specific code observation}
       Controls: {existing mitigations or "none observed"}
       Evidence: {file:line}
```

Do NOT list generic threats without code evidence.

### Step 6: Prioritize

Score each threat: **Likelihood × Impact**, adjusted for existing controls.

**Risk levels:**
- **HIGH** — pre-auth RCE, authentication bypass, cross-tenant data access, credential/key theft, mass data exfiltration. Fix before ship.
- **MEDIUM** — targeted DoS, partial data exposure (own data only), rate-limit bypass enabling abuse, log injection enabling confusion. Fix soon.
- **LOW** — low-sensitivity info leaks (stack traces, version headers), noisy DoS requiring sustained effort with easy mitigation. Track.

Justify the rating with one sentence referencing the existing controls and blast radius.

### Step 7: Validate Assumptions (skip if --report-only)

Generate 1-3 targeted questions to resolve the highest-uncertainty assumptions before finalizing. Examples:
- "Is endpoint X publicly reachable or behind a VPN/internal network?"
- "Does {table} contain real PII in production or only synthetic test data?"
- "Is {env var} ever committed to the repo or injected only at deploy time?"

Ask the questions and wait for answers before writing the final report. If the user doesn't respond, note the assumption made and proceed.

### Step 8: Mitigations

For each HIGH and MEDIUM threat, provide:

**Existing controls** — cite with file:line evidence. Don't credit controls you can't locate.

**Recommended mitigations** — concrete, tied to specific locations:
- What to add/change and where (file:line or "new file at path/")
- Estimated effort: Quick (< 1 day) / Medium (1-3 days) / Heavy (> 3 days)
- Whether it blocks a specific attacker tier or reduces blast radius

Do NOT recommend generic "add input validation" without specifying what input, where, and what rule.

### Step 9: Quality Check

Before emitting the report, verify:
- [ ] All entrypoints from Step 1 appear in at least one threat or are explicitly marked out-of-scope
- [ ] All trust boundaries from Step 2 are represented in at least one threat
- [ ] Every threat has a file:line reference
- [ ] Attacker non-capabilities are explicitly stated
- [ ] No threat is a generic OWASP category without code-specific evidence
- [ ] Runtime threats are distinguished from CI/build/dev-only risks

Flag any gaps in the report under "Coverage Gaps."

## Output Format

```markdown
## Threat Model: {project}, {date}

### System Scope
- Entrypoints: [list with paths]
- Data stores: [list with paths]
- External integrations: [list with paths]
- Runtime vs build-only: [distinction]

### Trust Boundaries
| Caller | Callee | Protocol | Auth | Encrypted | Validated |
|--------|--------|----------|------|-----------|-----------|

### Assets
| Asset | Type | Location | Blast Radius |
|-------|------|----------|--------------|

### Attacker Model
**In scope:** [tiers with rationale]
**Explicitly out of scope:** [with rationale]

### Threats
**HIGH**
- T-1: [abuse path] | [file:line] | [controls]

**MEDIUM**
- T-n: ...

**LOW**
- T-n: ...

### Mitigations
**T-1:** [existing controls (file:line)] → [recommended change at file:line] | {Quick/Medium/Heavy}

### Coverage Gaps
- [any entrypoints or boundaries not represented in threats]

### Assumptions Made
- [any unvalidated assumptions from Step 7]
```

## Save Output

If `--save` flag or user confirms, write the report to:
```
<your-output-dir>/security/{project-name}-threat-model.md
```

Create the directory if it doesn't exist.

## Source

Adapted from https://github.com/openai/skills (Apache-2.0, OpenAI, github.com/openai/skills). Changed for this repo by Lucas Cooper-Bey in 2026: wording mostly rewritten, keeping the same stage order.
