"""
Audio signal processing for chord detection.
Performs FFT analysis, pitch detection, and chroma feature extraction.
"""

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq


class AudioProcessor:
    """
    Processes audio data to extract features for chord detection.

    Uses FFT (Fast Fourier Transform) and chroma features to analyze
    the harmonic content of audio signals.
    """

    def __init__(self, sample_rate=44100):
        """
        Initialize audio processor.

        Args:
            sample_rate (int): Sample rate in Hz
        """
        self.sample_rate = sample_rate

        # Musical constants
        self.A4_FREQ = 440.0  # Reference frequency
        self.NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def compute_fft(self, audio_data):
        """
        Compute Fast Fourier Transform of audio data.

        Args:
            audio_data (numpy.ndarray): Audio samples

        Returns:
            tuple: (frequencies, magnitudes)
        """
        # Apply window function to reduce spectral leakage
        window = np.hanning(len(audio_data))
        windowed_data = audio_data * window

        # Compute FFT
        fft_data = fft(windowed_data)
        freqs = fftfreq(len(audio_data), 1.0 / self.sample_rate)

        # Keep only positive frequencies
        positive_freqs = freqs[:len(freqs) // 2]
        magnitudes = np.abs(fft_data[:len(fft_data) // 2])

        return positive_freqs, magnitudes

    def freq_to_note(self, frequency):
        """
        Convert frequency to musical note name and octave.

        Args:
            frequency (float): Frequency in Hz

        Returns:
            tuple: (note_name, octave, cents_off)
        """
        if frequency <= 0:
            return None, None, None

        # Calculate semitones from A4
        semitones_from_a4 = 12 * np.log2(frequency / self.A4_FREQ)
        note_number = int(round(semitones_from_a4)) + 9  # A4 is note 9 in octave 4

        # Calculate cents off from exact pitch
        cents_off = (semitones_from_a4 - round(semitones_from_a4)) * 100

        # Calculate octave and note
        octave = 4 + (note_number // 12)
        note_index = note_number % 12

        return self.NOTE_NAMES[note_index], octave, cents_off

    def note_to_chroma_index(self, note_name):
        """
        Convert note name to chroma index (0-11).

        Args:
            note_name (str): Note name (e.g., 'C', 'F#')

        Returns:
            int: Chroma index (0=C, 1=C#, ..., 11=B)
        """
        try:
            return self.NOTE_NAMES.index(note_name)
        except ValueError:
            return None

    def compute_chroma(self, audio_data, use_enhanced=True):
        """
        Compute chromagram (pitch class profile) from audio data.

        A chromagram represents the energy in each of the 12 pitch classes
        (C, C#, D, etc.) regardless of octave.

        Args:
            audio_data (numpy.ndarray): Audio samples
            use_enhanced (bool): Use enhanced chroma with harmonic weighting

        Returns:
            numpy.ndarray: 12-element array of chroma values (0-11 = C to B)
        """
        freqs, magnitudes = self.compute_fft(audio_data)

        # Initialize chroma bins
        chroma = np.zeros(12)

        # Frequency range for musical notes (C1 to C8)
        min_freq = 32.7  # C1
        max_freq = 4186.0  # C8

        for freq, mag in zip(freqs, magnitudes):
            if min_freq <= freq <= max_freq and mag > 0:
                note_name, octave, cents_off = self.freq_to_note(freq)

                if note_name is not None:
                    chroma_idx = self.note_to_chroma_index(note_name)

                    if chroma_idx is not None:
                        # Weight by magnitude and penalize if off-pitch
                        tuning_weight = 1.0 - (abs(cents_off) / 100.0) if cents_off is not None else 1.0
                        chroma[chroma_idx] += mag * tuning_weight

        # Normalize
        if np.sum(chroma) > 0:
            chroma = chroma / np.sum(chroma)

        return chroma

    def detect_pitches(self, audio_data, num_pitches=6, min_magnitude_ratio=0.1):
        """
        Detect the strongest pitches in audio data.

        Args:
            audio_data (numpy.ndarray): Audio samples
            num_pitches (int): Maximum number of pitches to detect
            min_magnitude_ratio (float): Minimum magnitude relative to strongest peak

        Returns:
            list: List of tuples (note_name, octave, magnitude)
        """
        freqs, magnitudes = self.compute_fft(audio_data)

        # Find peaks in the spectrum
        peak_indices, properties = signal.find_peaks(
            magnitudes,
            height=np.max(magnitudes) * min_magnitude_ratio,
            distance=5  # Minimum distance between peaks
        )

        # Sort peaks by magnitude
        peak_magnitudes = magnitudes[peak_indices]
        sorted_indices = np.argsort(peak_magnitudes)[::-1]

        pitches = []
        for idx in sorted_indices[:num_pitches]:
            freq = freqs[peak_indices[idx]]
            mag = magnitudes[peak_indices[idx]]

            # Convert to note
            note_name, octave, cents_off = self.freq_to_note(freq)

            if note_name is not None and 30 <= freq <= 4200:  # Musical range
                pitches.append((note_name, octave, mag, freq))

        return pitches

    def compute_spectral_centroid(self, audio_data):
        """
        Compute spectral centroid (brightness measure).

        Args:
            audio_data (numpy.ndarray): Audio samples

        Returns:
            float: Spectral centroid in Hz
        """
        freqs, magnitudes = self.compute_fft(audio_data)

        if np.sum(magnitudes) == 0:
            return 0.0

        centroid = np.sum(freqs * magnitudes) / np.sum(magnitudes)
        return centroid

    def compute_rms(self, audio_data):
        """
        Compute RMS (Root Mean Square) amplitude.

        Args:
            audio_data (numpy.ndarray): Audio samples

        Returns:
            float: RMS amplitude
        """
        return np.sqrt(np.mean(audio_data ** 2))

    def preprocess_audio(self, audio_data, apply_highpass=True):
        """
        Preprocess audio data for better chord detection.

        Args:
            audio_data (numpy.ndarray): Raw audio samples
            apply_highpass (bool): Apply high-pass filter to remove low rumble

        Returns:
            numpy.ndarray: Preprocessed audio
        """
        processed = audio_data.copy()

        # Apply high-pass filter to remove low-frequency noise (< 80 Hz)
        if apply_highpass:
            sos = signal.butter(4, 80, 'highpass', fs=self.sample_rate, output='sos')
            processed = signal.sosfilt(sos, processed)

        # Normalize
        max_val = np.max(np.abs(processed))
        if max_val > 0:
            processed = processed / max_val

        return processed

    def get_audio_features(self, audio_data):
        """
        Extract comprehensive audio features for chord detection.

        Args:
            audio_data (numpy.ndarray): Audio samples

        Returns:
            dict: Dictionary with chroma, pitches, rms, and spectral features
        """
        # Preprocess audio
        processed = self.preprocess_audio(audio_data)

        # Extract features
        chroma = self.compute_chroma(processed)
        pitches = self.detect_pitches(processed, num_pitches=6)
        rms = self.compute_rms(processed)
        spectral_centroid = self.compute_spectral_centroid(processed)

        return {
            'chroma': chroma,
            'pitches': pitches,
            'rms': rms,
            'spectral_centroid': spectral_centroid,
            'has_signal': rms > 0.01  # Threshold for detecting actual audio
        }
