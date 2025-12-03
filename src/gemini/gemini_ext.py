import os
from google.genai import Client
from google.genai.types import (
    GenerateContentConfig,
    GenerateContentResponse,
    Modality,
)


class GeminiExt:
    def __init__(self):
        # GeminiAI Tokens
        self.__api_key: str | None = os.getenv("API_KEY")
        self.__client: Client = Client(api_key=self.__api_key)
        self.__models = list(self.__client.models.list())
        self.__context_history = []
        self.__prompt = ""

    def generate_content(self, message: str):
        self.__prompt: str = message
        response: GenerateContentResponse | None = None

        try:
            if len(self.prompt) > 0:
                print(f"message:\t{message}")
                self.__context_history.append(self.__build_part("user", "Hello"))
                print("Thinking ...")
                response = self.__client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=self.__context_history,
                    config=GenerateContentConfig(
                        response_modalities=[Modality.TEXT],
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
