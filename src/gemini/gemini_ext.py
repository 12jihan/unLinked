import os
from google.genai import Client


class GeminiExt:
    m_context_history = []

    def __init__(self):
        # GeminiAI Tokens
        self.api_key: str | None = os.getenv("API_KEY")
        self.client: Client = Client(api_key=self.api_key)
        self.models = list(self.client.models.list())

    def get_available_models(self):
        print("Currently available models:")
        for item in self.models:
            _item = item.display_name
            print(f"\t- {_item}")

    def test(self):
        print("This is a test")

    def get_context_history(self):
        print(f"This is the history:\n\t{self.m_context_history}")
