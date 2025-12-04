from gemini.gemini_ext import GeminiExt
from dotenv import load_dotenv

running = True


def main():
    # add vars to the env
    load_dotenv()

    # URL, HEADER, BODY, REQUEST
    # url: str = "https://api.linkedin.com/v2/ugcPosts"
    # header: dict[str, str] = {
    #     "Authorization": f"Bearer {access_token}",
    #     "X-Restli-Protocol-Version": "2.0.0",
    #     "Content-Type": "application/json",
    #     "LinkedIn-Version": api_version if api_version else "",
    # }

    # req_body = {
    #     "author": f"{user_id}",
    #     "lifecycleState": "PUBLISHED",
    #     "specificContent": {
    #         "com.linkedin.ugc.ShareContent": {
    #             "shareCommentary": {"text": "This is an automated test..."},
    #             "shareMediaCategory": "IMAGE",
    #             "media": [
    #                 {
    #                     "status": "READY",
    #                     "description": {"text": "test media"},
    #                     "media": "urn:li:digitalmediaAsset:C5422AQEbc381YmIuvg",
    #                     "title": {"text": "This is a test"},
    #                 }
    #             ],
    #         },
    #     },
    #     # "visibility" an either be PUBLIC | CONNECTIONS Create ENUM LATER??
    #     "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"},
    # }

    # resp: requests.Response = requests.post(url=url, headers=header, json=req_body)
    #
    # if resp.status_code == 201:
    #     data = resp.json()
    #     print("Title", data["title"])
    # else:
    #     print(f"Request failed: {resp.status_code}")
    #     print(f"body: {resp.json()}")

    model_off = True
    gem_ext = GeminiExt()
    while running and gem_ext:
        user_input = "hello"
        # user_input = input("\n Enter a message: \n")
        gem_ext.generate_content(user_input)


if __name__ == "__main__":
    main()
