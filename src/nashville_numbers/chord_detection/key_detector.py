"""
Key detection using chord progression analysis and chroma features.
Determines the most likely musical key from a sequence of chords.
"""

import numpy as np
from collections import Counter, deque


class KeyDetector:
    """
    Detects musical key from chord progressions and chroma analysis.

    Uses multiple methods:
    1. Chord progression analysis (which chords appear together)
    2. Krumhansl-Schmuckler key-finding algorithm
    3. Weighted voting based on chord frequency
    """

    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    # Diatonic chords in major keys (I, ii, iii, IV, V, vi, vii°)
    MAJOR_KEY_CHORDS = {
        0: ['major', 'maj7'],      # I
        2: ['minor', 'min7'],      # ii
        4: ['minor', 'min7'],      # iii
        5: ['major', 'maj7'],      # IV
        7: ['major', '7'],         # V (often dominant 7th)
        9: ['minor', 'min7'],      # vi
        11: ['diminished', 'dim7'] # vii°
    }

    # Diatonic chords in minor keys (i, ii°, III, iv, v, VI, VII)
    MINOR_KEY_CHORDS = {
        0: ['minor', 'min7'],      # i
        2: ['diminished', 'dim7'], # ii°
        3: ['major', 'maj7'],      # III
        5: ['minor', 'min7'],      # iv
        7: ['minor', 'min7', 'major', '7'],  # v (can be major in harmonic minor)
        8: ['major', 'maj7'],      # VI
        10: ['major', '7']         # VII
    }

    # Krumhansl-Schmuckler key profiles (weights for each scale degree)
    MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

    def __init__(self, history_length=8):
        """
        Initialize key detector.

        Args:
            history_length (int): Number of recent chords to consider
        """
        self.history_length = history_length
        self.chord_history = deque(maxlen=history_length)
        self.current_key = None
        self.current_quality = 'major'
        self.confidence = 0.0

    def add_chord(self, chord_name, root, quality):
        """
        Add a detected chord to history.

        Args:
            chord_name (str): Full chord name (e.g., 'Am')
            root (str): Root note name
            quality (str): Chord quality (e.g., 'major', 'minor')
        """
        if chord_name is not None and root is not None:
            self.chord_history.append({
                'chord': chord_name,
                'root': root,
                'quality': quality
            })

    def detect_key_from_chords(self):
        """
        Detect key from chord progression history.

        Returns:
            dict: Dictionary with 'key', 'quality', and 'confidence'
        """
        if len(self.chord_history) < 2:
            return {
                'key': None,
                'quality': None,
                'confidence': 0.0
            }

        # Count chord occurrences
        chord_counter = Counter()
        for chord_info in self.chord_history:
            chord_counter[chord_info['chord']] += 1

        # Try each possible key and score it
        best_key = None
        best_quality = 'major'
        best_score = 0.0

        for key_idx, key_name in enumerate(self.NOTE_NAMES):
            # Try major
            major_score = self._score_key(key_idx, 'major')
            if major_score > best_score:
                best_score = major_score
                best_key = key_name
                best_quality = 'major'

            # Try minor
            minor_score = self._score_key(key_idx, 'minor')
            if minor_score > best_score:
                best_score = minor_score
                best_key = key_name
                best_quality = 'minor'

        # Calculate confidence (normalized score)
        confidence = min(1.0, best_score / len(self.chord_history))

        # Update current key
        if confidence > 0.4:  # Threshold for key change
            self.current_key = best_key
            self.current_quality = best_quality
            self.confidence = confidence

        return {
            'key': self.current_key,
            'quality': self.current_quality,
            'confidence': self.confidence
        }

    def _score_key(self, key_idx, quality):
        """
        Score how well the chord history fits a particular key.

        Args:
            key_idx (int): Root note index (0-11)
            quality (str): 'major' or 'minor'

        Returns:
            float: Score (higher is better fit)
        """
        score = 0.0

        # Get expected chords for this key
        if quality == 'major':
            expected_chords = self.MAJOR_KEY_CHORDS
        else:
            expected_chords = self.MINOR_KEY_CHORDS

        for chord_info in self.chord_history:
            root = chord_info['root']
            chord_quality = chord_info['quality']

            if root not in self.NOTE_NAMES:
                continue

            root_idx = self.NOTE_NAMES.index(root)

            # Calculate interval from key root
            interval = (root_idx - key_idx) % 12

            # Check if this chord is expected in this key
            if interval in expected_chords:
                if chord_quality in expected_chords[interval]:
                    score += 1.0  # Perfect match
                else:
                    score += 0.3  # Right root, wrong quality
            else:
                # Borrowed chord or out of key
                score -= 0.2

        return score

    def detect_key_from_chroma(self, chroma):
        """
        Detect key using Krumhansl-Schmuckler algorithm.

        Args:
            chroma (numpy.ndarray): 12-element chroma vector

        Returns:
            dict: Dictionary with 'key', 'quality', and 'confidence'
        """
        if np.sum(chroma) == 0:
            return {
                'key': None,
                'quality': None,
                'confidence': 0.0
            }

        best_correlation = -1.0
        best_key = None
        best_quality = 'major'

        # Try all 24 keys (12 major + 12 minor)
        for shift in range(12):
            # Rotate chroma to test different roots
            rotated_chroma = np.roll(chroma, -shift)

            # Correlate with major profile
            major_corr = np.corrcoef(rotated_chroma, self.MAJOR_PROFILE)[0, 1]
            if major_corr > best_correlation:
                best_correlation = major_corr
                best_key = self.NOTE_NAMES[shift]
                best_quality = 'major'

            # Correlate with minor profile
            minor_corr = np.corrcoef(rotated_chroma, self.MINOR_PROFILE)[0, 1]
            if minor_corr > best_correlation:
                best_correlation = minor_corr
                best_key = self.NOTE_NAMES[shift]
                best_quality = 'minor'

        # Convert correlation to confidence (0-1)
        confidence = (best_correlation + 1.0) / 2.0  # Correlation is in [-1, 1]

        return {
            'key': best_key,
            'quality': best_quality,
            'confidence': confidence
        }

    def get_current_key(self):
        """
        Get the currently detected key.

        Returns:
            dict: Dictionary with 'key', 'quality', and 'confidence'
        """
        return {
            'key': self.current_key,
            'quality': self.current_quality,
            'confidence': self.confidence
        }

    def reset(self):
        """Reset key detection state."""
        self.chord_history.clear()
        self.current_key = None
        self.current_quality = 'major'
        self.confidence = 0.0

    def get_scale_notes(self, key=None, quality=None):
        """
        Get the notes in a scale.

        Args:
            key (str): Key root note (uses current key if None)
            quality (str): 'major' or 'minor' (uses current quality if None)

        Returns:
            list: List of note names in the scale
        """
        if key is None:
            key = self.current_key
        if quality is None:
            quality = self.current_quality

        if key is None or key not in self.NOTE_NAMES:
            return []

        key_idx = self.NOTE_NAMES.index(key)

        # Scale intervals
        if quality == 'major':
            intervals = [0, 2, 4, 5, 7, 9, 11]  # Major scale
        else:  # minor
            intervals = [0, 2, 3, 5, 7, 8, 10]  # Natural minor scale

        scale_notes = []
        for interval in intervals:
            note_idx = (key_idx + interval) % 12
            scale_notes.append(self.NOTE_NAMES[note_idx])

        return scale_notes

    def get_scale_degree(self, note_name, key=None, quality=None):
        """
        Get the scale degree of a note in a key (1-7).

        Args:
            note_name (str): Note name
            key (str): Key root note (uses current key if None)
            quality (str): 'major' or 'minor' (uses current quality if None)

        Returns:
            int: Scale degree (1-7), or None if not in scale
        """
        scale_notes = self.get_scale_notes(key, quality)

        if note_name in scale_notes:
            return scale_notes.index(note_name) + 1

        return None
