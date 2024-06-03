import requests, json
from typing import Dict, List

class ConversationOver(Exception):
    pass


class ChatModel:
    claude = "claude-3-haiku-20240307"
    gpt = "gpt-3.5-turbo-0125"


class ChatInstance:
    def __init__(self, model: str):
        self.base = "https://duckduckgo.com/duckchat/v1%s"
        self.vqd: str = requests.get(
            self.base % "/status", headers={"x-vqd-accept": "1"}
        ).headers["x-vqd-4"]
        self.model: str = model
        self.transcript: List[Dict[str, str]] = []

    def chat(self, message: str) -> str:
        self.transcript.append({"role": "user", "content": message})
        res = requests.post(
            self.base % "/chat",
            headers={"x-vqd-4": self.vqd},
            json={"model": self.model, "messages": self.transcript},
        )
        self.vqd = res.headers["x-vqd-4"]

        out: str = ""
        for item in (i.removeprefix("data: ") for i in res.text.split("\n\n")):
            if item.startswith("[DONE]"):
                if item.endswith("[LIMIT_CONVERSATION]"):
                    raise ConversationOver
                break
            out += json.loads(item).get("message", "")

        self.transcript.append({"role": "assistant", "content": out})
        return out


if __name__ == "__main__":
    import readline

    chat = ChatInstance(ChatModel.claude)
    while True:
        print(chat.chat(input("> ")))
