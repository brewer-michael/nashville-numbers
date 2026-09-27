import io

from nashville_numbers.analysis.pipeline import AnalysisState
from nashville_numbers.displays import ResilientDisplay, create_display
from nashville_numbers.displays.base import ConsoleDisplay, Display, lcd_lines
from nashville_numbers.displays.drivers import HT16K33SevenSegment
from nashville_numbers.displays.lcd import LCDDisplay
from nashville_numbers.displays.led import SevenSegmentDisplay
from nashville_numbers.displays.sevenseg import FONT, state_cells
from nashville_numbers.theory import Chord, Key, to_nashville


def state(symbol='Am', key='C', locked=False, history=('C', 'G', 'Am')):
    k = Key.parse(key) if key else None
    chord = Chord.parse(symbol) if symbol else None
    hist = tuple(Chord.parse(h) for h in history)
    return AnalysisState(
        level_dbfs=-20, signal=True, chord=chord, key=k, key_locked=locked,
        number=to_nashville(chord, k) if chord and k else None, history=hist,
        history_numbers=tuple(to_nashville(h, k) for h in hist) if k else ())


def cells_text(cells):
    return ''.join(ch for ch, _ in cells)


def test_seven_segment_layouts():
    assert cells_text(state_cells(state('Am'))) == ' 6- '
    assert cells_text(state_cells(state('G7'))) == ' 5⁷ '
    assert cells_text(state_cells(state('Bb'))) == 'b7  '
    assert cells_text(state_cells(state('Am', key=None))) == 'A-  '     # name until key known
    assert cells_text(state_cells(AnalysisState(signal=True))) == '----'
    assert cells_text(state_cells(AnalysisState(signal=False))) == '    '
    assert cells_text(state_cells(state('Am'), digits=8)) == ' 6-  A- '


def test_lcd_16x2_lines():
    lines = lcd_lines(state('Am', locked=True), 16, 2, lock_glyph='*')
    assert lines == ['6m   Am       *C', '1 5 6m          ']
    assert all(len(line) == 16 for line in lines)
    idle = lcd_lines(AnalysisState(signal=False), 16, 2)
    assert 'waiting' in idle[1]
    finding = lcd_lines(state('Am', key=None), 16, 2)
    assert finding[1].startswith('finding key')


def test_lcd_20x4_has_key_and_level_lines():
    lines = lcd_lines(state('F'), 20, 4)
    assert len(lines) == 4 and lines[2].startswith('Key C major') and 'dB' in lines[3]


class FakeCharLCD:
    def __init__(self):
        self.writes, self.cursor_pos, self.chars = [], (0, 0), {}
        self.backlight_enabled = True

    def create_char(self, slot, bitmap):
        self.chars[slot] = bitmap

    def clear(self):
        self.writes.append('CLEAR')

    def write_string(self, text):
        self.writes.append((self.cursor_pos, text))

    def close(self, clear=False):
        pass


def test_lcd_display_only_rewrites_changed_rows():
    fake = FakeCharLCD()
    lcd = LCDDisplay(16, 2, lcd=fake)
    lcd.open()
    assert 0 in fake.chars                               # padlock glyph
    lcd.show(state('Am'))
    n = len(fake.writes)
    lcd.show(state('Am'))
    assert len(fake.writes) == n                         # nothing changed
    lcd.show(state('F', history=('C', 'G', 'Am', 'F')))
    assert len(fake.writes) == n + 2


class RecordingDriver:
    def __init__(self):
        self.written = []

    def open(self):
        pass

    def close(self):
        pass

    def write(self, segments):
        self.written.append(list(segments))


def test_seven_segment_display_lock_indicator_and_dedup():
    drv = RecordingDriver()
    disp = SevenSegmentDisplay(drv, 4, 'colon')
    disp.show(state('C'))
    disp.show(state('C'))
    assert drv.written == [[0, FONT['1'], 0, 0]]
    disp.show(state('C', locked=True))
    assert drv.written[-1][1] == FONT['1'] | 0x80          # colon = digit 2's DP on TM1637


class FakeHT(HT16K33SevenSegment):
    def __init__(self):
        super().__init__(smbus=object())
        self.colon = None

    def open(self):
        pass

    def write(self, segments, colon=False):
        self.colon = colon


def test_ht16k33_lock_uses_the_real_colon():
    drv = FakeHT()
    disp = SevenSegmentDisplay(drv, 4, 'colon')
    disp.show(state('C', locked=True))
    assert drv.colon is True


class Broken(Display):
    name = 'broken'

    def __init__(self):
        self.opens = 0
        self.fail = True

    def open(self):
        self.opens += 1
        if self.fail:
            raise OSError('not connected')

    def show(self, state):
        pass

    def message(self, code, detail=''):
        pass


def test_resilient_display_falls_back_and_retries(monkeypatch):
    out = io.StringIO()
    inner = Broken()
    disp = ResilientDisplay(inner, retry_seconds=0.0, fallback=ConsoleDisplay(out))
    disp.open()
    assert not disp.online
    disp.show(state('G'))
    assert 'G' in out.getvalue()                           # fell back to console
    inner.fail = False
    disp.show(state('G'))
    assert disp.online and inner.opens >= 2


def test_console_display_prints_changes_only():
    out = io.StringIO()
    con = ConsoleDisplay(out)
    con.show(state('Am'))
    con.show(state('Am'))
    con.message('reset')
    lines = out.getvalue().splitlines()
    assert len(lines) == 2 and '6m' in lines[0] and 'New song' in lines[1]


def test_factory_builds_console_for_console_type():
    from nashville_numbers.config import load_config
    assert isinstance(create_display(load_config()), ConsoleDisplay)
