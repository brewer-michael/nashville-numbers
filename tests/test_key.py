import pytest

from nashville_numbers.analysis.key import KeyTracker, chord_fit
from nashville_numbers.theory import Chord, Key, to_nashville

HOP = 0.1


def feed(tracker, symbols, seconds=2.0, key=None):
    """Feed chord symbols (or Nashville-free chord names) for `seconds` each."""
    est = None
    for sym in symbols:
        chord = Chord.parse(sym)
        for _ in range(int(round(seconds / HOP))):
            est = tracker.update(chord, None, HOP)
    return est


def transpose(symbols, semitones):
    out = []
    for s in symbols:
        c = Chord.parse(s)
        out.append(Chord((c.root + semitones) % 12, c.quality).name())
    return out


PROGRESSIONS = {
    'pop I-V-vi-IV': (['C', 'G', 'Am', 'F'], 'C'),
    'doo-wop I-vi-IV-V': (['C', 'Am', 'F', 'G'], 'C'),
    'country I-IV-I-V': (['C', 'F', 'C', 'G'], 'C'),
    'jazz ii-V-I': (['Dm7', 'G7', 'Cmaj7', 'Cmaj7'], 'C'),
    'blues': (['C7', 'C7', 'F7', 'C7', 'G7', 'F7', 'C7', 'G7'], 'C'),
    'minor i-VI-III-VII': (['Am', 'F', 'C', 'G'], 'C'),
    'harmonic minor i-iv-V-i': (['Am', 'Dm', 'E', 'Am'], 'C'),
    'mixolydian I-bVII-IV-I': (['C', 'Bb', 'F', 'C'], 'C'),
    'royal road IV-V-iii-vi': (['F', 'G', 'Em', 'Am'], 'C'),
}


@pytest.mark.parametrize('name', list(PROGRESSIONS))
@pytest.mark.parametrize('shift', [0, 2, 5, 7, 10])
def test_progressions_find_the_key_without_flip_flopping(name, shift):
    symbols, key_name = PROGRESSIONS[name]
    symbols = transpose(symbols, shift)
    expected = (Key.parse(key_name).tonic + shift) % 12
    tracker = KeyTracker()
    seen = set()
    for _ in range(4):
        for sym in symbols:
            est = feed(tracker, [sym])
            if est.key is not None:
                seen.add(est.key.relative_major_tonic)
    assert tracker.key is not None
    assert tracker.key.relative_major_tonic == expected
    assert seen == {expected}, "the reported key changed during a steady progression"


def test_key_is_not_guessed_from_a_single_chord_too_early():
    tracker = KeyTracker()
    est = feed(tracker, ['G'], seconds=3)
    assert est.key is None


def test_single_chord_vamp_eventually_gets_a_key():
    tracker = KeyTracker(commit_timeout=16)
    est = feed(tracker, ['E'], seconds=17)
    assert est.key == Key.parse('E')


def test_modulation_switches_after_hysteresis():
    tracker = KeyTracker(switch_seconds=6)
    for _ in range(3):
        feed(tracker, ['C', 'G', 'Am', 'F'])
    assert tracker.key.relative_major_tonic == 0
    est = feed(tracker, ['D', 'A', 'Bm', 'G'], seconds=0.5)
    assert est.key.relative_major_tonic == 0          # not yet
    for _ in range(4):
        est = feed(tracker, ['D', 'A', 'Bm', 'G'])
    assert est.key.relative_major_tonic == 2


def test_lock_holds_the_key_and_reset_clears_it():
    tracker = KeyTracker()
    for _ in range(2):
        feed(tracker, ['G', 'D', 'Em', 'C'])
    assert tracker.key == Key.parse('G')
    tracker.set_locked(True)
    for _ in range(6):
        est = feed(tracker, ['Eb', 'Bb', 'Cm', 'Ab'])
    assert est.key == Key.parse('G') and est.locked
    tracker.set_locked(False)
    tracker.reset()
    assert tracker.key is None and not tracker.events


def test_silence_reset_is_optional():
    tracker = KeyTracker(silence_reset_seconds=5)
    for _ in range(2):
        feed(tracker, ['A', 'E', 'F#m', 'D'])
    assert tracker.key is not None
    for _ in range(60):
        est = tracker.update(None, None, HOP)
    assert est.key is None


def test_minor_tonic_numbering_labels_minor_key():
    tracker = KeyTracker(numbering='minor_tonic')
    for _ in range(3):
        feed(tracker, ['Am', 'Dm', 'E', 'Am'])
    assert tracker.key == Key.parse('Am')
    assert str(to_nashville(Chord.parse('E'), tracker.key, 'minor_tonic')) == '5'


def test_chord_fit_table():
    c = Key.parse('C')
    assert chord_fit(Chord.parse('G7'), c) == 1.0
    assert chord_fit(Chord.parse('Bb'), c) > 0
    assert chord_fit(Chord.parse('F#'), c) < 0
