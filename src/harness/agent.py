import os
import sys
import json
from .brain import get_llm_client

# Note: We will implement tools/registry and tools/blueprints next
# from .tools.registry import execute_tool, tool_blueprints


def agent_loop(workspace_path: str):
    """
    The core execution loop of the coding agent harness.
    Manages state turns and routes tools dynamically against the target workspace.
    """
    print(f"🤖 HAL-9000 Engine online. Target workspace: {workspace_path}")

    TARGET_MODEL = os.environ.get("GROQ_MODEL")

    # 1. Initialize our LLM engine wrapper
    try:
        client = get_llm_client()
    except Exception as e:
        print(f"❌ Initialization Error: {str(e)}")
        sys.exit(1)

    # 2. Ask the user for their development goal inside the repo
    goal = input("\nWhat coding goal should I execute in this repository?\n> ")
    if not goal.strip():
        print("Empty goal. Exiting loop.")
        return

    # 3. CRITICAL SYSTEM PROMPT: Establish absolute rules for the model
    system_prompt = (
        "OPERATIONAL PROTOCOL:\n"
        f"1. You are an autonomous software engineering agent operating on a project located at: {workspace_path}\n"
        "2. Break your goal down into small, iterative steps.\n"
        "3. You must continuously execute tools to search files, read snippets, or test changes.\n"
        "4. DO NOT assume code works. After editing any file, you MUST verify it via testing tools.\n"
        "5. Respond exclusively using provided tool calls when taking actions. If finished, explicitly tell the user."
    )

    # 4. Initialize History State Tracker
    # We store a "Cold Ledger" of the true sequence, but will pass a sliced slice to the model
    full_history = []

    # Establish anchors
    base_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Execute this goal step-by-step: {goal}"},
    ]

    is_running = True
    iteration = 0
    max_iterations = 15  # Strict breaker to prevent infinite loop API costs

    while is_running and iteration < max_iterations:
        iteration += 1
        print(f"\n--- 🔄 [Turn {iteration}/{max_iterations}] Reasoning Phase ---")

        # 5. Build the Optimized sliding prompt window (Last 6 chat turns max)
        active_prompt = list(base_messages)
        if len(full_history) > 6:
            active_prompt.extend(full_history[-6:])
        else:
            active_prompt.extend(full_history)

        try:
            # 6. Query the Brain (Using low temperature for deterministic code/logic decisions)
            # Dummy tool variable for now until blueprints are wired up
            available_tools = []  # will be replaced by tool_blueprints

            response = client.chat.completions.create(
                messages=active_prompt,
                model=TARGET_MODEL,
                # tools=available_tools, # Uncomment when tool schemas are ready
                temperature=0.2,
            )
        except Exception as e:
            print(f"❌ Groq API Communication Failure: {str(e)}")
            break

        assistant_message = response.choices[0].message
        full_history.append(assistant_message)

        # Print out what the AI is thinking to the terminal console
        if assistant_message.content:
            print(f"\n🤖 HAL Thought:\n{assistant_message.content}")

        # 7. Check if the model requested a Tool Action
        if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                print(f"🔌 Action: Invoking '{tool_call.function.name}'...")

                # Parse arguments from the model output
                tool_args = json.loads(tool_call.function.arguments)

                # Execute the tool and fetch result (passing the workspace_path context down)
                # observation = execute_tool(tool_call.function.name, tool_args, workspace_path)
                observation = "Tool outputs placeholder."  # Temporary mock

                # Log the observation straight back into the history loop
                full_history.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": observation,
                    }
                )
        else:
            # If the model didn't ask to fire a tool, it completed the prompt workflow
            print("\n🏁 Agent has halted execution loop (No further tools requested).")
            is_running = False

    if iteration >= max_iterations:
        print("\n⚠️ Loop halted automatically: Reached maximum safety iteration depth.")
