import numpy as np

from nashville_numbers.app import App
from nashville_numbers.audio.sources import AudioError, AudioSource, RingBuffer, demo_chords
from nashville_numbers.audio.synth import render_progression
from nashville_numbers.config import load_config
from nashville_numbers.displays.base import Display
from nashville_numbers.theory import Key


class RecordingDisplay(Display):
    name = 'recording'

    def __init__(self):
        self.states, self.messages, self.opened, self.closed = [], [], False, False

    def open(self):
        self.opened = True

    def close(self):
        self.closed = True

    def show(self, state):
        self.states.append(state)

    def message(self, code, detail=''):
        self.messages.append(code)


class PreloadedSource(AudioSource):
    """Hands out a pre-rendered signal one hop at a time (no real time)."""

    def __init__(self, audio, sr, hop):
        super().__init__()
        self.audio, self.sample_rate, self.hop, self.pos = audio, sr, hop, 0

    def start(self):
        self.buffer = RingBuffer(self.sample_rate * 2)

    def latest(self, n):
        step = int(self.hop * self.sample_rate)
        self.buffer.write(self.audio[self.pos:self.pos + step])
        self.pos += step
        return self.buffer.latest(n)


def fast_config(hop=0.1):
    return load_config(overrides={'analysis': {'hop_seconds': hop}})


def test_app_runs_pipeline_and_handles_controls(monkeypatch):
    cfg = fast_config()
    sr = 22050
    chords = demo_chords('1 5 6m 4', Key.parse('D')) * 3
    audio = render_progression(chords, 2.0, sr, 'piano', rng=np.random.default_rng(2))
    display = RecordingDisplay()
    app = App(cfg, display, lambda: PreloadedSource(audio, sr, 0.1))
    monkeypatch.setattr('time.monotonic', _fake_clock())
    for _ in range(200):
        app.step()
    assert app.state.key is not None and app.state.key.relative_major_tonic == 2
    app.handle_event('lock')
    assert app.analyzer.keys.locked and display.messages[-1] == 'locked'
    app.handle_event('reset')
    assert app.analyzer.keys.key is None and display.messages[-1] == 'reset'


def _fake_clock():
    t = [1000.0]

    def monotonic():
        t[0] += 0.05
        return t[0]
    return monotonic


def test_app_retries_missing_audio_device():
    cfg = fast_config()
    display = RecordingDisplay()
    attempts = []

    def factory():
        attempts.append(1)
        raise AudioError('no such device')
    app = App(cfg, display, factory)
    assert app.step() is None
    assert display.messages == ['no_audio']
    assert app.step() is None and len(attempts) == 1      # waits before retrying


def test_app_run_loop_stops_and_closes_display():
    cfg = fast_config(hop=0.05)
    display = RecordingDisplay()
    sr = 8000
    app = App(cfg, display, lambda: PreloadedSource(np.zeros(sr * 5, np.float32), sr, 0.05))
    assert app.run(duration=0.5) == 0
    assert display.opened and display.closed and 'hello' in display.messages


def test_shutdown_event_runs_command():
    cfg = fast_config(hop=0.05)
    display = RecordingDisplay()
    sr = 8000
    ran = []

    class Controls:
        def __init__(self):
            self.sent = False

        def open(self):
            pass

        def poll(self):
            if not self.sent:
                self.sent = True
                return ['shutdown']
            return []

        def close(self):
            pass
    app = App(cfg, display, lambda: PreloadedSource(np.zeros(sr * 5, np.float32), sr, 0.05),
              Controls(), shutdown_command=['true'])
    app.step()                                   # create analyser first
    import subprocess
    real_run = subprocess.run

    def fake_run(cmd, **kw):
        ran.append(cmd)
        return real_run(cmd, **kw)
    import nashville_numbers.app as app_module
    app_module.subprocess.run = fake_run
    try:
        assert app.run(duration=2) == 0
    finally:
        app_module.subprocess.run = real_run
    assert ran == [['true']] and 'shutdown' in display.messages and not display.closed
