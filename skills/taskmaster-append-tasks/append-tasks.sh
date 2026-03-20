#!/bin/bash
export ASDF_NODEJS_VERSION=23.11.1
export TASKMASTER_SKIP_AUTO_UPDATE=1

# Parse arguments
PRD_FILE="$1"
TASK_TAG="${2:-master}"
ADDITIONAL_ARGS=("${@:3}")

asdf exec task-master parse-prd --research --input=$PRD_FILE --append --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
asdf exec task-master analyze-complexity "${ADDITIONAL_ARGS[@]}"
