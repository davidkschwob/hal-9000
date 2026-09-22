# HAL-9000

HAL-9000 is an educational Python agent harness for experimenting with an LLM-driven coding assistant in a local Git repository.

The project combines a Groq chat client, a bounded agent loop, a HAL-inspired system prompt, and an in-progress tool layer. It is a prototype rather than a production-ready autonomous coding agent.

## Status

The harness is working as a small, modular tool-enabled agent loop. Tool definitions are now organized under `src/harness/tools/` as independent modules rather than a single monolithic block.

| Area | Current state |
| --- | --- |
| Python package and CLI | Available through the `ask-hal` command |
| LLM client | Groq client configured from environment variables |
| Agent loop | Bounded to 15 iterations with a six-message history window |
| Tool discovery | Modules under `src/harness/tools/` are auto-discovered via `__init__.py` |
| Tool implementations | Split into individual modules with Pydantic-backed JSON schemas |
| Sandbox execution | Scaffolded, not integrated |
| File inspection and editing | Read-only repository inspection is implemented through tool modules; broader mutation tooling is still future work |

## Requirements

- Python 3.10 or later
- A Groq API key
- A Groq model name

## Installation

Create and activate a virtual environment, then install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

The included `Makefile` provides the shorter equivalent:

```bash
make
```

## Configuration

Set the required environment variables in your shell or in a `.env` file in the working directory:

```env
GROQ_API_KEY=your-api-key
GROQ_MODEL=your-model-name
```

`GROQ_API_KEY` is used to create the Groq client. `GROQ_MODEL` is passed to the chat completion request. The application exits during startup when either value is missing.

## Run HAL

Run the command from the repository you want the harness to work with:

```bash
ask-hal
```

HAL prints the target workspace and opens an interactive prompt. Enter a coding
goal to run one bounded agent conversation, then enter another goal when it
finishes. Blank inputs are ignored; `exit`, `quit`, EOF, or Ctrl-C ends the
session.

## How it works

1. `src/harness/cli.py` resolves the current working directory and loads `.env` values.
2. `src/harness/cli.py` reads goals in an interactive loop and starts one agent run per goal.
3. The agent builds a system prompt containing the workspace path and operating rules.
4. The loop sends the prompt to Groq for up to 15 iterations.
5. Recent history is retained in a sliding six-message window.
6. Tool modules under `src/harness/tools/` are auto-discovered and passed to the model as callable Groq functions.

The persona and response contract are documented in [`SYSTEM.md`](SYSTEM.md). The sample HAL phrases and trigger keywords are stored in [`data/dave.json`](data/dave.json).

## Tool architecture

The tool layer is intentionally split into small modules so each capability can be defined, tested, and expanded independently.

- `src/harness/tools/__init__.py` discovers modules that expose `GROQ_TOOL_SPEC` and `execute`, then exports them to the agent.
- Each tool has a Pydantic schema that defines the JSON arguments the model is allowed to emit.
- `src/harness/agent.py` sends the discovered specs to Groq and dispatches model output using the matching execution function.

A good rule of thumb is: the schema describes the contract, and the `execute()` function enforces the runtime behavior.

## Provisioning a new tool

Create a new Python module under `src/harness/tools/` and define a schema using `pydantic.BaseModel`.

```python
from __future__ import annotations

from pydantic import BaseModel, Field


class MyToolSchema(BaseModel):
    target: str = Field(..., description="Path or identifier the tool should inspect.")
    limit: int = Field(default=25, description="Maximum number of results to return.")


GROQ_TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "my_tool",
        "description": "Inspect a target and return a bounded result summary.",
        "parameters": MyToolSchema.model_json_schema(),
    },
}


def execute(target: str, limit: int = 25) -> str:
    """Perform the tool's work and return a serializable string result."""
    items = ["example", "result", "record"]
    return "\n".join(items[:limit]) if target else "No target provided."
```

The important parts are:

1. Use a `BaseModel` so the tool contract is explicit and validated.
2. Put the schema in `GROQ_TOOL_SPEC["function"]["parameters"]` using `model_json_schema()`.
3. Keep the `execute()` function signature aligned with the model schema fields.
4. Return plain text or bounded structured output, never raw exceptions.
5. Keep the tool read-only unless you intentionally want mutation or shell behavior.

If you add a tool module with a `GROQ_TOOL_SPEC` and `execute` function, the package loader will pick it up automatically. That means new capabilities can be added without rewriting the central dispatch code.

## Repository layout

```text
hal-9000/
├── data/
│   └── dave.json              # HAL-style phrases and trigger keywords
├── src/harness/
│   ├── cli.py                 # Console entry point
│   ├── agent.py               # Bounded LLM/ReAct-style loop
│   ├── brain/
│   │   └── client.py          # Groq client initialization
│   ├── sandbox/
│   │   └── executor.py        # Planned execution layer
│   └── tools/
│       ├── __init__.py        # Discovers tool modules and exports available specs
│       ├── git_lister.py      # Git-oriented repository inspection helper
│       └── git_viewer.py      # Git-oriented file inspection helper
├── SYSTEM.md                  # Persona and interaction rules
├── Makefile
├── pyproject.toml
└── README.md
```

## Development notes

This project is intentionally small and framework-light. The current implementation is a foundation for learning about:

- prompt construction and context windows
- model tool calling
- tool validation and dispatch
- sandbox boundaries
- testing agent workflows without depending on a live model

Contributions should keep the execution boundary explicit and should not treat the HAL persona as a security mechanism.

