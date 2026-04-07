# Reference: Browser Automation with Playwright/Puppeteer

This document describes how to take screenshots of rendered components for SSIM comparison.

## Using Playwright (Python)

```python
# Install: pip install playwright
# Setup: playwright install chromium

from playwright.sync_api import sync_playwright
from pathlib import Path


def take_screenshot(component_html: str, output_path: str, viewport_width: int = 1280, viewport_height: int = 720):
    """
    Render HTML component and take screenshot.

    Args:
        component_html: Full HTML markup or file path
        output_path: Where to save screenshot PNG
        viewport_width, viewport_height: Screenshot dimensions
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": viewport_width, "height": viewport_height}
        )
        page = context.new_page()

        # Load content (either HTML string or file)
        if component_html.startswith("<"):
            page.set_content(component_html)
        else:
            page.goto(f"file://{Path(component_html).absolute()}")

        # Wait for rendering
        page.wait_for_load_state("networkidle")

        # Take screenshot
        page.screenshot(path=output_path)
        browser.close()

        print(f"Screenshot saved: {output_path}")


# Example usage
if __name__ == "__main__":
    html = """
    <html>
    <head>
        <style>
            body { margin: 0; padding: 0; background: white; }
            .card { width: 320px; padding: 20px; background: white;
                    border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    font-family: sans-serif; }
            .card h2 { margin: 0 0 10px; font-size: 20px; color: #1a1a1a; }
            .card p { margin: 0 0 15px; color: #666; font-size: 14px; }
            .btn { background: #2563eb; color: white; border: none;
                   padding: 10px 16px; border-radius: 4px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Product Card</h2>
            <p>Beautiful responsive card component matching Figma design.</p>
            <button class="btn">Learn More</button>
        </div>
    </body>
    </html>
    """

    take_screenshot(html, "screenshot.png")
```

## Using Puppeteer (Node.js)

```javascript
// Install: npm install puppeteer

const puppeteer = require("puppeteer");
const fs = require("fs");

async function takeScreenshot(
  componentPath,
  outputPath,
  width = 1280,
  height = 720
) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  await page.setViewport({ width, height });
  await page.goto(`file://${require("path").resolve(componentPath)}`, {
    waitUntil: "networkidle0"
  });

  await page.screenshot({ path: outputPath });
  await browser.close();

  console.log(`Screenshot saved: ${outputPath}`);
}

// Usage
takeScreenshot("./card.html", "./screenshot.png");
```

## Using Chrome DevTools Protocol (MCP)

If your setup includes a Chrome MCP server, you can use it directly:

```python
# This would be called from the main skill workflow
# via the available MCPs in your environment

result = mcp_chrome.take_screenshot(
    url="file:///path/to/component.html",
    output="screenshot.png",
    viewport={"width": 1280, "height": 720}
)
```

## Tips for Consistent Screenshots

1. **Set viewport size** to match Figma export (usually 1280×720 or custom)
2. **Use a white background** to match Figma canvas
3. **Wait for rendering** with `waitForLoadState()` or `waitForNetworkIdle()`
4. **Disable animations** in CSS during testing (or wait for completion)
5. **Match DPI/zoom** - use 1x (100%) zoom to avoid scaling artifacts
6. **Use system fonts** consistently, or web fonts (Google Fonts) for reproducibility

## Automating Screenshots in the Loop

```python
def screenshot_for_iteration(component_file: str, iteration: int, output_dir: str):
    """Generate timestamped screenshot for each iteration."""
    output_path = f"{output_dir}/iteration_{iteration:02d}.png"
    take_screenshot(component_file, output_path)
    return output_path
```
