# HAL-9000

HAL-9000 is an educational Python agent harness for experimenting with an LLM-driven coding assistant in a local Git repository.

The project combines a Groq chat client, a bounded agent loop, a HAL-inspired system prompt, and an in-progress tool layer. It is a prototype rather than a production-ready autonomous coding agent.

## Status

The core harness is available, but tool execution is not wired into the agent yet.

| Area | Current state |
| --- | --- |
| Python package and CLI | Available through the `ask-hal` command |
| LLM client | Groq client configured from environment variables |
| Agent loop | Bounded to 15 iterations with a six-message history window |
| Tool schemas | Planned in `tools/blueprints.py` |
| Tool registry | Planned in `tools/registry.py` |
| Sandbox execution | Scaffolded, not integrated |
| File inspection and editing | Not yet implemented |

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

HAL prints the target workspace, asks for a coding goal, and sends the goal to the model. The current agent loop can display model output and recognize tool-call responses, but it returns a placeholder observation instead of executing a real tool.

## How it works

1. `harness.cli` resolves the current working directory and loads `.env` values.
2. `harness.agent` initializes the LLM client and prompts for a development goal.
3. The agent builds a system prompt containing the workspace path and operating rules.
4. The loop sends the prompt to Groq for up to 15 iterations.
5. Recent history is retained in a sliding six-message window.
6. Tool calls are detected, but execution is currently mocked.

The persona and response contract are documented in [`SYSTEM.md`](SYSTEM.md). The sample HAL phrases and trigger keywords are stored in [`data/dave.json`](data/dave.json).

## Implementing the first real tool

The next useful milestone is a read-only repository inspection tool. It would give the model a safe, testable capability before file mutation or shell execution is introduced.

### Recommended sequence

1. **Define a tool schema** in `src/harness/tools/blueprints.py`.
   - Start with a tool such as `list_files` or `read_file`.
   - Describe its name, purpose, and JSON arguments in the format expected by Groq tool calling.
   - Constrain paths to the target workspace and define useful error responses.

2. **Implement the function** in a dedicated module under `src/harness/tools/`.
   - Accept the workspace path explicitly.
   - Resolve paths safely and reject paths outside the workspace.
   - Return bounded, serializable text rather than raw exceptions.

3. **Register the function** in `src/harness/tools/registry.py`.
   - Map the schema name to its Python implementation.
   - Reject unknown tool names.
   - Validate and parse JSON arguments before dispatch.

4. **Wire the tool into `agent.py`.
   - Replace `available_tools = []` with the exported tool schemas.
   - Uncomment the `tools=available_tools` argument in the Groq request.
   - Replace the `"Tool outputs placeholder."` value with `execute_tool(...)`.
   - Preserve the tool-call ID when appending the observation to history.

5. **Verify the execution loop.**
   - Add unit tests for valid paths, invalid paths, missing arguments, and unknown tools.
   - Test that a tool result is sent back to the model with the correct tool-call ID.
   - Add an integration test using a fake client so tests do not require a live API key.

After a read-only tool is reliable, add file editing and command execution separately. Each should have explicit safety rules, bounded output, clear failure messages, and tests before being exposed to the model.

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
│       ├── blueprints.py      # Planned tool schemas
│       └── registry.py         # Planned tool dispatch
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
