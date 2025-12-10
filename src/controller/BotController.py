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
            print("test")
        except RuntimeError as e:
            print(e)
