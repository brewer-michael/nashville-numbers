"""Display interface and the text layouts shared by character displays."""

import logging
import time
from abc import ABC, abstractmethod
from typing import List

from ..analysis.pipeline import AnalysisState
from ..theory import NashvilleNumber, QUALITIES

log = logging.getLogger(__name__)

LOCK_GLYPH = '\x00'   # custom LCD character slot 0 (a padlock); '*' on the console

# Status messages: code -> (LCD line 1, LCD line 2, 4-character 7-segment text).
# '{detail}' is replaced with the detail passed to Display.message().
MESSAGES = {
    'hello': ('Nashville Numbers', 'starting...', 'HELO'),
    'no_audio': ('No audio input', '{detail}', 'noAu'),
    'reset': ('New song', 'key cleared', 'nEU'),
    'locked': ('Key locked', '{detail}', 'LOC'),
    'unlocked': ('Key unlocked', 'following music', 'FrEE'),
    'shutdown': ('Shutting down', 'unplug in 20 s', 'OFF'),
    'error': ('Error', '{detail}', 'Err'),
}


def message_text(code: str, detail: str = ''):
    """(line1, line2, seven_segment_text) for a status message code."""
    line1, line2, seg = MESSAGES.get(code, (code, '{detail}', code[:4]))
    return line1, line2.format(detail=detail), seg


class Display(ABC):
    """A device that shows the analysis state.

    `show()` is called on every analysis hop (10x per second); drivers must
    only talk to the hardware when what they display actually changes.
    `message()` shows a short status such as a boot or error message.
    """

    name = 'display'

    def open(self) -> None:  # noqa: B027 - optional hook, no-op by default
        """Initialise the hardware. Raise on failure."""

    def close(self) -> None:  # noqa: B027 - optional hook, no-op by default
        """Blank the display and release the hardware."""

    @abstractmethod
    def show(self, state: AnalysisState) -> None:
        ...

    @abstractmethod
    def message(self, code: str, detail: str = '') -> None:
        """Show a status message (a key of MESSAGES) until the next show()."""

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, *exc):
        self.close()
        return False


def nashville_text(number: NashvilleNumber) -> str:
    """Nashville number as plain text for character displays ('ø' is not in
    the HD44780 character ROM, so half-diminished is spelled m7b5)."""
    suffix = 'm7b5' if number.quality == 'hdim7' else QUALITIES[number.quality].nashville
    return f"{number.accidental}{number.degree}{suffix}"


def history_text(state: AnalysisState, width: int) -> str:
    """Most recent chords as Nashville numbers, newest last, fitted to width."""
    items = [nashville_text(n) for n in state.history_numbers]
    text = ''
    for item in reversed(items):
        candidate = item + (' ' + text if text else '')
        if len(candidate) > width:
            break
        text = candidate
    return text


def lcd_lines(state: AnalysisState, cols: int = 16, rows: int = 2,
              lock_glyph: str = LOCK_GLYPH) -> List[str]:
    """Text for an HD44780-style character LCD.

    16x2:   "6m   Em       G"      number, chord, key (padlock when locked)
            "1 5 6m 4 1 5 6m"      recent progression
    20x4 adds a key line with fit strength and an input level / tuning line.
    """
    key_label = ''
    if state.key is not None:
        key_label = state.key.name()
        if state.key_locked:
            key_label = lock_glyph + key_label
    elif state.key_locked:
        key_label = lock_glyph

    if not state.signal:
        top = 'Nashville #s'
        bottom = 'waiting for sound'
    elif state.chord is None:
        top = '--'
        bottom = history_text(state, cols) or 'listening...'
    else:
        chord = state.chord_name() or ''
        if state.number is not None:
            top = f"{nashville_text(state.number):<5}{chord}"
        else:
            top = f"{chord:<6}"
        bottom = history_text(state, cols) if state.key is not None else 'finding key...'
    if state.signal and state.key is None and state.chord is not None:
        key_label = key_label or 'key?'
    room = cols - len(key_label) - 1
    line1 = top[:room].ljust(room) + ' ' + key_label if key_label else top[:cols]
    lines = [line1, bottom]
    if rows >= 4:
        if state.key is not None:
            lock = ' locked' if state.key_locked else ''
            lines.append(f"Key {state.key.long_name()}{lock}")
        else:
            lines.append('Key: listening')
        lines.append(f"In {state.level_dbfs:5.0f}dB tune {state.tuning_cents:+3.0f}c")
    return [line[:cols].ljust(cols) for line in lines[:rows]]


class ConsoleDisplay(Display):
    """Prints one line per change - for `--simulate`, services and logs."""

    name = 'console'

    def __init__(self, stream=None):
        import sys
        self.stream = stream or sys.stdout
        self._last = None

    def _emit(self, line: str, dedupe_key=None):
        key = dedupe_key if dedupe_key is not None else line
        if key != self._last:
            stamp = time.strftime('%H:%M:%S')
            print(f"[{stamp}] {line}", file=self.stream, flush=True)
            self._last = key

    def show(self, state: AnalysisState) -> None:
        if not state.signal:
            self._emit('(silence)')
            return
        if state.chord is None:
            self._emit('--   listening')
            return
        chord = state.chord_name()
        if state.number is not None:
            key = state.key.name() + (' [locked]' if state.key_locked else '')
            # one line per chord/key change; the history is context, not a trigger
            self._emit(f"{nashville_text(state.number):<6} {chord:<6} key {key:<10} "
                       f"| {history_text(state, 40)}", (state.number, chord, key))
        else:
            self._emit(f"{chord:<6} (finding key...)")

    def message(self, code: str, detail: str = '') -> None:
        line1, line2, _ = message_text(code, detail)
        self._emit(f"{line1} - {line2}" if line2 else line1)
