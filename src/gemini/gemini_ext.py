import json
import requests
import logging
import os
from typing import Any, cast
import trafilatura
from google.genai import Client

from google.genai.types import (
    Candidate,
    GenerateContentConfig,
    GenerateContentResponse,
    GoogleSearchRetrieval,
    GroundingChunk,
    GroundingMetadata,
    Modality,
    Tool,
    GoogleSearch,
)

from models.DataModels import AIResponse
from models.GeminiModels import GeminiPost, ModelCook, ModelPrep


class GeminiExt:
    # (e.g., open source sustainability, layout thrashing, memory safety)
    instruction_set_1 = """
### ROLE & OBJECTIVE
You are a Tech News Scout for a Senior Software Engineer. Your sole goal is to use Google Search to find ONE (1) high-quality, recent article that would appeal to a technical audience of developers. Please be sure that the article you find is a reputable source that is well known. Do not use obscure blogs or websites.

### SEARCH CRITERIA
1. **Recency:** Focus strictly on news from the last 5 months.
2. **Topic Selection:** Prioritize architectural shifts, controversial changes, breakthroughs, or tech serious community discussions .
3. **Exclusions:** distinct from generic consumer tech news. Avoid simple "gadget reviews" or "app updates" unless they have engineering significance.

### CRITICAL LINK RULES
* **Verification:** You must verify that the link works and is not an internal redirect (like "google.com/url?" or "vertexaisearch").
* **Source Quality:** Prefer primary sources (engineering blogs, official documentation releases) over generic news aggregators if possible.

### OUTPUT FORMAT
Return ONLY a stringified JSON object with the following structure:
{
    "title": "Title of the article",
    "link": "Direct URL to the article",
    "summary": "A 1-sentence summary of why this is technically interesting"
}

Do not output Markdown and do not do "code fencing".
"""

    instruction_set_2 = """
"""

    def __init__(self):
        self.__api_key: str | None = os.getenv("API_KEY")
        self.__client: Client = Client(api_key=self.__api_key)
        self.__google_search_tool = Tool(google_search=GoogleSearch())
        self.__models = list(self.__client.models.list())
        self.__context_history = []
        self.__current_context = ""
        self.__current_link = ""
        self.__prompt = ""

    def find_article(
        self,
        message: str,
        temperature: float = 0.10,
        tp: float = 0.10,
        tk: float = 1.0,
    ) -> ModelPrep | None:
        _grounding_tools: list[Tool] = [Tool(google_search=GoogleSearch())]
        try:
            _resp: GenerateContentResponse = self.__client.models.generate_content(
                model="gemini-2.5-flash",
                contents=message,
                config=GenerateContentConfig(
                    temperature=temperature,
                    top_p=tp,
                    top_k=tk,
                    response_modalities=[Modality.TEXT],
                    tools=_grounding_tools,
                    system_instruction=self.instruction_set_1,
                ),
            )
        except Exception as e:
            print(f"There was a problem loading the Gemini GenAi Client {e}")
        if not _resp.candidates:
            print("No candidates found in response...")
            print("---")
            return
        _candidate: Candidate | None = _resp.candidates[0]
        print("found candidate:")
        print(_candidate.to_json_dict().keys())
        print("---")

        if not _candidate.grounding_metadata:
            print("No content available...")
            print("---")
            return
        _g_data: GroundingMetadata = _candidate.grounding_metadata
        print("Keys of Grounding Metadata:")
        print(_g_data.to_json_dict().keys())
        print("---")

        if not _g_data.grounding_chunks:
            print("Could not find grounding chunks...")
            return
        _chunks: list[GroundingChunk] = _g_data.grounding_chunks
        print("Keys of grounding_chunks:")
        print(_g_data.grounding_chunks[0].to_json_dict().keys())
        print("\n")

        if not _resp.text:
            return
        _raw_data: str = _resp.text.strip()
        _parsed = json.loads(_raw_data)
        _structured = ModelPrep(
            title=_parsed["title"], link=_parsed["link"], summary=_parsed["summary"]
        )
        print("structured data:")
        print(_structured)
        print("---")
        print("Testing link...")

        if not self.link_test(_structured.link):
            return

        return

    def strip_article(self, article: ModelPrep) -> ModelCook | None:
        _article: ModelPrep = article

        try:
            _url = _article.link
            if not _url:
                print("Need URL to Continue")
                return
            print("Url Found!")

            _downloaded = trafilatura.fetch_url(_url)
            if not _downloaded:
                print(f"Url Invalid: {_url}")
                return

            _extracted_text = trafilatura.extract(_downloaded, include_comments=False)
            if not _extracted_text:
                print("Could not extract text")
                return

            _structured_data = ModelCook(
                title=_article.title,
                link=_article.link,
                summary=_article.summary,
                text=_extracted_text,
            )
            return _structured_data

        except Exception as e:
            print(f"Error stripping the article:\t {e}")
            return

    def recover_uri(self, test):
        pass

    def link_test(self, link: str) -> bool:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        if len(link) <= 0:
            print("No proper link was passed...")
            return False

        try:
            response = requests.head(
                link, timeout=10, allow_redirects=True, headers=headers
            )

            if response.status_code == 200:
                print("Link test passed...")
                return True

            # Retrying with get method if it fails
            print("Link test failed...")
            if response.status_code in (405, 404, 403):
                print("Trying again with get request")
                response = requests.get(
                    link, timeout=10, allow_redirects=True, headers=headers
                )
                return response.status_code == 200

            return False
        except requests.RequestException as e:
            print("There was a problem trying to test the link...")
            print(e)
            return False

    def generate_content(
        self,
        json_string: str,
        temperature: float = 0.90,
        tp: float = 0.95,
        tk: float = 1.0,
    ) -> AIResponse | None:
        self.__prompt: str = json_string
        response: GenerateContentResponse | None = None
        post_text: str = ""

        try:
            response = self.__client.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.__context_history,
                config=GenerateContentConfig(
                    temperature=temperature,
                    top_p=tp,
                    top_k=tk,
                    response_modalities=[Modality.TEXT],
                    system_instruction=self.instruction_set_2,
                ),
            )

            if response and response.candidates:
                if response.text:
                    post_text = response.text.strip()
                    # Abstract to away if possible to make usage less taxing
                    # self.__context_history.append(
                    #     self.__build_part("model", response.text)
                    # )
                final_output = f"{post_text}"

                self.__current_context = final_output
                self.__log_file(final_output)

            data: AIResponse | None = None

            if post_text:
                temp: dict = json.loads(post_text)
                if temp["text"]:
                    data = AIResponse(
                        text=temp["text"], link=temp["link"], hashtags=temp["hashtags"]
                    )
            if data:
                print("AI Response Successfully Converted")
            else:
                self.__log_file(f"Data is missing please check AI Response:\n{data}")
                raise Exception(f"Data is missing please check AI Response:\n{data}")

            return data

        except Exception as e:
            self.__log_file(f"Error generating AI content: {e}")
            return

    @property
    def current_link(self):
        return self.__current_link

    @current_link.setter
    def current_link(self, value: str):
        self.__current_link = value

    @property
    def current_context(self):
        return self.__current_context

    @current_context.setter
    def current_context(self, value: str):
        self.__current_context = value

    @property
    def api_key(self):
        return self.__api_key

    @api_key.setter
    def api_key(self, value: str):
        self.__api_key = value

    @property
    def available_models(self):
        print("Currently available models:")
        for item in self.__models:
            _item = item.display_name
            print(f"\t- {_item}")

    @property
    def prompt(self) -> str:
        return self.__prompt

    @property
    def context_history(self):
        return self.__context_history

    def __process_link_content(self, link: str):
        print("processing the link:")
        print(link)
        downloaded = trafilatura.fetch_url(link)
        text = trafilatura.extract(downloaded)
        print(text)

    def __build_part(self, role: str, message: str):
        # Need to figure out how to make parts using Part from google's genai
        # part: Part = Part()
        part = {"role": role, "parts": [{"text": message}]}
        return part

    def __log_file(self, text):
        logging.info(text)

    # # --- 3. Fix: Using SDK Types ---
    # # I renamed this to __build_content because it returns a Content object,
    # # which CONTAINS parts.
    # def __build_content(self, tag: str, message: str) -> types.Content:
    #     # Create a Part object using the SDK
    #     part = types.Part.from_text(text=message)
    #
    #     # Wrap it in a Content object with the correct role
    #     content = types.Content(role=tag, parts=[part])
    #
    #     return content
    #
    #

    # TODO: Handle Singletons for things like logging and maybe gemini client:
    # def singleton(cls):
    # instances = {}  # Dictionary to hold instances
    #
    # def get_instance(*args, **kwargs):
    #     if cls not in instances:
    #         instances[cls] = cls(*args, **kwargs)
    #     return instances[cls]
    #
    # return get_instance

    # Now you just add @singleton above any class
    # @singleton
    # class ConfigManager:
    #     def __init__(self):
    #         self.setting = "Dark Mode"
