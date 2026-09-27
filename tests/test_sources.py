import numpy as np
import pytest

from nashville_numbers.audio.sources import (DemoInput, FileInput, RingBuffer, demo_chords,
                                             read_wav, to_mono, write_wav)
from nashville_numbers.theory import Chord, Key


def test_ring_buffer_wraps_and_returns_latest():
    rb = RingBuffer(10)
    assert rb.latest(4) is None
    rb.write(np.arange(7))
    rb.write(np.arange(7, 13))
    assert list(rb.latest(4)) == [9, 10, 11, 12]
    assert list(rb.latest(10)) == list(range(3, 13))
    rb.write(np.arange(100, 125))                       # bigger than capacity
    assert list(rb.latest(3)) == [122, 123, 124]


def test_to_mono():
    stereo = np.array([[1.0, 3.0], [2.0, 4.0]], dtype=np.float32)
    assert list(to_mono(stereo)) == [2.0, 3.0]
    assert list(to_mono(stereo, channel=1)) == [3.0, 4.0]


@pytest.mark.parametrize('width', [2, 3])
def test_wav_round_trip(tmp_path, width):
    sr = 22050
    x = (0.5 * np.sin(2 * np.pi * 440 * np.arange(sr) / sr)).astype(np.float32)
    path = str(tmp_path / 'tone.wav')
    if width == 2:
        write_wav(path, x, sr)
    else:
        import wave
        ints = np.round(x * (2 ** 23 - 1)).astype('<i4')
        raw = b''.join(int(v).to_bytes(3, 'little', signed=True) for v in ints)
        with wave.open(path, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(3)
            wf.setframerate(sr)
            wf.writeframes(raw)
    y, rate = read_wav(path)
    assert rate == sr and np.max(np.abs(y - x)) < 1e-3


def test_demo_chords_parse_nashville():
    chords = demo_chords('1 5 6m 4 b7 57 2m7 1maj7', Key.parse('G'))
    names = [c.name() for c in chords]
    assert names == ['G', 'D', 'Em', 'C', 'F', 'D7', 'Am7', 'Gmaj7']
    with pytest.raises(ValueError):
        demo_chords('1 5x', Key.parse('C'))
    assert demo_chords('1m', Key.parse('Am')) == [Chord.parse('Cm')]


def test_file_input_plays_into_buffer(tmp_path):
    sr = 8000
    path = str(tmp_path / 'x.wav')
    write_wav(path, np.zeros(sr // 4), sr)
    src = FileInput(path, realtime=False)
    src.start()
    assert src.finished.wait(2)
    assert src.latest(1000) is not None
    src.stop()


def test_demo_input_runs_in_real_time():
    src = DemoInput('1 4', 'C', seconds_per_chord=0.5, sample_rate=8000)
    src.start()
    import time
    time.sleep(0.3)
    got = src.buffer.total_written
    src.stop()
    assert 0.15 * 8000 < got < 0.6 * 8000
