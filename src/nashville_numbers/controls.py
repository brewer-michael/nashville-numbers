"""Panel button and footswitch.

Both are momentary switches to ground on a GPIO with the internal pull-up.
Actions (queued as strings for the main loop):

    short press          'reset'     new song: forget key and chords
    hold (1.5 s)         'lock'      lock / unlock the current key
    hold (6 s, panel)    'shutdown'  safe shutdown (panel button only)

The footswitch learns its polarity at start-up (normally-open pedals and
normally-closed ones such as many keyboard sustain pedals both work) and
re-learns it if it has been "pressed" for 10 s - that is a pedal being
plugged in or a polarity switch being flipped, not a stomp.
"""

import logging
import queue
import threading
from typing import List, Optional

log = logging.getLogger(__name__)

RELEARN_SECONDS = 10.0


class _Switch:
    def __init__(self, name: str, pin: int, events: 'queue.Queue[str]', hold_seconds: float,
                 shutdown_seconds: Optional[float], auto_polarity: bool, pin_factory=None):
        from gpiozero import DigitalInputDevice
        self.name = name
        self.events = events
        self.hold_seconds = hold_seconds
        self.shutdown_seconds = shutdown_seconds
        self.auto_polarity = auto_polarity
        self._lock = threading.Lock()
        self._timers: List[threading.Timer] = []
        self._pressed = False
        self._held = False
        self.device = DigitalInputDevice(pin, pull_up=True, bounce_time=0.02,
                                         pin_factory=pin_factory)
        # is_active is True when the pin is pulled low (switch closed).
        self.idle_active = bool(self.device.is_active) if auto_polarity else False
        if self.idle_active:
            log.info("%s: normally-closed switch detected", name)
        self.device.when_activated = self._changed
        self.device.when_deactivated = self._changed

    def _start_timer(self, delay: float, fn):
        t = threading.Timer(delay, fn)
        t.daemon = True
        self._timers.append(t)
        t.start()

    def _cancel_timers(self):
        for t in self._timers:
            t.cancel()
        self._timers = []

    def _changed(self):
        with self._lock:
            pressed = bool(self.device.is_active) != self.idle_active
            if pressed == self._pressed:
                return
            self._pressed = pressed
            if pressed:
                self._held = False
                self._start_timer(self.hold_seconds, self._on_hold)
                if self.shutdown_seconds:
                    self._start_timer(self.shutdown_seconds, self._on_shutdown)
                if self.auto_polarity:
                    self._start_timer(RELEARN_SECONDS, self._relearn)
            else:
                self._cancel_timers()
                if not self._held:
                    self.events.put('reset')

    def _on_hold(self):
        with self._lock:
            if self._pressed and not self._held:
                self._held = True
                self.events.put('lock')

    def _on_shutdown(self):
        with self._lock:
            if self._pressed:
                self.events.put('shutdown')

    def _relearn(self):
        with self._lock:
            if not self._pressed:
                return
            self.idle_active = not self.idle_active
            self._pressed = False
            self._cancel_timers()
            if self._held:
                self.events.put('lock')   # undo the accidental lock toggle
            self._held = False
            log.info("%s: polarity re-learned (pedal plugged in or switched)", self.name)

    def close(self):
        with self._lock:
            self._cancel_timers()
        self.device.close()


class Controls:
    def __init__(self, button_pin: Optional[int] = 17, footswitch_pin: Optional[int] = 27,
                 hold_seconds: float = 1.5, shutdown_seconds: float = 6.0,
                 allow_shutdown: bool = True, pin_factory=None):
        self.button_pin, self.footswitch_pin = button_pin, footswitch_pin
        self.hold_seconds = hold_seconds
        self.shutdown_seconds = shutdown_seconds if allow_shutdown else None
        self.pin_factory = pin_factory
        self.events: 'queue.Queue[str]' = queue.Queue()
        self._switches: List[_Switch] = []

    def open(self):
        if self.button_pin is not None:
            self._switches.append(_Switch('button', self.button_pin, self.events,
                                          self.hold_seconds, self.shutdown_seconds, False,
                                          self.pin_factory))
        if self.footswitch_pin is not None:
            self._switches.append(_Switch('footswitch', self.footswitch_pin, self.events,
                                          self.hold_seconds, None, True, self.pin_factory))

    def poll(self) -> List[str]:
        out = []
        while True:
            try:
                out.append(self.events.get_nowait())
            except queue.Empty:
                return out

    def close(self):
        for sw in self._switches:
            sw.close()
        self._switches = []
