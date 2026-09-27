"""Music theory primitives: pitch classes, chord qualities, keys and the
Nashville Number System.

Everything here is pure Python with no dependencies so that it can be used
(and tested) anywhere.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

SHARP_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
FLAT_NAMES = ('C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B')

_NAME_TO_PC = {name: pc for pc, name in enumerate(SHARP_NAMES)}
_NAME_TO_PC.update({name: pc for pc, name in enumerate(FLAT_NAMES)})
_NAME_TO_PC.update({'Cb': 11, 'B#': 0, 'Fb': 4, 'E#': 5})

# Major keys whose signature uses flats (by tonic pitch class): F Bb Eb Ab Db Gb.
_FLAT_MAJOR_TONICS = {5, 10, 3, 8, 1, 6}


@dataclass(frozen=True)
class ChordQuality:
    """A chord type: its intervals above the root and how to spell it."""

    name: str            # internal identifier, e.g. 'min7'
    intervals: Tuple[int, ...]
    symbol: str          # chord-symbol suffix, e.g. 'm7' (Am7)
    nashville: str       # Nashville suffix, e.g. 'm7' (6m7)
    is_seventh: bool = False


QUALITIES = {
    q.name: q for q in (
        ChordQuality('maj', (0, 4, 7), '', ''),
        ChordQuality('min', (0, 3, 7), 'm', 'm'),
        ChordQuality('dim', (0, 3, 6), 'dim', '°'),
        ChordQuality('aug', (0, 4, 8), 'aug', '+'),
        ChordQuality('sus2', (0, 2, 7), 'sus2', 'sus2'),
        ChordQuality('sus4', (0, 5, 7), 'sus4', 'sus4'),
        ChordQuality('7', (0, 4, 7, 10), '7', '7', True),
        ChordQuality('maj7', (0, 4, 7, 11), 'maj7', 'maj7', True),
        ChordQuality('min7', (0, 3, 7, 10), 'm7', 'm7', True),
        ChordQuality('hdim7', (0, 3, 6, 10), 'm7b5', 'ø7', True),
    )
}

# Chord vocabularies selectable in the config.  Bigger vocabularies can name
# more chords but make more mistakes on real audio.
VOCABULARIES = {
    'triads': ('maj', 'min'),
    'basic': ('maj', 'min', 'dim', '7'),
    'sevenths': ('maj', 'min', 'dim', '7', 'maj7', 'min7'),
    'full': ('maj', 'min', 'dim', 'aug', 'sus2', 'sus4', '7', 'maj7', 'min7', 'hdim7'),
}

MAJOR_SCALE = (0, 2, 4, 5, 7, 9, 11)
NATURAL_MINOR_SCALE = (0, 2, 3, 5, 7, 8, 10)

# Nashville degree names for every semitone above the reference "1".
# Interval 6 is spelled '#4' for diminished-type chords (passing #4°) and
# 'b5' otherwise.
_DEGREE_NAMES = {0: '1', 1: 'b2', 2: '2', 3: 'b3', 4: '3', 5: '4', 6: 'b5',
                 7: '5', 8: 'b6', 9: '6', 10: 'b7', 11: '7'}


def pitch_class(name: str) -> int:
    """Return the pitch class (0 = C) of a note name like 'F#' or 'Bb'."""
    try:
        return _NAME_TO_PC[name.strip()]
    except KeyError:
        raise ValueError(f"unknown note name: {name!r}") from None


def note_name(pc: int, flats: bool = False) -> str:
    return (FLAT_NAMES if flats else SHARP_NAMES)[pc % 12]


@dataclass(frozen=True)
class Chord:
    root: int                 # pitch class 0-11
    quality: str              # key into QUALITIES
    bass: Optional[int] = None  # lowest sounding pitch class, if known

    def __post_init__(self):
        if self.quality not in QUALITIES:
            raise ValueError(f"unknown chord quality: {self.quality!r}")

    @property
    def pitch_classes(self) -> Tuple[int, ...]:
        return tuple((self.root + i) % 12 for i in QUALITIES[self.quality].intervals)

    def name(self, flats: bool = False) -> str:
        return note_name(self.root, flats) + QUALITIES[self.quality].symbol

    @property
    def is_minor_type(self) -> bool:
        return self.quality in ('min', 'min7', 'dim', 'hdim7')

    @classmethod
    def parse(cls, text: str) -> 'Chord':
        """Parse a chord symbol such as 'C', 'Am', 'F#m7', 'Bbmaj7', 'Bdim'."""
        text = text.strip()
        if len(text) >= 2 and text[1] in '#b':
            root_txt, suffix = text[:2], text[2:]
        else:
            root_txt, suffix = text[:1], text[1:]
        root = pitch_class(root_txt)
        aliases = {'': 'maj', 'M': 'maj', 'maj': 'maj', 'm': 'min', 'min': 'min', '-': 'min',
                   'dim': 'dim', '°': 'dim', 'o': 'dim', 'aug': 'aug', '+': 'aug',
                   'sus2': 'sus2', 'sus4': 'sus4', 'sus': 'sus4', '7': '7',
                   'maj7': 'maj7', 'M7': 'maj7', 'Δ7': 'maj7', 'm7': 'min7', 'min7': 'min7',
                   '-7': 'min7', 'm7b5': 'hdim7', 'ø': 'hdim7', 'ø7': 'hdim7'}
        if suffix not in aliases:
            raise ValueError(f"unknown chord symbol: {text!r}")
        return cls(root, aliases[suffix])


@dataclass(frozen=True)
class Key:
    tonic: int      # pitch class
    mode: str       # 'major' or 'minor'

    def __post_init__(self):
        if self.mode not in ('major', 'minor'):
            raise ValueError(f"mode must be 'major' or 'minor', not {self.mode!r}")

    @property
    def relative_major_tonic(self) -> int:
        return self.tonic if self.mode == 'major' else (self.tonic + 3) % 12

    @property
    def uses_flats(self) -> bool:
        return self.relative_major_tonic in _FLAT_MAJOR_TONICS

    @property
    def scale(self) -> Tuple[int, ...]:
        steps = MAJOR_SCALE if self.mode == 'major' else NATURAL_MINOR_SCALE
        return tuple((self.tonic + s) % 12 for s in steps)

    def name(self) -> str:
        tonic = note_name(self.tonic, self.uses_flats)
        return tonic if self.mode == 'major' else tonic + 'm'

    def long_name(self) -> str:
        return f"{note_name(self.tonic, self.uses_flats)} {self.mode}"

    @property
    def relative(self) -> 'Key':
        if self.mode == 'major':
            return Key((self.tonic + 9) % 12, 'minor')
        return Key((self.tonic + 3) % 12, 'major')

    @classmethod
    def parse(cls, text: str) -> 'Key':
        """Parse 'G', 'Bb', 'F#m', 'C minor', 'Eb major'."""
        text = text.strip()
        parts = text.split()
        if len(parts) == 2:
            return cls(pitch_class(parts[0]), parts[1].lower())
        if text.endswith('m') and len(text) >= 2:
            return cls(pitch_class(text[:-1]), 'minor')
        return cls(pitch_class(text), 'major')


# How minor keys are numbered:
#   'relative_major' - numbers are relative to the relative major (A minor song
#                      charted in C: Am = 6m, F = 4, G = 5).  Common in Nashville,
#                      and it does not depend on deciding major vs. minor.
#   'minor_tonic'    - the minor tonic is 1m and other degrees are relative to
#                      its parallel major (Am = 1m, F = b6, G = b7, C = b3).
NUMBERING_STYLES = ('relative_major', 'minor_tonic')


@dataclass(frozen=True)
class NashvilleNumber:
    accidental: str   # '', 'b' or '#'
    degree: int       # 1-7
    quality: str      # key into QUALITIES

    @property
    def suffix(self) -> str:
        return QUALITIES[self.quality].nashville

    def __str__(self) -> str:
        return f"{self.accidental}{self.degree}{self.suffix}"


def to_nashville(chord: Chord, key: Key, style: str = 'relative_major') -> NashvilleNumber:
    """Convert a chord to its Nashville number in `key`."""
    if style not in NUMBERING_STYLES:
        raise ValueError(f"unknown numbering style {style!r}")
    ref = key.relative_major_tonic if style == 'relative_major' else key.tonic
    interval = (chord.root - ref) % 12
    name = _DEGREE_NAMES[interval]
    if interval == 6 and chord.quality in ('dim', 'hdim7'):
        name = '#4'
    accidental = name[0] if name[0] in 'b#' else ''
    degree = int(name[-1])
    return NashvilleNumber(accidental, degree, chord.quality)


def diatonic_chords(key: Key, sevenths: bool = False):
    """The seven diatonic chords of `key` as Chord objects (I..vii or i..VII)."""
    major_triads = ('maj', 'min', 'min', 'maj', 'maj', 'min', 'dim')
    major_sevenths = ('maj7', 'min7', 'min7', 'maj7', '7', 'min7', 'hdim7')
    if key.mode == 'major':
        qualities = major_sevenths if sevenths else major_triads
        return [Chord(pc, q) for pc, q in zip(key.scale, qualities)]
    # Natural minor is the relative major's chords rotated to start on vi.
    rel = diatonic_chords(key.relative, sevenths)
    return rel[5:] + rel[:5]
