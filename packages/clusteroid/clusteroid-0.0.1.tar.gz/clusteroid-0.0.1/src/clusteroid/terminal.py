from __future__ import annotations

from clusteroid.terminal_buffer import AnsiLineBuffer
from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Label, RichLog, TabbedContent
from typing import Optional, Sequence, Union
import fcntl
import os
import pty
import signal
import struct
import termios
import threading


class Terminal(Widget):
    """Embed a PTY-backed terminal inside any layout (e.g., a TabPane).

    - No modal, no buttons.
    - Focusable. Click to focus, or call .focus() from your app.
    - Pass a command via constructor. If None, uses $SHELL or /bin/bash.
      * If `command` is a str: runs under `$SHELL -lc "<command>"`.
      * If `command` is a sequence: execs it directly, e.g. ["python3","-q"].
    - Streams output into a scrollable history and a live editable line.
    - Not a full VT emulator; basic line editing and ANSI colors only.
    """

    can_focus = True

    DEFAULT_CSS = """
    Terminal {
        width: 1fr;
        height: 1fr;
        layout: vertical;
    }
    #history {
        height: 1fr;
        overflow: auto;
    }
    #live {
        height: 1;
        padding: 0 1;
        overflow: hidden;
    }
    """

    def __init__(
        self,
        command: Optional[Union[str, Sequence[str]]] = None,
        cwd: Optional[str] = None,
        env: Optional[dict] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._command = command
        self._cwd = cwd
        self._env = dict(os.environ)
        self._env.setdefault("TERM", "xterm-256color")
        if env:
            self._env.update(env)

        # PTY state
        self._child_pid: Optional[int] = None
        self._master_fd: Optional[int] = None
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_reader = threading.Event()

        # UI
        self._history: Optional[RichLog] = None
        self._live: Optional[Label] = None
        self._buf = AnsiLineBuffer()

    # ---------- Compose ----------

    def compose(self) -> ComposeResult:
        yield Container(
            RichLog(id="history", highlight=False, markup=False, auto_scroll=True),
            Label("", id="live"),
        )

    # ---------- Lifecycle ----------

    def on_mount(self) -> None:
        self._history = self.query_one("#history", RichLog)
        self._live = self.query_one("#live", Label)
        self.focus()  # give it focus on first show
        self._spawn_process()
        self._apply_winsize()

    async def on_unmount(self, _: events.Unmount) -> None:
        self._cleanup(child_too=True)

    # ---------- Interaction ----------

    def on_click(self, _: events.Click) -> None:
        self.focus()

    def on_key(self, event: events.Key) -> None:
        data = self._event_to_bytes(event)
        if data and self._master_fd is not None:
            try:
                os.write(self._master_fd, data)
            except OSError:
                pass

    def on_paste(self, event: events.Paste) -> None:
        if self._master_fd is not None and event.text:
            try:
                os.write(self._master_fd, event.text.encode("utf-8", "ignore"))
            except OSError:
                pass

    def on_resize(self, _: events.Resize) -> None:
        self._apply_winsize()

    # ---------- PTY / Process ----------

    def _spawn_process(self) -> None:
        try:
            pid, master_fd = pty.fork()
        except OSError as exc:
            if self._history:
                self._history.write(f"[red]Failed to fork PTY: {exc}[/red]")
            return

        if pid == 0:
            # Child
            try:
                if self._cwd:
                    os.chdir(self._cwd)
                argv = self._build_argv(self._command)
                os.execvpe(argv[0], argv, self._env)
            except Exception as exc:  # pragma: no cover
                os.write(1, f"exec failed: {exc}\r\n".encode())
                os._exit(1)
        else:
            # Parent
            self._child_pid = pid
            self._master_fd = master_fd
            self._stop_reader.clear()
            self._reader_thread = threading.Thread(
                target=self._reader_loop, name="terminal-pty-reader", daemon=True
            )
            self._reader_thread.start()

    def _build_argv(self, cmd: Optional[Union[str, Sequence[str]]]) -> list[str]:
        if cmd is None:
            shell = os.environ.get("SHELL") or "/bin/bash"
            return [shell]
        if isinstance(cmd, str):
            shell = os.environ.get("SHELL") or "/bin/bash"
            return [shell, "-lc", cmd]
        # sequence
        seq = list(cmd)
        if not seq:
            shell = os.environ.get("SHELL") or "/bin/bash"
            return [shell]
        return seq

    def _reader_loop(self) -> None:
        assert self._master_fd is not None
        fd = self._master_fd
        exit_code: Optional[int] = None
        try:
            while not self._stop_reader.is_set():
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                text = chunk.decode("utf-8", "replace")
                completed, live = self._buf.feed(text)
                self.app.call_from_thread(self._push_output, completed, live)
        finally:
            # Reap child if exited
            if self._child_pid is not None:
                try:
                    _, status = os.waitpid(self._child_pid, os.WNOHANG)
                    exit_code = status
                except ChildProcessError:
                    pass
            self.app.call_from_thread(self._on_child_exit, exit_code)

    def _push_output(self, completed: list[str], live: str) -> None:
        if self._history:
            for line in completed:
                self._history.write(Text.from_ansi(line))
        if self._live is not None:
            self._live.update(Text.from_ansi(live))

    def _on_child_exit(self, exit_code: Optional[int]) -> None:
        self._cleanup(child_too=False)
        if self._history is not None:
            msg = "Session ended" + (f" (status {exit_code})" if exit_code else "") + "."
            self._history.write(f"[dim]{msg}[/dim]")
        #close_active_tab(self.app)
        tabs = self.app.query_one("#tabs", TabbedContent)
        active = tabs.active
        tabs.remove_pane(active)
        self.remove()

    def _cleanup(self, child_too: bool) -> None:
        self._stop_reader.set()
        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None
        if child_too and self._child_pid is not None:
            try:
                os.kill(self._child_pid, signal.SIGHUP)
            except ProcessLookupError:
                pass
            self._child_pid = None

    def _apply_winsize(self) -> None:
        if self._master_fd is None or self.size.width <= 0 or self.size.height <= 0:
            return
        rows = max(2, int(self.size.height) - 1)  # minus live line
        cols = max(2, int(self.size.width) - 0)
        winsz = struct.pack("HHHH", rows, cols, 0, 0)
        try:
            fcntl.ioctl(self._master_fd, termios.TIOCSWINSZ, winsz)
        except OSError:
            pass
        if self._child_pid:
            try:
                os.kill(self._child_pid, signal.SIGWINCH)
            except ProcessLookupError:
                pass

    # ---------- Key mapping ----------

    @staticmethod
    def _event_to_bytes(event: events.Key) -> Optional[bytes]:
        k = event.key or ""
        c = event.character
        if c:
            return c.encode("utf-8", "ignore")
        keymap = {
            "enter": b"\r", "return": b"\r", "tab": b"\t", "backspace": b"\x7f",
            "escape": b"\x1b", "left": b"\x1b[D", "right": b"\x1b[C",
            "up": b"\x1b[A", "down": b"\x1b[B", "home": b"\x1b[H", "end": b"\x1b[F",
            "pageup": b"\x1b[5~", "pagedown": b"\x1b[6~", "delete": b"\x1b[3~", "insert": b"\x1b[2~",
            "f1": b"\x1bOP", "f2": b"\x1bOQ", "f3": b"\x1bOR", "f4": b"\x1bOS",
            "f5": b"\x1b[15~", "f6": b"\x1b[17~", "f7": b"\x1b[18~", "f8": b"\x1b[19~",
            "f9": b"\x1b[20~", "f10": b"\x1b[21~", "f11": b"\x1b[23~", "f12": b"\x1b[24~",
        }
        if k in keymap:
            return keymap[k]
        if k.startswith("ctrl+") and len(k) == 6:
            ch = k[-1]
            specials = {"[": 27, "\\": 28, "]": 29, "^": 30, "_": 31, "@": 0, "?": 127}
            if ch in specials:
                return bytes([specials[ch]])
            return bytes([ord(ch.upper()) & 0x1F])
        if k.startswith("alt+") and len(k) == 5:
            ch = k[-1]
            return b"\x1b" + ch.encode("utf-8", "ignore")
        return None

    # ---------- Public helpers ----------

    def focus_terminal(self) -> None:
        self.focus()

