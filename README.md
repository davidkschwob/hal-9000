====================================================================
EDUCATIONAL AGENT CODING HARNESS (ask-hal) - SYSTEM REPO LEDGER
====================================================================

An installable, out-of-repo CLI harness designed to run autonomous 
engineering execution loops against any local target Git repository. 
Optimized for cloud Groq and local Ollama architectures using strict 
ReAct patterns and optimized sliding prompt context windows.

--------------------------------------------------------------------
1. SYSTEM ARCHITECTURE & BLOCK BLUEPRINT
--------------------------------------------------------------------

+--------------------------------------------------------+

|               1. The Sandbox (Execution)               |
|  - Isolated workspace target directory context.        |
|  - Executes file-level operations & local shell cmds.  |
+---------------------------+----------------------------+
                            |
                            | (Executes code / reads files)
                            |
+---------------------------v----------------------------+

|               2. The Harness Loop (State)              |
|  - Python controller managing message history arrays.  |
|  - Enforces rolling sliding window to limit bloat.     |
+---------------------------+----------------------------+
                            |
                            | (Feeds structured text)
                            |
+---------------------------v----------------------------+

|               3. The Brain (LLM Engine)                |
|  - Reads System prompts, history & tool role arrays.   |
|  - Processes text via qwen-2.5-coder-32b (Temp 0.2).   |
+--------------------------------------------------------+

--------------------------------------------------------------------
2. COMPONENT DIRECTORY INDEX
--------------------------------------------------------------------

coding_agent_harness/
|-- pyproject.toml           # Package build spec & CLI entry script
|-- requirements.txt         # Flat runtime tracking copy of library constraints
|-- README.md                # THIS FILE: Current system state ledger
`-- src/
    `-- agent_harness/       # Primary package namespace folder
        |-- __init__.py      # Exposes high-level entry points
        |-- cli.py           # Evaluates target repo paths & loads profiles
        |-- agent.py         # Main ReAct loop controller & state engine
        |
        |-- brain/           # Model abstraction interface

        |   |-- __init__.py  # Exposes client factory shortcuts
        |   `-- client.py    # Authenticates & instantiates Groq connection
        |
        |-- sandbox/         # Host system task executor

        |   |-- __init__.py  # Exposes isolated execution wrappers
        |   `-- executor.py  # Runs terminal tests & catches stderr logs
        |
        `-- tools/           # Workspace discovery and injection suite
            |-- __init__.py  # Exposes tool blueprints & execution hooks
            |-- blueprints.py# JSON schemas declaring functional specifications
            `-- registry.py  # Maps JSON schemas to Python modules

--------------------------------------------------------------------
3. DEVELOPMENT STATUS LEDGER
--------------------------------------------------------------------

Fully Completed & Wired:
- Package Architecture: Fixed global namespace resolution and relative imports.
- Declarative Engine Entrypoint: Maps 'ask-hal' globally to agent_harness.cli:main.
- CLI Orchestrator: Captures dynamic target repo path via os.getcwd() and loads keys.
- Global Execution Controller: Foundations of ReAct loop engine built with a 6-turn maximum history sliding-window buffer.

Currently Missing / Under Active Construction:
- src/agent_harness/brain/client.py: Needs authenticated Groq client factory hook.
- src/agent_harness/tools/blueprints.py: Needs structural JSON schemas for search tools.
- src/agent_harness/tools/registry.py: Needs execution routing logic for workspace path tools.
- src/agent_harness/sandbox/executor.py: Needs subprocess handling for catching runtime errors.

--------------------------------------------------------------------
4. SYSTEM LIMITS & AGENT INSTRUCTIONS
--------------------------------------------------------------------

CRITICAL RUNTIME RULES FOR AGENT REFACTORING:
1. Context Bloat Mitigation: Maintain a maximum sliding window buffer of 6 messages at any given stage of code manipulation.
2. Absolute Structural Safety: Never reference modules globally outside of the agent_harness absolute root framework namespace.
3. Explicit Token Rules: All tools must return highly compressed structural descriptions. Do not return the entire body content of codebase directories or giant source scripts unless line limits are explicitly specified.
4. Isolate State Logic: Never let tool modules read conversation histories. Data properties must be fed explicitly downward from the primary orchestrator loop.
====================================================================
