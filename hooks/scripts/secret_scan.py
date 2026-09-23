"""Shared secret-scan primitives: detect-secrets + regex fallback.

Used by protect_files.py (PreToolUse, deny on match) and
scan_secrets_output.py (PostToolUse, redact on match) so the scan logic
lives in one place instead of being duplicated across both hooks.
"""

import json
import logging
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

DETECT_SECRETS_BIN = shutil.which("detect-secrets")

# Used only when detect-secrets isn't installed, so a content scan doesn't
# silently no-op on a machine without the binary.
FALLBACK_SECRET_PATTERNS = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    (
        "AWS Secret Key",
        re.compile(
            r"aws_secret_access_key\s*=\s*[\"']?[A-Za-z0-9/+=]{40}", re.IGNORECASE
        ),
    ),
    ("GitHub Token", re.compile(r"(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{36,}")),
    ("Private Key", re.compile(r"-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----")),
    (
        "Generic API Key",
        re.compile(r"api[_-]?key\s*[:=]\s*[\"'][a-zA-Z0-9]{20,}[\"']", re.IGNORECASE),
    ),
    ("Slack Token", re.compile(r"xox[bpors]-[0-9a-zA-Z-]{10,}")),
    ("Database URL", re.compile(r"(postgres|mysql|mongodb|redis)://[^:]+:[^@\s]+@")),
    (
        "JWT Token",
        re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    ),
]

ALLOWLIST_PRAGMA = re.compile(r"pragma:\s*allowlist\s*secret", re.IGNORECASE)


def is_allowlisted_line(lines: list[str], line_no: int) -> bool:
    """True if the finding's own line or the line above carries the bypass pragma.

    The `pragma: allowlist secret` comment matches detect-secrets' own
    inline-allowlist convention, so one marker works for both scan paths.

    Args:
        lines: The scanned content split into lines.
        line_no: 1-based line number of the finding.

    Returns:
        True if the finding is allowlisted via the bypass pragma.
    """
    idx = line_no - 1
    for candidate in (idx, idx - 1):
        if 0 <= candidate < len(lines) and ALLOWLIST_PRAGMA.search(lines[candidate]):
            return True
    return False


def scan_content_fallback(content: str) -> list[dict]:
    """Regex-based secret scan used when detect-secrets isn't installed.

    Args:
        content: File content to scan.

    Returns:
        A finding dict (type, line) for each regex match not allowlisted.
    """
    findings = []
    lines = content.split("\n")
    for name, regex in FALLBACK_SECRET_PATTERNS:
        for i, line in enumerate(lines):
            if regex.search(line) and not is_allowlisted_line(lines, i + 1):
                findings.append({"type": name, "line": i + 1})
    return findings


def scan_content_for_secrets(
    content: str, file_path: str, logger: logging.Logger
) -> list[dict]:
    """Run detect-secrets against `content` as if it were `file_path`.

    Scans by writing to a tempdir under the target's basename and cwd'ing
    into it — scanning by absolute path silently yields empty results, since
    detect-secrets' filters key off a repo-relative path.

    Args:
        content: The text to scan.
        file_path: Path used only to derive the scanned file's basename.
        logger: Logger for debug/warning output.

    Returns:
        Secret findings from detect-secrets, or the regex fallback's list.
    """
    if not DETECT_SECRETS_BIN:
        return scan_content_fallback(content)

    suffix = Path(file_path).name or "scanned_file"

    with tempfile.TemporaryDirectory() as tmpdir:
        target = Path(tmpdir) / suffix
        target.write_text(content, encoding="utf-8")

        try:
            result = subprocess.run(  # noqa: S603 - fixed argv, no shell, trusted local binary
                [DETECT_SECRETS_BIN, "scan", suffix],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as exc:
            logger.debug("detect-secrets invocation failed: %s", exc)
            return []

        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            logger.debug("detect-secrets non-JSON output: %s", result.stdout[:500])
            return []

        return report.get("results", {}).get(suffix, [])


def _demo() -> None:
    """Self-check: fallback scan catches an AWS key, misses a bare word."""
    findings = scan_content_fallback("key = AKIAABCDEFGHIJKLMNOP\nnothing = here")
    assert len(findings) == 1, findings  # noqa: S101 - demo self-check, not test code
    assert findings[0]["type"] == "AWS Access Key"  # noqa: S101

    allowlisted = scan_content_fallback(
        "key = AKIAABCDEFGHIJKLMNOP  # pragma: allowlist secret"
    )
    assert not allowlisted  # noqa: S101
    print("secret_scan: OK", file=sys.stderr)  # noqa: T201 - demo entrypoint, not lib output


if __name__ == "__main__":
    _demo()
