import logging
import inspect
from typing import Optional


def create_log_record(
    level: int,
    levelname: str,
    message: str,
    logger_name: Optional[str] = None,
    exc_info: Optional[tuple] = None
) -> logging.LogRecord:
    frame = inspect.currentframe().f_back.f_back
    pathname = frame.f_code.co_filename
    lineno = frame.f_lineno
    funcname = frame.f_code.co_name
    
    if logger_name is None:
        logger_name = logging.getLogger().name
    
    record = logging.LogRecord(
        name=logger_name,
        level=level,
        pathname=pathname,
        lineno=lineno,
        msg=message,
        args=(),
        exc_info=exc_info
    )
    
    record.funcName = funcname
    
    return record
