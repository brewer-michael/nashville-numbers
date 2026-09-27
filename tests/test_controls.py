import time

import pytest

gpiozero = pytest.importorskip('gpiozero')
from gpiozero.pins.mock import MockFactory, MockPin  # noqa: E402

from nashville_numbers.controls import Controls  # noqa: E402


def wait_for(controls, n=1, timeout=3.0):
    events, end = [], time.monotonic() + timeout
    while time.monotonic() < end and len(events) < n:
        events += controls.poll()
        time.sleep(0.01)
    return events


class SwitchPin(MockPin):
    """A mock pin with a switch to ground attached: while `closed` is set the
    pull-up can't raise it (MockPin alone would jump to the pull level)."""
    closed = False

    def _set_pull(self, value):
        super()._set_pull(value)
        if self.closed:
            self._change_state(False)


@pytest.fixture
def factory():
    f = MockFactory(pin_class=SwitchPin)
    yield f
    f.reset()


def make(factory, **kw):
    kw.setdefault('hold_seconds', 0.2)
    kw.setdefault('shutdown_seconds', 0.5)
    c = Controls(17, 27, pin_factory=factory, **kw)
    c.open()
    return c


def press(pin, seconds):
    pin.drive_low()
    time.sleep(seconds)
    pin.drive_high()


def test_short_press_is_new_song(factory):
    c = make(factory)
    press(factory.pin(17), 0.05)
    assert wait_for(c) == ['reset']
    c.close()


def test_hold_toggles_lock_without_reset(factory):
    c = make(factory, shutdown_seconds=5)
    press(factory.pin(17), 0.35)
    time.sleep(0.05)
    assert c.poll() == ['lock']
    c.close()


def test_long_hold_on_panel_button_requests_shutdown(factory):
    c = make(factory)
    press(factory.pin(17), 0.7)
    time.sleep(0.05)
    assert c.poll() == ['lock', 'shutdown']
    c.close()


def test_shutdown_can_be_disabled(factory):
    c = make(factory, allow_shutdown=False)
    press(factory.pin(17), 0.7)
    time.sleep(0.05)
    assert c.poll() == ['lock']
    c.close()


def test_footswitch_never_shuts_down(factory):
    c = make(factory)
    press(factory.pin(27), 0.7)
    time.sleep(0.05)
    assert c.poll() == ['lock']
    c.close()


def test_normally_closed_footswitch_is_learned(factory):
    pin = factory.pin(27)
    pin.closed = True                  # NC pedal plugged in: closed at rest
    pin.drive_low()
    c = make(factory)
    pin.closed = False
    pin.drive_high()                   # a stomp opens it...
    time.sleep(0.05)
    pin.drive_low()                    # ...and it closes again
    assert wait_for(c) == ['reset']
    c.close()


def test_footswitch_polarity_relearned_when_pedal_plugged_in(factory, monkeypatch):
    import nashville_numbers.controls as controls
    monkeypatch.setattr(controls, 'RELEARN_SECONDS', 0.4)
    c = make(factory)                  # nothing plugged in: open at rest
    pin = factory.pin(27)
    pin.drive_low()                    # NC pedal plugged in -> looks "pressed"
    time.sleep(0.6)
    # the accidental lock toggle is undone when the polarity is re-learned
    assert c.poll() == ['lock', 'lock']
    pin.drive_high()                   # now a real stomp
    time.sleep(0.05)
    pin.drive_low()
    assert wait_for(c) == ['reset']
    c.close()
