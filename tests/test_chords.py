import numpy as np
import pytest

from nashville_numbers.analysis.chords import ChordRecognizer
from nashville_numbers.analysis.features import FeatureExtractor
from nashville_numbers.audio.synth import render_chord
from nashville_numbers.theory import Chord, VOCABULARIES

SR = 44100
W = 16384


def chroma_of(pcs, bass=None):
    c = np.zeros(12)
    c[list(pcs)] = 1.0
    b = np.zeros(12)
    if bass is not None:
        b[bass] = 1.0
    return c, b


def test_templates_identify_clean_chromas():
    rec = ChordRecognizer('full')
    for chord in rec.labels:
        c, b = chroma_of(chord.pitch_classes, chord.root)
        assert rec.identify(c, b) == chord


@pytest.mark.parametrize('timbre', ['guitar', 'piano', 'organ'])
def test_synthetic_chords_are_recognised(timbre, rng):
    rec = ChordRecognizer('sevenths')
    wrong = []
    for quality in VOCABULARIES['sevenths']:
        for root in range(0, 12, 3):
            chord = Chord(root, quality)
            audio = render_chord(chord, 0.6, SR, timbre, rng=rng)
            f = FeatureExtractor(SR, W, auto_tuning=False).process(audio[2000:2000 + W])
            got = rec.identify(f.chroma, f.bass_chroma)
            if got != chord:
                wrong.append((chord.name(), got and got.name()))
    assert len(wrong) <= 1, wrong


def test_flat_chroma_is_no_chord():
    rec = ChordRecognizer('sevenths')
    assert rec.identify(np.ones(12)) is None


def test_silence_reports_no_chord_immediately():
    rec = ChordRecognizer()
    c, b = chroma_of((0, 4, 7), 0)
    for _ in range(5):
        est = rec.update(c, b)
    assert est.chord == Chord(0, 'maj')
    est = rec.update(None, silent=True)
    assert est.chord is None and est.changed


def test_a_non_tonal_frame_does_not_drop_the_chord():
    rec = ChordRecognizer()
    c, b = chroma_of((0, 4, 7), 0)
    for _ in range(5):
        rec.update(c, b)
    est = rec.update(None)                       # e.g. a drum hit
    assert est.chord == Chord(0, 'maj')
    for _ in range(6):
        est = rec.update(None)                   # sustained noise
    assert est.chord is None


def test_single_frame_glitches_are_debounced():
    rec = ChordRecognizer(min_switch_frames=2)
    c_major = chroma_of((0, 4, 7), 0)
    f_major = chroma_of((5, 9, 0), 5)
    for _ in range(10):
        rec.update(*c_major)
    est = rec.update(*f_major)                  # one odd frame
    assert est.chord == Chord(0, 'maj') and not est.changed
    est = rec.update(*c_major)
    assert est.chord == Chord(0, 'maj')
    changes = [rec.update(*f_major).changed for _ in range(6)]
    assert any(changes)
    assert rec.update(*f_major).chord == Chord(5, 'maj')


def test_unknown_vocabulary_rejected():
    with pytest.raises(ValueError):
        ChordRecognizer('everything')
