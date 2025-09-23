import os
import json
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

home_directory = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_directory, ".secrets", "copilot.env"))

chrome_path = (
    "/usr/bin/google-chrome"  # ou "/usr/bin/chromium" dependendo da instalação
)
user_data_dir = f"{home_directory}/.copiot_api/playwright-profile"  # Altere para o diretório desejado


def get_cookies():
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            executable_path=chrome_path,
            args=[
                "--no-sandbox"
            ],  # "no-sandbox" pode ser necessário em alguns ambientes Linux
        )
        page = context.new_page()
        response = page.goto("https://github.com/login")
        if response.url == "https://github.com/login":
            # Preencha login e senha (NUNCA exponha credenciais em código real)
            page.fill("input#login_field", os.getenv("USERNAME"))
            page.fill("input#password", os.getenv("PASSWORD"))
            page.click('input[name="commit"]')

        page.wait_for_url("https://github.com/")
        response = page.goto("https://github.com/copilot")
        page.wait_for_url("https://github.com/copilot")

        # Pegue os cookies
        cookies = context.cookies()
        with open(f"{home_directory}/.secrets/copilot_cookies.json", "w",encoding='utf-8') as f:
            json.dump(cookies, f)
        context.close()


if __name__ == "__main__":
    get_cookies()
