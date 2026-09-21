import json
import os
import sys
import importlib.resources
from pathlib import Path

from .brain import get_llm_client
from .tools import execute_tool, tool_blueprints


def _load_system_prompt() -> str:
    try:
        ref = importlib.resources.files("harness").joinpath("SYSTEM.md")
        system_md = ref.read_text(encoding="utf-8")
        return system_md
    except:
        print(
              "[WARN] SYSTEM.md not loaded from module resource path. "
              "Defaulting to a generic prompt."
              )
        return(
            "Your are a helpful coding agent. Inspect the target repository "
            "carefully and explain failures clearly."
            )

def _serialize_message(message):
    if hasattr(message,"model_dump"):
        return message.model_dump(exclude_none=True)
    if hasattr(message,"dict"):
        return message.dict(exclude_none=True)
    return message
    

    
def agent_loop(workspace_path: str):
    """Run the bounded agent loop against the target workspace."""
    print(f"🤖 HAL-9000 Engine online. Target workspace: {workspace_path}")

    target_model = os.environ.get("GROQ_MODEL")
    max_tokens = os.environ.get("GROQ_MAX_TOKENS")

    try:
        client = get_llm_client()
        system_prompt = _load_system_prompt()
    except Exception as exc:
        print(f"❌ Initialization Error: {exc}")
        sys.exit(1)

    goal = input("[me]")

    full_history = []
    base_messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Execute this goal step-by-step in {workspace_path}: {goal}"
            ),
        },
    ]

    is_running = True
    iteration = 0
    max_iterations = 15

    while is_running and iteration < max_iterations:
        iteration += 1
        print(f"\n--- 🔄 [Turn {iteration}/{max_iterations}] Reasoning Phase ---")
        active_prompt = list(base_messages)
        active_prompt.extend(full_history[-6:])

        try:
            response = client.chat.completions.create(
                messages=active_prompt,
                model=target_model,
                tools=tool_blueprints,
                max_tokens=512,
                temperature=0.2,
            )
        except Exception as exc:
            print(f"❌ Groq API Communication Failure: {exc}")
            break

        assistant_message = response.choices[0].message
        full_history.append(_serialize_message(assistant_message))

        if assistant_message.content:
            print(f"[hal] {assistant_message.content}")

        if getattr(assistant_message, "tool_calls", None):
            for tool_call in assistant_message.tool_calls:
                print(f"🔌 Action: Invoking '{tool_call.function.name}'...")
                try:
                    tool_args = json.loads(tool_call.function.arguments or "{}")
                    observation = execute_tool(
                        tool_call.function.name, tool_args, workspace_path
                    )
                except (ValueError, TypeError, json.JSONDecodeError, RuntimeError) as exc:
                    observation = f"Tool failure: {exc}"
                    print(f"❌ {observation}")
                full_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": observation,
                    }
                )
        else:
            print("[hal ] ...")
            # is_running = False

    if iteration >= max_iterations:
        print("\n⚠️ Loop halted automatically: Reached maximum safety iteration depth.")
