#!/bin/bash
export ASDF_NODEJS_VERSION=23.11.1
export TASKMASTER_SKIP_AUTO_UPDATE=1

# Parse arguments
SPEC_FILE="$1"
TASK_TAG="${2:-master}"
ADDITIONAL_ARGS=("${@:3}")

export TASK_PROMPT=`cat <<EOF
<context filepath="$SPEC_FILE">
$(cat $SPEC_FILE)
</context>
EOF
`

asdf exec task-master add-task --research --prompt="$TASK_PROMPT" --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
asdf exec task-master analyze-complexity --research --prompt="$TASK_PROMPT" --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
asdf exec task-master expand --all --research --prompt="$TASK_PROMPT" --tag="$TASK_TAG" "${ADDITIONAL_ARGS[@]}"
