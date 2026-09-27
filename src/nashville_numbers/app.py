"""The application loop: audio source -> analyser -> display, plus controls.

Designed to run unattended as a service: it waits for (and recovers from a
lost) audio interface, keeps going if the display fails, and shuts down
cleanly on SIGTERM.
"""

import logging
import signal
import subprocess
import threading
import time
from typing import Callable, Optional

from .analysis.pipeline import Analyzer, AnalysisState
from .audio.sources import AudioError, AudioSource
from .config import analyzer_settings
from .displays import Display

log = logging.getLogger(__name__)

MESSAGE_SECONDS = 1.2
AUDIO_RETRY_SECONDS = 3.0
SHUTDOWN_COMMAND = ['sudo', '-n', 'systemctl', 'poweroff']


class App:
    def __init__(self, cfg: dict, display: Display, source_factory: Callable[[], AudioSource],
                 controls=None, shutdown_command=None):
        self.cfg = cfg
        self.display = display
        self.source_factory = source_factory
        self.controls = controls
        self.shutdown_command = shutdown_command or SHUTDOWN_COMMAND
        self.source: Optional[AudioSource] = None
        self.analyzer: Optional[Analyzer] = None
        self.state = AnalysisState()
        self._stop = threading.Event()
        self._message_until = 0.0
        self._next_audio_attempt = 0.0
        self._audio_error_reported = False
        self._shutdown_requested = False
        self.frames = 0

    # -- lifecycle -------------------------------------------------------------
    def stop(self, *_):
        self._stop.set()

    def install_signal_handlers(self):
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def _show_message(self, code: str, detail: str = '', seconds: float = MESSAGE_SECONDS):
        self.display.message(code, detail)
        self._message_until = time.monotonic() + seconds

    def _ensure_audio(self) -> bool:
        if self.source is not None and self.source.healthy:
            return True
        if time.monotonic() < self._next_audio_attempt:
            return False
        if self.source is not None:
            log.warning("Audio input stopped delivering data; reopening")
            self.source.stop()
            self.source = None
        try:
            source = self.source_factory()
            source.start()
        except (AudioError, OSError) as exc:
            self._next_audio_attempt = time.monotonic() + AUDIO_RETRY_SECONDS
            if not self._audio_error_reported:
                log.error("No audio input: %s (retrying every %.0f s)", exc, AUDIO_RETRY_SECONDS)
                self._audio_error_reported = True
            self._show_message('no_audio', str(self.cfg['audio']['device'] or 'default')[:16],
                               AUDIO_RETRY_SECONDS)
            return False
        self._audio_error_reported = False
        self.source = source
        if self.analyzer is None or self.analyzer.sample_rate != source.sample_rate:
            self.analyzer = Analyzer(source.sample_rate,
                                     analyzer_settings(self.cfg, source.sample_rate))
            log.info("Analysing %d-sample windows every %.0f ms", self.analyzer.window,
                     1000 * self.analyzer.settings.hop_seconds)
        return True

    # -- events ----------------------------------------------------------------
    def handle_event(self, event: str):
        if self.analyzer is None:
            return
        if event == 'reset':
            self.analyzer.reset()
            log.info("New song: key and chords cleared")
            self._show_message('reset')
        elif event == 'lock':
            locked = self.analyzer.toggle_lock()
            key = self.analyzer.keys.key
            log.info("Key %s%s", 'locked' if locked else 'unlocked',
                     f" ({key.long_name()})" if key and locked else '')
            self._show_message('locked' if locked else 'unlocked',
                               key.long_name() if key else '')
        elif event == 'shutdown':
            log.warning("Shutdown requested from the panel button")
            self._show_message('shutdown', seconds=30)
            self._stop.set()
            self._shutdown_requested = True

    # -- main loop -------------------------------------------------------------
    def step(self) -> Optional[AnalysisState]:
        """Analyse the latest window once (if audio is available)."""
        if not self._ensure_audio():
            return None
        frame = self.source.latest(self.analyzer.window)
        if frame is None:
            return None
        prev = self.state
        self.state = state = self.analyzer.process(frame)
        self.frames += 1
        if state.key_changed and state.key is not None:
            log.info("Key: %s", state.key.long_name())
        if state.chord_changed and log.isEnabledFor(logging.DEBUG):
            log.debug("Chord %s -> %s (%.0f%%)", prev.chord_name(), state.chord_name(),
                      100 * state.chord_confidence)
        if time.monotonic() >= self._message_until:
            self.display.show(state)
        return state

    def run(self, duration: Optional[float] = None) -> int:
        self._shutdown_requested = False
        self.display.open()
        self._show_message('hello')
        if self.controls is not None:
            try:
                self.controls.open()
            except Exception as exc:
                log.error("Controls unavailable (%s); continuing without them", exc)
                self.controls = None
        hop = self.cfg['analysis']['hop_seconds']
        start = next_tick = time.monotonic()
        try:
            while not self._stop.is_set():
                if duration is not None and time.monotonic() - start >= duration:
                    break
                if self.controls is not None:
                    for event in self.controls.poll():
                        self.handle_event(event)
                self.step()
                next_tick += hop
                delay = next_tick - time.monotonic()
                if delay < -1.0:          # fell far behind (e.g. suspended); resync
                    next_tick = time.monotonic()
                elif delay > 0:
                    self._stop.wait(delay)
        finally:
            if self.controls is not None:
                self.controls.close()
            if self.source is not None:
                self.source.stop()
            if not self._shutdown_requested:
                self.display.close()
        if self._shutdown_requested:
            try:
                subprocess.run(self.shutdown_command, check=True, timeout=15)
            except Exception as exc:
                log.error("Shutdown command %s failed: %s", ' '.join(self.shutdown_command), exc)
                self.display.message('error', 'shutdown failed')
                return 1
        return 0
