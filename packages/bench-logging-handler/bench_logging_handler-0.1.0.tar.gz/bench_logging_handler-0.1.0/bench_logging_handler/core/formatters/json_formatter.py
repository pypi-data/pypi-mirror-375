import json
from typing import Any, Dict
from ..schema import LogEvent


class JsonFormatter:
    
    def __init__(self, indent: int = None, ensure_ascii: bool = False):
        self.indent = indent
        self.ensure_ascii = ensure_ascii
    
    def format(self, event: LogEvent) -> str:
        event_dict = event.to_dict()
        if self.indent is None:
            json_str_compact = json.dumps(event_dict, ensure_ascii=self.ensure_ascii)
            if len(json_str_compact) <= 120:
                return json_str_compact
            else:
                return json.dumps(event_dict, indent=2, ensure_ascii=self.ensure_ascii)
        else:
            return json.dumps(event_dict, indent=self.indent, ensure_ascii=self.ensure_ascii)
