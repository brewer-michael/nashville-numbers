"""HD44780 character LCDs (16x2, 20x4) on an I2C backpack, via RPLCD."""

import logging
from typing import List, Optional

from ..analysis.pipeline import AnalysisState
from .base import Display, LOCK_GLYPH, lcd_lines, message_text
from .drivers import DisplayHardwareError

log = logging.getLogger(__name__)

# 5x8 padlock for custom character slot 0.
LOCK_BITMAP = (0b01110, 0b10001, 0b10001, 0b11111, 0b11011, 0b11011, 0b11111, 0b00000)


class LCDDisplay(Display):
    name = 'lcd'

    def __init__(self, cols: int = 16, rows: int = 2, address: int = 0x27,
                 expander: str = 'PCF8574', port: int = 1, charmap: str = 'A00', lcd=None):
        self.cols, self.rows = cols, rows
        self.address, self.expander, self.port, self.charmap = address, expander, port, charmap
        self.lcd = lcd
        self._shown: List[Optional[str]] = [None] * rows

    def open(self):
        if self.lcd is None:
            try:
                from RPLCD.i2c import CharLCD
                self.lcd = CharLCD(i2c_expander=self.expander, address=self.address, port=self.port,
                                   cols=self.cols, rows=self.rows, charmap=self.charmap,
                                   auto_linebreaks=False, backlight_enabled=True)
            except OSError as exc:
                raise DisplayHardwareError(
                    f"No LCD at I2C address 0x{self.address:02X} on bus {self.port} ({exc}). "
                    f"Run 'i2cdetect -y {self.port}'; common addresses are 0x27 and 0x3F.") from exc
        self.lcd.create_char(0, LOCK_BITMAP)
        self.lcd.clear()
        self._shown = [None] * self.rows

    def close(self):
        if self.lcd is None:
            return
        try:
            self.lcd.clear()
            self.lcd.backlight_enabled = False
            self.lcd.close(clear=True)
        except Exception as exc:  # pragma: no cover - hardware already gone
            log.debug("LCD close failed: %s", exc)
        self.lcd = None

    def _write(self, lines: List[str]):
        for row, line in enumerate(lines[:self.rows]):
            line = line[:self.cols].ljust(self.cols)
            if line != self._shown[row]:
                self.lcd.cursor_pos = (row, 0)
                self.lcd.write_string(line)
                self._shown[row] = line

    def show(self, state: AnalysisState) -> None:
        self._write(lcd_lines(state, self.cols, self.rows, LOCK_GLYPH))

    def message(self, code: str, detail: str = '') -> None:
        line1, line2, _ = message_text(code, detail)
        self._write([line1, line2] + [''] * (self.rows - 2))
