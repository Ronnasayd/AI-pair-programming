#!/bin/bash
# Validate that spec files exist for given tag
# Usage: validate_tag.sh <tag> <project_root>

set -e

TAG="$1"
PROJECT_ROOT="${2:-.}"

# Check tag format (kebab-case)
if ! [[ "$TAG" =~ ^[a-z0-9]([a-z0-9-]*[a-z0-9])?$ ]]; then
  echo "ERROR: Invalid tag format. Use kebab-case (e.g., auto-null-cancellation)"
  exit 1
fi

# Check required files
DESIGN="${PROJECT_ROOT}/.specs/features/${TAG}/design.md"
SPEC="${PROJECT_ROOT}/.specs/features/${TAG}/spec.md"
METADATA="${PROJECT_ROOT}/.taskmaster/execution/metadata.json"

MISSING=()
[ -f "$DESIGN" ] || MISSING+=("$DESIGN")
[ -f "$SPEC" ] || MISSING+=("$SPEC")
[ -f "$METADATA" ] || MISSING+=("$METADATA")

if [ ${#MISSING[@]} -gt 0 ]; then
  echo "ERROR: Missing required files for tag '$TAG':"
  for file in "${MISSING[@]}"; do
    echo "  - $file"
  done
  exit 1
fi

echo "OK: All required files found for tag '$TAG'"
exit 0
