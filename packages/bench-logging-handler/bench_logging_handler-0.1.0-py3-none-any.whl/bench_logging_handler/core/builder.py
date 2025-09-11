import os, sys, traceback, logging, datetime, inspect, threading
from pathlib import Path
from typing import Sequence, Optional, Iterable
from .schema import LogEvent, Frame, TraceContext, LogLevel, _NAME_TO_LEVEL, BenchInfo
from .enrichers import enrich_system_info, enrich_meta_info


def _detect_my_root() -> str:
    here = Path(__file__).resolve()
    my_root = here.parent.parent
    return str(my_root)

_MY_ROOT = _detect_my_root()

def _is_excluded_path(path: str, exclude_logging: bool = True) -> bool:
    if not path:
        return False
    p = os.path.normpath(path)

    if exclude_logging and (os.path.sep + "logging" + os.path.sep) in p:
        return True
    if p.startswith(_MY_ROOT + os.path.sep):
        return True
    return False


def _filter_frames(frames: Iterable[traceback.FrameSummary], exclude_logging: bool = True, max_frames: Optional[int] = None):
    """
    Library Path Filtering
    """
    filtered = [f for f in frames if not _is_excluded_path(f.filename, exclude_logging)]
    if max_frames is not None and len(filtered) > max_frames:
        return filtered[-max_frames:]
    return filtered


def record_to_event(
    record: logging.LogRecord,
    trace_levels: Sequence[LogLevel] = ("ERROR", "CRITICAL"),
    stack_depth: int = 6,
) -> LogEvent:

    frame = Frame(file=record.pathname, line=record.lineno, func=record.funcName, code=None)
    trace_ctx: Optional[TraceContext] = None

    should_trace =record.levelname.upper() in trace_levels or "BENCH" in trace_levels and record.levelname.upper() in ("BENCH_START", "BENCH_END")
    
    if should_trace:
        if record.exc_info:
            et, ev, tb = record.exc_info
            raw = traceback.extract_tb(tb)
            userish = _filter_frames(raw, max_frames=stack_depth)

            frames = [Frame(file=f.filename, line=f.lineno, func=f.name, code=f.line)
                      for f in userish]

            exc_type_name = getattr(et, "__name__", str(et))
            formatted_text = "".join(traceback.format_list(userish) +
                                     traceback.format_exception_only(et, ev))

            trace_ctx = TraceContext(
                kind="exc",
                label=exc_type_name,
                type=exc_type_name,
                message=str(ev),
                frames=frames,
                text=formatted_text,
            )
        else:
            raw_stack = traceback.extract_stack()[:-1]
            userish = _filter_frames(raw_stack, max_frames=stack_depth)

            frames = [Frame(file=f.filename, line=f.lineno, func=f.name, code=f.line)
                      for f in userish]

            if (len(frames) > 0):
                trace_ctx = TraceContext(
                    kind="stack",
                    label=f"stack/{record.name}",
                    type="stack",
                    message=None,
                    frames=frames,
                    text="".join(traceback.format_list(userish)) if userish else None,
                )
            else:
                trace_ctx = None

    system = enrich_system_info()
    meta = enrich_meta_info(record)
    
    bench_info = None
    if hasattr(record, 'bench') and record.bench:
        bench_info = record.bench

    return LogEvent(
        ts_unix=record.created,
        ts_iso=datetime.datetime.utcfromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        level=record.levelname,
        levelno=record.levelno,
        logger=record.name,
        message=record.getMessage(),
        frame=frame,
        system=system,
        trace=trace_ctx,
        bench=bench_info,
        meta=meta,
    )
