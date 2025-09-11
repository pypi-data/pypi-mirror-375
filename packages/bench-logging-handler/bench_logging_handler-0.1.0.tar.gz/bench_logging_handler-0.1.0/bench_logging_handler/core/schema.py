from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional, Any, Dict, List, Literal, Type, Tuple
import datetime, time, uuid, traceback, logging
import os
import threading

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "BENCH_START", "BENCH_END"]
TraceKind = Literal["exc", "stack", "manual"]

_NAME_TO_LEVEL = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "BENCH_START": 15,
    "BENCH_END": 16,
}

def normalize_level(level_val: Any) -> Tuple[LogLevel, int]:
    if isinstance(level_val, int):
        name = logging.getLevelName(level_val)
        if isinstance(name, str) and name in _NAME_TO_LEVEL:
            return name, level_val 
        return "INFO", logging.INFO
    if isinstance(level_val, str):
        name = level_val.upper()
        if name in _NAME_TO_LEVEL:
            return name, _NAME_TO_LEVEL[name]  
    return "INFO", logging.INFO

@dataclass
class Frame:
    file: str
    line: int
    func: str
    code: Optional[str] = None

    @classmethod
    def from_dict(cls: Type["Frame"], d: Dict[str, Any]) -> "Frame":
        return cls(
            file=d.get("file", ""),
            line=int(d.get("line", 0)),
            func=d.get("func", ""),
            code=d.get("code"),
        )

@dataclass
class TraceContext:
    kind: TraceKind
    label: str
    type: str
    message: str
    frames: List[Frame] = field(default_factory=list)
    text: Optional[str] = None

    @classmethod
    def from_dict(cls: Type["TraceContext"], d: Dict[str, Any]) -> "TraceContext":
        return cls(
            kind=d.get("kind", "manual"),
            label=d.get("label", ""),
            type=d.get("type", ""),
            message=d.get("message"),
            frames=[Frame.from_dict(x) for x in d.get("frames", [])],
            text=d.get("text"),
        )

@dataclass
class SystemInfo:
    hostname: str
    pid: int
    thread_id: int
    python_version: str
    platform: str

    @classmethod
    def from_dict(cls: Type["SystemInfo"], d: Dict[str, Any]) -> "SystemInfo":
        return cls(
            hostname=d.get("hostname", ""),
            pid=d.get("pid", -1),
            thread_id=d.get("thread_id", -1),
            python_version=d.get("python_version", ""),
            platform=d.get("platform", ""),
        )

@dataclass
class BenchInfo:
    id: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None


    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls: Type["BenchInfo"], d: Dict[str, Any]) -> "BenchInfo":
        return cls(
            id=d.get("id", ""),
            start_time=d.get("start_time"),
            end_time=d.get("end_time"),
            duration=d.get("duration"),
        )

@dataclass
class LogEvent:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ts_unix: float = field(default_factory=time.time)
    ts_iso: str = field(
        default_factory=lambda: datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    )

    level: LogLevel = "INFO"
    levelno: int = logging.INFO 
    logger: str = ""
    message: str = ""

    frame: Frame = field(default_factory=lambda: Frame(file="", line=0, func=""))
    system: SystemInfo = field(default_factory=lambda: SystemInfo(hostname="", pid=0, thread_id=0, python_version="", platform=""))

    trace: Optional[TraceContext] = None
    bench: Optional[BenchInfo] = None
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def file(self) -> str: return self.frame.file

    @property
    def line(self) -> int: return self.frame.line

    @property
    def func(self) -> str: return self.frame.func

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls: Type["LogEvent"], d: Dict[str, Any]) -> "LogEvent":
        ts_unix = float(d.get("ts_unix", time.time()))
        ts_iso = d.get("ts_iso") or datetime.datetime.utcfromtimestamp(ts_unix).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        level_name, level_no = normalize_level(d.get("level", d.get("levelno", "INFO")))
        trace_d = d.get("trace")
        bench_d = d.get("bench")
        
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            ts_unix=ts_unix,
            ts_iso=ts_iso,
            level=level_name,
            levelno=int(d.get("levelno", level_no)),
            logger=d.get("logger", ""),
            message=d.get("message", ""),
            frame=Frame.from_dict(d.get("frame", {})),
            system=SystemInfo.from_dict(d.get("system", {})),
            trace=TraceContext.from_dict(trace_d) if trace_d else None,
            bench=BenchInfo.from_dict(bench_d) if bench_d else None,
            meta=d.get("meta") or {},
        )
