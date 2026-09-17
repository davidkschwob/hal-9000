import os
import sys
from groq import Groq
from dotenv import load_dotenv
from .agent import agent_loop


def main():
    target_workspace = os.getcwd()
    target_env_path = os.path.join(target_workspace, ".env")

    if os.path.exists(target_env_path):
        load_dotenv(dotenv_path=target_env_path)
    else:
        print(f"WARNING: no .env file found at {target_workspace}")
        print("Defaulting to GROQ_API_KEY in system env")

    agent_loop(workspace_path=target_workspace)
