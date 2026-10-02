#!/usr/bin/env bash
# why: tlc-exec is external to this repo; mirror its output into the shared external hook log.
# hazard: pipefail keeps tlc-exec's exit code (exit 2 = block) instead of tee's always-0.
set -o pipefail
mkdir -p "$HOME/.claude/logs"
node /home/ronnas/.tlc/harness/bin/tlc-exec.mjs "$@" 2>&1 | tee -a "$HOME/.claude/logs/external.log"
