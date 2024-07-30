"""
Simple Python client for ddg.gg/chat
"""

from typing import Dict, List
import requests, json

class ConversationOver(Exception):
    """Raised when the conversation limit is reached."""
    pass


class ChatModel:
    """Available models for chat."""
    claude = "claude-3-haiku-20240307"
    gpt = "gpt-4o-mini"
    llama = "meta-llama/Llama-3-70b-chat-hf"
    mistral = "mistralai/Mixtral-8x7B-Instruct-v0.1"


class ChatInstance:
    def __init__(self, model: str):
        self.base = "https://duckduckgo.com/duckchat/v1%s"
        self.vqd: str = requests.get(
            self.base % "/status",
            headers={"x-vqd-accept": "1"},
            timeout=5
        ).headers["x-vqd-4"]
        self.model: str = model
        self.transcript: List[Dict[str, str]] = []

    def chat(self, message: str) -> str:
        """
        Chat with the chosen model. Takes a message and returns the model's response.
        """
        self.transcript.append({"role": "user", "content": message})
        res = requests.post(
            self.base % "/chat",
            headers={"x-vqd-4": self.vqd},
            timeout=5,
            json={"model": self.model, "messages": self.transcript},
        )
        self.vqd = res.headers["x-vqd-4"]

        out: str = ""
        for item in (i.removeprefix("data: ") for i in res.text.split("\n\n")):
            if item.startswith("[DONE]"):
                if item.endswith("[LIMIT_CONVERSATION]"):
                    raise ConversationOver
                break
            out += json.loads(item).get("message", "").encode("latin-1").decode()

        self.transcript.append({"role": "assistant", "content": out})
        return out


if __name__ == "__main__":
    import readline

    chat = ChatInstance(ChatModel.gpt)
    while True:
        print(chat.chat(input("> ")))
