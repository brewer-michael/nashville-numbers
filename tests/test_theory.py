import pytest

from nashville_numbers.theory import (Chord, Key, NUMBERING_STYLES, diatonic_chords, note_name,
                                      pitch_class, to_nashville)


def test_pitch_class_names():
    assert pitch_class('C') == 0
    assert pitch_class('F#') == pitch_class('Gb') == 6
    assert pitch_class('Cb') == 11 and pitch_class('B#') == 0
    with pytest.raises(ValueError):
        pitch_class('H')
    assert note_name(10) == 'A#' and note_name(10, flats=True) == 'Bb'


@pytest.mark.parametrize('text,root,quality', [
    ('C', 0, 'maj'), ('Am', 9, 'min'), ('F#m7', 6, 'min7'), ('Bbmaj7', 10, 'maj7'),
    ('G7', 7, '7'), ('Bdim', 11, 'dim'), ('Ebaug', 3, 'aug'), ('Dsus4', 2, 'sus4'),
    ('Bm7b5', 11, 'hdim7')])
def test_chord_parse(text, root, quality):
    c = Chord.parse(text)
    assert (c.root, c.quality) == (root, quality)


def test_chord_name_round_trip():
    for text in ['C', 'C#m', 'D7', 'Ebmaj7', 'Fdim', 'G#m7']:
        flats = 'b' in text
        assert Chord.parse(text).name(flats=flats) == text


def test_key_parse_and_names():
    assert Key.parse('G') == Key(7, 'major')
    assert Key.parse('F#m') == Key(6, 'minor')
    assert Key.parse('Eb major') == Key(3, 'major')
    assert Key.parse('Bb').name() == 'Bb'
    assert Key(9, 'minor').relative == Key(0, 'major')
    assert Key(0, 'major').relative == Key(9, 'minor')
    assert Key(5, 'major').uses_flats and not Key(7, 'major').uses_flats


@pytest.mark.parametrize('tonic', range(12))
def test_diatonic_major_numbers_in_every_key(tonic):
    key = Key(tonic, 'major')
    numbers = [str(to_nashville(c, key)) for c in diatonic_chords(key)]
    assert numbers == ['1', '2m', '3m', '4', '5', '6m', '7°']
    sevenths = [str(to_nashville(c, key)) for c in diatonic_chords(key, sevenths=True)]
    assert sevenths == ['1maj7', '2m7', '3m7', '4maj7', '57', '6m7', '7ø7']


@pytest.mark.parametrize('tonic', range(12))
def test_minor_key_numbering_styles(tonic):
    key = Key(tonic, 'minor')
    chords = diatonic_chords(key)          # i ii° III iv v VI VII
    rel = [str(to_nashville(c, key, 'relative_major')) for c in chords]
    assert rel == ['6m', '7°', '1', '2m', '3m', '4', '5']
    par = [str(to_nashville(c, key, 'minor_tonic')) for c in chords]
    assert par == ['1m', '2°', 'b3', '4m', '5m', 'b6', 'b7']


def test_chromatic_chords_use_flats_except_sharp_four_diminished():
    key = Key.parse('C')
    assert str(to_nashville(Chord.parse('Bb'), key)) == 'b7'
    assert str(to_nashville(Chord.parse('Eb'), key)) == 'b3'
    assert str(to_nashville(Chord.parse('Ab'), key)) == 'b6'
    assert str(to_nashville(Chord.parse('Db'), key)) == 'b2'
    assert str(to_nashville(Chord.parse('F#dim'), key)) == '#4°'
    assert str(to_nashville(Chord.parse('Gb'), key)) == 'b5'
    assert str(to_nashville(Chord.parse('E'), key)) == '3'      # III (V of vi)
    assert str(to_nashville(Chord.parse('D7'), key)) == '27'    # II7 (V of V)


def test_harmonic_minor_dominant_in_relative_major_numbering():
    # E major in A minor is the V chord; charted in C it is a major 3.
    assert str(to_nashville(Chord.parse('E'), Key.parse('Am'))) == '3'
    assert str(to_nashville(Chord.parse('E'), Key.parse('Am'), 'minor_tonic')) == '5'


def test_unknown_style_rejected():
    assert 'relative_major' in NUMBERING_STYLES
    with pytest.raises(ValueError):
        to_nashville(Chord.parse('C'), Key.parse('C'), 'roman')
