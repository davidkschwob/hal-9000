import os
import sys
from groq import Groq
from dotenv import load_dotenv
from .agent import agent_loop


# helper
def get_llm_client():
    api_key = os.environ.get("GROQ_API_KEY")

    if not api_key:
        raise ValueError("CRITICAL: GROQ_API_KEY is missing")

    model = os.environ.get("GROQ_MODEL")
    if not model:
        raise ValueError("CRITICAL: GROQ_MODEL is missing")

    # instantiate using dotenv-specific api key and model name
    return Groq(api_key=api_key)


def main():
    target_workspace = os.getcwd()
    target_env_path = os.path.join(target_workspace, ".env")

    if os.path.exists(target_env_path):
        load_dotenv(dotenv_path=target_env_path)
    else:
        print(f"WARNING: no .env file found at {target_workspace}")
        print("Defaulting to GROQ_API_KEY in system env")

    agent_loop(workspace_path=target_workspace)
