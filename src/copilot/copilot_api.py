import asyncio
import json
import logging
import os

import requests
from copilot_playwright import get_cookies
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/copilot_ollama_proxy.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

home_directory = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_directory, ".secrets", "copilot.env"))


class CopilotAPI:
    def __init__(self, thread_id="6ad571dd-f9fc-436a-8cd1-d59d9c363da7"):
        logger.info(f"CopilotAPI.__init__ called with thread_id={thread_id}")
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
        self.get_token()
        self.headers["authorization"] = f"GitHub-Bearer {self.token}"
        logger.info("CopilotAPI.__init__ completed")

    def get_token(self):
        logger.info("CopilotAPI.get_token called")
        with open(
            f"{home_directory}/.secrets/copilot_token.json", "r", encoding="utf-8"
        ) as f:
            self.token = json.load(f).get("token")
        logger.info("CopilotAPI.get_token completed")

    async def auth(self):
        logger.info("CopilotAPI.auth called")
        # Aguarda a função assíncrona get_cookies
        await get_cookies()
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "content-type": "application/json",
            "dnt": "1",
            "github-verified-fetch": "true",
            "origin": "https://github.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        }
        with open(
            f"{home_directory}/.secrets/copilot_cookies.json", "r", encoding="utf-8"
        ) as f:
            list_cookies = json.load(f)
            cookies = dict()
            for cookie in list_cookies:
                cookies[cookie["name"]] = cookie["value"]
            response = requests.post(
                "https://github.com/github-copilot/chat/token",
                cookies=cookies,
                headers=headers,
                timeout=300,
            )
            with open(
                f"{home_directory}/.secrets/copilot_token.json", "w", encoding="utf-8"
            ) as f:
                json.dump(response.json(), f, indent=4)
        self.get_token()
        logger.info("CopilotAPI.auth completed")
        return self.token

    async def create_chat(self):
        logger.info("CopilotAPI.create_chat called")
        response = requests.post(
            "https://api.individual.githubcopilot.com/github/chat/threads",
            headers=self.headers,
            data="{}",
            timeout=300,
        )
        if response.status_code == 401:
            await self.auth()
            self.headers["authorization"] = f"GitHub-Bearer {self.token}"
            response = requests.post(
                "https://api.individual.githubcopilot.com/github/chat/threads",
                headers=self.headers,
                data="{}",
                timeout=300,
            )
        data = response.json()
        self.thread_id = data.get("thread_id")
        logger.info(f"CopilotAPI.create_chat response: {data}")
        return data

    def _handle_streaming_response(self, response):
        """
        Handle streaming response from GitHub Copilot API.

        Args:
            response: requests.Response object with streaming enabled

        Returns:
            Generator yielding streaming chunks or complete response data
        """
        logger.info("CopilotAPI._handle_streaming_response called")
        try:
            full_content = ""
            chunks = []
            response.encoding = "utf-8"
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    # Remove 'data: ' prefix if present
                    if line.startswith("data: "):
                        line = line[6:]

                    # Skip empty lines and special markers
                    if not line.strip() or line.strip() == "[DONE]":
                        continue

                    try:
                        chunk_data = json.loads(line)
                        chunks.append(chunk_data)
                        # Extract content from chunk if available
                        if "type" in chunk_data and chunk_data["type"] == "content":
                            content = chunk_data.get("body", "")
                            full_content += content
                            yield {
                                "type": "chunk",
                                "content": content,
                                "full_content": full_content,
                                "raw_data": chunk_data,
                            }
                        else:
                            # Yield other types of chunks (metadata, etc.)
                            yield {"type": "metadata", "raw_data": chunk_data}

                    except json.JSONDecodeError as e:
                        # If it's not valid JSON, treat as raw text
                        full_content += line
                        yield {
                            "type": "text",
                            "content": line,
                            "full_content": full_content,
                            "error": f"JSON decode error: {str(e)}",
                        }

            # Yield final summary
            yield {
                "type": "complete",
                "full_content": full_content,
                "total_chunks": len(chunks),
                "raw_chunks": chunks,
            }

        except (
            requests.exceptions.RequestException,
            json.JSONDecodeError,
            IOError,
        ) as e:
            yield {
                "type": "error",
                "error": str(e),
                "full_content": full_content if "full_content" in locals() else "",
            }

        finally:
            response.close()
        logger.info("CopilotAPI._handle_streaming_response completed")

    async def chat(
        self, message: str, references: list[str] = None, streaming: bool = False
    ):
        logger.info(
            f"CopilotAPI.chat called with message='{message[:50]}', references={references}, streaming={streaming}"
        )
        logger.debug(
            f"CopilotAPI.chat called with message='{message}', references={references}, streaming={streaming}"
        )
        logger.info(
            f"CopilotAPI.chat called with '{len(message)}' characters message. approximately {int(len(message)/4)} tokens"
        )
        if references is None:
            references = []

        data = {
            "responseMessageID": "",
            "content": message,
            "intent": "conversation",
            "references": [],
            "context": [],
            "currentURL": "https://github.com/copilot",
            "streaming": streaming,
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
            logger.info(f"CopilotAPI.chat including references: {references}")
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
            stream=streaming,
        )

        if response.status_code == 401:
            await self.auth()
            self.headers["authorization"] = f"GitHub-Bearer {self.token}"
            # Retry the request after authentication
            response = requests.post(
                f"https://api.individual.githubcopilot.com/github/chat/threads/{self.thread_id}/messages",
                params="",
                headers=self.headers,
                data=data,
                timeout=300,
                stream=streaming,
            )

        if streaming:
            logger.info("CopilotAPI.chat returning streaming response")
            return self._handle_streaming_response(response)
        else:
            response_data = response.json()
            logger.info(f"CopilotAPI.chat response: {str(response_data)[:200]}")
            logger.debug(f"CopilotAPI.chat response: {str(response_data)}")
            return response_data


if __name__ == "__main__":
    logger.info("CopilotAPI main execution started")
    api = CopilotAPI()
    asyncio.run(api.auth())
    # print(api.create_chat())

    # # Example 1: Non-streaming chat
    # print("=== Non-streaming response ===")
    # response = api.chat(
    #     "explique o codigo",
    #     [
    #         "/home/ronnas/develop/personal/AI-pair-programming/src/copilot/copilot_api.py"
    #     ],
    #     streaming=False,
    # )
    # print(response)

    # # Example 2: Streaming chat with real-time processing
    # print("\n=== Streaming response (real-time) ===")
    # for chunk in api.chat(
    #     "explique brevemente o codigo",
    #     [
    #         "/home/ronnas/develop/personal/AI-pair-programming/src/copilot/copilot_api.py"
    #     ],
    #     streaming=True,
    # ):
    #     if chunk["type"] == "chunk":
    #         print(chunk["content"], end="", flush=True)
    #     elif chunk["type"] == "complete":
    #         print(f"\n\n[Stream completed - {chunk['total_chunks']} chunks received]")
    #         break
    #     elif chunk["type"] == "error":
    #         print(f"\n[Error: {chunk['error']}]")
    #         break
    # logger.info("CopilotAPI main execution completed")
