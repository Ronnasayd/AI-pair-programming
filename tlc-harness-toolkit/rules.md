# Harness rules and triggers

How operator rules work in the tlc harness-toolkit. Derived from the harness source
(`~/.tlc/harness/src/core/rules/`: `rules.types.ts`, `rules.parse.ts`, `rules.trigger.ts`,
`rules.proof.ts`, `rules.decide.ts`). The source is the truth; re-check it if the harness version changes.

## Model

A rule is a markdown file with frontmatter. The file name (without extension) is the rule id.

```markdown
---
on: <trigger>
require:
  - <proof> [since HEAD|session]
otherwise: deny | ask | follow-up | warn
enabled: true # optional; false switches off a global rule
---

Free text, injected verbatim when the rule fires.
```

Flow: event happens → trigger matches → harness checks that **every** proof in `require` exists →
if any is missing, apply `otherwise`. If all hold, nothing is emitted.

- Proofs are a conjunction (AND). No OR / NOT, on purpose.
- A proof counts only if the harness itself observed it. The agent asserting it, or a model verdict, never counts.
- Tiers: `global` (runtime home `rules/`) and `project` (`.tlc/harness/rules/`). Both apply; a project rule with
  the same name replaces the global one.
- A rule that cannot be parsed (unknown trigger/proof, bad `otherwise`, or enabled with no `require`) is not
  silently ignored: it is recorded as an error and `tlc harness doctor` reports it.

## Triggers (`on:`)

| Trigger              | Fires when                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------------- |
| `pr-open`            | `gh pr create` (not `--draft`/`-d`) or `gh pr ready`; also `gh api repos/{o}/{r}/pulls` with POST |
| `commit`             | `git commit`                                                                                      |
| `push`               | `git push`                                                                                        |
| `pr-merge`           | `gh pr merge`                                                                                     |
| `stop`               | the agent tries to end its turn                                                                   |
| `tool(<name>)`       | a tool call with that name, e.g. `tool(Write)`                                                    |
| `command(<pattern>)` | a shell command containing those words, e.g. `command(gh pr create)`                              |

Shell matching notes:

- The command is tokenized, not substring-matched. `x && gh pr create` fires; a heredoc body that merely
  contains `gh pr create` does not.
- Wrappers in front (`sudo`, `time`, `env X=1`) do not hide the command. Word order matters; trailing args do not.
- A bare script name matches its full path (`build.sh` matches `./scripts/build.sh`); a token containing `/`
  must match exactly.
- `pr-open` escape hatch: a draft PR is not gated. Open as draft, produce the proof, then `gh pr ready`
  (which is gated normally).
- `tool(<name>)` sees only the tool name. It cannot tell _which_ skill a `Skill` call invoked, so
  `tool(Skill)` fires for every skill.

## Proofs (`require:`)

| Proof                | Satisfied by                                                                 |
| -------------------- | ---------------------------------------------------------------------------- |
| `subagent(<type>)`   | a subagent of that type ran, e.g. `subagent(the-jury)`                       |
| `command(<pattern>)` | a command with those words ran, e.g. `command(pytest)`                       |
| `gate(<name>)`       | a configured gate passed                                                     |
| `file(<glob>)`       | a file was written. Only three shapes: exact path, `*.ext`, or `dir/` prefix |

Freshness window:

- `since HEAD` (default): proof must be from the current commit. Never satisfiable outside a git checkout.
- `since session`: proof from the current session.

When a proof is missing, the message says whether it never ran or ran at a different commit/session.

There is **no** `skill(...)` proof or trigger, so "skill A must invoke skills B, C" cannot be a native rule.
Put that in the skill's `SKILL.md`, or use a `stop` rule that requires an artifact only those skills produce.

## Verdicts (`otherwise:`)

| Value       | Effect                                                                            |
| ----------- | --------------------------------------------------------------------------------- |
| `deny`      | blocks the action                                                                 |
| `ask`       | asks the operator, only in `paired` mode; in `solo` and `focus` it becomes `deny` |
| `follow-up` | proceeds and injects the text as a pending item                                   |
| `warn`      | warns only                                                                        |

`deny`, `follow-up` and `warn` are identical in every posture. Posture only governs `ask`.

## Examples

Require tests before every commit:

```markdown
---
on: commit
require:
  - command(pytest) since HEAD
otherwise: deny
---

Run the tests before committing.
```

Require a review subagent before opening a PR:

```markdown
---
on: pr-open
require:
  - subagent(the-jury) since HEAD
otherwise: deny
---

Convene the jury on this branch.
```
