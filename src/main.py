import os

import requests
from dotenv import load_dotenv

from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    Modality,
)


def main():
    # load environment variables
    load_dotenv()
    dir_list: list[str] = os.listdir("./imgs")

    # LinkedIn Tokens
    access_token = os.getenv("ACCESS_TOKEN")
    api_version: str | None = os.getenv("API_VERSION")
    user_id: str | None = os.getenv("USER_ID")

    # GeminiAI Tokens
    api_key: str | None = os.getenv("API_KEY")
    chat_history_context: list = []
    client: Client = Client(api_key=api_key)
    models = list(client.models.list())

    # URL, HEADER, BODY, REQUEST
    url: str = "https://api.linkedin.com/v2/ugcPosts"
    header: dict[str, str] = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": api_version if api_version else "",
    }
    req_body = {
        "author": f"{user_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": "This is an automated test..."},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": "test media"},
                        "media": "urn:li:digitalmediaAsset:C5422AQEbc381YmIuvg",
                        "title": {"text": "This is a test"},
                    }
                ],
            },
        },
        # "visibility" an either be PUBLIC | CONNECTIONS Create ENUM LATER??
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"},
    }

    resp: requests.Response = requests.post(url=url, headers=header, json=req_body)

    if resp.status_code == 201:
        data = resp.json()
        print("Title", data["title"])
    else:
        print(f"Request failed: {resp.status_code}")
        print(f"body: {resp.json()}")

    def create_text_post():
        print("Text")


if __name__ == "__main__":
    main()
