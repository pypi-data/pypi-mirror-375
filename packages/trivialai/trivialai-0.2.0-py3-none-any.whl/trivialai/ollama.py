import re

import requests

from .filesystem import FilesystemMixin
from .llm import LLMMixin, LLMResult


class Ollama(LLMMixin, FilesystemMixin):
    def __init__(self, model, ollama_server=None):
        if ollama_server is None:
            ollama_server = "http://localhost:11434"

        self.model = model
        self.server = ollama_server.rstrip("/")

    def generate(self, system, prompt, images=None):
        data = {
            "model": self.model,
            "stream": False,
            "prompt": f"SYSTEM PROMPT: {system} PROMPT: {prompt}",
        }
        if images is not None:
            data["images"] = images
        res = requests.post(f"{self.server}/api/generate", json=data)

        if res.status_code == 200:
            resp = res.json()["response"].strip()
            pattern = r"<think>.*?</think>"
            think_match = re.search(pattern, resp, re.DOTALL)
            if not think_match:
                return LLMResult(res, resp, None)

            matched = think_match.group(0)
            scratchpad = matched[7:-8].strip()
            content = resp.replace(matched, "").strip()
            return LLMResult(res, content, scratchpad)
        return LLMResult(res, None, None)
