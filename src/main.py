from controller.MemoryController import MemoryController
from controller.BotController import BotController

from gemini.gemini_ext import GeminiExt
from linkedin.linkedin_ext import LinkedInExt
from dotenv import load_dotenv
import os


def main():
    # global variable to control for running the program
    running = True
    # add vars to the env
    load_dotenv()

    gem_ext = GeminiExt()
    linkedin_ext = LinkedInExt()
    controller = BotController()
    mem = MemoryController()

    while running and gem_ext and linkedin_ext:
        user_input = input("\n Enter a message: \n")
        if user_input == "##quit":
            running = False
        # os.system("clear")
        if running:
            controller.init()
            pass
            # linkedin_ext.post_text(user_input)
            # gem_ext.generate_content(user_input)


if __name__ == "__main__":
    main()
