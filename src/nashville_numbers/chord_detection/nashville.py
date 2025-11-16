"""
Nashville Number System converter.
Converts chord names to Nashville numbers based on the current key.
"""


class NashvilleConverter:
    """
    Converts chords to Nashville Number System notation.

    The Nashville Number System uses numbers 1-7 to represent scale degrees,
    with additional symbols for chord quality:
    - Plain numbers (1, 4, 5) = Major chords
    - Numbers with 'm' (2m, 3m, 6m) = Minor chords
    - Numbers with '°' (7°) = Diminished chords
    - Numbers with '+' or 'aug' = Augmented chords
    - Additional symbols for 7ths, suspensions, etc.
    """

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Quality symbols for Nashville notation
    QUALITY_SYMBOLS = {
        'major': '',
        'minor': 'm',
        'diminished': '°',
        'augmented': '+',
        '7': '7',
        'maj7': 'M7',
        'min7': 'm7',
        'dim7': '°7',
        'sus2': 'sus2',
        'sus4': 'sus4',
    }

    def __init__(self):
        """Initialize Nashville converter."""
        self.current_key = None
        self.current_quality = 'major'

    def set_key(self, key_root, key_quality='major'):
        """
        Set the current key for conversion.

        Args:
            key_root (str): Root note of the key (e.g., 'C', 'G')
            key_quality (str): 'major' or 'minor'
        """
        if key_root in self.NOTE_NAMES:
            self.current_key = key_root
            self.current_quality = key_quality

    def chord_to_nashville(self, chord_root, chord_quality, key_root=None, key_quality=None):
        """
        Convert a chord to Nashville number notation.

        Args:
            chord_root (str): Root note of the chord (e.g., 'C', 'F')
            chord_quality (str): Quality of the chord (e.g., 'major', 'minor')
            key_root (str): Root of the key (uses current key if None)
            key_quality (str): Quality of the key (uses current quality if None)

        Returns:
            str: Nashville number (e.g., '1', '4', '5', '2m', '6m', '7°')
                 or None if key is not set or chord root not found
        """
        # Use current key if not specified
        if key_root is None:
            key_root = self.current_key
        if key_quality is None:
            key_quality = self.current_quality

        if key_root is None or key_root not in self.NOTE_NAMES:
            return None

        if chord_root not in self.NOTE_NAMES:
            return None

        # Calculate scale degree
        key_idx = self.NOTE_NAMES.index(key_root)
        chord_idx = self.NOTE_NAMES.index(chord_root)

        # Interval from key root (scale degree)
        interval = (chord_idx - key_idx) % 12

        # Map interval to scale degree
        scale_degree = self._interval_to_scale_degree(interval, key_quality)

        if scale_degree is None:
            # Chromatic chord (not in scale)
            # Use flat/sharp notation
            return self._chromatic_nashville(interval, chord_quality)

        # Get quality symbol
        quality_symbol = self.QUALITY_SYMBOLS.get(chord_quality, '')

        # Build Nashville number
        nashville = f"{scale_degree}{quality_symbol}"

        return nashville

    def _interval_to_scale_degree(self, interval, key_quality):
        """
        Convert chromatic interval to diatonic scale degree.

        Args:
            interval (int): Semitones from key root (0-11)
            key_quality (str): 'major' or 'minor'

        Returns:
            int: Scale degree (1-7), or None if not in scale
        """
        if key_quality == 'major':
            # Major scale intervals
            interval_map = {
                0: 1,   # Root
                2: 2,   # 2nd
                4: 3,   # 3rd
                5: 4,   # 4th
                7: 5,   # 5th
                9: 6,   # 6th
                11: 7   # 7th
            }
        else:  # minor
            # Natural minor scale intervals
            interval_map = {
                0: 1,   # Root
                2: 2,   # 2nd
                3: 3,   # b3rd
                5: 4,   # 4th
                7: 5,   # 5th
                8: 6,   # b6th
                10: 7   # b7th
            }

        return interval_map.get(interval, None)

    def _chromatic_nashville(self, interval, chord_quality):
        """
        Generate Nashville notation for chromatic (non-diatonic) chords.

        Args:
            interval (int): Semitones from key root
            chord_quality (str): Chord quality

        Returns:
            str: Nashville notation with flat/sharp symbols
        """
        # Approximate mapping of chromatic intervals
        chromatic_map = {
            1: 'b2',   # Flat 2
            3: 'b3',   # Flat 3
            6: 'b5',   # Flat 5 (tritone)
            8: 'b6',   # Flat 6
            10: 'b7',  # Flat 7
        }

        base = chromatic_map.get(interval, f"#{interval}")
        quality_symbol = self.QUALITY_SYMBOLS.get(chord_quality, '')

        return f"{base}{quality_symbol}"

    def get_expected_chords(self, key_root=None, key_quality=None):
        """
        Get the expected diatonic chords in a key with Nashville numbers.

        Args:
            key_root (str): Root of the key (uses current key if None)
            key_quality (str): Quality of the key (uses current quality if None)

        Returns:
            list: List of tuples (nashville_number, chord_name, chord_quality)
        """
        if key_root is None:
            key_root = self.current_key
        if key_quality is None:
            key_quality = self.current_quality

        if key_root is None or key_root not in self.NOTE_NAMES:
            return []

        key_idx = self.NOTE_NAMES.index(key_root)

        if key_quality == 'major':
            # I, ii, iii, IV, V, vi, vii°
            scale_chords = [
                (0, 'major'),   # I
                (2, 'minor'),   # ii
                (4, 'minor'),   # iii
                (5, 'major'),   # IV
                (7, 'major'),   # V
                (9, 'minor'),   # vi
                (11, 'diminished')  # vii°
            ]
        else:  # minor
            # i, ii°, III, iv, v, VI, VII
            scale_chords = [
                (0, 'minor'),   # i
                (2, 'diminished'),  # ii°
                (3, 'major'),   # III
                (5, 'minor'),   # iv
                (7, 'minor'),   # v
                (8, 'major'),   # VI
                (10, 'major')   # VII
            ]

        result = []
        for interval, quality in scale_chords:
            note_idx = (key_idx + interval) % 12
            chord_name = f"{self.NOTE_NAMES[note_idx]}{self.QUALITY_SYMBOLS[quality]}"
            nashville = self.chord_to_nashville(
                self.NOTE_NAMES[note_idx],
                quality,
                key_root,
                key_quality
            )
            result.append((nashville, chord_name, quality))

        return result

    def format_for_display(self, nashville_number, max_length=4):
        """
        Format Nashville number for display on limited displays (LCD/LED).

        Args:
            nashville_number (str): Nashville number (e.g., '1', '2m', '7°')
            max_length (int): Maximum display length

        Returns:
            str: Formatted string for display
        """
        if nashville_number is None:
            return "----"

        # Truncate if needed
        if len(nashville_number) > max_length:
            return nashville_number[:max_length]

        # Pad to max_length for consistent display
        return nashville_number.ljust(max_length)

    def parse_nashville(self, nashville_number, key_root=None, key_quality=None):
        """
        Convert Nashville number back to chord name.

        Args:
            nashville_number (str): Nashville number (e.g., '1', '4', '5', '2m')
            key_root (str): Root of the key (uses current key if None)
            key_quality (str): Quality of the key (uses current quality if None)

        Returns:
            tuple: (chord_root, chord_quality) or (None, None) if invalid
        """
        if key_root is None:
            key_root = self.current_key
        if key_quality is None:
            key_quality = self.current_quality

        if key_root is None or key_root not in self.NOTE_NAMES:
            return None, None

        # Parse the Nashville number
        # Extract numeric degree
        degree = None
        quality_str = ''

        for i, char in enumerate(nashville_number):
            if char.isdigit():
                degree = int(char)
            else:
                quality_str = nashville_number[i:]
                break

        if degree is None:
            return None, None

        # Get scale intervals
        if key_quality == 'major':
            scale_intervals = [0, 2, 4, 5, 7, 9, 11]
        else:
            scale_intervals = [0, 2, 3, 5, 7, 8, 10]

        # Get chord root
        if degree < 1 or degree > 7:
            return None, None

        key_idx = self.NOTE_NAMES.index(key_root)
        interval = scale_intervals[degree - 1]
        chord_idx = (key_idx + interval) % 12
        chord_root = self.NOTE_NAMES[chord_idx]

        # Determine chord quality from symbol
        chord_quality = 'major'  # Default
        for quality, symbol in self.QUALITY_SYMBOLS.items():
            if quality_str == symbol:
                chord_quality = quality
                break

        return chord_root, chord_quality
