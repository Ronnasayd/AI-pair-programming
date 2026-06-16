# TaskMaster Conversion Scripts

Fixed scripts for TaskMaster JSON generation and validation. These replace inline command-line operations.

## Scripts

### `merge-tasks.py`

Merges new task tag into existing `.taskmaster/tasks/tasks.json` without overwriting other tags.

**Usage:**

```bash
python3 merge-tasks.py <tasks_file> <tag> <tasks_json>
```

**Arguments:**

- `tasks_file`: Path to `.taskmaster/tasks/tasks.json`
- `tag`: Tag key (e.g., `"master"`, `"feature/auth"`)
- `tasks_json`: JSON string with tasks array for the tag

**Example:**

```bash
python3 merge-tasks.py .taskmaster/tasks/tasks.json "feature/auth" '[{"id":1,...}]'
```

**Behavior:**

- ✅ Reads existing file (if exists)
- ✅ Merges new tag without removing existing tags
- ✅ Writes back atomically
- ✅ Returns 0 on success, 1 on error

### `validate-tasks.py`

Validates TaskMaster JSON structure and required fields.

**Usage:**

```bash
python3 validate-tasks.py <file_type> <json_file>
```

**Arguments:**

- `file_type`: `"tasks"` or `"metadata"`
- `json_file`: Path to JSON file

**Validates tasks.json:**

- At least one tag present
- Each tag has `"tasks"` array
- Each task has required fields: `id`, `title`, `description`, `status`, `priority`, `dependencies`, `details`, `testStrategy`, `subtasks`, `metadata`
- Each task has `metadata.wave` and `metadata.onCriticalPath`

**Validates metadata.json:**

- Required fields: `projectName`, `version`, `createdAt`, `updatedAt`, `description`, `source`, `testCommands`, `executionWaves`, `criticalPath`, `parallelizationNotes`
- `executionWaves` is object
- `criticalPath` is array

**Example:**

```bash
python3 validate-tasks.py tasks .taskmaster/tasks/tasks.json
python3 validate-tasks.py metadata .taskmaster/execution/metadata.json
```

**Returns:** 0 on valid, 1 on error

## Testing

Run the test suite:

```bash
bash ../test-merge.sh
```

Tests verify:

- ✅ Initial merge creates file
- ✅ Validation passes valid structure
- ✅ Merging second tag preserves first tag
- ✅ Metadata validation works

## Integration with SKILL.md

The SKILL.md Step 6–7 workflow:

1. Build tasks JSON and metadata JSON in memory
2. Use `merge-tasks.py` to write tasks.json (preserves existing tags)
3. Write metadata.json directly (no merge needed)
4. Use `validate-tasks.py` to verify both files

This ensures:

- No data loss on repeated conversions
- Consistent validation across runs
- Fixed scripts instead of inline commands
