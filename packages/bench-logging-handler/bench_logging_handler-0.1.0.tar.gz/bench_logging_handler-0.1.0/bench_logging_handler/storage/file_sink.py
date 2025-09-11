import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from .base import Sink


class FileSink(Sink):
    
    def __init__(
        self, 
        filename: str, 
        mode: str = "a", 
        encoding: str = "utf-8",
        formatter: Optional[Any] = None
    ):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self.formatter = formatter
        self._first_write = True  
        
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
    
    def write(self, data: Dict[str, Any]) -> None:
        
        try:
            if self.formatter:
                from ..core.schema import LogEvent
                event = LogEvent.from_dict(data)
                formatted_output = self.formatter.format(event)
                
                from ..core.formatters.json_formatter import JsonFormatter
                if isinstance(self.formatter, JsonFormatter):
                    formatted_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
                else:
                    formatted_data = formatted_output
            else:
                formatted_data = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            
            if not formatted_data.endswith('\n'):
                formatted_data += '\n'
            
            current_mode = self.mode if self._first_write else 'a'
            
            with open(self.filename, current_mode, encoding=self.encoding) as f:
                f.write(formatted_data)
            
            if self._first_write:
                self._first_write = False
                
        except Exception as e:
            error_msg = f"FileSink error: {str(e)}\n"
            current_mode = self.mode if self._first_write else 'a'
            with open(self.filename, current_mode, encoding=self.encoding) as f:
                f.write(error_msg)
            if self._first_write:
                self._first_write = False
    
    def close(self) -> None:
        pass
