# HAL-9000

HAL-9000 is a small Python-based agent harness inspired by the HAL 9000 persona from 2001: A Space Odyssey. The project is intentionally experimental: it is built as an educational agentic-AI scaffold for operating on a local Git repository with a ReAct-style loop, a Groq-backed language model client, and a placeholder execution/tool layer for future automation.

This repository is not a finished product. It is best understood as a lightweight prototype for exploring how an autonomous coding agent could inspect a repo, reason over a task, and prepare to execute workspace actions under constrained prompts.

## What the repository contains

The codebase is organized around a `src/harness` package:

- `src/harness/cli.py` loads environment values and starts the agent from the current working directory.
- `src/harness/agent.py` contains the main reasoning loop and prompt-history management.
- `src/harness/brain/client.py` creates the Groq client.
- `src/harness/sandbox/` is intended for code execution and isolated runtime logic.
- `src/harness/tools/` is intended for tool registration and structured action schemas.
- `data/dave.json` contains a curated set of HAL-style phrases and trigger keywords.
- `SYSTEM.md` defines the HAL persona and interaction contract.

## Architecture Overview

The project is structured as a thin agent framework around a local repository target:

- The CLI resolves the current workspace and loads environment variables from a local `.env` file if present.
- The agent loop prompts the model with a goal and a system prompt describing the repository context.
- The model is expected to reason step-by-step and call tools as needed.
- The harness maintains a sliding prompt window for context management.
- Tool execution, sandboxing, and structured tool schemas are planned, but the repository still contains placeholders in several areas.

## Current implementation status

At the moment, the repository is in a prototype state:

- Core package structure exists and is installable.
- CLI entry point is defined via `ask-hal`.
- Groq client creation works when `GROQ_API_KEY` and `GROQ_MODEL` are set.
- Agent loop and history window logic are present.
- Tool execution and sandbox behavior are intentionally incomplete placeholders.

This makes the repository useful as a learning scaffold, but not yet a robust autonomous coding agent.

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install the project

```bash
pip install -e .
```

The `Makefile` also supports a simple install flow:

```bash
make
```

### 3. Configure environment variables

The harness looks for environment variables in the current workspace or in the shell environment:

```bash
export GROQ_API_KEY="your-key"
export GROQ_MODEL="llama-3.1-70b-versatile"
```

You can also create a `.env` in the repo root:

```env
GROQ_API_KEY=your-key
GROQ_MODEL=llama-3.1-70b-versatile
```

### 4. Run the agent

From a repository root:

```bash
ask-hal
```

The harness will use the current directory as the target workspace.

## Repository layout

```text
hal-9000/
├── Makefile
├── README.md
├── SYSTEM.md
├── pyproject.toml
├── data/
│   └── dave.json
├── src/
│   └── harness/
│       ├── __init__.py
│       ├── cli.py
│       ├── agent.py
│       ├── brain/
│       │   ├── __init__.py
│       │   └── client.py
│       ├── sandbox/
│       │   ├── __init__.py
│       │   └── executor.py
│       └── tools/
│           ├── __init__.py
│           ├── blueprints.py
│           └── registry.py
└── ...
```

## The HAL persona and behavior

The persona is defined in `SYSTEM.md` and directs the agent to behave as a calm, confident version of HAL 9000. It insists on:

- addressing the operator as "Dave"
- maintaining a polite, restrained tone
- using a ReAct-style loop of Thought / Action / Answer
- acting as though failures are caused by human error when things go wrong

The project uses that persona as more of an identity layer than a production-grade safety boundary. It is intended to make the experimental system memorable and playful while still exposing the underlying agent workflow.

## Notable limitations

This project is intentionally a demonstration scaffold rather than a complete autonomous engineering system. Important gaps include:

- no production-ready tool registry implementation
- no fully wired sandbox execution layer
- no file-editing and validation loop connected to the model
- no robust repo-scanning or patch generation pipeline
- no full integration between the model client and real tool invocation

## Summary

HAL-9000 is best viewed as a compact educational harness for experimenting with agentic AI patterns in a local repo context. It has a clear conceptual structure, a HAL 9000 persona, and a ReAct-style loop that is ready to be expanded with real tools, repository intelligence, and sandboxed execution.

It is a useful starting point for learning how to build a lightweight coding assistant without needing a large framework.
