from __future__ import annotations

import importlib.resources
import json
import os
import re
import sys
from collections.abc import Iterator
from typing import Any

from .brain import get_llm_client
from .output import OutputMode, render
from .tools import ALL_GROQ_TOOLS, TOOL_REGISTRY


_MAX_ITERATIONS = 15
_HISTORY_LIMIT = 6
_RESPONSE_TAG = re.compile(
    r"<(?P<section>thinking|hal|output)>(?P<section_text>.*?)"
    r"</(?P=section)>|<tool name=\"(?P<tool_name>[^\"]+)\">"
    r"(?P<tool_arguments>.*?)</tool>",
    re.DOTALL,
)


def _load_system_prompt() -> str:
    try:
        resource = importlib.resources.files("harness").joinpath("SYSTEM.md")
        return resource.read_text(encoding="utf-8")
    except (OSError, ModuleNotFoundError, TypeError) as exc:
        raise RuntimeError(f"Unable to load the packaged SYSTEM.md prompt: {exc}") from exc


def _parse_response(text: str) -> Iterator[tuple[str, str, str | None]]:
    """Yield tagged sections and preserve text outside recognized tags."""
    position = 0
    for match in _RESPONSE_TAG.finditer(text):
        if match.start() > position:
            yield "hal", text[position : match.start()], None
        if match.group("section") is not None:
            yield match.group("section"), match.group("section_text"), None
        else:
            yield "tool", match.group("tool_arguments"), match.group("tool_name")
        position = match.end()
    if position < len(text):
        yield "hal", text[position:], None


def _execute_tool(name: str, argument_text: str) -> str:
    try:
        arguments = json.loads(argument_text)
    except json.JSONDecodeError as exc:
        return f"Tool failure: invalid JSON for '{name}': {exc}"
    if not isinstance(arguments, dict):
        return f"Tool failure: arguments for '{name}' must be a JSON object"

    function = TOOL_REGISTRY.get(name)
    if function is None:
        return f"Tool failure: unknown tool '{name}'"

    print(f"\n🔌 Action: Invoke '{name} ({arguments})'")
    try:
        authorization = input("Type Y/N to proceed: [Y] ").strip().upper()
    except (EOFError, KeyboardInterrupt):
        authorization = "N"
    if authorization not in {"", "Y"}:
        return "Tool execution declined by the operator."

    try:
        result = function(**arguments)
    except (ValueError, TypeError, RuntimeError, OSError) as exc:
        return f"Tool failure: {exc}"
    if not isinstance(result, str):
        return f"Tool failure: '{name}' returned a non-text result."
    return result


def _section_mode(section: str) -> OutputMode:
    if section == "thinking":
        return OutputMode.THINKING
    if section == "output":
        return OutputMode.MARKDOWN
    return OutputMode.HAL


def agent_loop(workspace_path: str, goal: str) -> None:
    """Run one bounded, one-response-per-turn agent conversation."""
    print(f"🤖 HAL-9000 Engine online. Target workspace: {workspace_path}")

    try:
        client = get_llm_client()
        system_prompt = _load_system_prompt()
    except Exception as exc:
        print(f"❌ Initialization Error: {exc}")
        sys.exit(1)

    function_specs = [spec["function"] for spec in ALL_GROQ_TOOLS]
    system_prompt += (
        "\n\nAvailable tools and their JSON argument schemas:\n"
        + json.dumps(function_specs, indent=2)
    )
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"Execute this goal step-by-step in {workspace_path}: {goal}",
        },
    ]

    for iteration in range(1, _MAX_ITERATIONS + 1):
        print(f"\n--- 🔄 [Turn {iteration}/{_MAX_ITERATIONS}] ---")
        try:
            response = client.chat.completions.create(
                messages=messages,
                model=os.environ.get("GROQ_MODEL"),
                max_tokens=512,
                temperature=0.2,
            )
        except Exception as exc:
            print(f"❌ Groq API Communication Failure: {exc}")
            break

        try:
            content = response.choices[0].message.content
        except (AttributeError, IndexError, KeyError, TypeError) as exc:
            print(f"❌ Groq response did not contain a message: {exc}")
            break
        if not isinstance(content, str) or not content:
            print("❌ Groq returned an empty response.")
            break

        messages.append({"role": "assistant", "content": content})
        tool_results: list[str] = []
        for section, text, tool_name in _parse_response(content):
            if section == "tool":
                result = _execute_tool(tool_name or "", text)
                tool_results.append(f"Tool '{tool_name}' result:\n{result}")
            elif text:
                render(text, _section_mode(section))

        if not tool_results:
            break
        messages.append(
            {
                "role": "user",
                "content": "\n\n".join(tool_results),
            }
        )
        messages = messages[:2] + messages[2:][-_HISTORY_LIMIT:]
    else:
        print("\n⚠️ Loop halted automatically: Reached maximum safety iteration depth.")
