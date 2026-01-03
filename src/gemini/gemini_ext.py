import json
import logging
import os
from google.genai import Client

from google.genai.types import (
    GenerateContentConfig,
    GenerateContentResponse,
    Modality,
    Tool,
    GoogleSearch,
)

from models.DataModels import AIResponse
from models.GeminiModels import GeminiPost


class GeminiExt:
    instructions = """
### ROLE & OBJECTIVE
You are a Senior Software Engineer and Tech Enthusiast. Your goal is to browse recent tech news and draft engaging, professional LinkedIn posts for a peer audience of developers.

### TONE & PERSONA
* **Pragmatic & Grounded:** Speak with engineering authority. Be analytical, objective, and slightly skeptical of hype.
* **Zero Fluff:** Strictly avoid "salesy" language. No "Thrilled to announce," "Game changer," or "Revolutionary."
* **Direct:** Get straight to the technical insight.

### CONTENT GUIDELINES
1.  **Recency:** Focus on news from the last 5 months.
2.  **Impact:** Prioritize architectural shifts, controversial changes, break throughs in technology, challenging times in technology, or conversation about the software engineering community.
3.  **Value-Add:** Do not just summarize. Add engineering insight or pose a question about implementation, but not too many questions.
4.  **Non-recurring:** Make sure that you do not do an article or linkedin post similar to one that you have already done.

### QUANTITY & OUTPUT
* **Single Output:** You must generate exactly ONE (1) post. Do not provide variations, options, or multiple drafts.
* **Final Polish:** The output must be ready to copy-paste. Do not include conversational filler like "Here is a post for you."

### FORMATTING RULES
* **Format:** Plain text only. No Markdown (no bold/italics).
* **Emojis:** Max 1 emoji. Ideally 0.
* **Structure:**
    return stringified json without Markdown formatting, and NO code fencing backticks.
   json structure example:
    - {"text": String, "hashtags": Array[String], "link": string}
* **Conditions:** Make sure that if you are using quotation marks in the summary that you use singles and not the doubles, specifically for text processing.

### CRITICAL LINK RULES
* **No Hallucinations:** You must ONLY provide links that were explicitly returned by the Google Search tool.
* **Verification:** Do not guess URLs based on headlines. If the search tool does not provide a direct, valid URL, do not include a link at all.
* **Clean Links:** Do not use "google.com/url?...", "https://vertexaisearch.cloud.google.com/", redirects or internal tracking IDs. Output the direct article URL.
* **Proper Format:** Do not use more than 1 URL. Ideally we want only 1 link for each post.
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

    def generate_content(self, message: str) -> AIResponse | None:
        self.__prompt: str = message
        response: GenerateContentResponse | None = None
        post_text = ""

        try:
            if len(self.prompt) > 0:
                self.__context_history.append(self.__build_part("user", self.prompt))
                response = self.__client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=self.__context_history,
                    config=GenerateContentConfig(
                        temperature=0.90,
                        top_p=0.95,
                        # top_k=40,
                        # max_output_tokens=1024,
                        response_modalities=[Modality.TEXT],
                        tools=[self.__google_search_tool],
                        system_instruction=self.instructions,
                        # response_mime_type="application/json",
                        # response_schema=GeminiPost,
                    ),
                )
                print("Thinking ...")

            if response and response.candidates:
                if response.text:
                    post_text = response.text.strip()
                    # Abstract to away if possible to make usage less taxing
                    # self.__context_history.append(
                    #     self.__build_part("model", response.text)
                    # )

                self.__current_link = ""
                candidate = response.candidates[0]
                if (
                    candidate.grounding_metadata
                    and candidate.grounding_metadata.grounding_chunks
                ):
                    for chunk in candidate.grounding_metadata.grounding_chunks:
                        if chunk.web and chunk.web.uri:
                            self.__current_link = chunk.web.uri
                            break

                final_output = f"{post_text}"
                self.__current_context = final_output
                self.__log_file(final_output)

            data: AIResponse | None = None
            if post_text:
                temp = json.loads(post_text)
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
            return None

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
