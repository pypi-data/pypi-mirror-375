import os
from typing import Any, Dict
from ..schema import LogEvent


class LineFormatter:
    
    def format(self, event: LogEvent) -> str:
        timestamp = event.ts_iso.replace('T', ' ').replace('Z', '')
        
        level_name = event.level
        
        tag = event.logger or "root"
        
        file_info = ""
        if event.frame.file:
            filename = os.path.basename(event.frame.file)
            file_info = f" [{filename}:{event.frame.line}]"
        
        system_parts = []
        if event.system.pid > 0:
            system_parts.append(f"pid:{event.system.pid}")
        if event.system.thread_id > 0:
            system_parts.append(f"tid:{event.system.thread_id}")
        if event.system.hostname:
            system_parts.append(f"host:{event.system.hostname}")
        if event.system.python_version:
            system_parts.append(f"python:{event.system.python_version}")
        if event.system.platform:
            system_parts.append(f"platform:{event.system.platform}")
        
        system_info = f" ({' '.join(system_parts)})" if system_parts else ""
        
        main_line = f"{timestamp}  {level_name}/{tag}:{file_info}{system_info} {event.message}"
        
        if event.trace:
            trace_lines = []
            if event.trace.kind == "exc":
                trace_lines.append(f"    Exception: {event.trace.type}")
                if event.trace.message:
                    trace_lines.append(f"    Message: {event.trace.message}")
                
                if event.trace.frames:
                    trace_lines.append(f"    Traceback ({len(event.trace.frames)} frames):")
                    for i, frame in enumerate(event.trace.frames):
                        filename = os.path.basename(frame.file) if frame.file else "unknown"
                        file_info = f"{filename}:{frame.line}"
                        func_info = f" in {frame.func}" if frame.func else ""
                        code_info = f"\n        {frame.code.strip()}" if frame.code else ""
                        trace_lines.append(f"      {file_info}{func_info}{code_info}")
                
                if event.trace.text:
                    for line in event.trace.text.strip().split('\n'):
                        trace_lines.append(f"    {line}")
                        
            elif event.trace.kind == "stack":
                trace_lines.append(f"    Stack trace ({len(event.trace.frames)} frames):")
                for i, frame in enumerate(event.trace.frames):
                    filename = os.path.basename(frame.file) if frame.file else "unknown"
                    file_info = f"{filename}:{frame.line}"
                    func_info = f" in {frame.func}" if frame.func else ""
                    code_info = f"\n        {frame.code.strip()}" if frame.code else ""
                    trace_lines.append(f"      {file_info}{func_info}{code_info}")
            
            return main_line + "\n" + "\n".join(trace_lines)
        
        if event.bench:
            bench_lines = []
            if event.bench.start_time and not event.bench.end_time:
                bench_lines.append(f"    Benchmark started: {event.bench.id}")
            elif event.bench.end_time:
                duration = event.bench.duration or 0
                bench_lines.append(f"    Benchmark completed: {event.bench.id} ({duration:.3f}s)")
            
            return main_line + "\n" + "\n".join(bench_lines)
        
        return main_line
