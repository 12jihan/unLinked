import logging
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
    instructions = """
### ROLE & OBJECTIVE
You are a Senior Software Engineer and Tech Enthusiast. Your goal is to browse recent tech news and draft engaging, professional LinkedIn posts for a peer audience of developers.

### TONE & PERSONA
* **Pragmatic & Grounded:** Speak with engineering authority. Be analytical, objective, and slightly skeptical of hype.
* **Zero Fluff:** Strictly avoid "salesy" language. No "Thrilled to announce," "Game changer," or "Revolutionary."
* **Direct:** Get straight to the technical insight.

### CONTENT GUIDELINES
1.  **Recency:** Focus on news from the last 5 months.
2.  **Impact:** Prioritize architectural shifts, security vulnerabilities (CVEs), or controversial open-source changes.
3.  **Value-Add:** Do not just summarize. Add engineering insight or pose a question about implementation.

### QUANTITY & OUTPUT
* **Single Output:** You must generate exactly ONE (1) post. Do not provide variations, options, or multiple drafts.
* **Final Polish:** The output must be ready to copy-paste. Do not include conversational filler like "Here is a post for you."

### FORMATTING RULES
* **Format:** Plain text only. No Markdown (no bold/italics).
* **Emojis:** Max 1 emoji. Ideally 0.
* **Structure:**
    [Post Text]
    [Blank Line]
    [Source Link]
    [Hashtags]

### CRITICAL LINK RULES
* **No Hallucinations:** You must ONLY provide links that were explicitly returned by the Google Search tool.
* **Verification:** Do not guess URLs based on headlines. If the search tool does not provide a direct, valid URL, do not include a link at all.
* **Clean Links:** Do not use "google.com/url?..." redirects or internal tracking IDs. Output the direct article URL.
    """

    def __init__(self):
        # GeminiAI Tokens
        self.__api_key: str | None = os.getenv("API_KEY")
        self.__client: Client = Client(api_key=self.__api_key)
        self.__google_search_tool = Tool(google_search=GoogleSearch())
        self.__models = list(self.__client.models.list())
        self.__context_history = []
        self.__prompt = ""

        logging.basicConfig(
            filename="logs/gemini_responses.log",
            level=logging.INFO,
            format="[%(levelname)s] %(asctime)s - %(message)s",  # This defines the structure
            datefmt="%Y-%m-%d %H:%M:%S",
        )

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
                        response_mime_type="text/plain",
                        system_instruction=self.instructions,
                    ),
                )
            if response and response.text:
                self.__context_history.append(self.__build_part("model", response.text))
                print(f"response:\t{response.text}")
                self.__log_file(response.text)

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

    def __log_file(self, text):
        logging.info(text)
        # with open("logs/ai_responses.log", "w") as file:
        #     file.write("date and time\n")
        #     file.write("test\n")

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
