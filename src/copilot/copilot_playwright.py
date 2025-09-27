import asyncio
import json
import os

from dotenv import load_dotenv
from playwright.async_api import async_playwright

home_directory = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_directory, ".secrets", "copilot.env"))

chrome_path = (
    "/usr/bin/google-chrome"  # ou "/usr/bin/chromium" dependendo da instalação
)
user_data_dir = f"{home_directory}/.copiot_api/playwright-profile"  # Altere para o diretório desejado


async def get_cookies():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            executable_path=chrome_path,
            args=[
                "--no-sandbox"
            ],  # "no-sandbox" pode ser necessário em alguns ambientes Linux
        )
        page = await context.new_page()
        response = await page.goto("https://github.com/login")
        if response.url == "https://github.com/login":
            # Preencha login e senha (NUNCA exponha credenciais em código real)
            await page.fill("input#login_field", os.getenv("USERNAME"))
            await page.fill("input#password", os.getenv("PASSWORD"))
            await page.click('input[name="commit"]')

        await page.wait_for_url("https://github.com/")
        response = await page.goto("https://github.com/copilot")
        await page.wait_for_url("https://github.com/copilot")

        # Pegue os cookies
        cookies = await context.cookies()
        with open(
            f"{home_directory}/.secrets/copilot_cookies.json", "w", encoding="utf-8"
        ) as f:
            json.dump(cookies, f)
        await context.close()


if __name__ == "__main__":
    asyncio.run(get_cookies())
