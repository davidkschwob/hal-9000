"""Dispatch model tool calls to implementations."""

from __future__ import annotations

from typing import Any

from .list_files import list_files


_TOOL_REGISTRY = {"list_files": list_files}


def execute_tool(
    tool_name: str, tool_args: dict[str, Any], workspace_path: str
) -> str:
    """Validate and execute a registered tool for the target workspace."""
    if tool_name not in _TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")
    if not isinstance(tool_args, dict):
        raise TypeError("Tool arguments must be a JSON object")
    if tool_args:
        raise ValueError(f"Unexpected arguments for {tool_name}: {sorted(tool_args)}")
    return _TOOL_REGISTRY[tool_name](workspace_path)
