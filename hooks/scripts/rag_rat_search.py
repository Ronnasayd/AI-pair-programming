#!/usr/bin/python3
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from utils import extract_query_text, get_by_key, get_hooks_logger  # noqa: E402

LOG = get_hooks_logger("RagRatSearch")

MIN_SCORE = 0.5
TOP_N = 3
TIMEOUT_SECONDS = 10


def isRagRatAvailable(cwd: str) -> bool:
    return shutil.which("rag-rat") is not None and (Path(cwd) / "rag-rat.toml").exists()


def runQuery(query: str, cwd: str) -> list[dict] | None:
    try:
        result = subprocess.run(
            ["rag-rat", "--json", "query", query],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=cwd,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        LOG.warning(f"rag-rat query failed: {e}")
        return None

    if result.returncode != 0:
        LOG.warning(f"rag-rat query exited {result.returncode}: {result.stderr[:300]}")
        return None

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        LOG.warning(f"Failed to parse rag-rat JSON output: {e}")
        return None


def filterTopHits(hits: list[dict]) -> list[dict]:
    scored = [h for h in hits if h.get("score", 0) >= MIN_SCORE]
    scored.sort(key=lambda h: h.get("score", 0), reverse=True)
    return scored[:TOP_N]


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError) as e:
        LOG.debug(f"Failed to parse stdin JSON: {e}")
        sys.exit(0)

    try:
        cwd = get_by_key(payload, "cwd") or "."

        if not isRagRatAvailable(cwd):
            LOG.debug(f"rag-rat not installed locally in {cwd} — skipping")
            sys.exit(0)

        prompt = extract_query_text(payload)
        if not prompt:
            LOG.debug("No prompt/answer text in payload — skipping")
            sys.exit(0)

        LOG.debug(f"Querying rag-rat ({len(prompt)} chars): {prompt[:80]!r}...")

        hits = runQuery(prompt, cwd)
        if not hits:
            LOG.debug("No rag-rat results")
            sys.exit(0)

        top_hits = filterTopHits(hits)
        LOG.debug(
            f"Top hits (score>={MIN_SCORE}): "
            f"{[(h['path'], h.get('score')) for h in top_hits]}"
        )

        if not top_hits:
            sys.exit(0)

        results = [
            {
                "path": h.get("path"),
                "ref": h.get("ref"),
                "score": h.get("score"),
                "start_line": h.get("start_line"),
                "end_line": h.get("end_line"),
                "summary": h.get("summary"),
            }
            for h in top_hits
        ]

        hook_event_name = (
            "PostToolUse" if get_by_key(payload, "tool_name") else "UserPromptSubmit"
        )
        output = {
            "hookSpecificOutput": {
                "hookEventName": hook_event_name,
                "additionalContext": json.dumps(
                    {
                        "instruction": (
                            "these rag-rat repo-search hits are relevant to the user's "
                            "request; use them as local code context before answering — "
                            "read the referenced path/lines if more detail is needed"
                        ),
                        "results": results,
                    },
                    ensure_ascii=False,
                ),
            }
        }
        LOG.debug(f"[additionalContext]: {json.dumps(output, ensure_ascii=False)}")
        print(json.dumps(output, ensure_ascii=False))

    except Exception as e:
        LOG.warning(f"Unexpected error: {type(e).__name__}: {e}", exc_info=True)

    sys.exit(0)


if __name__ == "__main__":
    main()
