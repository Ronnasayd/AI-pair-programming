#!/bin/bash
export ASDF_NODEJS_VERSION=23.11.1
export TASKMASTER_SKIP_AUTO_UPDATE=1

# Parse arguments
SPEC_FILE="$1"
TASK_ID="$2"
TASK_TAG="${3:-master}"
ADDITIONAL_ARGS=("${@:4}")

export TASK_PROMPT=`cat <<EOF
<context filepath="$SPEC_FILE">
$(cat $SPEC_FILE)
</context>
EOF
`
asdf exec task-master expand --research --id="$TASK_ID" --tag="$TASK_TAG" --prompt="$TASK_PROMPT" "${ADDITIONAL_ARGS[@]}"
