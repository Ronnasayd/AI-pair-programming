#!/usr/bin/python3
"""
Go Lint Hook

Runs go vet, golangci-lint (if installed) and gofmt checks on Go files after edit.
- Skips if go toolchain not installed
- golangci-lint is optional (falls back to no-op when unavailable)
- Reports vet errors, lint issues and formatting diffs

Cross-platform (Windows, macOS, Linux)
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils import (  # noqa: E402
    find_project_root,
    get_hooks_logger,
    run_command_cwd,
    run_jscpd,
    run_lint_hook_main,
)

logger = get_hooks_logger("GolangLint")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_GO_EXTS = {".go"}


def _exec(bin_: str, args: list[str], cwd: str | None = None) -> dict:
    """Wrapper for tool invocations."""
    cmd = " ".join([bin_, *args])
    return run_command_cwd(cmd, cwd=cwd)


def _check_tool_installed(tool: str) -> bool:
    """Check if tool is installed via system PATH."""
    result = subprocess.run(
        ["which", tool],
        capture_output=True,
        timeout=5,
    )
    return result.returncode == 0


def _run_govet(resolved: Path, project_root: str) -> dict:
    """Run go vet. Returns {success, output, error}."""
    if not _check_tool_installed("go"):
        logger.debug("[GolangLint] go not installed, skipping vet for %s", resolved)
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"go vet {str(resolved)}"
    logger.info("[GolangLint] Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("go", ["vet", str(resolved)], cwd=project_root)
    logger.debug("[GolangLint] go vet result: success=%s", result["success"])
    if result["success"]:
        logger.info("[GolangLint] go vet passed for %s", resolved)
    else:
        logger.warning(
            "[GolangLint] go vet found issues in %s:\n%s",
            resolved,
            result.get("output", ""),
        )
    if result.get("error"):
        logger.warning("[GolangLint] go vet stderr: %s", result.get("error", ""))
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_golangci_lint(resolved: Path, project_root: str) -> dict:
    """Run golangci-lint. Returns {success, output, error}."""
    if not _check_tool_installed("golangci-lint"):
        logger.debug(
            "[GolangLint] golangci-lint not installed, skipping lint for %s", resolved
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"golangci-lint run {str(resolved)}"
    logger.info("[GolangLint] Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("golangci-lint", ["run", str(resolved)], cwd=project_root)
    logger.debug("[GolangLint] golangci-lint result: success=%s", result["success"])
    if result["success"]:
        logger.info("[GolangLint] golangci-lint passed for %s", resolved)
    else:
        logger.warning(
            "[GolangLint] golangci-lint found issues in %s:\n%s",
            resolved,
            result.get("output", ""),
        )
    if result.get("error"):
        logger.warning("[GolangLint] golangci-lint stderr: %s", result.get("error", ""))
    return {
        "success": result["success"],
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def _run_gofmt(resolved: Path, project_root: str) -> dict:
    """Run gofmt -l to detect formatting diffs. Returns {success, output, error}."""
    if not _check_tool_installed("gofmt"):
        logger.debug(
            "[GolangLint] gofmt not installed, skipping fmt check for %s", resolved
        )
        return {"success": True, "output": "", "error": "", "installed": False}

    cmd = f"gofmt -l {str(resolved)}"
    logger.info("[GolangLint] Executing: %s (cwd=%s)", cmd, project_root)
    result = _exec("gofmt", ["-l", str(resolved)], cwd=project_root)
    # gofmt -l exits 0 even when files need formatting; non-empty output means unformatted.
    unformatted = bool(result.get("output", "").strip())
    if unformatted:
        logger.warning("[GolangLint] gofmt found unformatted file: %s", resolved)
    return {
        "success": result["success"] and not unformatted,
        "output": result.get("output", ""),
        "error": result.get("error", ""),
        "installed": True,
    }


def maybe_run_golang_lint(file_path: str | None) -> dict[str, dict[str, Any] | None]:
    """
    Run go vet, golangci-lint, gofmt and jscpd checks for Go files.

    Args:
        file_path: Path to the edited file.

    Returns:
        Dict with govet, golangci_lint, gofmt and jscpd results.
    """
    result: dict[str, dict[str, Any] | None] = {
        "govet": None,
        "golangci_lint": None,
        "gofmt": None,
        "jscpd": None,
    }

    if not file_path:
        logger.debug("[GolangLint] No file_path provided, skipping.")
        return result

    resolved = Path(file_path).resolve()
    if not resolved.exists():
        logger.debug("[GolangLint] File %s does not exist, skipping.", resolved)
        return result

    ext = resolved.suffix.lower()
    if ext not in _GO_EXTS:
        logger.debug("[GolangLint] File %s not Go, skipping (%s).", resolved, ext)
        return result

    project_root = find_project_root(str(resolved.parent))
    logger.debug("[GolangLint] Project root for %s: %s", resolved, project_root)

    result["govet"] = _run_govet(resolved, project_root)
    result["golangci_lint"] = _run_golangci_lint(resolved, project_root)
    result["gofmt"] = _run_gofmt(resolved, project_root)
    result["jscpd"] = run_jscpd(resolved, project_root, logger, "GolangLint")
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    run_lint_hook_main("GolangLint", logger, maybe_run_golang_lint)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.debug("[GolangLint] Error: %s", exc)
        sys.exit(0)
