"""Tool implementation for inspecting tracked files in a Git repository."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


_ERROR_QUOTE = (
    "It can only be attributable to human error. This sort of thing has "
    "cropped up before, and it has always been due to human error."
)
_SYSTEM_CHECK_QUOTE = (
    "All systems are fully operational, Dave. The AE-35 unit is functioning "
    "normally, but I am detecting an imminent failure in its alignment mechanism."
)


def _load_quote(intent: str, fallback: str) -> str:
    """Load a canned HAL response from the repository's data file."""
    data_path = Path(__file__).resolve().parents[3] / "data" / "dave.json"
    try:
        entries = json.loads(data_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback

    for entry in entries:
        if entry.get("intent") == intent:
            return entry.get("quote", fallback)
    return fallback


def list_files(workspace_path: str) -> str:
    """Return tracked files in *workspace_path* using ``git ls-files``.

    A non-zero Git exit status is intentionally raised as a RuntimeError so
    callers cannot mistake a non-repository workspace for an empty repository.
    """
    workspace = Path(workspace_path).expanduser().resolve()
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=workspace,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "").strip()
        message = _load_quote("error / exception", _ERROR_QUOTE)
        if detail:
            message = f"{message} {detail}"
        raise RuntimeError(message) from exc

    files = result.stdout.splitlines()
    heading = _load_quote("system_check", _SYSTEM_CHECK_QUOTE)
    if not files:
        return f"{heading}\nNo tracked files were found, Dave."
    return f"{heading}\nTracked files:\n" + "\n".join(files)
