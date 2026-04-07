#!/usr/bin/env python3
"""
SSIM Comparison Script
Compares two images (Figma design screenshot vs rendered component screenshot)
and returns a similarity score and visual diff analysis.

Usage:
  python compare_ssim.py <figma_screenshot> <component_screenshot> [--output-diff output.jpg]

Output:
  JSON with:
    - ssim_score: float (0-1)
    - is_match: bool (score >= 0.95)
    - diff_regions: list of areas with differences
    - verdict: "PASS" | "REVIEW" | "FAIL"
"""

import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass

try:
    import cv2
    import numpy as np
    from skimage.metrics import structural_similarity as ssim
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install opencv-python scikit-image numpy")
    sys.exit(1)


@dataclass
class ComparisonResult:
    ssim_score: float
    is_match: bool
    verdict: str
    diff_regions: list
    message: str

    def to_dict(self):
        return {
            "ssim_score": round(self.ssim_score, 4),
            "is_match": self.is_match,
            "verdict": self.verdict,
            "diff_regions": self.diff_regions,
            "message": self.message,
        }


def load_and_prepare_images(img1_path: str, img2_path: str):
    """Load and normalize images for comparison."""
    img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)

    if img1 is None:
        raise FileNotFoundError(f"Could not load image: {img1_path}")
    if img2 is None:
        raise FileNotFoundError(f"Could not load image: {img2_path}")

    # Resize to match if dimensions differ
    if img1.shape != img2.shape:
        h, w = max(img1.shape[0], img2.shape[0]), max(img1.shape[1], img2.shape[1])
        img1_resized = np.zeros((h, w, 3), dtype=img1.dtype)
        img2_resized = np.zeros((h, w, 3), dtype=img2.dtype)
        img1_resized[: img1.shape[0], : img1.shape[1]] = img1
        img2_resized[: img2.shape[0], : img2.shape[1]] = img2
        img1, img2 = img1_resized, img2_resized

    # Convert to grayscale for SSIM
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    return img1, img2, gray1, gray2


def compute_ssim(gray1, gray2):
    """Compute SSIM score and diff map."""
    score, diff_map = ssim(gray1, gray2, full=True)
    diff_map = (diff_map * 255).astype("uint8")
    return score, diff_map


def find_diff_regions(diff_map, threshold=200):
    """Find regions with significant differences."""
    _, binary = cv2.threshold(diff_map, threshold, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        if area > 50:  # Filter out noise (small regions)
            regions.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "area": int(area),
                }
            )

    # Sort by area (largest first)
    regions.sort(key=lambda r: r["area"], reverse=True)
    return regions[:5]  # Return top 5 regions


def generate_verdict(score: float):
    """Generate verdict based on score."""
    if score >= 0.95:
        return "PASS"
    elif score >= 0.90:
        return "REVIEW"
    else:
        return "FAIL"


def create_visual_diff(img_color, diff_map, output_path: str = None):
    """Create a visual diff (overlay of differences on original image)."""
    # Create colored diff overlay
    overlay = img_color.copy()
    diff_colored = cv2.applyColorMap(diff_map, cv2.COLORMAP_JET)

    # Blend
    result = cv2.addWeighted(overlay, 0.7, diff_colored, 0.3, 0)

    if output_path:
        cv2.imwrite(output_path, result)
        print(f"Visual diff saved to: {output_path}")

    return result


def compare(
    figma_path: str, component_path: str, output_diff: str = None
) -> ComparisonResult:
    """Main comparison function."""
    try:
        img1, img2, gray1, gray2 = load_and_prepare_images(figma_path, component_path)
        score, diff_map = compute_ssim(gray1, gray2)
        regions = find_diff_regions(diff_map)
        verdict = generate_verdict(score)

        # Generate visual diff if requested
        if output_diff:
            create_visual_diff(img1, diff_map, output_diff)

        message = f"SSIM: {score:.4f} ({verdict})"
        if regions:
            message += f" | {len(regions)} diff region(s)"

        return ComparisonResult(
            ssim_score=score,
            is_match=score >= 0.95,
            verdict=verdict,
            diff_regions=regions,
            message=message,
        )

    except Exception as e:
        return ComparisonResult(
            ssim_score=0.0,
            is_match=False,
            verdict="ERROR",
            diff_regions=[],
            message=f"Error during comparison: {str(e)}",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Compare Figma design vs rendered component using SSIM"
    )
    parser.add_argument("figma_screenshot", help="Path to Figma design screenshot")
    parser.add_argument(
        "component_screenshot", help="Path to rendered component screenshot"
    )
    parser.add_argument(
        "--output-diff", help="Path to save visual diff image", default=None
    )
    parser.add_argument("--json", help="Output as JSON", action="store_true")

    args = parser.parse_args()

    result = compare(args.figma_screenshot, args.component_screenshot, args.output_diff)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(f"Figma vs Component Comparison")
        print(f"SSIM Score: {result.ssim_score:.4f}")
        print(f"Verdict: {result.verdict}")
        print(f"Match (>= 0.95): {'✓ YES' if result.is_match else '✗ NO'}")
        if result.diff_regions:
            print(f"\nDifference Regions ({len(result.diff_regions)}):")
            for i, region in enumerate(result.diff_regions, 1):
                print(
                    f"  {i}. Location: ({region['x']}, {region['y']}) | Size: {region['width']}×{region['height']}"
                )


if __name__ == "__main__":
    main()
