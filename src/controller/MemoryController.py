import os
from google import genai
from google.genai import Client


class MemoryController:
    def __init__(self):
        self.api_key: str | None = os.getenv("API_KEY")
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "dbname": "vectordb",
            "user": "postgres",
            "pass": "postgres",
        }
        db_url = "postgresql://postgres:postgres@localhost:5432/vectordb"
        gemini = Client(api_key=self.api_key)
        embeded_dim = 768

    def test(self):
        print("test")
        pass
