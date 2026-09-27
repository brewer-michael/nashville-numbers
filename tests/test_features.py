import numpy as np
import pytest

from nashville_numbers.analysis.features import FeatureExtractor, rms_dbfs
from nashville_numbers.audio.synth import midi_to_hz, render_chord, render_note
from nashville_numbers.theory import Chord

SR = 44100
W = 16384


def tone(freq, seconds=0.5, sr=SR, amp=0.3):
    t = np.arange(int(seconds * sr)) / sr
    return (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)


def test_rms_dbfs():
    assert abs(rms_dbfs(tone(440, amp=1.0)) - (-3.01)) < 0.05
    assert rms_dbfs(np.zeros(1000)) < -150


def test_pure_tone_lands_in_its_pitch_class():
    fe = FeatureExtractor(SR, W, auto_tuning=False)
    for midi in (45, 52, 57, 64, 69, 76):
        f = fe.process(tone(midi_to_hz(midi))[:W])
        assert int(np.argmax(f.chroma)) == midi % 12


@pytest.mark.parametrize('timbre', ['guitar', 'piano', 'organ'])
@pytest.mark.parametrize('midi', [45, 48, 55, 60])
def test_harmonics_are_attributed_to_the_fundamental(timbre, midi, rng):
    # A bright single note has strong 3rd and 5th harmonics (a fifth and a
    # major third above); transcription must give most of the activation to
    # the played note's pitch class, not leave "ghost" notes on its harmonics.
    note = render_note(midi, 0.6, SR, timbre, rng=rng)
    fe = FeatureExtractor(SR, W, auto_tuning=False)
    f = fe.process(note[1000:1000 + W])
    pcs = fe.midi_notes % 12
    share = f.notes[pcs == midi % 12].sum() / f.notes.sum()
    fifth = f.notes[pcs == (midi + 7) % 12].sum() / f.notes.sum()
    assert share > 0.6
    assert fifth < 0.25


def test_bass_chroma_follows_the_lowest_note(rng):
    audio = render_chord(Chord(0, 'maj', bass=4), 0.6, SR, 'piano', rng=rng)  # C/E
    f = FeatureExtractor(SR, W, auto_tuning=False).process(audio[2000:2000 + W])
    assert int(np.argmax(f.bass_chroma)) == 4


def test_auto_tuning_follows_a_flat_instrument(rng):
    fe = FeatureExtractor(SR, W, auto_tuning=True)
    audio = np.concatenate([render_chord(Chord(r, 'maj'), 0.5, SR, 'piano', rng=rng, a4=434.0)
                            for r in (0, 5, 7, 9, 2, 4) * 6])
    for start in range(0, len(audio) - W, 4410):
        f = fe.process(audio[start:start + W])
    expected = 1200 * np.log2(434.0 / 440.0)          # about -24 cents
    assert abs(f.tuning_cents - expected) < 6


def test_digital_silence_has_no_notes():
    f = FeatureExtractor(SR, W).process(np.zeros(W, dtype=np.float32))
    assert f.energy == 0 and not np.any(f.chroma)
