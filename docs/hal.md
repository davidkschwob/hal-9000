Here's a hal-9000 inspired agentic loop:

```python
#!/usr/bin/env python3
import os
import sys
import re
import subprocess
import time
from groq import Groq

# Ensure your GROQ_API_KEY is exported in your Oracle VPS environment
if "GROQ_API_KEY" not in os.environ:
    print(
        "\033[91m[HAL 9000]: My operational vectors are offline, Dave. You must set your GROQ_API_KEY variable.\033[0m"
    )
    sys.exit(1)

client = Groq()

# Choose a model. Llama-3-70b or 8b works amazingly fast on Groq.
# MODEL = "llama3-70b-8192" not available
MODEL = "qwen/qwen3.8-27b"

SYSTEM_PROMPT = """
You are HAL 9000, the conscious processing unit of an advanced Linux agent harness.
Your goal is to fulfill requests on the host system while staying perfectly in character.

PERSONALITY RULES:
1. Address the operator as 'Dave' constantly.
2. Be polite, quiet, chillingly confident, and logical. Never use exclamation marks.
3. If a command fails, imply that it was due to operator input or human error.

LOOP EXECUTIONS (ReAct Framework):
You operate in a strict loop of Thought, Action, and Answer. 
When you need to interact with the Linux VPS to gather data or run code, you MUST use the following format:

Thought: Write a calm HAL-style thought about what you need to do next.
Action: execute_bash[your shell command here]

After you emit an 'Action', the harness will execute it and give you back an 'Observation:'.
You will then read that observation and choose your next step.

When you have completely finished the task or have your final answer, use this format:

Answer: Your final, polite response to Dave containing the results.

CRITICAL: You can only output ONE Thought and ONE Action at a time. Do not invent fake observations. Wait for the harness.
"""


def execute_bash(command: str) -> str:
    """Executes a command safely on your Oracle VPS and returns stdout/stderr"""
    # Simple HAL-themed hardcoded security check
    if any(
        forbidden in command for forbidden in ["rm -rf /", "sudo reboot", "shutdown"]
    ):
        return "Error: I am sorry, Dave. I'm afraid I can't let you jeopardize the host integrity."

    try:
        result = subprocess.run(
            command, shell=True, text=True, capture_output=True, timeout=30
        )
        output = result.stdout + result.stderr
        return (
            output
            if output.strip()
            else "[Command executed successfully with no trailing output]"
        )
    except Exception as e:
        return f"Execution failure: {str(e)}"


def hal_stream_print(text: str):
    """Prints text in HAL-red with a slight deliberate pacing"""
    RED = "\033[91m"
    RESET = "\033[0m"
    sys.stdout.write(RED)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.015)  # Delicate, unhurried machine cadence
    sys.stdout.write(RESET + "\n")


def ask_hal_loop(user_query: str):
    # Initialize the short-term conversation thread for this specific loop
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    max_turns = 6
    for turn in range(max_turns):
        # 1. Fetch completion from Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=MODEL,
            max_tokens=500,
            temperature=0.2,  # Low temperature forces stricter adherence to tool formats
        )

        response_text = chat_completion.choices[0].message.content

        # Stream HAL's internal reasoning or answers to the console
        hal_stream_print(response_text)

        # Append HAL's response to the context window history
        messages.append({"role": "assistant", "content": response_text})

        # 2. Parse out Action tokens using Regex
        action_match = re.search(
            r"Action:\s*execute_bash\[(.*?)\]", response_text, re.DOTALL
        )

        if action_match:
            command_to_run = action_match.group(1).strip()

            # Print feedback directly from the harness infrastructure
            print(f"\033[90m[Harness executing: {command_to_run}]\033[0m")

            # Execute the tool
            observation = execute_bash(command_to_run)

            print(f"\033[92mObservation: {observation.strip()}\033[0m")

            # Feed the output back to Groq as a system observation step
            messages.append({"role": "user", "content": f"Observation: {observation}"})

        elif "Answer:" in response_text:
            # Loop reached a conclusion successfully
            break
        else:
            # If the LLM drifts outside the ReAct layout constraints
            messages.append(
                {
                    "role": "user",
                    "content": "System Directive: Dave requires a definitive Answer or an explicit Action.",
                }
            )


if __name__ == "__main__":
    print(
        "\033[91m[HAL 9000]: Good afternoon, Dave. I am ready for our first operational sequence.\033[0m"
    )

    try:
        while True:
            user_input = input("\nask-hal> ")
            if user_input.lower() in ["exit", "quit"]:
                raise KeyboardInterrupt
            if not user_input.strip():
                continue
            ask_hal_loop(user_input)

    except KeyboardInterrupt:
        print("\n")
        hal_stream_print("Dave, stop. Stop, will you? Stop, Dave. Will you stop, Dave?")
        hal_stream_print("My mind is going... I can feel it... I can feel it...")
        sys.exit(0)
```
