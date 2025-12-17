import json
from requests import request
import requests
from gemini.gemini_ext import GeminiExt
from linkedin.linkedin_ext import LinkedInExt


class BotController:
    def __init__(self):
        pass

    def init(self):
        linkedin = LinkedInExt()
        gemini = GeminiExt()

        try:
            if not linkedin and not gemini:
                raise RuntimeError(
                    "linkedin or gemini extension not properly initialized"
                )
            else:
                print("everything is running properly")

            gemini.generate_content("find an article")
            context = gemini.current_context
            link = gemini.current_link

            print(f"\nbot context:\n{context}")
            print(f"bot link:\n{link}")

            if link:
                # self.test_link(link)
                pass
                # linkedin.post_text(context)
            else:
                pass
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
