from dotenv import load_dotenv
import os

load_dotenv()

class Env:
    def __init__(self):
        # Dynamically load ENV and set them as a attribute

        for key, value in  os.environ.items():
            setattr(self, key, value)

    def get(self, key: str, default=None):
        return getattr(self, key, default)