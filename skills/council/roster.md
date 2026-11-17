# Roster

Edit this file to choose who sits on the council. Each row is one seat. Claude
Code reads it at the start of a run.

| Seat | Model (as the harness names it) | Effort | Harness or command | How identity is checked |
|---|---|---|---|---|
| 1 | opus | high | `claude -p --model opus --effort high` | key of `modelUsage` in the call's JSON output |
| 2 | sonnet | high | `claude -p --model sonnet --effort high` | key of `modelUsage` in the call's JSON output |
| 3 | haiku | high | `claude -p --model haiku --effort high` | key of `modelUsage` in the call's JSON output |

Any model your plans give you can replace a row. Keep one row per model you
want heard, and use the identity column to say where its model id can be read.
If you delete every row, the skill proposes this same three-seat roster and says
so in the result.

## Example for a roster across vendors

This second table is a template, not a working roster. Fill in the cells from the
help output of each tool you have installed and signed in to.

| Seat | Model (as the harness names it) | Effort | Harness or command | How identity is checked |
|---|---|---|---|---|
| 1 | your model id here | your effort here | `claude -p` | `modelUsage` key in the JSON output |
| 2 | your model id here | your effort here | `codex exec` | model field in the tool's own machine-readable output, if it has one |
| 3 | your model id here | your effort here | `gemini -p` | model field in the tool's own machine-readable output, if it has one |
