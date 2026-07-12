#!/usr/bin/env python3
"""Overlay a pixel grid on an image."""

import argparse

from PIL import Image, ImageDraw


def add_grid(image_path, output_path, spacing=8, color="white"):
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    width, height = img.size

    for x in range(0, width, spacing):
        draw.line([(x, 0), (x, height)], fill=color)
    for y in range(0, height, spacing):
        draw.line([(0, y), (width, y)], fill=color)

    img.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Add a grid overlay to an image.")
    parser.add_argument("input", help="Path to input image")
    parser.add_argument("output", help="Path to save gridded image")
    parser.add_argument(
        "--spacing", type=int, default=8, help="Grid spacing in pixels (default: 8)"
    )
    parser.add_argument(
        "--color", default="white", help="Grid line color (default: white)"
    )
    args = parser.parse_args()

    add_grid(args.input, args.output, args.spacing, args.color)
    print(f"Saved: {args.output}")


if __name__ == "__main__":
    main()
