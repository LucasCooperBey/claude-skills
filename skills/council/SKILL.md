---
name: council
description: >-
  Convene a decision roundtable of real models for an important, uncertain
  choice where several independent views help. Check each seat's model from the
  harness's own record, run independent positions and cross-examination, keep
  dissent by name, and have a separate reviewer check the recommendation. Use
  when asked for a council, roundtable, or multiple model perspectives. Do not
  use it for plain factual lookups or for work that is already decided.
---

# Council: real models, inspectable decisions

Produce a source-grounded recommendation with the actual participating roster,
the strongest alternative, corrected errors, live disagreements and the next
useful test. The council advises. It does not appoint people, change prices or
authorize outside action. Follow the user's requested output format and scope.

## Roster and preflight

Read `roster.md` in this skill's own folder. Each row is one seat: the model as
the harness names it, the effort to request, the command that runs it, and how
its identity is checked. A later explicit choice by the user about models or
seats governs over the file.

When `roster.md` lists no seats, propose the smallest real roster the current
harness offers and say so in the result. In Claude Code that is the `opus`,
`sonnet` and `haiku` model aliases, each run as its own call.

Before the run, confirm that each seat answers a minimal request through its
command, and record the model the harness reports for that answer. Record the
requested model and effort separately from the model the harness reports. A
model naming itself is not proof. Effort is a request: say so unless the
harness's own record reports the effort that was used.

Use harnesses the user has already signed in to. An alternate route to the same
model and effort is allowed when you verify and record it. Do not silently
downgrade a seat, buy credits, use a metered API key the user has not
approved, enable new access, or present a simulated persona as a real seat.

### Identity check

Read each seat's model from the harness's own machine-readable record, never
from the seat's own words.

In Claude Code, run each seat as its own call:

```
claude -p --model ALIAS --effort LEVEL --tools "" --disable-slash-commands \
  --output-format json --setting-sources project --strict-mcp-config \
  --no-session-persistence < INPUT.md > SEAT.json
```

Then read the model id from the JSON, which is the key of the `modelUsage`
object:

```
jq -r '.modelUsage | keys[]' SEAT.json
```

Read the seat's answer with `jq -r .result SEAT.json`, and check that
`.is_error` is false. The `--tools ""` flag gives the seat no tools, so the
packet must carry everything the seat needs. If a seat must read files, grant
it read-only tools, put that in the result, and keep its input scope inside the
packet's folder.

Subagents are an acceptable seat mechanism only when the model id of each one
can be read from a record the harness keeps. Otherwise do not count them as
verified seats.

For other command line tools, read the model field of that tool's own JSON
output. If the tool offers no machine-readable record of the model, mark the
seat "model not verified" in the result.

## Freeze the decision packet

Name the decision, its owner, the horizon and a useful deadline. Include dated
facts and source locators, decisions the owner already made, unresolved
assumptions, the actual options, constraints and the requested deliverable.
Keep source authority: a new model opinion does not overrule a later decision
by the user, and it does not turn a missing receipt into proof of no activity.

All seats receive the same initial packet. Give later factual corrections to
every seat in a labeled addendum. Send only authorized, relevant context. Keep
credentials, private family, health or customer information and unrelated
archives out of the packet. When a task truly needs private material, use
handling the user has approved. Keep confidential prompts and secrets out of
process arguments and logs; pass the packet through standard input or a file.
Never load a whole private project just because a tool defaults to the current
folder.

## Independent positions and model-owned specialists

Each seat writes its recommendation, strongest alternative, assumptions,
failure modes, required evidence, next test and what would change its mind.
Save each original position to its own file before any seat sees another
seat's answer. The positions are produced by separate calls with the same
packet and no shared context.

Use bounded specialist delegation where it helps and the harness supports it.
Economics and delivery, system design, and the concerns of users or
contributors are examples, not compulsory departments. Give intelligent
specialists the strongest model and effort the roster allows. Check real
evidence that a specialist ran, which model it used and what it returned.
A custom definition or a leader's claim does not prove a specialist ran. Do not
let a framework silently pick a cheaper default model. Respect concurrency
limits and avoid uncontrolled recursion. The default roster runs no
specialists; say that in the result.

If the current session is itself one of the verified seats, it may write that
seat's first position before reading the others. Record that, and use a
separate final reviewer. If a harness cannot support or pin specialists, say
which seats completed directly and that no verified specialist team ran. Never
role-play a missing provider as its answer.

## Durable execution and recovery

Keep a run folder with the packet, one file per seat for input and raw JSON
output, and the review. Use tracked, nonblocking sessions that can be resumed
when the harness has them, and keep session ids, raw result streams, input scope
and errors. Run seats in parallel when they are independent. Keep each wait
short enough that the user sees progress. Do not set token caps, cut useful
context, or kill a seat that is still reasoning only because a generic shell
timeout ran out.

Check real progress and failure signals. An explicit cancellation or deadline
from the user, a budget limit, repeated refusal by a provider, an authentication
failure or a genuinely stalled process needs bounded recovery or a reported
blocker. Do not start a duplicate run while a valid one is active. If an exact
route fails, try an already authorized route to the same model. Do not weaken
permissions or tests to make a run finish.

A probe proves access, not a judgment. Count only complete, non-error results:
the JSON must show no error, the `result` must not be empty, and a model id must
be present. If a seat cannot finish, record why and name the incomplete roster.
Do not call a partial panel a complete council.

## Cross-examination and adjudication

Label the peers MEMBER-A, MEMBER-B, MEMBER-C and so on, and remove identity
cues where practical while keeping sources and meaning. This reduces explicit
brand cues. It does not make the seats blind. Give each seat the same complete
record of all positions and the same correction addendum. Ask each for the
strongest opposing insight, any retraction or narrowing of its own position,
the material disagreements, arithmetic checks, and the observation that would
resolve the dispute.

Synthesize the agreements, the rejected claims with reasons, the remaining
uncertainty and the best next action. Agreement among models is not market
evidence. Keep minority concerns, by label and by seat once the roster is
shown, and separate terms already decided from new proposals. Attack the chosen
recommendation yourself: state the strongest case against it, the conditions
under which it fails and a trigger for revising it.

The final reviewer is a fresh call to a roster model that has no position in
this run, never the synthesizer reviewing its own work. Give it the packet, the
recommendation and the evidence, and ask it to find errors and unsupported
claims. Read its model id the same way as for a seat. When no roster model is
free, because every row held a seat, say in the result that the review is not
independent, and say which seat's model was reused. Never relabel the
synthesizer's self-review as independent. A named judge does not establish
truth.

## Result and follow-up

Lead with the decision and the next action. Then give a compact roster showing,
for each seat, the model id as the harness reported it, the effort that was
requested, the command or harness, whether it completed, any specialist use and
any failures. Report usage or cost only as measured, and say when it is an
estimate. Keep the full original positions, the challenge round, the packet and
the review receipt in the run folder. Offer the format the user asked for. Do
not force a PDF or build application code for an advisory request.

Record: the decision owner, the recommended option, the alternatives, the
evidence, the disagreement, the limits, an acceptance test and a revision
trigger. Keep recommendations below any existing source of record. Say which
requested work remains. A written workflow is not a deployed service or a
scheduled job.

When asked what a seat said, read its stored answer. For a deeper question, ask
that real model again, or give your own analysis clearly attributed to you. Do
not impersonate another vendor. Reuse unchanged evidence and run only the
further inquiry that is needed.
