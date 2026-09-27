"""Audio sources. All produce mono float32 samples into a ring buffer; the app
reads the latest analysis window from it at every hop.

* LiveInput  - a sound card / USB audio interface (sounddevice, or PyAudio).
* FileInput  - plays a WAV file in real time (testing with recordings).
* DemoInput  - synthesises a looping chord progression (no audio hardware).
"""

import logging
import threading
import time
import wave
from typing import List, Optional, Sequence

import numpy as np

log = logging.getLogger(__name__)


class AudioError(RuntimeError):
    pass


class RingBuffer:
    """Thread-safe mono sample ring buffer."""

    def __init__(self, capacity: int):
        self._buf = np.zeros(capacity, dtype=np.float32)
        self._write = 0
        self._filled = 0
        self._lock = threading.Lock()
        self.total_written = 0

    def write(self, samples: np.ndarray):
        samples = np.asarray(samples, dtype=np.float32).ravel()
        n = len(samples)
        cap = len(self._buf)
        with self._lock:
            if n >= cap:
                self._buf[:] = samples[-cap:]
                self._write = 0
            else:
                end = self._write + n
                if end <= cap:
                    self._buf[self._write:end] = samples
                else:
                    split = cap - self._write
                    self._buf[self._write:] = samples[:split]
                    self._buf[:n - split] = samples[split:]
                self._write = end % cap
            self._filled = min(cap, self._filled + n)
            self.total_written += n

    def latest(self, n: int) -> Optional[np.ndarray]:
        """The most recent `n` samples, oldest first (None until available)."""
        with self._lock:
            if self._filled < n:
                return None
            start = (self._write - n) % len(self._buf)
            if start + n <= len(self._buf):
                return self._buf[start:start + n].copy()
            return np.concatenate((self._buf[start:], self._buf[:self._write]))


def to_mono(block: np.ndarray, channel: Optional[int] = None) -> np.ndarray:
    block = np.asarray(block, dtype=np.float32)
    if block.ndim == 1:
        return block
    if channel is not None:
        return block[:, channel]
    return block.mean(axis=1)


class AudioSource:
    sample_rate: int
    description: str = 'audio'

    def __init__(self, buffer_seconds: float = 3.0):
        self.buffer_seconds = buffer_seconds
        self.buffer: Optional[RingBuffer] = None

    def start(self):
        raise NotImplementedError

    def stop(self):
        pass

    def latest(self, n: int) -> Optional[np.ndarray]:
        return self.buffer.latest(n) if self.buffer is not None else None

    @property
    def healthy(self) -> bool:
        return True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc):
        self.stop()
        return False


class _ThreadedSource(AudioSource):
    """Feeds pre-rendered or generated audio into the buffer in real time."""

    block = 1024

    def __init__(self, sample_rate: int, realtime: bool = True):
        super().__init__()
        self.sample_rate = sample_rate
        self.realtime = realtime
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self.finished = threading.Event()

    def _next_block(self) -> Optional[np.ndarray]:
        raise NotImplementedError

    def _run(self):
        period = self.block / self.sample_rate
        next_t = time.monotonic()
        while not self._stop.is_set():
            block = self._next_block()
            if block is None:
                self.finished.set()
                return
            self.buffer.write(block)
            if self.realtime:
                next_t += period
                delay = next_t - time.monotonic()
                if delay > 0:
                    self._stop.wait(delay)

    def start(self):
        self.buffer = RingBuffer(int(self.buffer_seconds * self.sample_rate))
        self._stop.clear()
        self.finished.clear()
        self._thread = threading.Thread(target=self._run, name=self.description, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)
            self._thread = None


def read_wav(path: str):
    """Read a PCM WAV file -> (mono float32 samples, sample_rate). Stdlib only."""
    with wave.open(path, 'rb') as wf:
        channels, width, rate = wf.getnchannels(), wf.getsampwidth(), wf.getframerate()
        raw = wf.readframes(wf.getnframes())
    if width == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif width == 2:
        data = np.frombuffer(raw, dtype='<i2').astype(np.float32) / 32768.0
    elif width == 3:
        b = np.frombuffer(raw, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
        ints = (b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16))
        ints = np.where(ints & 0x800000, ints - (1 << 24), ints)
        data = ints.astype(np.float32) / float(1 << 23)
    elif width == 4:
        data = np.frombuffer(raw, dtype='<i4').astype(np.float32) / float(1 << 31)
    else:
        raise AudioError(f"{path}: unsupported sample width {width}")
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    return data, rate


def write_wav(path: str, samples: np.ndarray, sample_rate: int):
    pcm = np.clip(np.asarray(samples, dtype=np.float64), -1.0, 1.0)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(sample_rate))
        wf.writeframes((pcm * 32767.0).astype('<i2').tobytes())


class FileInput(_ThreadedSource):
    def __init__(self, path: str, loop: bool = False, realtime: bool = True):
        data, rate = read_wav(path)
        super().__init__(rate, realtime)
        self.samples = data
        self.loop = loop
        self.pos = 0
        self.description = f"file {path}"

    def _next_block(self):
        if self.pos >= len(self.samples):
            if not self.loop:
                return None
            self.pos = 0
        block = self.samples[self.pos:self.pos + self.block]
        self.pos += self.block
        return block


class DemoInput(_ThreadedSource):
    """Loops a synthesised progression, e.g. '1 5 6m 4' in G."""

    def __init__(self, progression: str = '1 5 6m 4', key: str = 'G',
                 seconds_per_chord: float = 2.0, timbre: str = 'guitar',
                 sample_rate: int = 44100, seed: int = 0):
        super().__init__(sample_rate)
        from ..theory import Key
        from .synth import render_progression
        self.description = f"demo '{progression}' in {key}"
        chords = demo_chords(progression, Key.parse(key))
        rng = np.random.default_rng(seed)
        self.samples = render_progression(chords, seconds_per_chord, sample_rate, timbre,
                                          rng=rng, level_db=-14.0)
        self.pos = 0

    def _next_block(self):
        if self.pos >= len(self.samples):
            self.pos = 0
        block = self.samples[self.pos:self.pos + self.block]
        self.pos += self.block
        return block


def demo_chords(progression: str, key) -> List:
    """Nashville numbers ('1 5 6m 4', 'b7', '57', '2m7') -> Chords in `key`."""
    from ..theory import Chord, MAJOR_SCALE
    suffixes = {'': 'maj', 'm': 'min', '-': 'min', '°': 'dim', 'dim': 'dim', '+': 'aug',
                '7': '7', 'maj7': 'maj7', 'm7': 'min7', '-7': 'min7', 'sus4': 'sus4',
                'sus2': 'sus2'}
    ref = key.relative_major_tonic
    chords = []
    for tok in progression.split():
        acc = tok[0] if tok[0] in 'b#' else ''
        degree = int(tok[len(acc)])
        suffix = tok[len(acc) + 1:]
        if suffix not in suffixes:
            raise ValueError(f"can't parse Nashville number {tok!r}")
        root = ref + MAJOR_SCALE[degree - 1] + {'': 0, 'b': -1, '#': 1}[acc]
        chords.append(Chord(root % 12, suffixes[suffix]))
    return chords


class LiveInput(AudioSource):
    """Captures from an audio input device via sounddevice (PortAudio) or PyAudio."""

    def __init__(self, device=None, sample_rate: Optional[int] = None,
                 channels: Optional[int] = None, channel: Optional[int] = None,
                 block_size: int = 1024, backend: str = 'auto'):
        super().__init__()
        self.device = device
        self.requested_rate = sample_rate
        self.requested_channels = channels
        self.channel = channel
        self.block_size = block_size
        self.backend = backend
        self._stream = None
        self._pa = None
        self._last_callback = 0.0
        self.overflows = 0
        self.sample_rate = sample_rate or 48000

    # -- backends ----------------------------------------------------------
    def _open_sounddevice(self):
        import sounddevice as sd
        try:
            info = sd.query_devices(self.device, 'input')
        except (ValueError, sd.PortAudioError) as exc:
            raise AudioError(f"input device {self.device!r} not found: {exc}") from exc
        rate = int(self.requested_rate or info['default_samplerate'])
        channels = self.requested_channels or (1 if info['max_input_channels'] >= 1 else 0)
        if self.channel is not None:
            channels = max(channels, self.channel + 1)
        if channels < 1:
            raise AudioError(f"device {info['name']!r} has no inputs")
        self.sample_rate = rate
        self.description = f"{info['name']} @ {rate} Hz"

        def callback(indata, frames, time_info, status):
            if status:
                self.overflows += 1
            self.buffer.write(to_mono(indata, self.channel))
            self._last_callback = time.monotonic()

        self.buffer = RingBuffer(int(self.buffer_seconds * rate))
        self._stream = sd.InputStream(device=self.device, channels=channels, samplerate=rate,
                                      blocksize=self.block_size, dtype='float32',
                                      callback=callback)
        self._stream.start()

    def _open_pyaudio(self):
        import pyaudio
        pa = pyaudio.PyAudio()
        index = self.device if isinstance(self.device, int) else None
        if isinstance(self.device, str):
            for i in range(pa.get_device_count()):
                info = pa.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0 and self.device.lower() in info['name'].lower():
                    index = i
                    break
            else:
                pa.terminate()
                raise AudioError(f"input device {self.device!r} not found")
        info = pa.get_device_info_by_index(index) if index is not None else \
            pa.get_default_input_device_info()
        rate = int(self.requested_rate or info['defaultSampleRate'])
        channels = self.requested_channels or 1
        if self.channel is not None:
            channels = max(channels, self.channel + 1)
        self.sample_rate = rate
        self.description = f"{info['name']} @ {rate} Hz"
        self.buffer = RingBuffer(int(self.buffer_seconds * rate))

        def callback(in_data, frame_count, time_info, status):
            block = np.frombuffer(in_data, dtype=np.float32).reshape(-1, channels)
            self.buffer.write(to_mono(block, self.channel))
            self._last_callback = time.monotonic()
            if status:
                self.overflows += 1
            return None, pyaudio.paContinue

        self._pa = pa
        self._stream = pa.open(format=pyaudio.paFloat32, channels=channels, rate=rate, input=True,
                               input_device_index=index, frames_per_buffer=self.block_size,
                               stream_callback=callback)
        self._stream.start_stream()

    def start(self):
        backends = ['sounddevice', 'pyaudio'] if self.backend == 'auto' else [self.backend]
        errors = []
        for name in backends:
            try:
                (self._open_sounddevice if name == 'sounddevice' else self._open_pyaudio)()
                self._last_callback = time.monotonic()
                log.info("Audio input: %s (%s)", self.description, name)
                return
            except ImportError as exc:
                errors.append(f"{name}: not installed ({exc})")
            except AudioError:
                raise
            except Exception as exc:
                errors.append(f"{name}: {exc}")
        raise AudioError("could not open audio input - " + '; '.join(errors))

    def stop(self):
        stream, self._stream = self._stream, None
        if stream is not None:
            try:
                if hasattr(stream, 'stop_stream'):
                    stream.stop_stream()
                else:
                    stream.stop()
                stream.close()
            except Exception as exc:  # pragma: no cover - device already gone
                log.debug("closing audio stream: %s", exc)
        if self._pa is not None:
            self._pa.terminate()
            self._pa = None

    @property
    def healthy(self) -> bool:
        """False when callbacks stopped arriving (device unplugged, xrun storm)."""
        return self._stream is not None and time.monotonic() - self._last_callback < 2.0


def list_input_devices(backend: str = 'auto') -> List[str]:
    lines: List[str] = []
    try:
        import sounddevice as sd
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_input_channels'] > 0:
                lines.append(f"{i:3d}: {dev['name']}  ({dev['max_input_channels']} in, "
                             f"{int(dev['default_samplerate'])} Hz)")
        return lines
    except ImportError:
        pass
    import pyaudio
    pa = pyaudio.PyAudio()
    try:
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                lines.append(f"{i:3d}: {info['name']}  ({info['maxInputChannels']} in, "
                             f"{int(info['defaultSampleRate'])} Hz)")
    finally:
        pa.terminate()
    return lines


def make_source(cfg: dict, input_file: Optional[str] = None, demo: Optional[Sequence[str]] = None
                ) -> AudioSource:
    """Build the audio source described by the config / command line."""
    if input_file:
        return FileInput(input_file)
    if demo is not None:
        progression, key = demo
        return DemoInput(progression, key)
    a = cfg['audio']
    return LiveInput(a['device'], a['sample_rate'], a['channels'], a['channel'],
                     a['block_size'], a['backend'])
