#!/usr/bin/env python3
"""
Color Diff Script
Compares average color per region between two images. SSIM is
structure/luminance-focused and can miss a wrong palette (e.g. #3B82F6
vs #2563EB score high on SSIM but read as visually wrong). This script
flags regions whose average color diverges beyond a threshold.

Usage:
  python compare_color.py <target> <render> --regions '[{"x":0,"y":0,"width":100,"height":40,"label":"header"}]'
  python compare_color.py <target> <render> --grid 4x4   # auto-split into a grid instead of named regions

Output:
  JSON list of {label, target_hex, render_hex, delta_e_approx, flagged}
"""

import sys
import json
import argparse

try:
    import cv2
    import numpy as np
except ImportError:
    print("ERROR: Missing dependencies. Install with:")
    print("  pip install opencv-python numpy")
    sys.exit(1)

FLAG_THRESHOLD = 30  # approx perceptual distance; tune per project


def to_hex(bgr):
    b, g, r = [int(c) for c in bgr]
    return f"#{r:02X}{g:02X}{b:02X}"


def avg_color(img, x, y, w, h):
    crop = img[y : y + h, x : x + w]
    if crop.size == 0:
        return (0, 0, 0)
    return crop.reshape(-1, 3).mean(axis=0)


def color_distance(c1, c2):
    return float(np.linalg.norm(np.array(c1) - np.array(c2)))


def build_grid_regions(width, height, cols, rows):
    regions = []
    cw, ch = width // cols, height // rows
    for r in range(rows):
        for c in range(cols):
            regions.append(
                {
                    "x": c * cw,
                    "y": r * ch,
                    "width": cw,
                    "height": ch,
                    "label": f"grid_{r}_{c}",
                }
            )
    return regions


def compare_colors(target_path, render_path, regions):
    target = cv2.imread(target_path, cv2.IMREAD_COLOR)
    render = cv2.imread(render_path, cv2.IMREAD_COLOR)
    if target is None:
        raise FileNotFoundError(f"Could not load image: {target_path}")
    if render is None:
        raise FileNotFoundError(f"Could not load image: {render_path}")

    results = []
    for region in regions:
        x, y, w, h = region["x"], region["y"], region["width"], region["height"]
        t_color = avg_color(target, x, y, w, h)
        r_color = avg_color(render, x, y, w, h)
        dist = color_distance(t_color, r_color)
        results.append(
            {
                "label": region.get("label", f"({x},{y})"),
                "x": x,
                "y": y,
                "width": w,
                "height": h,
                "target_hex": to_hex(t_color),
                "render_hex": to_hex(r_color),
                "distance": round(dist, 1),
                "flagged": dist > FLAG_THRESHOLD,
            }
        )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Compare average color per region between target and render"
    )
    parser.add_argument("target", help="Path to target/reference image")
    parser.add_argument("render", help="Path to rendered screenshot")
    parser.add_argument(
        "--regions", help="JSON list of {x,y,width,height,label} regions", default=None
    )
    parser.add_argument("--grid", help="Auto-grid as COLSxROWS, e.g. 4x4", default=None)
    parser.add_argument("--json", help="Output as JSON", action="store_true")
    args = parser.parse_args()

    if args.regions:
        regions = json.loads(args.regions)
    elif args.grid:
        cols, rows = (int(v) for v in args.grid.lower().split("x"))
        img = cv2.imread(args.target, cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(f"Could not load image: {args.target}")
        h, w = img.shape[:2]
        regions = build_grid_regions(w, h, cols, rows)
    else:
        print("ERROR: pass --regions or --grid")
        sys.exit(1)

    results = compare_colors(args.target, args.render, regions)
    flagged = [r for r in results if r["flagged"]]

    if args.json:
        print(json.dumps({"results": results, "flagged_count": len(flagged)}, indent=2))
    else:
        print(f"Color comparison: {len(results)} region(s), {len(flagged)} flagged")
        for r in results:
            mark = "⚠" if r["flagged"] else " "
            print(
                f"  {mark} {r['label']:<16} target={r['target_hex']} render={r['render_hex']} dist={r['distance']}"
            )


if __name__ == "__main__":
    main()
