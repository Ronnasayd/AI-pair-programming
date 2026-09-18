---
name: quality-gate
description: Run or explain the ratchet-style quality gate (scripts/quality-gate.js) for Node/TS projects — lint violations, code duplication %, test coverage %, and files over a line-count limit compared against a frozen baseline. Use when the user says "run the quality gate", "check quality-gate.js", "set up the ratchet gate", "update the baseline", "why did the quality gate fail", or wants to wire it into CI so PRs never regress quality metrics silently.
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Quality Gate

Ratchet-style quality gate for Node/TS projects. Compares four metrics against a frozen `baseline.json`; any regression (even 0.1 point) fails the run. Never improves the baseline on its own — only `--update-baseline` advances it.

Script: `<skills-dir>/quality-gate/scripts/quality-gate.js` (this repo).

## Working directory: `.quality-gate/`

All work happens in a `.quality-gate/` scratch dir at the target project's root — never scatter generated files loose in the project root:

```bash
mkdir -p .quality-gate
cp <skills-dir>/quality-gate/scripts/quality-gate.js .quality-gate/
```

Every ad-hoc generated file (eslint-report.json, jscpd-report.json, coverage/, quality-gate-report.md) is written inside `.quality-gate/`. `baseline.json` is the one exception — it's a persistent artifact, keep it at the project root (or wherever `--baseline-path` points) so it survives cleanup.

Delete `.quality-gate/` when done — after the report's been read/posted, remove the whole dir (`rm -rf .quality-gate`). Nothing avulso left behind in the target repo.

## Before running

The script only reads pre-generated reports — it never runs eslint/jscpd/jest itself. Generate them first, into `.quality-gate/`:

```bash
npx eslint . --format json > .quality-gate/eslint-report.json
npx jscpd . --reporters json -o .quality-gate          # writes .quality-gate/jscpd-report.json
npx jest --coverage --coverageReporters=json-summary --coverageDirectory=.quality-gate/coverage
```

Missing any of the three → the script fails with a clear message naming the exact missing file (never a generic crash).

## Running it

```bash
node .quality-gate/quality-gate.js --root . \
  --report-path .quality-gate/quality-gate-report.md \
  --eslint-report .quality-gate/eslint-report.json \
  --jscpd-report .quality-gate/jscpd-report.json \
  --coverage-summary .quality-gate/coverage/coverage-summary.json
```

| Situation                                            | Behavior                                                           |
| ---------------------------------------------------- | ------------------------------------------------------------------ |
| No `baseline.json` yet                               | Creates it from current metrics, prints a bootstrap notice, exit 0 |
| `baseline.json` exists, nothing regressed            | Writes `quality-gate-report.md`, exit 0                            |
| `baseline.json` exists, something regressed          | Writes `quality-gate-report.md` with per-metric delta, exit 1      |
| `baseline.json` malformed (bad JSON / missing field) | Fails naming the bad field, does NOT overwrite the file            |

## Flags

```
--root <path>               default: cwd
--max-lines <n>             default: 500        (line-count threshold for "large file")
--baseline-path <path>      default: baseline.json
--report-path <path>        default: quality-gate-report.md
--eslint-report <path>      default: eslint-report.json
--jscpd-report <path>       default: jscpd-report.json
--coverage-summary <path>   default: coverage/coverage-summary.json
--update-baseline           overwrite baseline.json with current metrics (advances the ratchet)
```

All paths resolve relative to `--root`. Point the three `--*-report`/`--coverage-summary` flags at `.quality-gate/` since that's where they're generated; leave `--baseline-path` at the project root default.

`--update-baseline` never triggers implicitly — only explicit. Use it right after a merged refactor that legitimately improved the numbers.

## Reading the report

`quality-gate-report.md` always has three sections: a current-vs-baseline summary table, a Failures table (empty → "None.") with baseline/current/delta per regressed metric, and a large-files section (empty → "None.", never omitted — an absent section would be ambiguous with "didn't run").

## Wiring into CI (GitHub Actions)

Run the three collection commands, then the script, in the same job — no TTY, no prompts, deterministic exit code. Read the generated `quality-gate-report.md` in a later step to post it as a PR comment (publishing itself is the workflow YAML's job, not the script's).

```yaml
- run: mkdir -p .quality-gate && cp <skills-dir>/quality-gate/scripts/quality-gate.js .quality-gate/
- run: npx eslint . --format json > .quality-gate/eslint-report.json
- run: npx jscpd . --reporters json -o .quality-gate
- run: npx jest --coverage --coverageReporters=json-summary --coverageDirectory=.quality-gate/coverage
- run: |
    node .quality-gate/quality-gate.js --root . \
      --report-path .quality-gate/quality-gate-report.md \
      --eslint-report .quality-gate/eslint-report.json \
      --jscpd-report .quality-gate/jscpd-report.json \
      --coverage-summary .quality-gate/coverage/coverage-summary.json
  # non-zero exit here fails the job — that's the gate
- if: always()
  run: cat .quality-gate/quality-gate-report.md # or use it to post a PR comment
- if: always()
  run: rm -rf .quality-gate
```

## Troubleshooting

- **"required file not found: .quality-gate/eslint-report.json"** → run the collection command for that tool first; the script never runs it for you.
- **"malformed baseline"** → someone hand-edited or truncated `baseline.json`. Fix the named field manually; the script refuses to auto-overwrite a corrupt baseline.
- **Gate fails on a PR that only touched unrelated files** → any of the four metrics regressing anywhere in the repo fails the whole run; there's no per-file scoping in this version (see spec's "Accepted consequences").
- **Baseline feels stuck / too strict after a real improvement** → run with `--update-baseline` once, deliberately, after merging.
