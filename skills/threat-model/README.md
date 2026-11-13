# threat-model

A Claude Code skill that builds a threat model of a repository from its code. It maps the entrypoints, trust boundaries, assets and attackers it can find in the files, then lists abuse paths ranked HIGH, MEDIUM and LOW, each tied to a file and line, with a fix and an effort estimate for each.

## Install

```bash
git clone https://github.com/LucasCooperBey/claude-skills.git
cp -R claude-skills/skills/threat-model ~/.claude/skills/
```

The skill says to use `/grill` for general code review. That is the grill skill in the same repo; copy `claude-skills/skills/grill` too if you want it.

## Quick start

In Claude Code, inside the project you want modeled, type:

```
Use the threat-model skill with --report-only on the app/ folder in this project and print the report in the skill's output format.
```

The flags, from SKILL.md:

- `--scope "api,auth,db"` limits the model to the named components or folders.
- `--attacker "external"` keeps only external attackers.
- `--report-only` skips the questions it would otherwise ask you to confirm its assumptions.
- `--save` writes the report to `<your-output-dir>/security/{project}-threat-model.md`. There is no default folder: name one in your request (for example "for the output folder, use reports/ in this project"), or replace `<your-output-dir>` in your copy of SKILL.md with the folder you want.

## Example

The fixture was a 42-line Flask app, `app/server.py`, with three planted flaws: a search route that builds its SQL by string concatenation, an invoice route that checks login but not who owns the invoice, and a payment webhook with no signature check. Next to it sat a `config.example` that lists a `PAYMENT_WEBHOOK_SECRET` the code never reads, and a `requirements.txt`. The request was:

```
Use the threat-model skill with --report-only --save on the app/ folder in this project. For the output folder, use reports/ in this project. Print the report in the skill's output format.
```

It saved the report to `reports/security/p44-threat-model.md` (the fixture folder was named `p44`) and printed the same text. The report ran 82 lines: System Scope, Trust Boundaries, Assets, Attacker Model, nine threats, Mitigations, Coverage Gaps and Assumptions Made. Below are its title, the HIGH threats, the first three mitigations and the coverage gaps, as printed:

```
## Threat Model: p44 (app/), 2026-11-12

### Threats
**HIGH**
- **T-1:** An external unauthenticated attacker can dump the whole database, including `users.email` and `users.pw_hash`, by sending a `UNION SELECT` payload in `GET /search?q=`. The `q` parameter is concatenated into the SQL string. Because the login endpoint compares the client-supplied `pw_hash` directly against the stored value, the dumped hashes can be replayed to log in as any user. | `app/server.py:27` (injection), `app/server.py:18` (hash-as-password) | Controls: none observed.
  - Example: `q=' UNION SELECT email, pw_hash FROM users --`
- **T-2:** An external authenticated attacker can read any customer's invoice, including `total` and `card_last4`, by walking through `GET /invoices/1..N`. The handler fetches `user_id` but never compares it with `session["user_id"]`. | `app/server.py:33-36` | Controls: `require_login()` (`server.py:32`) blocks only unauthenticated callers; sequential integer IDs make enumeration easy.
- **T-3:** An external unauthenticated attacker can mark any invoice as paid by POSTing `{"invoice_id": N}` to `/webhooks/payment`. There is no signature or shared-secret check, and `PAYMENT_WEBHOOK_SECRET` (`config.example:3`) is never read. | `app/server.py:38-42` | Controls: none observed. *Note:* the handler never calls `commit()` on the connection (`server.py:41`), so the `UPDATE` is probably rolled back and **legitimate webhooks also fail to persist** right now. That is a separate bug. Once someone adds the commit, this abuse path is fully live.
- **T-4 (config-dependent):** An infrastructure/config attacker can forge a Flask session cookie with any `user_id` if `SECRET_KEY` is left unset (the fallback is `"dev"`) or set to the `config.example` placeholder `change-me`. That gives full impersonation without credentials, and it combines with T-2. | `app/server.py:5`, `app/config.example:1` | Controls: none. The app does not refuse to start with a weak or default key.

[MEDIUM and LOW threats T-5 to T-9 left out]

### Mitigations
- **T-1:** Existing controls: none. → At `server.py:27`, use a bound parameter: `db().execute("SELECT id, name FROM products WHERE name LIKE ?", (f"%{q}%",))`. Separately, at `server.py:18`, accept a plaintext password over TLS and check it server-side with `werkzeug.security.check_password_hash` (or argon2/bcrypt), so a leaked DB hash can no longer be replayed. Rotate all stored hashes after the fix. | Injection: Quick. Password scheme migration: Medium.
- **T-2:** Existing: `require_login()` at `server.py:32`. → At `server.py:33`, add `AND user_id=?` bound to `session["user_id"]` and return 404 on mismatch. Optionally switch to non-sequential invoice IDs to make enumeration harder. | Quick
- **T-3:** Existing: none. → At `server.py:39-40`, read `PAYMENT_WEBHOOK_SECRET` and check the provider's HMAC signature header over `request.data` with `hmac.compare_digest`, returning 401 on failure. Also reject events whose amount or currency doesn't match the invoice, and handle replays with an idempotency key or event ID. Add `conn.commit()` after the `UPDATE` at `server.py:41`. | Quick to Medium, depending on the provider SDK

[mitigations T-4 to T-6 left out]

### Coverage Gaps
- No DB schema or migrations are in the repo, so the column list is inferred from queries. There may be more sensitive columns that the `/search` injection (T-1) would also expose.
- Deployment topology (reverse proxy, TLS, WAF, network exposure of the webhook) is not in the repo, so the "Encrypted" column is unverified for every boundary.
- How the client computes `pw_hash` (algorithm, salt) is not in this repo, so the T-5 analysis assumes a client-side hash.
- No CI/CD config exists, so build-pipeline supply-chain threats beyond `requirements.txt` were not assessed.
- All 4 entrypoints and all 5 trust boundaries map to at least one threat.
```

All three planted flaws came back HIGH at the right lines (27, 33 to 36, and 38 to 42). It also found things that were not planted and are true of the file: the `"dev"` fallback for `SECRET_KEY`, the client-sent `pw_hash` that works as the password, and the webhook `UPDATE` that is never committed.

## Needs

- Claude Code. The skill uses only reading and search tools, plus a file write for `--save`.

## Limits

- It reads code. Anything outside the repo (TLS, a reverse proxy, network exposure) it lists as an assumption or a coverage gap rather than a finding.
- The SKILL.md sets a 20 minute budget and stops with a partial report at that point.
- Without `--report-only` it asks you questions to confirm its assumptions before writing the report.

Source and credit: see the Source section of SKILL.md. The skill is adapted from openai/skills under the Apache-2.0 license in `LICENSE.txt`.
