#!/bin/bash
export ASDF_NODEJS_VERSION=23.11.1
export TASKMASTER_SKIP_AUTO_UPDATE=1

# Parse arguments
SPEC_FILE="$1"
TASK_ID="$2"
TASK_TAG="${3:-master}"
ADDITIONAL_ARGS=("${@:4}")

export TASK_PROMPT="Add $SPEC_FILE to references links. Extract the relevant information and expand the task in subtasks. The subtasks should be clear, concise, and actionable. They should capture the essence of the specification and provide a clear direction for implementation."

asdf exec task-master analyze-complexity --research  --id="$TASK_ID" --tag="$TASK_TAG" --prompt="$TASK_PROMPT" "${ADDITIONAL_ARGS[@]}"
asdf exec task-master expand --research --id="$TASK_ID" --tag="$TASK_TAG" --prompt="$TASK_PROMPT" "${ADDITIONAL_ARGS[@]}"
