#!/usr/bin/env python3
"""
Agentic Loop Controller
Tracks state, detects convergence, and manages the iteration lifecycle
for the Figma-to-Code validation loop.

Usage:
  # Initialize / start a new loop session:
  python scripts/agentic_loop.py init --framework react --max-iterations 10

  # Log an iteration result:
  python scripts/agentic_loop.py log --ssim 0.91 --verdict REVIEW --notes "padding off on left side"

  # Check whether to continue:
  python scripts/agentic_loop.py status

  # Save final report:
  python scripts/agentic_loop.py report --output loop_report.json
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime

SESSION_FILE = "/tmp/figma_loop_session.json"


class AgenticLoopController:
    def __init__(self, framework: str = "react", max_iterations: int = 10, ssim_threshold: float = 0.95):
        self.framework = framework
        self.max_iterations = max_iterations
        self.ssim_threshold = ssim_threshold
        self.iteration = 0
        self.history = []
        self.started_at = datetime.now().isoformat()

    # --- Persistence ---

    def save(self, path: str = SESSION_FILE):
        data = {
            "framework": self.framework,
            "max_iterations": self.max_iterations,
            "ssim_threshold": self.ssim_threshold,
            "iteration": self.iteration,
            "history": self.history,
            "started_at": self.started_at,
        }
        Path(path).write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: str = SESSION_FILE) -> "AgenticLoopController":
        if not Path(path).exists():
            print(f"ERROR: No active session found at {path}. Run 'init' first.", file=sys.stderr)
            sys.exit(1)
        data = json.loads(Path(path).read_text())
        ctrl = cls(
            framework=data["framework"],
            max_iterations=data["max_iterations"],
            ssim_threshold=data["ssim_threshold"],
        )
        ctrl.iteration = data["iteration"]
        ctrl.history = data["history"]
        ctrl.started_at = data["started_at"]
        return ctrl

    # --- Core logic ---

    def log_iteration(self, ssim_score: float, verdict: str, diff_regions: list = None, notes: str = ""):
        self.iteration += 1
        self.history.append({
            "iteration": self.iteration,
            "timestamp": datetime.now().isoformat(),
            "ssim_score": ssim_score,
            "verdict": verdict,
            "diff_regions": diff_regions or [],
            "notes": notes,
        })

    def should_continue(self) -> tuple[bool, str]:
        """Return (should_continue, reason)."""
        if not self.history:
            return True, "no iterations yet"

        last_score = self.history[-1]["ssim_score"]

        if last_score >= self.ssim_threshold:
            return False, f"target reached: SSIM {last_score:.4f} >= {self.ssim_threshold}"

        if self.iteration >= self.max_iterations:
            return False, f"max iterations reached ({self.max_iterations})"

        stalled, reason = self.detect_convergence()
        if stalled:
            return False, reason

        return True, f"iteration {self.iteration}/{self.max_iterations}, score {last_score:.4f}"

    def detect_convergence(self) -> tuple[bool, str]:
        """Detect if score is stalling (no meaningful progress)."""
        if len(self.history) < 3:
            return False, ""

        recent = [h["ssim_score"] for h in self.history[-3:]]

        # Completely flat
        if recent[-1] == recent[-2] == recent[-3]:
            return True, f"Score stalled at {recent[-1]:.4f} for 3 consecutive iterations"

        # Micro-improvements (< 0.001 per step)
        diffs = [recent[i] - recent[i - 1] for i in range(1, len(recent))]
        if all(d < 0.001 for d in diffs):
            return True, f"Score improvements < 0.001 over last 3 iterations (last: {recent[-1]:.4f})"

        # Regression (score went down)
        if recent[-1] < recent[-2] - 0.01:
            return True, f"Score regressed from {recent[-2]:.4f} to {recent[-1]:.4f} — last edit made things worse"

        return False, ""

    def best_iteration(self) -> dict:
        if not self.history:
            return {}
        return max(self.history, key=lambda h: h["ssim_score"])

    def get_summary(self) -> dict:
        if not self.history:
            return {"status": "no_iterations"}

        scores = [h["ssim_score"] for h in self.history]
        cont, reason = self.should_continue()
        best = self.best_iteration()

        return {
            "framework": self.framework,
            "total_iterations": len(self.history),
            "final_score": scores[-1],
            "best_score": best["ssim_score"],
            "best_iteration": best["iteration"],
            "initial_score": scores[0],
            "improvement": best["ssim_score"] - scores[0],
            "converged": scores[-1] >= self.ssim_threshold,
            "should_continue": cont,
            "stop_reason": reason if not cont else None,
            "started_at": self.started_at,
            "history": self.history,
        }


# --- CLI ---

def cmd_init(args):
    ctrl = AgenticLoopController(
        framework=args.framework,
        max_iterations=args.max_iterations,
        ssim_threshold=args.ssim_threshold,
    )
    ctrl.save()
    print(json.dumps({
        "status": "initialized",
        "framework": ctrl.framework,
        "max_iterations": ctrl.max_iterations,
        "ssim_threshold": ctrl.ssim_threshold,
        "session_file": SESSION_FILE,
    }, indent=2))


def cmd_log(args):
    ctrl = AgenticLoopController.load()
    ctrl.log_iteration(
        ssim_score=args.ssim,
        verdict=args.verdict,
        notes=args.notes or "",
    )
    cont, reason = ctrl.should_continue()
    ctrl.save()
    print(json.dumps({
        "iteration": ctrl.iteration,
        "ssim_score": args.ssim,
        "verdict": args.verdict,
        "should_continue": cont,
        "reason": reason,
    }, indent=2))


def cmd_status(args):
    ctrl = AgenticLoopController.load()
    cont, reason = ctrl.should_continue()
    last = ctrl.history[-1] if ctrl.history else {}
    print(json.dumps({
        "iteration": ctrl.iteration,
        "max_iterations": ctrl.max_iterations,
        "last_score": last.get("ssim_score"),
        "best_score": ctrl.best_iteration().get("ssim_score"),
        "should_continue": cont,
        "reason": reason,
    }, indent=2))


def cmd_report(args):
    ctrl = AgenticLoopController.load()
    summary = ctrl.get_summary()
    output = json.dumps(summary, indent=2)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Report saved to: {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(description="Agentic loop controller for Figma-to-code refinement")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Start a new loop session")
    p_init.add_argument("--framework", default="react", choices=["react", "vue", "vanilla"], help="Target framework")
    p_init.add_argument("--max-iterations", type=int, default=10, help="Maximum iterations")
    p_init.add_argument("--ssim-threshold", type=float, default=0.95, help="Target SSIM score")

    # log
    p_log = subparsers.add_parser("log", help="Log an iteration result")
    p_log.add_argument("--ssim", type=float, required=True, help="SSIM score (0-1)")
    p_log.add_argument("--verdict", choices=["PASS", "REVIEW", "FAIL", "ERROR"], default="REVIEW")
    p_log.add_argument("--notes", help="Notes about this iteration's differences")

    # status
    subparsers.add_parser("status", help="Check loop status and whether to continue")

    # report
    p_report = subparsers.add_parser("report", help="Generate final summary report")
    p_report.add_argument("--output", help="Path to save JSON report")

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
