# Step 5 — Apply corrections, file by file

Create one tracker task per file/group; in-progress before edit, complete after.

| File            | Edits                                                                                                                                                                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| spec.md         | Out of Scope, Assumptions, Acceptance Criteria, Implicit-requirement sweep, Requirement Traceability, Success Criteria. Number new ACs **after** existing ones (don't break refs in other docs); note explicitly if order ends out of sequence |
| design.md       | Fix truncated code blocks; adjust component/data diagram; add decisions to Error Handling + Risks tables; detail Tech Decisions rationale                                                                                                      |
| tasks.md        | Fix "What"/"Where"/"Depends on"/"Done when" of affected tasks; reconcile diagram-definition cross-check table so cross-phase deps are explicit (not only within phase)                                                                         |
| requirements.md | Add/adjust FR lines; update "accepted consequences" table; build/fix traceability map between this doc's IDs and spec.md/tasks IDs                                                                                                             |
| context-map.md  | Mark at top which parts later decisions superseded (link source-of-truth doc); resolve "Not Checked" items now verifiable in code                                                                                                              |
| cited ADRs      | Update decision section, accepted negative consequences, context — same correction                                                                                                                                                             |
