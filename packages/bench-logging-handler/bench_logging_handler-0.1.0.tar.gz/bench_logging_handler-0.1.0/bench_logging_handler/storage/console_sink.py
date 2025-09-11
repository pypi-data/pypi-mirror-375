from __future__ import annotations
from typing import Any, Dict, TextIO
import sys
from ..core.formatters import LineFormatter
from ..core.schema import LogEvent


class ConsoleSink:
    def __init__(self, stream: TextIO = sys.stdout, formatter: LineFormatter = LineFormatter()):
        self.stream = stream
        self.formatter = formatter

    def write(self, event: Dict[str, Any]) -> None:
        try:
            log_event = LogEvent.from_dict(event)
            line = self.formatter.format(log_event)
            self.stream.write(line + "\n")
        except Exception:
            pass

    def flush(self) -> None:
        try:
            self.stream.flush()
        except Exception:
            pass

    def close(self) -> None:
        self.flush()
