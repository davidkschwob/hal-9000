"""Render complete response sections in the terminal."""

from enum import Enum
import sys


class OutputMode(str, Enum):
    HAL = "hal"
    THINKING = "thinking"
    MARKDOWN = "markdown"
    RAW = "raw"


_COLORS = {
    OutputMode.HAL: "\033[91m",
    OutputMode.THINKING: "\033[93m",
}
_RESET = "\033[0m"


def render(text: str, mode: OutputMode = OutputMode.HAL) -> None:
    mode = OutputMode(mode)
    color = _COLORS.get(mode, "")
    if text:
        sys.stdout.write(color + text + (_RESET if color else ""))
        if not text.endswith("\n"):
            sys.stdout.write("\n")
        sys.stdout.flush()
