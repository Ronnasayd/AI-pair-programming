#!/usr/bin/env bash
# why: tee replacement — passes stdin through untouched (hook JSON must reach Claude) while logging
#      each line as "<date> [<sid8>]-[DEBUG]-[<Name>]: <line>", matching utils.get_hooks_logger.
# usage: some-hook | ext-log.sh Name
name=${1:-External}
sid=${CLAUDE_CODE_SESSION_ID:0:8}
log="$CLAUDE_CONFIG_DIR/logs/external.log"
mkdir -p "${log%/*}"
while IFS= read -r line || [ -n "$line" ]; do
  printf '%s\n' "$line"
  t=$EPOCHREALTIME; f=${t#*[.,]}
  printf '%(%F %T)T,%s [%s]-[DEBUG]-[%s]: %s\n' "${t%[.,]*}" "${f:0:3}" "${sid:-$(printf '%(%H%M%S)T' -1)}" "$name" "$line" >>"$log"
done
