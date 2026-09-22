# Copilot instructions for hal-9000

## Build, run, test, and lint

- Python 3.10 or newer is required.
- Create an environment and install the package in editable mode with:
  `python -m venv .venv && source .venv/bin/activate && pip install -e .`
- `make` runs the repository's only Make target, which installs the package with
  `pip install .`.
- Run the CLI from the repository that HAL should inspect:
  `ask-hal`
- Before running the CLI, provide `GROQ_API_KEY` and `GROQ_MODEL` in the
  environment or in a `.env` file in the target working directory.
- There is currently no committed test suite, test runner, or lint configuration.
  There is therefore no repository-defined full-test or single-test command.
  Do not add instructions that imply pytest, Ruff, or another tool is configured
  unless the repository adds that configuration.

## Architecture

- `src/harness/cli.py` is the console entry point. It uses the current working
  directory as the target workspace, loads that workspace's `.env`, and owns
  the persistent interactive prompt. Each non-empty goal starts one
  independent `agent_loop` run; `exit`, `quit`, EOF, and Ctrl-C end the session.
- `src/harness/brain/client.py` validates `GROQ_API_KEY` and `GROQ_MODEL` and
  constructs the Groq client. Model selection is passed separately by
  `agent.py` through the `GROQ_MODEL` environment value.
- `src/harness/agent.py` owns one bounded conversation loop per goal. It loads
  the packaged `src/harness/SYSTEM.md`, combines it with the user goal and
  target workspace, retains only the last six history messages, and makes at
  most 15 model iterations. A response without tool calls completes that goal;
  the CLI then returns to its prompt.
- Model tool schemas live in `src/harness/tools/blueprints.py`; implementations
  are registered in `src/harness/tools/registry.py`. Tool calls are decoded from
  JSON, dispatched with the target workspace, and returned as `role: tool`
  messages using the model-provided tool-call ID.
- The implemented `list_files` tool runs `git ls-files` in the target workspace
  and deliberately raises a `RuntimeError` for Git failures, so a non-Git
  directory is not silently treated as empty. HAL-themed fallback/error text is
  loaded from `data/dave.json` when available.
- `src/harness/sandbox/` is scaffolded and exported, but is not wired into the
  current agent loop. File editing and shell execution are not available tools.
- `SYSTEM.md` at the repository root is the standalone prompt/example, while
  `src/harness/SYSTEM.md` is the prompt packaged and loaded at runtime. Keep
  those files intentionally synchronized when changing the agent contract.

## Repository-specific conventions

- Keep the execution boundary explicit: tools receive the workspace path,
  validate their arguments, return bounded serializable text, and must not
  assume the process's current directory is the target.
- When adding a tool, update all three surfaces: its schema in
  `tools/blueprints.py`, its implementation, and `_TOOL_REGISTRY` in
  `tools/registry.py`. Reject unknown tools and unexpected arguments rather than
  silently ignoring them.
- Preserve the Groq tool-call message shape, especially `tool_call_id`, when
  feeding observations back into the conversation.
- Keep model-independent tests possible by injecting or faking the client;
  tests must not require a live API key or network access.
- Runtime failures should be surfaced as explicit initialization, API, or tool
  failures. Do not convert Git errors, invalid JSON, or unsupported tool names
  into successful-looking empty results.
- The HAL persona is presentation behavior, not a security boundary. Safety
  decisions belong in validation, path/process boundaries, and explicit tool
  permissions.
- Package data matters: `src/harness/SYSTEM.md` is included through
  `[tool.setuptools.package-data]` in `pyproject.toml`; preserve that packaging
  configuration when relocating or renaming prompt resources.
