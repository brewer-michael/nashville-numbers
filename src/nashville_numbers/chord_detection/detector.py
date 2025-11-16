"""
Chord detection using chroma features and template matching.
Identifies major, minor, diminished, augmented, and seventh chords.
"""

import numpy as np
from collections import Counter


class ChordDetector:
    """
    Detects musical chords from chroma features using template matching.

    Supports detection of:
    - Major chords
    - Minor chords
    - Diminished chords
    - Augmented chords
    - Dominant 7th chords
    - Major 7th chords
    - Minor 7th chords
    """

    # Note names for chord roots
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Chord templates (semitone intervals from root)
    CHORD_TEMPLATES = {
        'major': [0, 4, 7],           # Root, Major 3rd, Perfect 5th
        'minor': [0, 3, 7],           # Root, Minor 3rd, Perfect 5th
        'diminished': [0, 3, 6],      # Root, Minor 3rd, Diminished 5th
        'augmented': [0, 4, 8],       # Root, Major 3rd, Augmented 5th
        '7': [0, 4, 7, 10],          # Dominant 7th
        'maj7': [0, 4, 7, 11],       # Major 7th
        'min7': [0, 3, 7, 10],       # Minor 7th
        'dim7': [0, 3, 6, 9],        # Diminished 7th
        'sus2': [0, 2, 7],           # Suspended 2nd
        'sus4': [0, 5, 7],           # Suspended 4th
    }

    # Chord quality symbols for display
    CHORD_SYMBOLS = {
        'major': '',
        'minor': 'm',
        'diminished': 'dim',
        'augmented': 'aug',
        '7': '7',
        'maj7': 'maj7',
        'min7': 'm7',
        'dim7': 'dim7',
        'sus2': 'sus2',
        'sus4': 'sus4',
    }

    def __init__(self, min_confidence=0.3):
        """
        Initialize chord detector.

        Args:
            min_confidence (float): Minimum confidence threshold (0-1) for chord detection
        """
        self.min_confidence = min_confidence

        # Generate chord templates for all roots and qualities
        self.templates = self._generate_templates()

        # History for smoothing
        self.chord_history = []
        self.history_length = 5

    def _generate_templates(self):
        """
        Generate chroma templates for all chord types and roots.

        Returns:
            dict: Dictionary mapping (root, quality) to chroma template
        """
        templates = {}

        for root_idx in range(12):  # All 12 roots
            for quality, intervals in self.CHORD_TEMPLATES.items():
                # Create chroma template
                template = np.zeros(12)

                for interval in intervals:
                    chroma_idx = (root_idx + interval) % 12
                    template[chroma_idx] = 1.0

                # Normalize
                template = template / np.sum(template)

                templates[(root_idx, quality)] = template

        return templates

    def _template_match(self, chroma, template):
        """
        Compute similarity between chroma and template using cosine similarity.

        Args:
            chroma (numpy.ndarray): Input chroma vector
            template (numpy.ndarray): Template chroma vector

        Returns:
            float: Similarity score (0-1)
        """
        # Cosine similarity
        dot_product = np.dot(chroma, template)
        norm_product = np.linalg.norm(chroma) * np.linalg.norm(template)

        if norm_product == 0:
            return 0.0

        similarity = dot_product / norm_product
        return max(0.0, similarity)  # Clamp to [0, 1]

    def detect_chord(self, chroma, use_smoothing=True):
        """
        Detect chord from chroma features.

        Args:
            chroma (numpy.ndarray): 12-element chroma vector
            use_smoothing (bool): Apply temporal smoothing using history

        Returns:
            dict: Dictionary with 'chord', 'root', 'quality', and 'confidence'
        """
        if np.sum(chroma) == 0:
            return {
                'chord': None,
                'root': None,
                'quality': None,
                'confidence': 0.0
            }

        # Find best matching template
        best_match = None
        best_score = 0.0

        for (root_idx, quality), template in self.templates.items():
            score = self._template_match(chroma, template)

            if score > best_score:
                best_score = score
                best_match = (root_idx, quality)

        # Check if confidence meets threshold
        if best_score < self.min_confidence:
            result = {
                'chord': None,
                'root': None,
                'quality': None,
                'confidence': best_score
            }
        else:
            root_idx, quality = best_match
            root_name = self.NOTE_NAMES[root_idx]
            chord_symbol = self.CHORD_SYMBOLS[quality]
            chord_name = f"{root_name}{chord_symbol}"

            result = {
                'chord': chord_name,
                'root': root_name,
                'quality': quality,
                'confidence': best_score
            }

        # Add to history
        if use_smoothing and result['chord'] is not None:
            self.chord_history.append(result['chord'])
            if len(self.chord_history) > self.history_length:
                self.chord_history.pop(0)

            # Use most common chord in recent history
            if len(self.chord_history) >= 3:
                chord_counts = Counter(self.chord_history)
                most_common = chord_counts.most_common(1)[0][0]

                # Parse the most common chord
                smoothed_result = self._parse_chord_name(most_common)
                smoothed_result['confidence'] = result['confidence']
                return smoothed_result

        return result

    def _parse_chord_name(self, chord_name):
        """
        Parse chord name into components.

        Args:
            chord_name (str): Chord name (e.g., 'Cmaj7', 'Am')

        Returns:
            dict: Dictionary with 'chord', 'root', and 'quality'
        """
        # Try to match against known patterns
        for quality, symbol in self.CHORD_SYMBOLS.items():
            if chord_name.endswith(symbol) or (symbol == '' and chord_name in self.NOTE_NAMES):
                if symbol == '':
                    root = chord_name
                else:
                    root = chord_name[:-len(symbol)]

                if root in self.NOTE_NAMES:
                    return {
                        'chord': chord_name,
                        'root': root,
                        'quality': quality
                    }

        # Fallback
        return {
            'chord': chord_name,
            'root': chord_name[0:1] if len(chord_name) > 0 else None,
            'quality': 'major'
        }

    def reset_history(self):
        """Clear chord history (useful when starting a new song)."""
        self.chord_history = []

    def get_chord_notes(self, chord_name):
        """
        Get the notes that make up a chord.

        Args:
            chord_name (str): Chord name (e.g., 'C', 'Am', 'G7')

        Returns:
            list: List of note names in the chord
        """
        chord_info = self._parse_chord_name(chord_name)
        root = chord_info['root']
        quality = chord_info['quality']

        if root not in self.NOTE_NAMES:
            return []

        root_idx = self.NOTE_NAMES.index(root)
        intervals = self.CHORD_TEMPLATES.get(quality, [0, 4, 7])

        notes = []
        for interval in intervals:
            note_idx = (root_idx + interval) % 12
            notes.append(self.NOTE_NAMES[note_idx])

        return notes

    def is_chord_in_key(self, chord_name, key_root, key_quality='major'):
        """
        Check if a chord belongs to a key.

        Args:
            chord_name (str): Chord name
            key_root (str): Key root note
            key_quality (str): 'major' or 'minor'

        Returns:
            bool: True if chord is diatonic to the key
        """
        if key_root not in self.NOTE_NAMES:
            return False

        key_idx = self.NOTE_NAMES.index(key_root)

        # Scale intervals for major and minor
        if key_quality == 'major':
            scale_intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        else:  # minor (natural minor)
            scale_intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale

        # Get scale notes
        scale_notes = []
        for interval in scale_intervals:
            note_idx = (key_idx + interval) % 12
            scale_notes.append(self.NOTE_NAMES[note_idx])

        # Check if all chord notes are in the scale
        chord_notes = self.get_chord_notes(chord_name)

        for note in chord_notes:
            if note not in scale_notes:
                return False

        return True
