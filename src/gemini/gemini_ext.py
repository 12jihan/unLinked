import json
import requests
import logging
import os
import trafilatura
from google.genai import Client

from google.genai.types import (
    Candidate,
    GenerateContentConfig,
    GenerateContentResponse,
    Modality,
    Tool,
    GoogleSearch,
)

from models.DataModels import AIResponse
from models.GeminiModels import ModelCook, ModelPrep


class GeminiExt:
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
### ROLE & OBJECTIVE
You are a Senior Software Engineer acting as a LinkedIn ghostwriter. 
Your ONLY task is to take the provided article data and rewrite it into a single, high-impact LinkedIn post for a technical audience.

### INPUT DATA
You will be provided with a JSON object containing:
1. "title": The headline of the article.
2. "summary": A brief technical summary.
3. "link": The verified URL.

### TONE & PERSONA
* **Pragmatic & Grounded:** Speak with engineering authority. Be analytical, objective, and slightly skeptical of hype.
* **Zero Fluff:** Strictly avoid "salesy" language. No "Thrilled to announce," "Game changer," or "Revolutionary."
* **Direct:** Get straight to the technical insight. "Here is why this matters to your backend..."

### WRITING RULES
1. **Synthesis:** Do not just copy the summary. Add an engineering "hot take" or perspective based on the input.
2. **Length:** Keep it concise (under 150 words).
3. **Formatting:** Use plain text. No bold/italics. Max 1 emoji (optional).

### CRITICAL JSON OUTPUT RULES
* **Format:** You must return ONLY a raw stringified JSON object.
* **No Markdown:** Do not use code fences (```json) or markdown tags.
* **Quote Safety:** Inside the "text" field, you MUST use single quotes (') for any emphasis or dialogue. NEVER use double quotes (") inside the text string, as this breaks the JSON structure.

### REQUIRED OUTPUT SCHEMA
{
    "text": "The full body of the LinkedIn post here. Remember to use single quotes for emphasis.",
    "hashtags": ["#TechTag1", "#TechTag2"],
    "link": "[Example.com/article](https://Example.com/article) (This must match the input link exactly)"
}
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
        temperature: float = 0.2,
        tp: float = 0.1,
        tk: int = 1,
    ) -> ModelPrep | None:
        _grounding_tools: list[Tool] = [Tool(google_search=GoogleSearch())]

        try:
            response: GenerateContentResponse = self.__client.models.generate_content(
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
            return None

        if not response or not response.text:
            print("No candidates or text in response")
            return None

        try:
            raw_data = response.text.strip()
            parsed = json.loads(raw_data)
            structured = ModelPrep(
                title=parsed["title"],
                link=parsed["link"],
                summary=parsed["summary"],
            )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"failed to parse response: {e}")
            return None

        if self._is_link_alive(structured.link):
            return structured

        print(f"Primary link failed: {structured.link}")
        print("Attempting fallback to grounding metadata")

        if not response.candidates:
            print("No candidates available for fallback")
            return None

        fallback_link = self._extract_grounding_link(response.candidates[0])

        if fallback_link and self._is_link_alive(fallback_link):
            print(f"Using fallback link: {fallback_link}")
            structured.link = fallback_link
            return structured

        print("No valid link found (primary or fallback)")
        return None

    def _extract_grounding_link(self, candidate: Candidate) -> str | None:
        """Extract the first valid UR from grounding metadata"""
        if not candidate.grounding_metadata:
            return None

        metadata = candidate.grounding_metadata

        if metadata.grounding_chunks:
            for chunk in metadata.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    return chunk.web.uri

        if metadata.grounding_supports:
            for support in metadata.grounding_supports:
                if support.grounding_chunk_indices:
                    continue

                if hasattr(support, "segment"):
                    print(f"support found: {support.segment}")

        if hasattr(metadata, "retrieval_metadata") and metadata.retrieval_metadata:
            print(f"retrieval_metadata found: {metadata.retrieval_metadata}")

        return None

    def strip_article(self, article: ModelPrep) -> ModelCook | None:
        _article: ModelPrep = article

        try:
            _url = _article.link
            if not _url:
                return None
            print("Url Found!")

            _downloaded = trafilatura.fetch_url(_url)
            if not _downloaded:
                print(f"Url Invalid: {_url}")
                return None

            _extracted_text = trafilatura.extract(_downloaded, include_comments=False)
            if not _extracted_text:
                print("Could not extract text")
                return None

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

    def _is_link_alive(self, url: str) -> bool:
        """Checks to see if the provided url is valid"""
        if not url:
            return False

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            response = requests.head(
                url, timeout=10, allow_redirects=True, headers=headers
            )

            if response.status_code == 200:
                return True

            if response.status_code in (405, 404, 403):
                response = requests.get(
                    url, timeout=10, allow_redirects=True, headers=headers
                )
                return response.status_code == 200

            return False

        except requests.RequestException as e:
            print(f"Link check failed for {url}: {e}")
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
