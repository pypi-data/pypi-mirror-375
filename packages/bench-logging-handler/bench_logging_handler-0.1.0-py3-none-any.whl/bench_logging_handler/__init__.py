"""
Bench Logging Handler - A smart logging handler with structured output, benchmarking, and automatic stacktrace.

This package provides enhanced logging capabilities including:
- Structured logging with JSON output
- Built-in performance benchmarking
- Automatic stack trace filtering and formatting
- Multiple output sinks (console, file, etc.)

Example usage:
    import logging
    from bench_logging_handler import BenchHandler, ConsoleSink
    
    # Setup structured logging
    handler = BenchHandler(
        trace_levels=("ERROR", "CRITICAL"),
        sink=ConsoleSink()
    )
    
    logging.getLogger().addHandler(handler)
    logging.info("Hello, bench logging handler!")
"""

__version__ = "0.1.0"
__author__ = "imguno"
__email__ = "imguno0629@gmail.com"
__license__ = "MIT"

# Import main classes for easy access
from .core.handler import BenchLoggingHandler as BenchHandler
from .core.schema import LogLevel, LogEvent
from .storage.console_sink import ConsoleSink
from .storage.file_sink import FileSink
from .core.formatters import BoxFormatter, JsonFormatter, LineFormatter

# Keep original name for compatibility
BenchLoggingHandler = BenchHandler

__all__ = [
    "BenchHandler",
    "BenchLoggingHandler",  # for compatibility
    "LogLevel",
    "LogEvent", 
    "ConsoleSink",
    "FileSink",
    "BoxFormatter",
    "JsonFormatter", 
    "LineFormatter",
    "__version__",
]