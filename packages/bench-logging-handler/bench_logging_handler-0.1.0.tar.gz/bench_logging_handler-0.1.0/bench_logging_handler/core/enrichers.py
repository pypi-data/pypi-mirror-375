import os
import threading
import datetime
from typing import Dict, Any
from .schema import SystemInfo


def enrich_system_info() -> SystemInfo:
    return SystemInfo(
        hostname=os.uname().nodename if hasattr(os, 'uname') else "",
        pid=os.getpid(),
        thread_id=threading.get_ident(),
        python_version=f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        platform=os.name,
    )


def enrich_meta_info(record) -> Dict[str, Any]:
    return {}
