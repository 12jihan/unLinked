import logging
import requests
from controller.MemoryController import MemoryController
from gemini.gemini_ext import GeminiExt
from linkedin.linkedin_ext import LinkedInExt
from models.GeminiModels import ModelCook


class BotController:
    def __init__(self):
        self.gemini = GeminiExt()
        if not self.gemini:
            return

        self.linkedin = LinkedInExt()
        if not self.linkedin:
            return

        self.memory = MemoryController()
        if not self.memory:
            return

    def start(self):
        # initialize the search for an article to use.
        _message: str = "Using google search find an article that follows the guildlines of the provided instructions"
        print("Finding an article to use...")

        # check if article was found
        _article = self.gemini.find_article(message=_message)
        if _article is None:
            print("Problem finding an article... Try again...")
            return
        print(f"Article succesfully found!:\n {_article}")

        # check if stripping worked
        _article_stripped = self.gemini.strip_article(_article)
        if _article_stripped is None:
            print("Problem stripping the article... Try again...")
            return
        print("Article succesfully stripped!")

        # generate content from the data created
        print("Creating post from article data")
        self.__generate(_article_stripped)

    def __generate(self, article: ModelCook):
        _json_data: str = article.model_dump_json()
        # print(f"testing json data:\n{_json_data}")

        # try:
        #     _gem_data: AIResponse | None = self.gemini.generate_content(
        #         json_string=_json_data, temperature=0.75, tp=0.95, tk=1.0
        #     )
        #
        #     if _gem_data:
        #         print(f"text:\n\t{_gem_data.text}\n\n")
        #         print(f"link:\n\t{_gem_data.link}\n\n")
        #         if not self.memory.is_unique(_gem_data.text, threshold=0.65):
        #             return
        #
        #         _data = DocumentCreate(
        #             text=_gem_data.text,
        #             link=_gem_data.link,
        #             hashtags=_gem_data.hashtags,
        #         )
        #
        #         # INFO: So currently there is already a link tester in the article finder I think I'm just going to have to go with making a post with a link and no option to make a post without one. Since I presume that I will be making sure that this applicaiton keeps trying until it get it right (with a limit of course)...
        #         # So this is commented out for now until I replace it with something a bit more beneficial.
        #         #
        #         #
        #         # if _gem_data.link:
        #         #     print("Link Found:")
        #         #     print(f"{gem_data.link}")
        #         #     link_passed = self.__link_test(gem_data.link)
        #         #
        #         #     if link_passed:
        #         #         self.__log_file(f"Link Test Passed With --> {link_passed}")
        #         #     else:
        #         #         self.__log_file(f"Link Testing Failed With --> {link_passed}")
        #         #         self.__log_file("Removing link and leaving blank")
        #         #         data.link = ""
        #         #
        #         #     self.memory.add(data)
        #         #     # self.linkedin.post_text(
        #         #     #     text=data.text, hashtags=data.hashtags, link_url=data.link
        #         #     # )
        #         # else:
        #         #     self.__log_file("No Link Found")
        #         #     self.__log_file("Posting Without Link")
        #         # data.link = ""
        #         # self.memory.add(data)
        #         # self.linkedin.post_text(text=data.text,hashtags=data.hashtags link_url=data.link)
        #
        # except RuntimeError as e:
        #     self.__log_file(f"Error: {e}")
        #     raise RuntimeError(f"There was an error: {e}")

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
