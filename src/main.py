import logging
from controller.MemoryController import MemoryController
from controller.BotController import BotController

from gemini.gemini_ext import GeminiExt
from linkedin.linkedin_ext import LinkedInExt
from dotenv import load_dotenv
import os


def main():
    running = True
    load_dotenv()

    # TODO:
    # need to set this up in a way that wil lmake it easier down the road but for now we will just use this here
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/bot_logs.log",
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s - %(message)s",  # This defines the structure
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    controller = BotController()

    while running and controller:
        user_input = input("\n Enter a message: \n")
        if user_input == "##quit":
            running = False

        if running:
            controller.start()


if __name__ == "__main__":
    main()
