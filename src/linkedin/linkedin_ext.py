import os
import requests
import json

from models.LinkinModels import (
    Media,
    ShareCommentary,
    ShareContent,
    SpecificContent,
    TextPostRequestBody,
    Visibility,
)


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


class LinkedInExt:
    def __init__(self):
        self.__access_token = os.getenv("TOKEN")
        self.__api_version: str | None = os.getenv("API_VERSION")
        self.__user_id: str | None = os.getenv("USER_ID")

        self.__url_text: str = "https://api.linkedin.com/v2/ugcPosts"
        self.__url_register: str = "https://api.linkedin.com/v2/ugcPosts"
        self.__url_multimedia: str = "https://api.linkedin.com/v2/ugcPosts"

        self.__post_text: str = ""
        self.__post_link: str = ""

        self.__request_body = {
            "author": f"{self.__user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": self.__post_text},
                    "shareMediaCategory": "NONE",
                },
            },
            # "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"},
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        self.__request_body_model = TextPostRequestBody(
            author=os.getenv("USER_ID", ""),
            lifecycleState="PUBLISHED",
            # visibility=Visibility(**{"memberNetworkVisibility": "CONNECTIONS"}),
            visibility=Visibility(**{"memberNetworkVisibility": "PUBLIC"}),
            specificContent=SpecificContent(
                **{
                    "ugcShareContent": ShareContent(
                        shareCommentary=ShareCommentary(text="asdk"),
                    )
                }
            ),
        )

        self.__header = {
            "Authorization": f"Bearer {self.__access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
            "LinkedIn-Version": self.__api_version if self.__api_version else "",
        }

    def post_text(
        self, text: str, hashtags: list[str] | None = None, link_url: str | None = None
    ):
        full_text: str = text
        print(f"hashtags: {hashtags}")

        if hashtags:
            hashtag_str = " ".join(f"#{tag.lstrip('#')}" for tag in hashtags)
            full_text = f"{text}\n\n{hashtag_str}"

        self.__post_text = full_text
        self.__request_body_model.specificContent.ugcShareContent.shareCommentary.text = full_text

        print(f"request header: {self.__header}")
        print(f"request body: {self.__request_body}")

        if link_url:
            self.__post_link = link_url
            print(f"Link Found: {self.__post_link}")

            # switch category to ARTICLE
            self.__request_body_model.specificContent.ugcShareContent.shareMediaCategory = "ARTICLE"

            link_media = Media(
                status="READY",
                originalUrl=link_url,
            )
            # Add to the list
            self.__request_body_model.specificContent.ugcShareContent.media = [
                link_media
            ]
        else:
            print("No Link Found")
            # Text only
            self.__request_body_model.specificContent.ugcShareContent.shareMediaCategory = "NONE"
            self.__request_body_model.specificContent.ugcShareContent.media = []

        payload = self.__request_body_model.model_dump(by_alias=True)
        response = requests.post(
            url=self.__url_text,
            headers=self.__header,
            json=payload,
        )

        if response.status_code == 201:
            print("POST Request Successful!")
            print("Server Response:")
            print(json.dumps(response.json(), indent=4) + "\n\n")
        else:
            print(f"POST Request Failed. Status Code: {response.status_code}\n\n")
            print("Error Message:")
            print(json.dumps(response.json(), indent=4) + "\n\n")
