import logging
import requests
from controller.MemoryController import MemoryController
from gemini.gemini_ext import GeminiExt
from linkedin.linkedin_ext import LinkedInExt
from models.DataModels import AIResponse, DocumentCreate


class BotController:
    def __init__(self):
        self.gemini = GeminiExt()
        self.linkedin = LinkedInExt()
        self.memory = MemoryController()

    def start(self):
        try:
            if self.linkedin and self.gemini and self.memory:
                self.__log_file("LinkedIn Ext. and Gemini Ext. Initialized...")
            else:
                raise RuntimeError("LinkedIn or Gemini Ext. not properly initialized")

            protocol: str = "Find an article and create a post"
            gem_data: AIResponse | None = self.gemini.generate_content(protocol)

            if gem_data:
                if not self.memory.is_unique(gem_data.text, threshold=0.85):
                    return

                data = DocumentCreate(
                    text=gem_data.text, link=gem_data.link, hashtags=gem_data.hashtags
                )

                self.__log_file("Checking Link:")
                if gem_data.link:
                    self.__log_file("Link Found:")
                    self.__log_file(f"{gem_data.link}")
                    link_passed = self.__link_test(gem_data.link)

                    if link_passed:
                        self.__log_file(f"Link Test Passed With --> {link_passed}")
                    else:
                        self.__log_file(f"Link Testing Failed With --> {link_passed}")
                        self.__log_file("Removing link and leaving blank")
                        data.link = ""

                    self.memory.add(data)
                    self.linkedin.post_text(data.text)
                else:
                    self.__log_file("No Link Found")
                    self.__log_file("Posting Without Link")
                    data.link = ""
                    self.memory.add(data)
                    self.linkedin.post_text(data.text, link_url=data.link)

        except RuntimeError as e:
            self.__log_file(f"Error: {e}")
            raise RuntimeError(f"There was an error: {e}")

    def __link_test(self, link: str) -> bool:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            response = requests.head(
                link, timeout=10, allow_redirects=True, headers=headers
            )

            if response.status_code == 200:
                return True

            # Retrying with get method if it fails
            if response.status_code in (405, 403):
                self.__log_file("Trying again with get request")
                response = requests.get(
                    link, timeout=10, allow_redirects=True, headers=headers
                )
                return response.status_code == 200

            return False
        except requests.RequestException as e:
            self.__log_file(f"Error trying to make a request for:\n{link}\n{e}")
            # raise Exception(f"Error trying to make a request for:\n{link}\n{e}")
            return False

    def __log_file(self, text):
        logging.info(text)
