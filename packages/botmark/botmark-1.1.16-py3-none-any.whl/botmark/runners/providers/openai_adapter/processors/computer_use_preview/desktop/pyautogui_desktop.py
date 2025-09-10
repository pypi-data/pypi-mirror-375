from __future__ import annotations

import io
import time
import base64
import platform
from typing import List, Dict, Literal, TYPE_CHECKING

# Only for type checkers; avoids runtime dependency on pyautogui
if TYPE_CHECKING:  # pragma: no cover
    import pyautogui as _pyautogui  # noqa: F401

_OS = platform.system().lower()  # 'windows', 'darwin', 'linux'


def _map_key(k: str) -> str:
    """Normalize common key names to pyautogui's names across platforms."""
    k = (k or "").strip().lower()

    basic = {
        "enter": "enter",
        "return": "enter",
        "esc": "esc",
        "escape": "esc",
        "tab": "tab",
        "space": "space",
        "backspace": "backspace",
        "delete": "delete",
        "insert": "insert",
        "home": "home",
        "end": "end",
        "pageup": "pageup",
        "pagedown": "pagedown",
        "capslock": "capslock",
        "shift": "shift",
        "ctrl": "ctrl",
        "control": "ctrl",
        "alt": "alt",
        "option": "alt",
        "left": "left",
        "arrowleft": "left",
        "right": "right",
        "arrowright": "right",
        "up": "up",
        "arrowup": "up",
        "down": "down",
        "arrowdown": "down",
        "/": "/",
        "\\": "\\",
    }
    if k in basic:
        return basic[k]

    # Super/meta/win/command differences
    if k in ("cmd", "command", "meta", "super", "win", "windows"):
        if _OS == "darwin":
            return "command"
        # On Windows/Linux pyautogui uses 'winleft' / 'winright'; default to left
        return "winleft"

    # Fallback to whatever was passed
    return k


class LocalPyAutoGuiDesktop:
    """
    A desktop 'Computer' implementation using pyautogui.
    Provides mouse/keyboard/screenshot primitives for the local OS desktop.
    """

    def __init__(self, environment: str = None):
        self.environment = environment
        self._pyautogui = None  # set on demand

    # ---- Internal: lazy import helper ----
    def _ensure_pyautogui(self):
        if self._pyautogui is not None:
            return self._pyautogui
        try:
            import pyautogui  # type: ignore
        except Exception as e:
            raise RuntimeError(
                "The 'pyautogui' package is required for the desktop computer.\n"
                "Install with: pip install pyautogui pillow"
            ) from e
        # Make it a bit safer / configurable
        try:
            pyautogui.FAILSAFE = False  # avoid raising if mouse hits corner
            # pyautogui.PAUSE = 0.01  # optional, slower human-like movement
        except Exception:
            pass
        self._pyautogui = pyautogui
        return self._pyautogui

    # ---- Context mgmt to mirror Playwright-based class ----
    def __enter__(self):
        # Ensure pyautogui is available when entering the context
        self._ensure_pyautogui()
        return self

    def __exit__(self, exc_type, exc, tb):
        # Nothing to tear down for pyautogui
        return False

    # ---- Environment / meta ----
    def get_environment(self) -> Literal["windows", "mac", "ubuntu"]:
        if self.environment:
            return self.environment

        if _OS == "darwin":
            return "mac"
        if _OS.startswith("win"):
            return "windows"
        return "ubuntu"

    def get_dimensions(self) -> tuple[int, int]:
        pg = self._ensure_pyautogui()
        w, h = pg.size()
        return int(w), int(h)

    def get_current_url(self) -> str:
        # Not applicable for desktop; return empty string
        return ""

    # ---- Visuals ----
    def screenshot(self) -> str:
        pg = self._ensure_pyautogui()
        img = pg.screenshot()  # PIL Image
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue()).decode("utf-8")

    # ---- Mouse ----
    def move(self, x: int, y: int) -> None:
        pg = self._ensure_pyautogui()
        pg.moveTo(int(x), int(y))

    def click(self, x: int, y: int, button: str = "left") -> None:
        pg = self._ensure_pyautogui()
        b = (button or "left").lower()

        # Special cases to mimic browser back/forward/wheel semantics
        if b in ("back", "forward"):
            self._browser_nav_hotkey(b)
            return
        if b == "wheel":
            # Treat x=horizontal delta, y=vertical delta: positive = scroll up/right
            if y:
                pg.scroll(int(y))
            try:
                if x:
                    pg.hscroll(int(x))
            except Exception:
                pass
            return

        mapped = {"left": "left", "right": "right", "middle": "middle"}.get(b, "left")
        pg.click(int(x), int(y), button=mapped)

    def double_click(self, x: int, y: int) -> None:
        pg = self._ensure_pyautogui()
        pg.doubleClick(int(x), int(y))

    def drag(self, path: List[Dict[str, int]]) -> None:
        if not path:
            return
        pg = self._ensure_pyautogui()
        start = path[0]
        pg.moveTo(int(start["x"]), int(start["y"]))
        pg.mouseDown()
        for pt in path[1:]:
            pg.moveTo(int(pt["x"]), int(pt["y"]))
        pg.mouseUp()

    def scroll(self, x: int, y: int, scroll_x: int, scroll_y: int) -> None:
        pg = self._ensure_pyautogui()
        # Move to a reference point, then scroll
        try:
            pg.moveTo(int(x), int(y))
        except Exception:
            pass
        if scroll_y:
            pg.scroll(int(scroll_y))
        if scroll_x:
            try:
                pg.hscroll(int(scroll_x))
            except Exception:
                pass

    # ---- Keyboard ----
    def type(self, text: str) -> None:
        if not text:
            return
        pg = self._ensure_pyautogui()
        pg.typewrite(text, interval=0.0)

    def keypress(self, keys: List[str]) -> None:
        if not keys:
            return
        pg = self._ensure_pyautogui()
        mapped = [_map_key(k) for k in keys]
        # Press all down then release in reverse (to match the Playwright pattern)
        for k in mapped:
            pg.keyDown(k)
        for k in reversed(mapped):
            pg.keyUp(k)

    # ---- Timing ----
    def wait(self, ms: int = 1000) -> None:
        time.sleep(max(0, int(ms)) / 1000.0)

    # ---- Helpers ----
    def _browser_nav_hotkey(self, which: str) -> None:
        pg = self._ensure_pyautogui()
        # Simulate back/forward navigation hotkeys when available
        if which == "back":
            if _OS == "darwin":
                pg.hotkey("command", "[")
            else:
                pg.hotkey("alt", "left")
        elif which == "forward":
            if _OS == "darwin":
                pg.hotkey("command", "]")
            else:
                pg.hotkey("alt", "right")
