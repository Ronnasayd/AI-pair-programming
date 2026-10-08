# Step 6 — Sync derived task tracker (e.g. taskmaster)

Only when spec feeds a structured tracker separate from markdown.

| #   | Action                                                                                                                                                                                 |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Read an existing record → learn its fields                                                                                                                                             |
| 2   | Write small disposable script (scratchpad, outside repo): parse tasks.md by section, overwrite **only** derived fields (description, details); keep status + manually set dependencies |
| 3   | Back up original file before running                                                                                                                                                   |
| 4   | Run; content-diff vs backup (not bytes) → only expected fields changed                                                                                                                 |
| 5   | Watch reserialization altering non-ASCII escaping; normalize output to file's original escape format                                                                                   |
