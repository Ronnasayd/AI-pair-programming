#!/usr/bin/env python3
"""
Agentic Loop Controller
Manages the iteration loop for refining component code until SSIM >= 0.95.

Usage:
  python agentic_loop.py <component_code_path> <figma_screenshot_path> --framework react --max-iterations 10
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


class AgenticLoopController:
    def __init__(
        self, framework: str, max_iterations: int = 10, ssim_threshold: float = 0.95
    ):
        self.framework = framework
        self.max_iterations = max_iterations
        self.ssim_threshold = ssim_threshold
        self.iteration = 0
        self.history = []

    def log_iteration(
        self,
        iteration_num: int,
        ssim_score: float,
        verdict: str,
        diff_regions: list,
        notes: str = "",
    ):
        """Log iteration result."""
        self.history.append(
            {
                "iteration": iteration_num,
                "timestamp": datetime.now().isoformat(),
                "ssim_score": ssim_score,
                "verdict": verdict,
                "diff_regions": diff_regions,
                "notes": notes,
            }
        )

    def should_continue(self, ssim_score: float) -> bool:
        """Determine if loop should continue."""
        if ssim_score >= self.ssim_threshold:
            return False
        if self.iteration >= self.max_iterations:
            return False
        return True

    def detect_convergence(self) -> tuple[bool, str]:
        """Detect if score is stalling (no progress)."""
        if len(self.history) < 3:
            return False, ""

        recent = [h["ssim_score"] for h in self.history[-3:]]
        if recent[-1] == recent[-2] == recent[-3]:
            return True, "Score stalled: no improvement in last 3 iterations"

        diffs = [recent[i] - recent[i - 1] for i in range(1, len(recent))]
        if all(d < 0.001 for d in diffs):
            return True, "Score converging slowly: improvements < 0.001"

        return False, ""

    def get_summary(self) -> dict:
        """Generate summary of the loop run."""
        if not self.history:
            return {"status": "no_iterations"}

        scores = [h["ssim_score"] for h in self.history]
        return {
            "total_iterations": len(self.history),
            "final_score": scores[-1],
            "initial_score": scores[0],
            "best_score": max(scores),
            "improvement": max(scores) - scores[0],
            "converged": scores[-1] >= self.ssim_threshold,
            "history": self.history,
        }

    def save_report(self, output_path: str):
        """Save loop report to JSON."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(self.get_summary(), f, indent=2)
        print(f"Loop report saved to: {output_path}")


def run_agentic_loop(
    component_code_path: str,
    figma_screenshot_path: str,
    framework: str = "react",
    max_iterations: int = 10,
):
    """
    Main agentic loop runner.

    This would be called by the main skill workflow. In practice, this would be
    orchestrated by the Claude agent running the skill, which would:
    1. Call this to initialize the loop
    2. Generate code
    3. Take screenshot
    4. Call compare_ssim.py
    5. Refine code if needed
    6. Loop back
    """
    controller = AgenticLoopController(
        framework=framework, max_iterations=max_iterations
    )
    print(f"Starting agentic loop: {framework} component")
    print(f"Target: SSIM >= 0.95 (max {max_iterations} iterations)")
    print(f"Component: {component_code_path}")
    print(f"Figma ref: {figma_screenshot_path}")
    print("-" * 60)

    # This is a placeholder - the actual loop is orchestrated by the skill
    print("\nThis controller would be called from the main skill workflow.")
    print("Current iteration would be tracked and reported to the user.")

    return controller


def main():
    parser = argparse.ArgumentParser(
        description="Agentic loop controller for Figma-to-code refinement"
    )
    parser.add_argument("component_code", help="Path to component code file")
    parser.add_argument("figma_screenshot", help="Path to Figma design screenshot")
    parser.add_argument(
        "--framework", default="react", help="Target framework (react, vue, vanilla)"
    )
    parser.add_argument(
        "--max-iterations", type=int, default=10, help="Maximum iterations"
    )
    parser.add_argument("--output-report", help="Path to save loop report JSON")

    args = parser.parse_args()

    controller = run_agentic_loop(
        args.component_code,
        args.figma_screenshot,
        framework=args.framework,
        max_iterations=args.max_iterations,
    )

    if args.output_report:
        controller.save_report(args.output_report)


if __name__ == "__main__":
    main()
