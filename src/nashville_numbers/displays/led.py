"""7-segment LED displays (TM1637, HT16K33 backpacks, MAX7219)."""

from typing import List, Optional

from ..analysis.pipeline import AnalysisState
from .base import Display, message_text
from .drivers import HT16K33SevenSegment, MAX7219, TM1637
from .sevenseg import encode, state_cells, text_cells, with_dp


class SevenSegmentDisplay(Display):
    """Shows Nashville numbers on a 4- or 8-digit 7-segment display.

    `lock_indicator` is how a locked key is shown: 'colon' (TM1637 clock
    modules wire their colon to digit 2's decimal point; HT16K33 backpacks have
    a separate colon) or 'dp' (decimal point of the last digit).
    """

    def __init__(self, driver, digits: int = 4, lock_indicator: str = 'colon', name: str = 'led'):
        self.driver = driver
        self.digits = digits
        self.lock_indicator = lock_indicator
        self.name = name
        self._last: Optional[tuple] = None

    def open(self):
        self.driver.open()
        self._last = None

    def close(self):
        self.driver.close()

    def _write(self, segments: List[int], colon: bool):
        key = (tuple(segments), colon)
        if key == self._last:
            return
        if isinstance(self.driver, HT16K33SevenSegment):
            self.driver.write(segments, colon=colon)
        else:
            self.driver.write(segments)
        self._last = key

    def _emit(self, cells, locked: bool):
        colon = False
        if locked:
            if isinstance(self.driver, HT16K33SevenSegment) and self.lock_indicator == 'colon':
                colon = True
            elif self.lock_indicator == 'colon' and self.digits >= 2:
                cells = with_dp(cells, 1)
            else:
                cells = with_dp(cells, self.digits - 1)
        self._write(encode(cells), colon)

    def show(self, state: AnalysisState) -> None:
        self._emit(state_cells(state, self.digits), state.key_locked)

    def message(self, code: str, detail: str = '') -> None:
        _, _, text = message_text(code, detail)
        self._emit(text_cells(text, self.digits), code == 'locked')


def tm1637_display(clk_pin=23, dio_pin=24, brightness=7, pin_factory=None) -> SevenSegmentDisplay:
    driver = TM1637(clk_pin, dio_pin, brightness, pin_factory)
    return SevenSegmentDisplay(driver, 4, 'colon', 'tm1637')


def ht16k33_display(address=0x70, bus=1, brightness=15, smbus=None) -> SevenSegmentDisplay:
    return SevenSegmentDisplay(HT16K33SevenSegment(address, bus, brightness, smbus), 4, 'colon',
                               'ht16k33')


def max7219_display(port=0, device=0, digits=8, brightness=8, reverse=True, spi=None
                    ) -> SevenSegmentDisplay:
    return SevenSegmentDisplay(MAX7219(port, device, digits, brightness, reverse, spi=spi),
                               digits, 'dp', 'max7219')
