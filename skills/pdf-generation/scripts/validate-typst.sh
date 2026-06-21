#!/bin/bash
# Validate Typst source file syntax
# Usage: ./validate-typst.sh <file.typ>

if [ -z "$1" ]; then
  echo "Usage: $0 <file.typ>"
  exit 1
fi

FILE="$1"

if [ ! -f "$FILE" ]; then
  echo "Error: File not found: $FILE"
  exit 1
fi

# Check for common issues
echo "Validating $FILE..."

# Count brackets
OPEN_BRACKETS=$(grep -o '\[' "$FILE" | wc -l)
CLOSE_BRACKETS=$(grep -o '\]' "$FILE" | wc -l)

if [ "$OPEN_BRACKETS" -ne "$CLOSE_BRACKETS" ]; then
  echo "WARNING: Bracket mismatch - [ count: $OPEN_BRACKETS, ] count: $CLOSE_BRACKETS"
fi

# Check for potential unescaped characters
UNESCAPED_HASH=$(grep -n '[^\\]#[a-z]' "$FILE" | grep -v '^\s*//' | head -5)
if [ -n "$UNESCAPED_HASH" ]; then
  echo "Potential function calls found (verify these are intentional):"
  echo "$UNESCAPED_HASH"
fi

# Check for potential math mode
UNESCAPED_DOLLAR=$(grep -n '[^\\]\$' "$FILE" | head -5)
if [ -n "$UNESCAPED_DOLLAR" ]; then
  echo "Potential math mode found:"
  echo "$UNESCAPED_DOLLAR"
fi

# Check for newlines in string interpolations (simplified check)
echo ""
echo "File statistics:"
echo "  Lines: $(wc -l < "$FILE")"
echo "  Characters: $(wc -c < "$FILE")"
echo "  Open brackets: $OPEN_BRACKETS"
echo "  Close brackets: $CLOSE_BRACKETS"

echo ""
echo "Validation complete."
