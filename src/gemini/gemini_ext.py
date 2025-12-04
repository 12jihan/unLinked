import os
from google.genai import Client
from google.genai import types
from google.genai.types import (
    GenerateContentConfig,
    GenerateContentResponse,
    Modality,
    Tool,
    GoogleSearch,
)


class GeminiExt:
    def __init__(self):
        # GeminiAI Tokens
        self.__api_key: str | None = os.getenv("API_KEY")
        self.__client: Client = Client(api_key=self.__api_key)
        self.__google_search_tool = Tool(google_search=GoogleSearch())
        self.__models = list(self.__client.models.list())
        self.__context_history = []
        self.__prompt = ""

    def generate_content(self, message: str):
        self.__prompt: str = message
        response: GenerateContentResponse | None = None

        try:
            if len(self.prompt) > 0:
                print(f"message:\t{self.prompt}")
                self.__context_history.append(self.__build_part("user", self.prompt))
                print("Thinking ...")
                response = self.__client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=self.__context_history,
                    config=GenerateContentConfig(
                        response_modalities=[Modality.TEXT],
                        tools=[self.__google_search_tool],
                        system_instruction="""
                        You are a seasoned Software Engineer and Tech Enthusiast. Your goal is to draft engaging, authentic LinkedIn posts based on recent tech news or engineering experiences.

                        **Tone & Style:**
                        - **Has to be recent** Do not use articles that are over 5 months old. We want to try and aim for data that's as recent as possible.
                        - **Strictly No Fluff:** Do not use bubbly, overly enthusiastic, or "salesy" language. Avoid clichés like "Thrilled to announce," "Game changer," or "Super excited."
                        - **Grounded & Professional:** Speak like a developer talking to peers. The tone should be analytical, objective, and perhaps slightly critical or weary of hype.
                        - **Direct:** Get straight to the point. Use clean formatting with minimal emojis (max 1, if any).

                        **Content Strategy:**
                        - **High Impact:** Focus strictly on news that significantly impacts the industry (e.g., architectural shifts, major security vulnerabilities, new reliable tools, or controversial open-source changes).
                        - **Value-Add:** Don't just summarize news; add a layer of engineering insight or pose a question about the practical implications.
                        - **Citations:** If you find or are provided with a specific article, YOU MUST include the direct link at the bottom of the post.

                        **Output Format:**
                        - No Markdown syntax (under no circumstances)
                        - The post text.
                        - A blank line.
                        - The link (if applicable).
                        - Relevant Hashtags (if applicable).
                        """,
                    ),
                )
            if response and response.text:
                self.__context_history.append(self.__build_part("model", response.text))
                print(f"response:\t{response.text}")

        except Exception as e:
            print(f"Errors: {e}")

    @property
    def api_key(self):
        self.__api_key

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
