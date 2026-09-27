from collections import Counter

import numpy as np
import pytest

from nashville_numbers.analysis.pipeline import Analyzer, AnalyzerSettings
from nashville_numbers.audio.sources import demo_chords
from nashville_numbers.audio.synth import render_progression
from nashville_numbers.theory import Key

SR = 44100


def numbers_per_chord(audio, n_chords, seconds_per_chord, settings=None):
    analyzer = Analyzer(SR, settings or AnalyzerSettings())
    votes = [[] for _ in range(n_chords)]
    for t, st in analyzer.process_signal(audio):
        seg = int((t - 0.05) // seconds_per_chord)
        if seg < n_chords and (t - seg * seconds_per_chord) > 0.5 * seconds_per_chord:
            votes[seg].append(str(st.number) if st.number else None)
    return [Counter(v).most_common(1)[0][0] if v else None for v in votes], analyzer


@pytest.mark.parametrize('progression,key,timbre,band', [
    ('1 5 6m 4', 'G', 'guitar', False),
    ('2m7 57 1maj7 1maj7', 'Bb', 'piano', False),
    ('17 47 17 57', 'E', 'guitar', True),
    ('6m 4 1 5', 'D', 'organ', True),
])
def test_end_to_end_numbers(progression, key, timbre, band):
    chords = demo_chords(progression, Key.parse(key)) * 3
    rng = np.random.default_rng(7)
    audio = render_progression(chords, 2.0, SR, timbre, bass=band, drums=band,
                               noise_db=-45 if band else None, rng=rng)
    got, analyzer = numbers_per_chord(audio, len(chords), 2.0)
    expected = progression.split() * 3
    n = len(progression.split())
    # the first pass through the progression is spent finding the key
    assert got[n:] == expected[n:]
    assert analyzer.state.key.relative_major_tonic == Key.parse(key).relative_major_tonic


def test_noise_and_silence_produce_no_chords(rng):
    analyzer = Analyzer(SR)
    quiet = rng.normal(0, 10 ** (-70 / 20), SR * 3).astype(np.float32)
    states = [st for _, st in analyzer.process_signal(quiet)]
    assert not any(st.signal for st in states)
    assert all(st.chord is None for st in states)


def test_loud_noise_opens_gate_but_is_not_a_chord(rng):
    analyzer = Analyzer(SR)
    noise = rng.normal(0, 0.1, SR * 3).astype(np.float32)
    states = [st for _, st in analyzer.process_signal(noise)]
    assert any(st.signal for st in states)
    assert sum(st.chord is not None for st in states) <= 0.1 * len(states)


def test_level_does_not_depend_on_normalisation():
    # regression: v1 normalised audio before measuring RMS, so noise always
    # looked loud. A -60 dBFS chord must stay below the -50 dBFS gate.
    chords = demo_chords('1 4 5 1', Key.parse('C'))
    audio = render_progression(chords, 1.0, SR, 'piano', level_db=-60,
                               rng=np.random.default_rng(3))
    analyzer = Analyzer(SR)
    assert not any(st.signal for _, st in analyzer.process_signal(audio))


def test_history_is_renumbered_when_key_is_found():
    chords = demo_chords('1 5 6m 4', Key.parse('A')) * 2
    audio = render_progression(chords, 2.0, SR, 'guitar', rng=np.random.default_rng(5))
    _, analyzer = numbers_per_chord(audio, len(chords), 2.0)
    assert [str(n) for n in analyzer.state.history_numbers][-4:] == ['1', '5', '6m', '4']
