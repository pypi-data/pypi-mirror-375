import logging
import atexit
import os
from .builder import record_to_event
from ..storage.console_sink import ConsoleSink
from ..storage.file_sink import FileSink
from ..storage.base import Sink
from typing import Optional

class BenchLoggingHandler(logging.Handler):
    def __init__(
        self, 
        trace_levels=("ERROR","CRITICAL"),
        sink: Optional[Sink] = None,
        ):
        super().__init__()
        self.trace_levels = tuple(l.upper() for l in trace_levels)
        self.sink: Sink = sink or ConsoleSink()
        
        from ..extensions.benchlogger import add_bench_methods
        add_bench_methods()

    def set_sink(self, sink: Sink) -> None:
        self.sink = sink

    def emit(self, record: logging.LogRecord):
        try:
            event = record_to_event(record, trace_levels=self.trace_levels)
            self.sink.write(event.to_dict())
        except Exception:
            self.handleError(record)