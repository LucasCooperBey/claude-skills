#!/usr/bin/env bash
# Deterministic full-corpus miner over ALL Claude Code JSONL sessions.
# Zero LLM tokens — pure jq/awk. Feeds the model-migration workflow.
set -uo pipefail

OUT="${MODEL_MIGRATION_OUT:-$HOME/model-migration-output}"
PROJ="$HOME/.claude/projects"
mkdir -p "$OUT"

# Build the file list once (NUL-safe).
mapfile -d '' FILES < <(find "$PROJ" -name '*.jsonl' -print0 2>/dev/null)
echo "files: ${#FILES[@]}"

# 1) Model usage histogram (all assistant turns)
printf '%s\0' "${FILES[@]}" | xargs -0 jq -r 'select(.type=="assistant") | .model // empty' 2>/dev/null \
  | sort | uniq -c | sort -rn > "$OUT/01-models.txt"

# 2) Tool-use histogram
printf '%s\0' "${FILES[@]}" | xargs -0 jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="tool_use") | .name' 2>/dev/null \
  | sort | uniq -c | sort -rn > "$OUT/02-tools.txt"

# 3) Token totals
printf '%s\0' "${FILES[@]}" | xargs -0 jq -r 'select(.type=="assistant") | .message.usage // {} | "\(.input_tokens // 0) \(.output_tokens // 0) \(.cache_read_input_tokens // 0) \(.cache_creation_input_tokens // 0)"' 2>/dev/null \
  | awk '{i+=$1;o+=$2;cr+=$3;cc+=$4;n++} END{printf "assistant_turns: %d\ninput_tokens: %d\noutput_tokens: %d\ncache_read_tokens: %d\ncache_creation_tokens: %d\n", n,i,o,cr,cc}' > "$OUT/03-tokens.txt"

# 4) User-authored prompt corpus (THE signal for prompting-pattern analysis).
#    Handles string content and array-of-text content. Covers ALL sessions.
printf '%s\0' "${FILES[@]}" | xargs -0 jq -r '
  select(.type=="user") |
  (.message.content // .content) as $c |
  if ($c|type)=="string" then $c
  elif ($c|type)=="array" then ([$c[] | select(.type=="text") | .text] | join(" "))
  else empty end
  | select(. != null and (.|length)>0)
' 2>/dev/null | grep -vE '^\s*(tool_result|<|\[)' > "$OUT/04-user-prompts.txt"

# 5) Per-session length distribution (lines per session = activity proxy)
for f in "${FILES[@]}"; do wc -l < "$f"; done | sort -n | awk '
  {a[NR]=$1; sum+=$1}
  END{
    n=NR;
    printf "sessions: %d\ntotal_records: %d\nmedian_records: %d\nmax_records: %d\nmean_records: %.1f\n", n, sum, a[int(n/2)], a[n], sum/n
  }' > "$OUT/05-session-dist.txt"

# Sizes
echo "user-prompt corpus size:" > "$OUT/00-meta.txt"
wc -lc "$OUT/04-user-prompts.txt" >> "$OUT/00-meta.txt"

echo "=== DONE ==="
echo "--- models ---"; cat "$OUT/01-models.txt"
echo "--- tokens ---"; cat "$OUT/03-tokens.txt"
echo "--- session dist ---"; cat "$OUT/05-session-dist.txt"
echo "--- top 25 tools ---"; head -25 "$OUT/02-tools.txt"
echo "--- prompt corpus ---"; cat "$OUT/00-meta.txt"
