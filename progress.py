from __future__ import annotations

import sys
from typing import Optional


class ProgressBar:


    def __init__(self, total: int, label: str = "", width: int = 30, stream=None):
        self.total = max(total, 0)
        self.label = label
        self.width = width
        self.current = 0
        self.stream = stream or sys.stdout
        self._last_rendered_len = 0

    def update(self, amount: int = 1) -> None:
        self.current += amount
        self._render()

    def set(self, value: int) -> None:
        self.current = value
        self._render()

    def _render(self) -> None:
        if not self.stream.isatty():
            return

        if self.total > 0:
            fraction = min(self.current / self.total, 1.0)
            filled = int(self.width * fraction)
            bar = "#" * filled + "-" * (self.width - filled)
            line = f"\r{self.label} [{bar}] {self.current}/{self.total} ({fraction * 100:5.1f}%)"
        else:
            line = f"\r{self.label} {self.current} processed..."

        padding = max(0, self._last_rendered_len - len(line))
        self.stream.write(line + (" " * padding))
        self.stream.flush()
        self._last_rendered_len = len(line)

    def finish(self) -> None:
        if self.stream.isatty():
            self.stream.write("\n")
            self.stream.flush()
