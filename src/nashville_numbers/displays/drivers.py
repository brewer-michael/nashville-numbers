"""Low-level drivers for the supported LED display chips.

Each driver talks to exactly one chip and knows nothing about music; the
`SevenSegmentDisplay` in `led.py` turns analysis states into segment bytes
(see `sevenseg.py` for the bit order) and hands them to one of these.

* TM1637  - two-wire bit-banged protocol on any GPIO pins (gpiozero pins, so
            it works with lgpio on Pi 5, Pi 4 and older). Both lines are driven
            open-drain: the Pi only ever pulls low and releases, never drives
            high, so it can not fight the chip's ACK or the module pull-ups.
* HT16K33 - I2C (smbus2), Adafruit 7-segment backpacks (0.56" and 1.2").
* MAX7219 - SPI (spidev), 8-digit 7-segment modules, no-decode mode.
"""

import logging
import time
from typing import Optional, Sequence

log = logging.getLogger(__name__)


class DisplayHardwareError(RuntimeError):
    pass


# --------------------------------------------------------------------------
# TM1637
# --------------------------------------------------------------------------
class TM1637:
    CMD_DATA_AUTO = 0x40      # write data, auto-increment address
    CMD_ADDRESS = 0xC0        # set start address
    CMD_DISPLAY_ON = 0x88     # display on | brightness 0-7
    CMD_DISPLAY_OFF = 0x80

    def __init__(self, clk_pin: int = 23, dio_pin: int = 24, brightness: int = 7,
                 pin_factory=None, bit_delay: float = 5e-6):
        if not 0 <= brightness <= 7:
            raise ValueError("TM1637 brightness must be 0-7")
        self.clk_pin, self.dio_pin = clk_pin, dio_pin
        self.brightness = brightness
        self.bit_delay = bit_delay
        self._factory = pin_factory
        self._clk = self._dio = None
        self.acks_ok = True

    def open(self):
        if self._factory is None:
            from gpiozero import Device
            self._factory = Device.ensure_pin_factory()
        self._clk = self._factory.pin(self.clk_pin)
        self._dio = self._factory.pin(self.dio_pin)
        self._release(self._clk)
        self._release(self._dio)
        if not self.write([0, 0, 0, 0]):
            raise DisplayHardwareError(
                f"TM1637 on GPIO{self.clk_pin}/GPIO{self.dio_pin} did not acknowledge. "
                "Check CLK/DIO wiring and that the module's VCC is on 3.3 V.")

    def close(self):
        if self._clk is None:
            return
        try:
            self._command(self.CMD_DISPLAY_OFF)
        finally:
            for pin in (self._clk, self._dio):
                pin.close()
            self._clk = self._dio = None

    # open-drain helpers
    @staticmethod
    def _low(pin):
        pin.output_with_state(0)

    @staticmethod
    def _release(pin):
        pin.input_with_pull('up')

    def _wait(self):
        if self.bit_delay:
            time.sleep(self.bit_delay)

    def _start(self):
        self._release(self._dio)
        self._release(self._clk)
        self._wait()
        self._low(self._dio)
        self._wait()
        self._low(self._clk)
        self._wait()

    def _stop(self):
        self._low(self._clk)
        self._low(self._dio)
        self._wait()
        self._release(self._clk)
        self._wait()
        self._release(self._dio)
        self._wait()

    def _write_byte(self, value: int) -> bool:
        for bit in range(8):                     # LSB first
            if (value >> bit) & 1:
                self._release(self._dio)
            else:
                self._low(self._dio)
            self._wait()
            self._release(self._clk)
            self._wait()
            self._low(self._clk)
        self._release(self._dio)                 # let the chip drive ACK
        self._wait()
        self._release(self._clk)
        self._wait()
        ack = self._dio.state == 0
        self._low(self._clk)
        self._wait()
        return ack

    def _command(self, cmd: int) -> bool:
        self._start()
        ok = self._write_byte(cmd)
        self._stop()
        return ok

    def write(self, segments: Sequence[int], position: int = 0) -> bool:
        """Write raw segment bytes starting at digit `position`.
        Returns False if the chip did not acknowledge every byte."""
        ok = self._command(self.CMD_DATA_AUTO)
        self._start()
        ok &= self._write_byte(self.CMD_ADDRESS | (position & 0x07))
        for seg in segments:
            ok &= self._write_byte(seg & 0xFF)
        self._stop()
        ok &= self._command(self.CMD_DISPLAY_ON | self.brightness)
        if not ok and self.acks_ok:
            log.warning("TM1637 stopped acknowledging (loose wire?)")
        self.acks_ok = ok
        return ok

    def set_brightness(self, level: int):
        self.brightness = max(0, min(7, int(level)))
        self._command(self.CMD_DISPLAY_ON | self.brightness)


# --------------------------------------------------------------------------
# HT16K33 (Adafruit 7-segment backpacks)
# --------------------------------------------------------------------------
class HT16K33SevenSegment:
    """Adafruit 0.56"/1.2" 4-digit backpack: digits at RAM 0x00, 0x02, 0x06,
    0x08; the colon is bit 1 of 0x04."""

    OSC_ON = 0x21
    DISPLAY_ON = 0x81
    DISPLAY_OFF = 0x80
    DIMMING = 0xE0
    DIGIT_ADDR = (0x00, 0x02, 0x06, 0x08)
    COLON_ADDR = 0x04
    COLON_BIT = 0x02

    def __init__(self, address: int = 0x70, bus: int = 1, brightness: int = 15, smbus=None):
        if not 0 <= brightness <= 15:
            raise ValueError("HT16K33 brightness must be 0-15")
        self.address, self.bus_number = address, bus
        self.brightness = brightness
        self._bus = smbus

    def open(self):
        if self._bus is None:
            from smbus2 import SMBus
            self._bus = SMBus(self.bus_number)
        try:
            self._bus.write_byte(self.address, self.OSC_ON)
            self._bus.write_byte(self.address, self.DISPLAY_ON)
            self._bus.write_byte(self.address, self.DIMMING | self.brightness)
        except OSError as exc:
            raise DisplayHardwareError(
                f"No HT16K33 at I2C address 0x{self.address:02X} on bus {self.bus_number} "
                f"({exc}). Run 'i2cdetect -y {self.bus_number}' and check wiring.") from exc
        self.write([0, 0, 0, 0])

    def close(self):
        if self._bus is None:
            return
        try:
            self.write([0, 0, 0, 0])
            self._bus.write_byte(self.address, self.DISPLAY_OFF)
        finally:
            try:
                self._bus.close()
            except Exception:  # pragma: no cover - best effort
                pass
            self._bus = None

    def write(self, segments: Sequence[int], colon: bool = False):
        buf = [0] * 16
        for addr, seg in zip(self.DIGIT_ADDR, segments):
            buf[addr] = seg & 0xFF
        if colon:
            buf[self.COLON_ADDR] = self.COLON_BIT
        self._bus.write_i2c_block_data(self.address, 0x00, buf)

    def set_brightness(self, level: int):
        self.brightness = max(0, min(15, int(level)))
        self._bus.write_byte(self.address, self.DIMMING | self.brightness)


# --------------------------------------------------------------------------
# MAX7219
# --------------------------------------------------------------------------
def to_max7219_bits(seg: int) -> int:
    """Standard A..G,DP (bit0..bit7) -> MAX7219 no-decode order DP,A,B,C,D,E,F,G."""
    out = 0x80 if seg & 0x80 else 0
    for i in range(7):                 # A..G
        if seg & (1 << i):
            out |= 1 << (6 - i)
    return out


class MAX7219:
    REG_DIGIT0 = 0x01
    REG_DECODE = 0x09
    REG_INTENSITY = 0x0A
    REG_SCAN_LIMIT = 0x0B
    REG_SHUTDOWN = 0x0C
    REG_TEST = 0x0F

    def __init__(self, port: int = 0, device: int = 0, digits: int = 8, brightness: int = 8,
                 reverse: bool = True, speed_hz: int = 1_000_000, spi=None):
        if not 0 <= brightness <= 15:
            raise ValueError("MAX7219 brightness must be 0-15")
        self.port, self.device, self.digits = port, device, digits
        self.brightness, self.reverse, self.speed_hz = brightness, reverse, speed_hz
        self._spi = spi

    def _reg(self, reg: int, value: int):
        self._spi.xfer2([reg & 0xFF, value & 0xFF])

    def open(self):
        if self._spi is None:
            import spidev
            self._spi = spidev.SpiDev()
            try:
                self._spi.open(self.port, self.device)
            except OSError as exc:
                raise DisplayHardwareError(
                    f"Cannot open /dev/spidev{self.port}.{self.device} ({exc}). "
                    "Enable SPI with raspi-config.") from exc
            self._spi.max_speed_hz = self.speed_hz
            self._spi.mode = 0
        self._reg(self.REG_TEST, 0)
        self._reg(self.REG_DECODE, 0)
        self._reg(self.REG_SCAN_LIMIT, self.digits - 1)
        self._reg(self.REG_INTENSITY, self.brightness)
        self.write([0] * self.digits)
        self._reg(self.REG_SHUTDOWN, 1)

    def close(self):
        if self._spi is None:
            return
        try:
            self.write([0] * self.digits)
            self._reg(self.REG_SHUTDOWN, 0)
        finally:
            try:
                self._spi.close()
            except Exception:  # pragma: no cover
                pass
            self._spi = None

    def write(self, segments: Sequence[int]):
        """segments[0] is the left-most digit."""
        for i, seg in enumerate(list(segments)[:self.digits]):
            digit = (self.digits - 1 - i) if self.reverse else i
            self._reg(self.REG_DIGIT0 + digit, to_max7219_bits(seg))

    def set_brightness(self, level: int):
        self.brightness = max(0, min(15, int(level)))
        self._reg(self.REG_INTENSITY, self.brightness)


def parse_address(value) -> Optional[int]:
    """Accept 39, '39', '0x27' or None."""
    if value is None or isinstance(value, int):
        return value
    return int(str(value), 0)
