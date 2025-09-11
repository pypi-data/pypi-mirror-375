# pylogboard/formatters/stacked_box_formatter.py
from __future__ import annotations
import os
import re
from typing import Any, Dict, List, Literal, Optional
from ..schema import LogEvent

_PathStyle = Literal["base", "full"]

_LEVEL_THEME_16 = {
    "CRITICAL":    {"fg": "97",  "square_bg": "41"}, 
    "ERROR":       {"fg": "97",  "square_bg": "101"}, 
    "WARNING":     {"fg": "30",  "square_bg": "103"}, 
    "INFO":        {"fg": "30",  "square_bg": "104"}, 
    "DEBUG":       {"fg": "30",  "square_bg": "47"},  
    "BENCH_START": {"fg": "30",  "square_bg": "106"}, 
    "BENCH_END":   {"fg": "30",  "square_bg": "105"}, 
}

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s or "")

class BoxFormatter:
    def __init__(
        self,
        *,
        use_color: bool = True,
        path_style: _PathStyle = "base",
        width: int = 120,           
        meta_keys: Optional[List[str]] = None,  
        show_system: bool = True,
        show_meta: bool = True,
        show_bench: bool = True,
        show_trace: bool = True,
        trace_show_text: bool = False,
        tabsize: int = 2,
        bold_level: bool = True,
        show_level_square: bool = True,
        header_gap: int = 2,        
    ):
        self.use_color = use_color
        self.path_style = path_style
        self.width = max(60, width)
        self.inner = self.width - 2
        self.meta_keys = meta_keys
        self.show_system = show_system
        self.show_meta = show_meta
        self.show_bench = show_bench
        self.show_trace = show_trace
        self.trace_show_text = trace_show_text
        self.tabsize = max(1, tabsize)
        self.bold_level = bold_level
        self.show_level_square = show_level_square
        self.header_gap = max(1, header_gap)

    def format(self, e: LogEvent) -> str:
        W, IN = self.width, self.inner
        out: List[str] = []


        out.append("┌" + "─" * (W - 2) + "┐")

        logger_line = self._sanitize(e.logger or "root")
        out.extend(self._box_multiline(self._wrap(logger_line, IN - 1), pad_left=1))

       
        level = (e.level or "").upper()
        err_label = level
        if e.trace and e.trace.kind == "exc" and e.trace.type:
            err_label = e.trace.type

        left = self._level_square(level) + (" " if self.show_level_square else "")
        left += self._level_text(level) + "  " + err_label

        where = f"{self._format_path(e.frame.file)} / {e.frame.func}:{e.frame.line}"

        out.extend(self._box_left_right_stacked(left, where, IN, gap=self.header_gap))

        
        ts = (e.ts_iso or "").replace("T", " ").replace("Z", "")
        out.append(self._box(self._right(ts, IN)))

       
        out.append("├" + "─" * (W - 2) + "┤")

        for m in self._wrap(self._sanitize(e.message or ""), IN - 1):
            out.append(self._box(" " + m))

       
        tails = self._tails(e)
        if tails:
            out.append("├" + "─" * (W - 2) + "┤")
            out.append(self._box(" context"))
            for t in tails:
                for line in self._wrap(t, IN - 2):
                    out.append(self._box(" " + line))

       
        if self.show_trace and e.trace:
            out.append("├" + "─" * (W - 2) + "┤")
            t = e.trace
            if t.kind == "exc":
                out.append(self._box(" Traceback (most recent call last):"))
                for i, fr in enumerate(t.frames or []):
                    file_path = self._format_path(fr.file) if fr.file else "<unknown>"
                    func_name = fr.func if fr.func else "<module>"
                    line_num = fr.line if fr.line else 0
                    
                    frame_line = f"  File \"{file_path}\", line {line_num}, in {func_name}"
                    for wl in self._wrap(frame_line, IN - 2):
                        out.append(self._box(" " + wl))
                    
                    if fr.code:
                        code_line = str(fr.code).strip("\n")
                        if code_line:
                            code_display = f"    {code_line}"
                            for cl in self._wrap(code_display, IN - 2):
                                out.append(self._box(" " + cl))
                
                if t.type and t.message:
                    exc_line = f"{t.type}: {t.message}"
                    for el in self._wrap(exc_line, IN - 2):
                        out.append(self._box(" " + el))
                elif t.type:
                    for el in self._wrap(t.type, IN - 2):
                        out.append(self._box(" " + el))
            elif t.kind == "stack":
                out.append(self._box(" Stack trace:"))
                for fr in t.frames or []:
                    file_path = self._format_path(fr.file) if fr.file else "<unknown>"
                    func_name = fr.func if fr.func else "<module>"
                    line_num = fr.line if fr.line else 0
                    
                    frame_line = f"  File \"{file_path}\", line {line_num}, in {func_name}"
                    for wl in self._wrap(frame_line, IN - 2):
                        out.append(self._box(" " + wl))
                    
                    if fr.code:
                        code_line = str(fr.code).strip("\n")
                        if code_line:
                            code_display = f"    {code_line}"
                            for cl in self._wrap(code_display, IN - 2):
                                out.append(self._box(" " + cl))

            if self.trace_show_text and t.text:
                out.append(self._box(" exception text"))
                for ln in str(t.text).rstrip("\n").splitlines():
                    for wl in self._wrap(ln, IN - 1):
                        out.append(self._box(" " + wl))
        out.append("└" + "─" * (W - 2) + "┘")
        return "\n".join(out)


    def _tails(self, e: LogEvent) -> List[str]:
        out: List[str] = []

        if self.show_bench and e.bench:
            p: List[str] = []
            if e.bench.id:
                p.append(f"id={e.bench.id}")
            if e.level == "BENCH_START":
                if e.bench.start_time is not None:
                    p.append(f"start={e.bench.start_time:.6f}")
            elif e.level == "BENCH_END":
                if e.bench.duration is not None:
                    p.append(f"dur_ms={e.bench.duration*1000:.2f}")
                    p.append(f"dur_s={e.bench.duration:.6f}")
                if e.bench.start_time is not None:
                    p.append(f"start={e.bench.start_time:.6f}")
                if e.bench.end_time is not None:
                    p.append(f"end={e.bench.end_time:.6f}")
            if p:
                out.append("bench  " + "  |  ".join(p))

        if self.show_system and e.system:
            sp: List[str] = []
            if e.system.pid and e.system.pid > 0:
                sp.append(f"pid={e.system.pid}")
            if e.system.thread_id and e.system.thread_id > 0:
                sp.append(f"tid={e.system.thread_id}")
            if e.system.hostname:
                sp.append(f"host={e.system.hostname}")
            if e.system.python_version:
                sp.append(f"py={e.system.python_version}")
            if e.system.platform:
                sp.append(f"plat={e.system.platform}")
            if sp:
                out.append("system " + "  |  ".join(sp))

        if self.show_meta and e.meta:
            keys = self.meta_keys or sorted(e.meta.keys())
            mp: List[str] = []
            for k in keys:
                v = e.meta.get(k, None)
                if v is not None and v != "":
                    mp.append(f"{k}={v}")
            if mp:
                out.append("meta   " + "  |  ".join(mp))

        return out


    def _format_path(self, path: str) -> str:
        if not path:
            return ""
        return os.path.basename(path) if self.path_style == "base" else path

    def _sanitize(self, s: str) -> str:
        return (s or "").expandtabs(self.tabsize)

    def _vislen(self, s: str) -> int:
        return len(_strip_ansi(self._sanitize(s)))

    def _viscrop(self, s: str, width: int) -> str:
        if self._vislen(s) <= width:
            return s
        out = []
        taken = 0
        raw = self._sanitize(s)
        i = 0
        while i < len(raw) and taken < width:
            m = _ANSI_RE.match(raw, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
            out.append(raw[i])
            taken += 1
            i += 1
        return "".join(out)

    def _box(self, content: str) -> str:
        IN = self.inner
        s = self._sanitize(content)
        vis = self._vislen(s)
        if vis < IN:
            s = s + " " * (IN - vis)
        elif vis > IN:
            s = self._viscrop(s, IN)
        return "│" + s + "│"

    def _box_multiline(self, lines: List[str], pad_left: int = 0) -> List[str]:
        out: List[str] = []
        IN = self.inner
        for ln in lines:
            s = " " * pad_left + ln
            vis = self._vislen(s)
            if vis < IN:
                s = s + " " * (IN - vis)
            elif vis > IN:
                s = self._viscrop(s, IN)
            out.append("│" + s + "│")
        return out

    def _left(self, text: str, width: int) -> str:
        s = self._sanitize(text)
        vis = self._vislen(s)
        if vis < width:
            return s + " " * (width - vis)
        return self._viscrop(s, width)

    def _right(self, text: str, width: int) -> str:
        s = self._sanitize(text)
        vis = self._vislen(s)
        if vis < width:
            return " " * (width - vis) + s
        return self._viscrop(s, width)

    def _wrap(self, s: str, width: int) -> List[str]:
        if width <= 0:
            return [s]
        raw = self._sanitize(s)
        out: List[str] = []
        cur = raw
        while cur:
            if self._vislen(cur) <= width:
                out.append(cur)
                break
            plain = _strip_ansi(cur)
            if len(plain) <= width:
                out.append(cur)
                break
            cutpos = plain.rfind(" ", 0, width)
            if cutpos <= 0:
                cutpos = width
            first = self._viscrop(cur, cutpos)
            out.append(first.rstrip())
            cur = cur[len(first):].lstrip()
        if not out:
            out = [""]
        return out

    def _box_left_right_stacked(self, left: str, right: str, width: int, *, gap: int = 2) -> List[str]:
        L: List[str] = []
        left_s = self._sanitize(left)
        right_s = self._sanitize(right)

        wrapped_right = self._wrap(right_s, width - 1) 
        left_vis = self._vislen(left_s)
        first_right_room = max(0, width - left_vis - gap)
        first_right = wrapped_right[0] if wrapped_right else ""
        first_right = self._viscrop(first_right, first_right_room)
        first_line = self._left(left_s, left_vis) + " " * gap + self._right(first_right, first_right_room)
        L.append(self._box(first_line))

        cont_prefix = " " * (left_vis + gap)
        remaining = "".join(wrapped_right)[len(first_right):].lstrip()
        if remaining:
            for chunk in self._wrap(remaining, width - left_vis - gap):
                L.append(self._box(cont_prefix + self._right(chunk, width - left_vis - gap)))

        return L

    def _level_square(self, level: str) -> str:
        if not self.use_color or not self.show_level_square:
            return "■"
        theme = _LEVEL_THEME_16.get(level, {"square_bg": "47"})
        return f"\x1b[{theme['square_bg']}m \x1b[0m"  

    def _level_text(self, level: str) -> str:
        if not self.use_color:
            return level
        theme = _LEVEL_THEME_16.get(level, {"fg": "97"})
        b = "\x1b[1m" if self.bold_level else ""
        e = "\x1b[0m" if self.bold_level else ""
        return f"{b}\x1b[{theme['fg']}m{level}\x1b[0m{e}"
