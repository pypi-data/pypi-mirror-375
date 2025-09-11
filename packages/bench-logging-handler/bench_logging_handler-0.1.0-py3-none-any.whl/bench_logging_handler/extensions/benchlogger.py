import logging
import time
import threading
import uuid
from typing import Dict, Optional, Tuple
from ..core.schema import BenchInfo
from .base import create_log_record


_bench_storage: Dict[str, float] = {}
_bench_lock = threading.Lock()


def benchstart(message: str = "", bench_id: str = "", task_name: str = "") -> str:
    if not bench_id:
        bench_id = str(uuid.uuid4())[:8]
    
    start_time = time.time()
    
    with _bench_lock:
        _bench_storage[bench_id] = start_time
    
    # 현재는 시간만 측정되고 있음
    bench_info = BenchInfo(
        id=bench_id,
        start_time=start_time
    )
    
    display_name = task_name or bench_id
    
    record = create_log_record(
        level=15,  # BENCH_START
        levelname="BENCH_START",
        message=message or f"Benchmark started: {display_name}"
    )
    record.levelname = "BENCH_START"
    record.bench = bench_info
    
    logging.getLogger().handle(record)
    return bench_id


def benchend(message: str = "",bench_id: str = None, task_name: str = "") -> None:
    if (bench_id is None): 
        logging.warning("Benchmark ID is not provided")
        return
    """벤치마킹 종료"""
    end_time = time.time()
    
    with _bench_lock:
        start_time = _bench_storage.pop(bench_id, None)
    
    if start_time is None:
        logging.warning(f"Benchmark '{bench_id}' was not started")
        return
    
    duration = end_time - start_time
    
    bench_info = BenchInfo(
        id=bench_id,
        start_time=start_time,
        end_time=end_time,
        duration=duration
    )
    
    display_name = task_name or bench_id
    
    record = create_log_record(
        level=16,  # BENCH_END
        levelname="BENCH_END",
        message=message or f"Benchmark ended: {display_name} (duration: {duration:.4f}s)"
    )
    record.levelname = "BENCH_END"
    record.bench = bench_info
    
    logging.getLogger().handle(record)


def add_bench_methods():
    print("add_bench_methods")
    """logging 모듈에 benchstart, benchend 메서드 추가"""
    logging.benchstart = benchstart
    logging.benchend = benchend
