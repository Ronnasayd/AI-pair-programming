#!/bin/bash
# Test merge-tasks.py and validate-tasks.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MERGE_SCRIPT="$SCRIPT_DIR/scripts/merge-tasks.py"
VALIDATE_SCRIPT="$SCRIPT_DIR/scripts/validate-tasks.py"

# Temp directory for test files
TEST_DIR=$(mktemp -d)
trap "rm -rf $TEST_DIR" EXIT

TASKS_FILE="$TEST_DIR/tasks.json"
METADATA_FILE="$TEST_DIR/metadata.json"

echo "🧪 Testing merge-tasks.py and validate-tasks.py..."

# Test 1: Initial merge (empty file)
echo -n "Test 1: Initial merge... "
TASKS_JSON='[{"id":1,"title":"Task 1","description":"First task","status":"pending","priority":"high","dependencies":[],"details":"Do first","testStrategy":"none","subtasks":[],"metadata":{"wave":1,"onCriticalPath":true}}]'
python3 "$MERGE_SCRIPT" "$TASKS_FILE" "master" "$TASKS_JSON"

if [ -f "$TASKS_FILE" ]; then
  echo "✓"
else
  echo "✗ File not created"
  exit 1
fi

# Test 2: Validate tasks.json structure
echo -n "Test 2: Validate tasks.json... "
if python3 "$VALIDATE_SCRIPT" tasks "$TASKS_FILE"; then
  echo "✓"
else
  echo "✗ Validation failed"
  exit 1
fi

# Test 3: Merge second tag (should preserve master)
echo -n "Test 3: Merge second tag without losing first... "
TASKS_JSON2='[{"id":1,"title":"Feature Task 1","description":"Feature first","status":"pending","priority":"medium","dependencies":[],"details":"Do feature","testStrategy":"unit","subtasks":[],"metadata":{"wave":1,"onCriticalPath":false}}]'
python3 "$MERGE_SCRIPT" "$TASKS_FILE" "feature/auth" "$TASKS_JSON2"

# Check both tags exist
if grep -q '"master"' "$TASKS_FILE" && grep -q '"feature/auth"' "$TASKS_FILE"; then
  echo "✓"
else
  echo "✗ Tags not preserved"
  exit 1
fi

# Test 4: Validate after merge
echo -n "Test 4: Validate merged tasks.json... "
if python3 "$VALIDATE_SCRIPT" tasks "$TASKS_FILE"; then
  echo "✓"
else
  echo "✗ Validation failed"
  exit 1
fi

# Test 5: Create and validate metadata.json
echo -n "Test 5: Create and validate metadata.json... "
cat > "$METADATA_FILE" <<'EOF'
{
  "projectName": "test-project",
  "version": "1.0.0",
  "createdAt": "2026-06-16T00:00:00Z",
  "updatedAt": "2026-06-16T00:00:00Z",
  "description": "Test project",
  "source": "tasks.md",
  "testCommands": {"unit": "test"},
  "executionWaves": {"wave1_serial": [1]},
  "criticalPath": [1],
  "parallelizationNotes": {"wave1": "Single task"}
}
EOF

if python3 "$VALIDATE_SCRIPT" metadata "$METADATA_FILE"; then
  echo "✓"
else
  echo "✗ Metadata validation failed"
  exit 1
fi

echo ""
echo "✅ All tests passed!"
echo "   - Merge preserves existing tags"
echo "   - Validation works for tasks.json and metadata.json"
echo "   - Fixed scripts ready for use in SKILL execution"
