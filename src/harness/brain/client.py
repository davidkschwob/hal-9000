import os
import sys
import textwrap
import time
from groq import Groq


# bootsraps llm client
def get_llm_client():
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("CRITICAL: GROQ_API_KEY is missing")

    model = os.environ.get("GROQ_MODEL")
    if not model:
        raise ValueError("CRITICAL: GROQ_MODEL is missing")

    # instantiate using dotenv-specific api key and model name
    return Groq(api_key=api_key)


# print in hal-speak
def hal_stream_print(text: str, width: int = 75):
    """Prints text in HAL-red with a slight deliberate pacing"""
    RED = "\033[91m"
    RESET = "\033[0m"
    sys.stdout.write(RED)
    for l in (textwrap.wrap(text,width)):
        for char in l:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(0.015) 
        sys.stdout.write("\n")
    sys.stdout.write(RESET + "\n")
