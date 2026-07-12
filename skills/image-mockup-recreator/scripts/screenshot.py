#!/usr/bin/env python3
"""Render an HTML file to a PNG at a fixed viewport using Playwright.

Usage:
    python screenshot.py <html_path> <output_png> --width 1600 --height 720
"""

import argparse

from playwright.sync_api import sync_playwright


def render(
    html_path: str,
    output_path: str,
    width: int,
    height: int,
    executable_path: str | None,
) -> None:
    with sync_playwright() as p:
        browser = (
            p.chromium.launch(executable_path=executable_path)
            if executable_path
            else p.chromium.launch()
        )
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(f"file://{html_path}")
        page.screenshot(path=output_path)
        browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Screenshot an HTML file at a fixed size"
    )
    parser.add_argument("html_path", help="Absolute path to the HTML file")
    parser.add_argument("output_path", help="Path to save the PNG")
    parser.add_argument(
        "--width",
        type=int,
        required=True,
        help="Viewport width in px (match target image)",
    )
    parser.add_argument(
        "--height",
        type=int,
        required=True,
        help="Viewport height in px (match target image)",
    )
    parser.add_argument(
        "--executable-path",
        default=None,
        help="Path to a system browser binary, e.g. /usr/bin/google-chrome, "
        "if the bundled Playwright browser isn't installed",
    )
    args = parser.parse_args()

    render(
        args.html_path, args.output_path, args.width, args.height, args.executable_path
    )
    print(f"Saved: {args.output_path}")


if __name__ == "__main__":
    main()
