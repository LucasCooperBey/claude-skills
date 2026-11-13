#!/usr/bin/env bash
# write-entry.sh, append-only writer.
# Usage: write-entry.sh <type> <slug> < frontmatter-and-body-on-stdin
#   <type>: decision | synthesis | incident | reflection
#   <slug>: kebab-case, no date prefix (the date is added here)
# Stdin omits the opening --- fence and omits id, type, and date.
# Those three are injected. A closing --- line before the body is expected.
# WIKI_DIR defaults to ./wiki. WIKI_ENTRY_DATE overrides the date when set.
# The writer does not edit an existing file. A later entry can name the
# older id in supersedes. The index skips a file whose status is superseded.

set -euo pipefail

WIKI="${WIKI_DIR:-./wiki}"
TYPE="${1:-}"
SLUG="${2:-}"

if [[ -z "$TYPE" || -z "$SLUG" ]]; then
  echo "ERROR: usage: write-entry.sh <type> <slug>" >&2
  exit 64
fi

case "$TYPE" in
  decision|incident) DIR="$WIKI/decisions" ;;
  synthesis)         DIR="$WIKI/synthesis" ;;
  reflection)        DIR="$WIKI/counterfactuals" ;;
  *)
    echo "ERROR: invalid type '$TYPE' (decision|synthesis|incident|reflection)" >&2
    exit 64
    ;;
esac

if ! [[ "$SLUG" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "ERROR: slug must be kebab-case" >&2
  exit 64
fi

if ! mkdir -p "$DIR"; then
  echo "ERROR: could not create $DIR" >&2
  exit 1
fi

DATE="${WIKI_ENTRY_DATE:-$(date +%Y-%m-%d)}"
ID="${DATE}-${SLUG}"
FILE="$DIR/${ID}.md"

# duplicate-id check
if [[ -f "$WIKI/decisions/${ID}.md" || -f "$WIKI/synthesis/${ID}.md" || -f "$WIKI/counterfactuals/${ID}.md" ]]; then
  echo "ERROR: duplicate id '$ID'" >&2
  exit 65
fi

BODY=$(cat)

for field in actors tags summary; do
  if ! grep -qE "^${field}:" <<<"$BODY"; then
    echo "ERROR: missing required frontmatter field: $field" >&2
    exit 66
  fi
done

# Atomic write: tempfile plus hard link. A concurrent writer cannot clobber
# an entry that appeared after the duplicate-id check.
TMP_FILE="${FILE}.tmp.$$"
trap 'rm -f "$TMP_FILE"' EXIT
{
  printf '%s\n' "---"
  printf '%s\n' "id: $ID"
  printf '%s\n' "type: $TYPE"
  printf '%s\n' "date: $DATE"
  printf '%s\n' "$BODY"
} > "$TMP_FILE"

# Warn when stdin has no line that is exactly '---'. Still publish.
# The check scans the whole input, so a long body cannot hide a missing fence.
if ! grep -q "^---$" <<<"$BODY"; then
  echo "WARN: closing '---' not found in input, caller must format frontmatter properly" >&2
fi

if ln "$TMP_FILE" "$FILE" 2>/dev/null; then
  rm -f "$TMP_FILE"
  trap - EXIT
else
  echo "ERROR: $FILE appeared between the duplicate check and publish" >&2
  trap - EXIT
  exit 65
fi

printf '%s\n' "WROTE: $FILE"
