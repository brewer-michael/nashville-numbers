"""Displays: console, HD44780 LCD, and 7-segment LEDs (TM1637, HT16K33, MAX7219)."""

import logging
import time
from typing import Optional

from ..analysis.pipeline import AnalysisState
from .base import ConsoleDisplay, Display
from .drivers import parse_address

log = logging.getLogger(__name__)

__all__ = ['Display', 'ConsoleDisplay', 'ResilientDisplay', 'create_display']


class ResilientDisplay(Display):
    """Keeps the app running when display hardware fails.

    If the hardware can't be opened, or stops responding mid-gig (a loose
    wire), output falls back to the console/log and the hardware is re-opened
    every `retry_seconds`.
    """

    def __init__(self, inner: Display, retry_seconds: float = 5.0,
                 fallback: Optional[Display] = None):
        self.inner = inner
        self.name = inner.name
        self.retry_seconds = retry_seconds
        self.fallback = fallback or ConsoleDisplay()
        self.online = False
        self._next_retry = 0.0
        self._reported = False

    def _try_open(self):
        try:
            self.inner.open()
        except Exception as exc:
            self.online = False
            self._next_retry = time.monotonic() + self.retry_seconds
            if not self._reported:
                log.error("%s display unavailable: %s (retrying every %.0f s; output goes to "
                          "the log meanwhile)", self.inner.name, exc, self.retry_seconds)
                self._reported = True
            return
        if self._reported:
            log.info("%s display is back", self.inner.name)
        self.online = True
        self._reported = False

    def _fail(self, exc: Exception):
        log.error("%s display stopped responding: %s", self.inner.name, exc)
        self._reported = True
        self.online = False
        self._next_retry = time.monotonic() + self.retry_seconds
        try:
            self.inner.close()
        except Exception:
            pass

    def open(self):
        self._try_open()

    def close(self):
        if self.online:
            try:
                self.inner.close()
            except Exception as exc:
                log.debug("closing display: %s", exc)
        self.online = False

    def _maybe_reopen(self):
        if not self.online and time.monotonic() >= self._next_retry:
            self._try_open()

    def show(self, state: AnalysisState) -> None:
        self._maybe_reopen()
        if self.online:
            try:
                self.inner.show(state)
                return
            except Exception as exc:
                self._fail(exc)
        self.fallback.show(state)

    def message(self, code: str, detail: str = '') -> None:
        self._maybe_reopen()
        if self.online:
            try:
                self.inner.message(code, detail)
                return
            except Exception as exc:
                self._fail(exc)
        self.fallback.message(code, detail)


def create_display(cfg: dict) -> Display:
    """Build the display described by `cfg['display']`."""
    d = cfg['display']
    kind = d['type']
    if kind == 'console':
        return ConsoleDisplay()
    if kind == 'lcd':
        from .lcd import LCDDisplay
        c = d['lcd']
        inner = LCDDisplay(c['cols'], c['rows'], parse_address(c['address']), c['expander'],
                           c['port'], c['charmap'])
    elif kind == 'ht16k33':
        from .led import ht16k33_display
        c = d['ht16k33']
        inner = ht16k33_display(parse_address(c['address']), c['bus'], c['brightness'])
    elif kind == 'tm1637':
        from .led import tm1637_display
        c = d['tm1637']
        inner = tm1637_display(c['clk_pin'], c['dio_pin'], c['brightness'])
    elif kind == 'max7219':
        from .led import max7219_display
        c = d['max7219']
        inner = max7219_display(c['port'], c['device'], c['digits'], c['brightness'], c['reverse'])
    else:
        raise ValueError(f"unknown display type {kind!r}")
    return ResilientDisplay(inner)
