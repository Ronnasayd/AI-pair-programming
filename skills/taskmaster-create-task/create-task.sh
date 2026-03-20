#!/bin/bash
export ASDF_NODEJS_VERSION=23.11.1
export TASKMASTER_SKIP_AUTO_UPDATE=1

# Parse arguments
SPEC_FILE="$1"
TASK_TAG="${2:-master}"
ADDITIONAL_ARGS=("${@:3}")

export TASK_PROMPT="Extract the relevant information and create the task. The task should be clear, concise, and actionable. It should capture the essence of the specification and provide a clear direction for implementation."

asdf exec task-master add-task --research --file="$SPEC_FILE" --prompt="$TASK_PROMPT" --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
asdf exec task-master analyze-complexity --research --file="$SPEC_FILE" --prompt="$TASK_PROMPT" --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
asdf exec task-master expand --all --research --file="$SPEC_FILE" --prompt="$TASK_PROMPT" --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
