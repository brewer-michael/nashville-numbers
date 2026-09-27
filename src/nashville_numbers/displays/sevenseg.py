"""7-segment font and Nashville-number layout for 4- and 8-digit displays.

Segment bits use the common TM1637/HT16K33 order: bit 0 = A (top),
1 = B (upper right), 2 = C (lower right), 3 = D (bottom), 4 = E (lower left),
5 = F (upper left), 6 = G (middle), 7 = DP / colon.

      A
    F   B
      G
    E   C
      D    DP

Stage-readable conventions used on 4 digits (degree always in the 2nd cell):

    " 1  "  1 (major)        " 6- "  6m (minor: Nashville "dash" notation)
    " 7° "  7° (diminished)  " 5⁷ "  57  (dominant 7: small raised 7)
    " 2-⁷"  2m7              " 1M⁷"  1maj7
    "b7  "  b7 (flat seven)  "----"  listening, no chord yet
    " A- "  chord *name* (Am) shown until the key is known (letters, no number)
"""

from typing import List, Sequence, Tuple

from ..analysis.pipeline import AnalysisState
from ..theory import Chord, NashvilleNumber, note_name

A, B, C, D, E, F, G, DP = (1 << i for i in range(8))

FONT = {
    ' ': 0,
    '0': A | B | C | D | E | F, '1': B | C, '2': A | B | D | E | G,
    '3': A | B | C | D | G, '4': B | C | F | G, '5': A | C | D | F | G,
    '6': A | C | D | E | F | G, '7': A | B | C, '8': A | B | C | D | E | F | G,
    '9': A | B | C | D | F | G,
    'A': A | B | C | E | F | G, 'b': C | D | E | F | G, 'C': A | D | E | F,
    'c': D | E | G, 'd': B | C | D | E | G, 'E': A | D | E | F | G,
    'F': A | E | F | G, 'G': A | C | D | E | F, 'H': B | C | E | F | G,
    'h': C | E | F | G, 'I': E | F, 'i': E, 'J': B | C | D, 'L': D | E | F,
    'n': C | E | G, 'o': C | D | E | G, 'O': A | B | C | D | E | F,
    'P': A | B | E | F | G, 'r': E | G, 'S': A | C | D | F | G,
    't': D | E | F | G, 'U': B | C | D | E | F, 'u': C | D | E,
    'y': B | C | D | F | G, '-': G, '_': D, '=': D | G,
    '°': A | B | F | G,        # degree sign: diminished
    '⁷': A | B,                # small raised 7: seventh chords
    'M': A | B | C | E | F,    # "∩", stands in for M in maj7
    '#': B | C | E | F | G,    # sharp (looks like H)
    '?': A | B | E | G,
}

Cell = Tuple[str, bool]   # (glyph, decimal point / colon)


def encode(cells: Sequence[Cell]) -> List[int]:
    """Glyph cells -> segment bytes (unknown glyphs render blank)."""
    return [FONT.get(ch, 0) | (DP if dp else 0) for ch, dp in cells]


def text_cells(text: str, width: int) -> List[Cell]:
    """Plain text, left-aligned and padded/truncated to `width` cells.
    A '.' after a character lights that cell's decimal point."""
    cells: List[Cell] = []
    for ch in text:
        if ch == '.' and cells:
            cells[-1] = (cells[-1][0], True)
        else:
            cells.append((ch, False))
    cells = cells[:width]
    return cells + [(' ', False)] * (width - len(cells))


_QUALITY_CELLS = {
    'maj': '', 'min': '-', 'dim': '°', 'aug': 'A', 'sus2': 'S2', 'sus4': 'S4',
    '7': '⁷', 'maj7': 'M⁷', 'min7': '-⁷', 'hdim7': '°⁷',
}


def number_cells(number: NashvilleNumber) -> List[Cell]:
    """A Nashville number in 4 cells: [accidental][degree][quality...]."""
    acc = {'': ' ', 'b': 'b', '#': '#'}[number.accidental]
    text = acc + str(number.degree) + _QUALITY_CELLS[number.quality]
    return [(ch, False) for ch in text[:4].ljust(4)]


def chord_name_cells(chord: Chord, flats: bool = False) -> List[Cell]:
    """A chord name in up to 4 cells, e.g. 'A-' for Am, 'Eb' for E-flat."""
    # 'B' would look like '8', so it is drawn as a lower-case b.
    root = note_name(chord.root, flats).replace('B', 'b', 1)
    text = root + _QUALITY_CELLS[chord.quality]
    return [(ch, False) for ch in text[:4].ljust(4)]


def state_cells(state: AnalysisState, digits: int = 4) -> List[Cell]:
    """Everything a 4- or 8-digit display should show for an analysis state.

    4 digits: the Nashville number (or chord name before the key is known).
    8 digits: Nashville number, a gap, then the chord name.
    Drivers add their own key-locked indicator (colon or decimal point).
    """
    if not state.signal:
        cells = text_cells('', digits)
    elif state.chord is None:
        cells = text_cells('----', 4) + text_cells('', digits - 4)
    else:
        flats = state.key.uses_flats if state.key is not None else False
        if state.number is not None:
            main = number_cells(state.number)
            extra = chord_name_cells(state.chord, flats)
        else:
            main = chord_name_cells(state.chord, flats)
            extra = text_cells('', 4)
        cells = main if digits <= 4 else main + [(' ', False)] + extra[:digits - 5]
        cells = (cells + text_cells('', digits))[:digits]
    return cells


def with_dp(cells: Sequence[Cell], index: int, on: bool = True) -> List[Cell]:
    """Copy of `cells` with the decimal point of cell `index` set."""
    out = list(cells)
    ch, dp = out[index]
    out[index] = (ch, dp or on)
    return out
