import json
import os
import sys
from pathlib import Path

from .brain import get_llm_client
from .tools import execute_tool, tool_blueprints


def _load_system_prompt(workspace_path: str) -> str:
    system_path = Path(workspace_path).resolve() / "SYSTEM.md"
    try:
        return system_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Unable to load system prompt from {system_path}") from exc


def agent_loop(workspace_path: str):
    """Run the bounded agent loop against the target workspace."""
    print(f"🤖 HAL-9000 Engine online. Target workspace: {workspace_path}")

    target_model = os.environ.get("GROQ_MODEL")

    try:
        client = get_llm_client()
        system_prompt = _load_system_prompt(workspace_path)
    except Exception as exc:
        print(f"❌ Initialization Error: {exc}")
        sys.exit(1)

    goal = input("\nWhat coding goal should I execute in this repository?\n> ")
    if not goal.strip():
        print("Empty goal. Exiting loop.")
        return

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
                temperature=0.2,
            )
        except Exception as exc:
            print(f"❌ Groq API Communication Failure: {exc}")
            break

        assistant_message = response.choices[0].message
        full_history.append(assistant_message)
        if assistant_message.content:
            print(f"\n🤖 HAL Thought:\n{assistant_message.content}")

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
            print("\n🏁 Agent has halted execution loop (No further tools requested).")
            is_running = False

    if iteration >= max_iterations:
        print("\n⚠️ Loop halted automatically: Reached maximum safety iteration depth.")
