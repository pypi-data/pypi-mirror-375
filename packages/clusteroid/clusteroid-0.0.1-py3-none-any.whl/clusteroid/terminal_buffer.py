# Minimal ANSI-aware single-line buffer for PTY output.
# Handles: \n, \r, backspace, CSI K / C / D, and passes SGR (..m) through.
from __future__ import annotations

class AnsiLineBuffer:
    def __init__(self) -> None:
        self._line: str = ""
        self._cursor: int = 0  # visual cell index

    # Public API --------------------------------------------------------------

    def feed(self, data: str) -> tuple[list[str], str]:
        """Feed raw text. Returns (completed_lines, current_line)."""
        out: list[str] = []
        i = 0
        n = len(data)
        while i < n:
            ch = data[i]
            if ch == "\x1b":  # ESC
                seq, final, params, consumed = self._parse_csi(data, i)
                if final is None:
                    # Literal ESC; ignore for now
                    i += consumed
                    continue
                if final == "m":  # SGR — keep styles in the stream
                    self._insert_raw(seq)
                elif final == "K":  # Erase in line
                    self._apply_el(params)
                elif final == "D":  # Cursor left
                    self._cursor = max(0, self._cursor - (int(params or "1")))
                elif final == "C":  # Cursor right
                    self._cursor = min(self._vis_len(), self._cursor + (int(params or "1")))
                # ignore everything else
                i += consumed
                continue
            if ch == "\n":  # commit line
                out.append(self._line)
                self._line = ""
                self._cursor = 0
            elif ch == "\r":  # CR: move to column 0
                self._cursor = 0
            elif ch == "\x08":  # BS: move left
                if self._cursor > 0:
                    self._cursor -= 1
            else:
                self._insert_char(ch)
            i += 1
        return out, self._line

    # Internals ---------------------------------------------------------------

    def _parse_csi(self, s: str, i: int) -> tuple[str, str | None, str, int]:
        """Parse ESC [ ... <final>. Returns (full_seq, final, params, consumed)."""
        if i + 1 >= len(s) or s[i + 1] != "[":
            return s[i], None, "", 1
        j = i + 2
        while j < len(s) and not s[j].isalpha():
            j += 1
        if j >= len(s):
            return s[i:], None, "", len(s) - i
        final = s[j]
        params = s[i + 2 : j]
        seq = s[i : j + 1]
        return seq, final, params, (j - i + 1)

    def _vis_map(self) -> list[int]:
        """Map visual cells -> string indices (skips ANSI CSI)."""
        m: list[int] = []
        i = 0
        s = self._line
        n = len(s)
        while i < n:
            if s[i] == "\x1b" and i + 1 < n and s[i + 1] == "[":
                j = i + 2
                while j < n and not s[j].isalpha():
                    j += 1
                i = min(n, j + 1)
                continue
            m.append(i)
            i += 1
        return m

    def _vis_len(self) -> int:
        return len(self._vis_map())

    def _str_index(self, vis_index: int) -> int:
        m = self._vis_map()
        if vis_index >= len(m):
            return len(self._line)
        return m[vis_index]

    def _insert_raw(self, raw: str) -> None:
        si = self._str_index(self._cursor)
        self._line = self._line[:si] + raw + self._line[si:]

    def _insert_char(self, ch: str) -> None:
        si = self._str_index(self._cursor)
        if si >= len(self._line):
            self._line += ch
        else:
            self._line = self._line[:si] + ch + self._line[si + 1 :]
        self._cursor += 1

    def _apply_el(self, params: str) -> None:
        mode = params or "0"
        si = self._str_index(self._cursor)
        if mode == "0":  # cursor -> end
            self._line = self._line[:si]
        elif mode == "1":  # start -> cursor
            self._line = self._line[si:]
            self._cursor = 0
        elif mode == "2":  # whole line
            self._line = ""
            self._cursor = 0

