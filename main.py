import requests
import os
from dotenv import load_dotenv


def main():
    # load environment variables
    load_dotenv()
    access_token = os.getenv("ACCESS_TOKEN")
    api_version: str | None = os.getenv("API_VERSION")

    # POST to this URL
    url: str = "https://api.linkedin.com/v2/ugcPosts"
    header: dict[str, str] = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
        "LinkedIn-Version": api_version if api_version else "",
    }
    req_body = {
        "author": "urn:li:person:8675309",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": "Hello World! This is my first Share on LinkedIn!"
                },
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    resp: requests.Response = requests.post(url=url, headers=header, json=req_body)

    if resp.status_code == 200:
        data = resp.json()
        print("Title", data["title"])
    else:
        print(f"Request failed: {resp.status_code}")


if __name__ == "__main__":
    main()
