import json
from requests import request
import requests
from controller.MemoryController import MemoryController
from gemini.gemini_ext import GeminiExt
from linkedin.linkedin_ext import LinkedInExt
from models.DataModels import AIResponse, DocumentCreate


class BotController:
    def __init__(self):
        pass

    def init(self):
        memory = MemoryController()
        linkedin = LinkedInExt()
        gemini = GeminiExt()

        try:
            if not linkedin and not gemini:
                raise RuntimeError(
                    "Linkedin or gemini extension not properly initialized"
                )
            else:
                pass
                # print("everything is running properly")

            gem_data: AIResponse | None = gemini.generate_content("find an article")

            # print(f"bot context:\n{context}")
            # print(f"bot link:\n{link}")

            if gem_data:
                data = DocumentCreate(
                    text=gem_data.text, link=gem_data.link, hashtags=gem_data.hashtags
                )

                print("Checking link:")
                if gem_data.link:
                    print("-\tLink Found:")
                    print(gem_data.link)
                    print("\n-\tTesting Link:")
                    status_code = self.test_link(gem_data.link)

                    if status_code != 200:
                        print("-\tLink Testing Failed:")
                        data.link = ""
                    else:
                        print("-\tLink Testing Passed:")

                    memory.add(data)
                    # linkedin.post_text(context)
                else:
                    print("-\tNo Link Found")
                    print("-\tPosting Without Link")
                    # print(gem_data.link)
                    memory.add(data)
                    # linkedin.post_text(context, link_url=link)

        except RuntimeError as e:
            print(e)

    def test_link(self, link: str):
        response = requests.get(link)
        print("\n\n~~~testing_link_begin~~~")
        # print(f"content:\n{response.content}"[:1000] + "\n")
        print(f"status:\n{response.status_code}\n")
        # print(f"\n\n\n\ntesting link:\n{json.dumps(response.json(), indent=4)}")
        print("\n~~~testing_link_end~~~\n")
        # pass
        return response.status_code
