#!/usr/bin/env python3
"""Red/green channel overlay diff between target and render.

Target grayscale goes into the green channel, render grayscale goes into
the red channel. Where both agree the pixel reads yellow; pure green means
the target has something the render is missing (or it's offset away from
there); pure red means the render has something the target doesn't (or
it's offset into there). Unlike the SSIM heatmap (blurred, thresholded,
bbox-summarized) this shows raw per-pixel offset direction at a glance —
better for spotting "this element is N px too far left/right/big/small"
than for getting a single similarity number.
"""

import argparse

import numpy as np
from PIL import Image


def overlay(target_path: str, render_path: str, output_path: str) -> None:
    target = Image.open(target_path).convert("L")
    render = Image.open(render_path).convert("L")

    if target.size != render.size:
        render = render.resize(target.size)

    t_arr = np.array(target)
    r_arr = np.array(render)

    h, w = t_arr.shape
    out = np.zeros((h, w, 3), dtype=np.uint8)
    out[:, :, 0] = r_arr  # red = render
    out[:, :, 1] = t_arr  # green = target
    out[:, :, 2] = 0

    Image.fromarray(out).save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Red/green overlay diff: green=target-only, red=render-only, yellow=match"
    )
    parser.add_argument("target", help="Path to target reference image")
    parser.add_argument("render", help="Path to rendered screenshot")
    parser.add_argument("output", help="Path to save the overlay PNG")
    args = parser.parse_args()

    overlay(args.target, args.render, args.output)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
