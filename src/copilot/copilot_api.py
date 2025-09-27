import asyncio
import json
import logging
import os

import requests
from copilot_playwright import get_cookies
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

home_directory = os.path.expanduser("~")
load_dotenv(dotenv_path=os.path.join(home_directory, ".secrets", "copilot.env"))


class CopilotAPI:
    def __init__(self, thread_id="6ad571dd-f9fc-436a-8cd1-d59d9c363da7"):
        logging.info(f"CopilotAPI.__init__ called with thread_id={thread_id}")
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
        logging.info("CopilotAPI.__init__ completed")

    def get_token(self):
        logging.info("CopilotAPI.get_token called")
        with open(
            f"{home_directory}/.secrets/copilot_token.json", "r", encoding="utf-8"
        ) as f:
            self.token = json.load(f).get("token")
        logging.info("CopilotAPI.get_token completed")

    def auth(self):
        logging.info("CopilotAPI.auth called")
        # Aguarda a função assíncrona get_cookies
        asyncio.run(get_cookies())
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
        logging.info("CopilotAPI.auth completed")

    def create_chat(self):
        logging.info("CopilotAPI.create_chat called")
        response = requests.post(
            "https://api.individual.githubcopilot.com/github/chat/threads",
            headers=self.headers,
            data="{}",
            timeout=300,
        )
        if response.status_code == 401:
            self.auth()
            self.get_token()
            self.headers["authorization"] = f"GitHub-Bearer {self.token}"
            response = requests.post(
                "https://api.individual.githubcopilot.com/github/chat/threads",
                headers=self.headers,
                data="{}",
                timeout=300,
            )
        data = response.json()
        self.thread_id = data.get("thread_id")
        logging.info(f"CopilotAPI.create_chat response: {data}")
        return data

    def _handle_streaming_response(self, response):
        """
        Handle streaming response from GitHub Copilot API.

        Args:
            response: requests.Response object with streaming enabled

        Returns:
            Generator yielding streaming chunks or complete response data
        """
        logging.info("CopilotAPI._handle_streaming_response called")
        try:
            full_content = ""
            chunks = []

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
                        if "content" in chunk_data:
                            content = chunk_data.get("content", "")
                            full_content += content
                            yield {
                                "type": "chunk",
                                "content": content,
                                "full_content": full_content,
                                "raw_data": chunk_data,
                            }
                        elif "choices" in chunk_data:
                            # Handle OpenAI-style streaming format
                            for choice in chunk_data["choices"]:
                                if "delta" in choice and "content" in choice["delta"]:
                                    content = choice["delta"]["content"]
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
        logging.info("CopilotAPI._handle_streaming_response completed")

    def chat(self, message: str, references: list[str] = None, streaming: bool = False):
        logging.info(
            f"CopilotAPI.chat called with message='{message[:50]}', references={references}, streaming={streaming}"
        )
        logging.debug(
            f"CopilotAPI.chat called with message='{message}', references={references}, streaming={streaming}"
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
            self.auth()
            self.get_token()
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
            logging.info("CopilotAPI.chat returning streaming response")
            return self._handle_streaming_response(response)
        else:
            response_data = response.json()
            logging.info(f"CopilotAPI.chat response: {str(response_data)[:200]}")
            logging.debug(f"CopilotAPI.chat response: {str(response_data)}")
            return response_data

    def chat_complete(
        self, message: str, references: list[str] = None, streaming: bool = False
    ):
        """
        Chat method that returns complete response, even for streaming requests.

        Args:
            message: The message to send
            references: List of file paths to include as references
            streaming: Whether to use streaming API

        Returns:
            dict: Complete response data with full content
        """
        logging.info(
            f"CopilotAPI.chat_complete called with message='{message[:50]}', references={references}, streaming={streaming}"
        )
        logging.debug(
            f"CopilotAPI.chat_complete called with message='{message}', references={references}, streaming={streaming}"
        )
        if references is None:
            references = []

        if not streaming:
            result = self.chat(message, references, streaming)
            logging.info(f"CopilotAPI.chat_complete result: {str(result)[:200]}")
            logging.info(f"CopilotAPI.chat_complete result: {str(result)}")
            return result

        # Handle streaming response by collecting all chunks
        full_content = ""
        metadata = []

        for chunk in self.chat(message, references, streaming=True):
            if chunk["type"] == "chunk":
                full_content = chunk["full_content"]
            elif chunk["type"] == "complete":
                logging.info(
                    f"CopilotAPI.chat_complete streaming result: {str(chunk)[:200]}"
                )
                return {
                    "content": chunk["full_content"],
                    "streaming": True,
                    "total_chunks": chunk["total_chunks"],
                    "raw_chunks": chunk["raw_chunks"],
                }
            elif chunk["type"] == "metadata":
                metadata.append(chunk["raw_data"])
            elif chunk["type"] == "error":
                logging.error(f"CopilotAPI.chat_complete error: {chunk['error']}")
                return {
                    "error": chunk["error"],
                    "content": chunk["full_content"],
                    "streaming": True,
                }

        # Fallback return
        logging.info(
            f"CopilotAPI.chat_complete fallback result: {str(full_content)[:200]}"
        )
        return {
            "content": full_content,
            "streaming": True,
            "metadata": metadata,
        }


if __name__ == "__main__":
    logging.info("CopilotAPI main execution started")
    api = CopilotAPI()
    # api.auth()
    # print(api.create_chat())

    # Example 1: Non-streaming chat
    print("=== Non-streaming response ===")
    response = api.chat(
        "explique o codigo",
        [
            "/home/ronnas/develop/personal/AI-pair-programming/src/copilot/copilot_api.py"
        ],
        streaming=False,
    )
    print(response)

    # Example 2: Streaming chat with real-time processing
    print("\n=== Streaming response (real-time) ===")
    for chunk in api.chat(
        "explique brevemente o codigo",
        [
            "/home/ronnas/develop/personal/AI-pair-programming/src/copilot/copilot_api.py"
        ],
        streaming=True,
    ):
        if chunk["type"] == "chunk":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "complete":
            print(f"\n\n[Stream completed - {chunk['total_chunks']} chunks received]")
            break
        elif chunk["type"] == "error":
            print(f"\n[Error: {chunk['error']}]")
            break

    # Example 3: Streaming chat with complete response
    print("\n=== Streaming response (complete) ===")
    complete_response = api.chat_complete(
        "resuma o codigo em uma frase",
        [
            "/home/ronnas/develop/personal/AI-pair-programming/src/copilot/copilot_api.py"
        ],
        streaming=True,
    )
    print(complete_response)
    logging.info("CopilotAPI main execution completed")
