import json
import os

import requests
from dotenv import load_dotenv

home_directory = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_directory, ".secrets", "copilot.env"))


class CopilotAPI:
    def __init__(self, thread_id="6ad571dd-f9fc-436a-8cd1-d59d9c363da7"):
        self.token = os.getenv("GITHUB_COPILOT_TOKEN")
        self.thread_id = thread_id
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "text/plain;charset=UTF-8",
            "copilot-integration-id": "copilot-chat",
            "dnt": "1",
            "origin": "https://github.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://github.com/",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "x-github-api-version": "2025-05-01",
        }
        self.headers["authorization"] = f"GitHub-Bearer {self.token}"

    def create_chat(self):
        response = requests.post(
            "https://api.individual.githubcopilot.com/github/chat/threads",
            headers=self.headers,
            data="{}",
            timeout=300,
        )
        data = response.json()
        self.thread_id = data.get("thread_id")
        return data

    def chat(self, message: str, references: list[str] = []):

        data = {
            "responseMessageID": "",
            "content": message,
            "intent": "conversation",
            "references": [],
            "context": [],
            "currentURL": "https://github.com/copilot",
            "streaming": False,
            "confirmations": [],
            "customInstructions": [],
            "model": "gpt-4.1",
            "mode": "immersive",
            "parentMessageID": "root",
            "tools": [],
            "mediaContent": [],
            "skillOptions": {"deepCodeSearch": False},
            "requestTrace": False,
        }

        if len(references) > 0:
            for ref in references:
                with open(ref, "r", encoding="utf-8") as f:
                    data["references"].append(
                        {
                            "name": os.path.basename(ref),
                            "text": f.read(),
                            "type": "thread-scoped-file",
                        }
                    )
        data = json.dumps(data)

        response = requests.post(
            f"https://api.individual.githubcopilot.com/github/chat/threads/{self.thread_id}/messages",
            params="",
            headers=self.headers,
            data=data,
            timeout=300,
        )
        data = response.json()

        return data


if __name__ == "__main__":
    api = CopilotAPI()
    # print(api.create_chat())
    print(api.chat("explique o codigo",["/home/ronnas/develop/personal/AI-pair-programming/src/copilot_api.py"]))  # type: ignore
