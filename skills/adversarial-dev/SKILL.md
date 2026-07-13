---
name: adversarial-dev
description: Orchestrates a code task through two separate agents in an adversarial loop — an executor that implements and a strict evaluator (no write tools) that scores the result 0-10 and demands fixes. Use when the user wants a task "executed and evaluated by 2 agents", "adversarial dev", "generator/evaluator loop", higher-reliability implementation with independent review, or says "turn this into an adversarial workflow". Do NOT use for simple one-shot edits, multi-task wave orchestration (use orchestrate), or single-pass code review of existing code (use code-review).
metadata:
  author: Ronnasayd Machado - github.com/Ronnasayd
  version: "1.0.0"
---

# Adversarial Dev

Runs one coding task through two independent agents — an **executor** that implements and an **evaluator** that only critiques — looping until the evaluator scores the result 8+/10 or 10 iterations are exhausted. The evaluator never writes code; it only reads, runs lint/tests on changed files, and scores. This mirrors GAN-style adversarial review: the same agent grading its own work is structurally biased, so grading must live in a separate, tool-restricted context.

## Instructions

### Step 0: Gather task input

From the user's request extract:

- **Objective**: what must be built/fixed.
- **Acceptance criteria** (optional): if the user gave explicit criteria, use them verbatim. If absent, generate 3-6 concrete, checkable criteria yourself from the objective (functional behavior, edge cases, existing conventions in the repo).
- **Difficulty**: classify once, now, 0-10 — easy (0-3), medium (4-7), hard (8-10) — based on scope (files touched, new logic vs. edit, ambiguity). This does not change the iteration cap; it's for your own calibration and for the log.

Create a log file at `<scratchpad>/adversarial-dev/<task-slug>/log.md` (use the session scratchpad directory) with objective, criteria, and difficulty. Append to this file after every iteration — it is the durable record if the loop stops without success. If this run is one of several parallel invocations (see "Parallel usage" below), `<task-slug>` MUST include a unique id (e.g. from the calling orchestrator), not just a human-readable name — two tasks named similarly must never collide on the same log path.

### Step 1: Spawn the two agents

Spawn both via the `Agent` tool, `subagent_type: general-purpose`, `run_in_background: false` (you need each result before continuing), each **kept alive across iterations** — reuse the same agent by sending follow-up messages (`SendMessage` to its id) rather than spawning fresh agents each round. Two separate threads, two separate contexts:

- **Executor**: full tool access. Briefed with the objective, acceptance criteria, and (from iteration 2+) the evaluator's prior feedback verbatim. Told explicitly to implement, not to self-review or self-grade.
- **Evaluator**: `general-purpose` but instructed in its prompt to never use Edit/Write/NotebookEdit — read-only critique role. Told explicitly: "You are adversarial QA. Your job is to find every reason this implementation is wrong or incomplete. Do not soften findings. Do not fix anything yourself." Give it: the objective, the acceptance criteria, and instructions to run lint/tests scoped ONLY to files the executor modified (get the changed-file list from `git diff --name-only` or from the executor's report — never run the full suite).

### Step 2: The loop (max 10 iterations, hard cap regardless of difficulty)

For iteration N (1 to 10):

1. **Executor turn**: send the objective + criteria (iteration 1) or the evaluator's previous verdict + specific fixes required (iteration 2+). Wait for the executor to report what it changed and why.
2. **Evaluator turn**: send the executor's diff/summary. Evaluator must return, in a fixed structure:
   - Qualitative findings (specific, per-criterion)
   - Objective check results (lint/test pass-fail on changed files only)
   - A single score 0-10
   - Verdict: `APPROVED` (8-10) / `CONDITIONAL` (4-7, list what's missing) / `REJECTED` (0-3, list why)
3. Append iteration N (score, verdict, key findings) to the log file.
4. **Decide**:
   - Score ≥ 8 → stop, go to Step 3 (success).
   - Score 4-7 or 0-3 → continue loop, feeding the evaluator's findings back to the executor next round.
   - N == 10 and score still < 8 → stop, go to Step 4 (exhausted).

Never let the executor see the evaluator's raw score-seeking framing (e.g. don't tell it "just get to 8") — always relay concrete findings, so it fixes substance, not the number.

### Step 3: Success

Report to the user: final score, iteration count, summary of what was built, path to the log file. Task done.

### Step 4: Exhausted without approval

Do NOT auto-accept the best version. Stop and report to the user:

- Last score and verdict
- Full list of outstanding findings from the final evaluation
- Path to the log file with full history

Let the user decide: accept as-is, adjust criteria, or authorize more iterations (if they do, resume the loop past 10 explicitly — the cap only stops the automatic run).

## Example

User says: "Implementa validação de CPF no form de cadastro, usa esse padrão adversarial"

Actions:

1. Objective: add CPF validation to signup form. No explicit criteria given → generate: valid CPF accepted, invalid CPF rejected with clear error, malformed input (letters, wrong length) handled, existing form tests still pass, follows repo's existing validation pattern. Difficulty: easy-medium (4).
2. Spawn executor (full tools) and evaluator (no write tools).
3. Loop: executor implements → evaluator runs `npm test -- <changed files>` + lint on changed files + reviews logic → scores 5/10 first pass (missing malformed-input case) → executor fixes → evaluator scores 9/10 → stop.
4. Report: approved at iteration 2, log at `<scratchpad>/adversarial-dev/cpf-validation/log.md`.

## Parallel usage

This skill may be invoked multiple times concurrently by an outer orchestrator (e.g. `orchestrate`) running several independent tasks at once. Each concurrent invocation runs 2 live agents (executor + evaluator) for up to 10 iterations — this has real implications, not just a token-cost multiplier:

- **Working tree isolation is mandatory.** If two parallel invocations touch the same git working tree, the evaluator's `git diff --name-only` for task A can pick up task B's in-flight changes, causing wrong scoring against the wrong diff. Each parallel invocation of this skill MUST spawn its executor in an isolated git worktree (`isolation: "worktree"` on the `Agent` call) so its file changes and `git diff` are scoped to that task alone. The evaluator for that task must also operate against the same worktree.
- **Unique log paths.** Per Step 0, the task-slug must be collision-proof across concurrent runs — use an id supplied by the calling orchestrator, not a freehand name.
- **This skill does not self-limit parallelism.** The 10-iteration cap bounds a single task's own loop, not how many tasks run at once. If you are the outer orchestrator invoking this skill for multiple tasks, cap concurrent invocations yourself (e.g. 3-4 at a time) — don't fire all tasks simultaneously without a concurrency limit, since each one holds 2 agents open for the duration of its loop.
- **Report per-task, not batched.** Each invocation reports its own Step 3/Step 4 outcome independently; don't wait for all parallel tasks to finish before surfacing a task's result if the caller wants incremental updates.

## Notes

- This skill assumes a code task (implementation/bugfix), per its scope — for non-code deliverables, adapt manually or use `orchestrate`.
- The evaluator's inability to write code is the core guarantee — do not give it Edit/Write/NotebookEdit under any circumstance, even "just to show the fix."
- If the user gives partial criteria, merge with your auto-generated ones rather than discarding either.
