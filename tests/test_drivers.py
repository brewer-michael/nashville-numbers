import pytest

from nashville_numbers.displays.drivers import (DisplayHardwareError, HT16K33SevenSegment,
                                                MAX7219, TM1637, parse_address,
                                                to_max7219_bits)
from nashville_numbers.displays.sevenseg import FONT


# ---------------------------------------------------------------- TM1637 ---
class TM1637Bus:
    """Simulates the TM1637 side of the 2-wire bus and decodes what it hears."""

    def __init__(self, present=True):
        self.present = present
        self.master = {'clk': 1, 'dio': 1}      # 1 = released (pulled up)
        self.slave_low = False
        self.frames, self._frame = [], None
        self._bits = self._value = 0
        self._acking = False

    def level(self, line):
        if line == 'dio' and self.slave_low:
            return 0
        return self.master[line]

    def set(self, line, value):
        old = {'clk': self.level('clk'), 'dio': self.level('dio')}
        self.master[line] = value
        new = {'clk': self.level('clk'), 'dio': self.level('dio')}
        if line == 'dio' and old['clk'] == 1 and new['clk'] == 1:
            if old['dio'] == 1 and new['dio'] == 0:          # start
                self._frame, self._bits, self._value, self._acking = [], 0, 0, False
            elif old['dio'] == 0 and new['dio'] == 1 and self._frame is not None:   # stop
                self.frames.append(self._frame)
                self._frame = None
        if line == 'clk' and self._frame is not None:
            if old['clk'] == 0 and new['clk'] == 1 and not self._acking and self._bits < 8:
                self._value |= new['dio'] << self._bits
                self._bits += 1
            elif old['clk'] == 1 and new['clk'] == 0:
                if self._bits == 8 and not self._acking:
                    self._acking = True
                    self.slave_low = self.present
                elif self._acking:
                    self._acking = False
                    self.slave_low = False
                    self._frame.append(self._value)
                    self._bits = self._value = 0


class FakePin:
    def __init__(self, bus, line):
        self.bus, self.line = bus, line

    def output_with_state(self, state):
        assert state == 0, "open-drain: the Pi must never drive a TM1637 line high"
        self.bus.set(self.line, 0)

    def input_with_pull(self, pull):
        assert pull == 'up'
        self.bus.set(self.line, 1)

    @property
    def state(self):
        return self.bus.level(self.line)

    def close(self):
        pass


class FakeFactory:
    def __init__(self, bus, clk=23, dio=24):
        self.bus, self.clk, self.dio = bus, clk, dio

    def pin(self, n):
        return FakePin(self.bus, 'clk' if n == self.clk else 'dio')


def test_tm1637_protocol_frames():
    bus = TM1637Bus()
    tm = TM1637(23, 24, brightness=5, pin_factory=FakeFactory(bus), bit_delay=0)
    tm.open()
    assert bus.frames == [[0x40], [0xC0, 0, 0, 0, 0], [0x88 | 5]]
    bus.frames.clear()
    assert tm.write([FONT['1'], FONT['-'], FONT['°'], 0xFF])
    assert bus.frames == [[0x40], [0xC0, 0x06, 0x40, 0x63, 0xFF], [0x8D]]
    bus.frames.clear()
    tm.close()
    assert bus.frames == [[0x80]]


def test_tm1637_missing_module_is_reported():
    bus = TM1637Bus(present=False)
    tm = TM1637(23, 24, pin_factory=FakeFactory(bus), bit_delay=0)
    with pytest.raises(DisplayHardwareError, match='3.3 V'):
        tm.open()


def test_tm1637_rejects_bad_brightness():
    with pytest.raises(ValueError):
        TM1637(brightness=8)


def test_tm1637_with_gpiozero_mock_pins():
    pytest.importorskip('gpiozero')
    from gpiozero.pins.mock import MockFactory
    tm = TM1637(23, 24, pin_factory=MockFactory(), bit_delay=0)
    # No chip on mock pins -> no ACK -> a clear error instead of silence.
    with pytest.raises(DisplayHardwareError):
        tm.open()


# --------------------------------------------------------------- HT16K33 ---
class FakeSMBus:
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def write_byte(self, addr, value):
        if self.fail:
            raise OSError(121, 'Remote I/O error')
        self.calls.append(('byte', addr, value))

    def write_i2c_block_data(self, addr, reg, data):
        self.calls.append(('block', addr, reg, list(data)))

    def close(self):
        self.calls.append(('close',))


def test_ht16k33_init_and_digit_layout():
    bus = FakeSMBus()
    ht = HT16K33SevenSegment(0x70, brightness=9, smbus=bus)
    ht.open()
    assert bus.calls[:3] == [('byte', 0x70, 0x21), ('byte', 0x70, 0x81), ('byte', 0x70, 0xE9)]
    ht.write([1, 2, 3, 4], colon=True)
    _, addr, reg, data = bus.calls[-1]
    assert (addr, reg, len(data)) == (0x70, 0, 16)
    assert data[0] == 1 and data[2] == 2 and data[6] == 3 and data[8] == 4
    assert data[4] == 0x02                                  # colon
    ht.close()
    assert ('byte', 0x70, 0x80) in bus.calls


def test_ht16k33_missing_device_message():
    with pytest.raises(DisplayHardwareError, match='i2cdetect'):
        HT16K33SevenSegment(0x70, smbus=FakeSMBus(fail=True)).open()


# --------------------------------------------------------------- MAX7219 ---
class FakeSPI:
    def __init__(self):
        self.writes = []

    def xfer2(self, data):
        self.writes.append(tuple(data))

    def close(self):
        pass


def test_max7219_bit_order():
    assert to_max7219_bits(FONT['8']) == 0x7F
    assert to_max7219_bits(0x01) == 0x40            # A
    assert to_max7219_bits(0x40) == 0x01            # G
    assert to_max7219_bits(0x80) == 0x80            # DP


def test_max7219_init_and_reversed_digits():
    spi = FakeSPI()
    mx = MAX7219(digits=8, brightness=3, reverse=True, spi=spi)
    mx.open()
    regs = dict(spi.writes)
    assert regs[0x09] == 0 and regs[0x0B] == 7 and regs[0x0A] == 3 and regs[0x0C] == 1
    spi.writes.clear()
    mx.write([FONT['1']] + [0] * 7)
    assert (0x08, to_max7219_bits(FONT['1'])) in spi.writes   # left-most = DIG7


def test_parse_address():
    assert parse_address('0x27') == 39 and parse_address(63) == 63 and parse_address('39') == 39
