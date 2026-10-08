# Step 2 — Verify claims against code

Spec text = hypothesis. Confirm each in source.

| #   | Area                | Verify                                                                                                                              |
| --- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Routes/controllers  | Central routes file + cited module routers: paths, middlewares applied, order                                                       |
| 2   | RBAC/permissions    | Whole matrix (all roles, not only cited) + consuming use case: what each resource/action allows today                               |
| 3   | Data schema         | Cited + related models (Prisma or equiv.): FKs, uniques, column types, naming conventions                                           |
| 4   | Auth context        | Where populated (middleware/adapter): exact fields, source (token claim vs DB column), extra checks (e.g. local record requirement) |
| 5   | Error handling      | How validator errors become HTTP responses in the "pattern to reuse" controllers: uniform across project or divergent per module    |
| 6   | Pagination/listing  | Reference endpoint schema + response, field by field, vs what spec promises to reuse                                                |
| 7   | Toolchain/versions  | Real dependency versions (ORM, validator) in manifest; run `--help` on command cited in task to confirm flags exist                 |
| 8   | Data write paths    | Grep who writes/updates field spec assumes "never written by API" / "always in format X" (seeds, scripts, other modules)            |
| 9   | Existing test fakes | Every file using the contract that will change (not just cited example) → count fakes/mocks that will break                         |
| 10  | Transactions        | Grep transaction usage (e.g. `$transaction`): first use or existing pattern? Tests hit real DB or mocks only?                       |
