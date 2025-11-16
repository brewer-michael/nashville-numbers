#!/usr/bin/env python3
"""
Example: Test chord detection with synthetic audio or recorded files.
Demonstrates the chord detection algorithm without hardware.
"""

import sys
sys.path.insert(0, '../src')

import numpy as np
from nashville_numbers.audio.processor import AudioProcessor
from nashville_numbers.chord_detection.detector import ChordDetector
from nashville_numbers.chord_detection.key_detector import KeyDetector
from nashville_numbers.chord_detection.nashville import NashvilleConverter


def generate_chord_frequencies(root_note, chord_type='major', sample_rate=44100, duration=1.0):
    """
    Generate synthetic audio for a chord.

    Args:
        root_note (str): Root note name (e.g., 'C', 'G', 'Am')
        chord_type (str): Chord type ('major', 'minor', 'diminished')
        sample_rate (int): Sample rate in Hz
        duration (float): Duration in seconds

    Returns:
        numpy.ndarray: Audio samples
    """
    # Note frequencies (A4 = 440 Hz)
    note_freqs = {
        'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
        'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
        'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
    }

    # Chord intervals in semitones
    chord_intervals = {
        'major': [0, 4, 7],
        'minor': [0, 3, 7],
        'diminished': [0, 3, 6],
        '7': [0, 4, 7, 10]
    }

    # Get root frequency
    root_freq = note_freqs.get(root_note, 440.0)

    # Get intervals
    intervals = chord_intervals.get(chord_type, [0, 4, 7])

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Generate chord tones
    audio = np.zeros_like(t)
    for interval in intervals:
        freq = root_freq * (2 ** (interval / 12.0))
        audio += np.sin(2 * np.pi * freq * t)

    # Normalize
    audio = audio / np.max(np.abs(audio))

    # Apply envelope (fade in/out)
    envelope = np.ones_like(t)
    fade_samples = int(0.1 * sample_rate)
    envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
    envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
    audio *= envelope

    return audio.astype(np.float32)


def test_single_chord():
    """Test detection of a single chord."""
    print("Testing single chord detection...")
    print("-" * 60)

    # Initialize components
    processor = AudioProcessor(sample_rate=44100)
    detector = ChordDetector(min_confidence=0.3)

    # Test chords
    test_chords = [
        ('C', 'major'),
        ('G', 'major'),
        ('Am', 'minor'),
        ('F', 'major'),
        ('Dm', 'minor'),
        ('E', 'major'),
        ('Bdim', 'diminished')
    ]

    for note, chord_type in test_chords:
        # Handle note names with quality (e.g., 'Am')
        if note.endswith('m'):
            root = note[:-1]
            quality = 'minor'
        elif note.endswith('dim'):
            root = note[:-3]
            quality = 'diminished'
        else:
            root = note
            quality = chord_type

        # Generate audio
        audio = generate_chord_frequencies(root, quality)

        # Extract features
        features = processor.get_audio_features(audio)

        # Detect chord
        result = detector.detect_chord(features['chroma'], use_smoothing=False)

        # Display results
        print(f"Input: {note:6s} → Detected: {result['chord']:8s} "
              f"(Confidence: {result['confidence']:.2f})")

    print("-" * 60)


def test_progression():
    """Test key detection from a chord progression."""
    print("\nTesting chord progression and key detection...")
    print("-" * 60)

    # Initialize components
    processor = AudioProcessor(sample_rate=44100)
    chord_detector = ChordDetector(min_confidence=0.3)
    key_detector = KeyDetector(history_length=8)
    nashville = NashvilleConverter()

    # Test progression: I - IV - V - vi in C major
    progression = [
        ('C', 'major'),
        ('F', 'major'),
        ('G', 'major'),
        ('Am', 'minor'),
        ('F', 'major'),
        ('G', 'major'),
        ('C', 'major')
    ]

    print("Playing progression: C - F - G - Am - F - G - C")
    print()

    for i, (note, chord_type in enumerate(progression, 1):
        # Generate audio
        audio = generate_chord_frequencies(note, chord_type)

        # Extract features
        features = processor.get_audio_features(audio)

        # Detect chord
        chord_result = chord_detector.detect_chord(features['chroma'])

        # Update key detector
        if chord_result['chord']:
            key_detector.add_chord(
                chord_result['chord'],
                chord_result['root'],
                chord_result['quality']
            )

        # Detect key
        key_result = key_detector.detect_key_from_chords()

        # Get Nashville number
        if chord_result['chord'] and key_result['key']:
            nashville.set_key(key_result['key'], key_result['quality'])
            nash_num = nashville.chord_to_nashville(
                chord_result['root'],
                chord_result['quality']
            )
        else:
            nash_num = '?'

        # Display
        print(f"Chord {i}: {chord_result['chord']:6s} → Nashville: {nash_num:4s} | "
              f"Key: {key_result['key'] or '?':2s} {key_result['quality']:5s} "
              f"({key_result['confidence']:.2f})")

    print("-" * 60)
    print(f"\nFinal detected key: {key_result['key']} {key_result['quality']}")


def test_different_keys():
    """Test same progression in different keys."""
    print("\nTesting same progression in different keys...")
    print("-" * 60)

    # Define progressions in different keys
    keys = {
        'C': ['C', 'Am', 'F', 'G'],
        'G': ['G', 'Em', 'C', 'D'],
        'D': ['D', 'Bm', 'G', 'A'],
    }

    processor = AudioProcessor(sample_rate=44100)
    chord_detector = ChordDetector(min_confidence=0.3)

    for key_name, chords in keys.items():
        print(f"\nKey of {key_name}: {' - '.join(chords)}")

        key_detector = KeyDetector()
        nashville = NashvilleConverter()

        nash_progression = []

        for chord_name in chords:
            # Determine root and quality
            if chord_name.endswith('m'):
                root = chord_name[:-1]
                quality = 'minor'
            else:
                root = chord_name
                quality = 'major'

            # Generate and detect
            audio = generate_chord_frequencies(root, quality)
            features = processor.get_audio_features(audio)
            chord_result = chord_detector.detect_chord(features['chroma'])

            # Update key
            if chord_result['chord']:
                key_detector.add_chord(
                    chord_result['chord'],
                    chord_result['root'],
                    chord_result['quality']
                )

            key_result = key_detector.detect_key_from_chords()

            # Get Nashville number
            if chord_result['chord'] and key_result['key']:
                nashville.set_key(key_result['key'], key_result['quality'])
                nash_num = nashville.chord_to_nashville(
                    chord_result['root'],
                    chord_result['quality']
                )
                nash_progression.append(nash_num)

        print(f"Nashville progression: {' - '.join(nash_progression)}")
        print(f"(Should be: 1 - 6m - 4 - 5 in all keys)")

    print("-" * 60)


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Nashville Numbers - Chord Detection Test")
    print("=" * 60)

    test_single_chord()
    test_progression()
    test_different_keys()

    print("\n" + "=" * 60)
    print("All tests complete!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
