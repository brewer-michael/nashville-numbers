"""Audio feature extraction: level, tuning, note activations and chroma.

Pipeline for one analysis frame (default 16384 samples, ~0.35 s):

1. Hann window + real FFT -> linear magnitude spectrum.
2. Map onto a log-frequency axis (3 bins per semitone, E1..C8) with a
   precomputed matrix.
3. Spectral whitening: subtract a running mean (one octave wide) and divide
   by the square root of the running standard deviation; negative values are
   clipped. This removes broadband noise and most of the instrument's spectral
   tilt while keeping enough of the harmonic amplitude pattern for step 4.
   (Dividing by the full standard deviation, as in Mauch & Dixon, flattens
   isolated partials and leaves 'ghost' notes on the 3rd and 5th harmonics.)
4. Approximate note transcription: explain the whitened spectrum as a
   non-negative combination of harmonic note templates (NNLS). Overtones are
   attributed to the note that produced them instead of leaking into other
   pitch classes, which is the main failure of a naive FFT chroma.
5. Fold note activations into a treble chroma and a bass chroma.

This follows the NNLS-chroma approach of Mauch & Dixon, "Approximate Note
Transcription for the Improved Identification of Difficult Chords" (ISMIR
2010), simplified for real-time use on a Raspberry Pi.
"""

from dataclasses import dataclass

import numpy as np

A4_MIDI = 69


@dataclass
class Features:
    rms_dbfs: float
    notes: np.ndarray        # activation per MIDI note (note_min..note_max)
    chroma: np.ndarray       # 12 treble pitch-class weights, max-normalised
    bass_chroma: np.ndarray  # 12 bass pitch-class weights, max-normalised
    energy: float            # total note activation (0 when nothing tonal)
    tuning_cents: float      # current tuning offset estimate vs A440
    tonality: float = 0.0    # 0..1: share of the spectrum explained by harmonic notes
                             # (chords ~0.6-0.8, noise and drums ~0.2-0.3)


def rms_dbfs(frame: np.ndarray) -> float:
    rms = float(np.sqrt(np.mean(np.square(frame, dtype=np.float64))))
    return 20.0 * np.log10(max(rms, 1e-10))


def _nnls_mu(D: np.ndarray, DtD: np.ndarray, y: np.ndarray, x0: np.ndarray,
             iterations: int) -> np.ndarray:
    """Non-negative least squares by multiplicative updates (warm start).

    Deterministic, allocation-light and fast enough to run every frame; with
    a warm start from the previous frame ~30 iterations converge well.
    """
    Dty = D.T @ y
    x = np.maximum(x0, 1e-6)
    for _ in range(iterations):
        x *= Dty / (DtD @ x + 1e-9)
    return x


class FeatureExtractor:
    """Turns raw audio frames into note activations and chroma vectors."""

    def __init__(self, sample_rate: int, window: int = 16384,
                 bins_per_semitone: int = 3, spec_min_midi: float = 26.0,
                 spec_max_midi: float = 108.0, note_min: int = 28, note_max: int = 88,
                 harmonic_decay: float = 0.7, n_harmonics: int = 12,
                 auto_tuning: bool = True, tuning_cents: float = 0.0,
                 nnls_iterations: int = 40):
        self.sample_rate = int(sample_rate)
        self.window = int(window)
        self.bps = int(bins_per_semitone)
        self.spec_min_midi = spec_min_midi
        self.spec_max_midi = spec_max_midi
        self.note_min = note_min
        self.note_max = note_max
        self.harmonic_decay = harmonic_decay
        self.n_harmonics = n_harmonics
        self.auto_tuning = auto_tuning
        self.nnls_iterations = nnls_iterations

        self._hann = np.hanning(self.window).astype(np.float64)
        self._hann_gain = float(np.sum(self._hann))
        self._fft_freqs = np.fft.rfftfreq(self.window, 1.0 / self.sample_rate)

        n_log = int(round((spec_max_midi - spec_min_midi) * self.bps)) + 1
        self._log_midi = spec_min_midi + np.arange(n_log) / self.bps
        self.midi_notes = np.arange(note_min, note_max + 1)

        # Tuning state: exponentially averaged complex phasor of peak deviations.
        self._tuning_phasor = 0j
        self.tuning_cents = float(tuning_cents)
        self._built_tuning = None
        self._build(self.tuning_cents)

        self._activations = np.full(len(self.midi_notes), 1e-3)
        self._treble_w, self._bass_w = self._chroma_weights()

    # -- setup -----------------------------------------------------------
    def _build(self, tuning_cents: float):
        """(Re)build the log-frequency map and note dictionary for a tuning."""
        ref = 440.0 * 2.0 ** (tuning_cents / 1200.0)
        centers = ref * 2.0 ** ((self._log_midi - A4_MIDI) / 12.0)
        df_fft = self.sample_rate / self.window
        half_width = np.maximum(centers * (2.0 ** (1.0 / (12 * self.bps)) - 1.0), df_fft)
        lo = int(np.searchsorted(self._fft_freqs, centers[0] - half_width[0]))
        hi = int(np.searchsorted(self._fft_freqs, centers[-1] + half_width[-1])) + 1
        lo, hi = max(lo, 1), min(hi, len(self._fft_freqs))
        f = self._fft_freqs[lo:hi]
        W = np.maximum(0.0, 1.0 - np.abs(f[None, :] - centers[:, None]) / half_width[:, None])
        W /= np.maximum(W.sum(axis=1, keepdims=True), 1e-12)
        self._fft_lo, self._fft_hi = lo, hi
        self._logmap = W

        # Note dictionary: each column is a harmonic series with geometric decay,
        # linearly interpolated onto the log-frequency bins.
        n_log = len(self._log_midi)
        D = np.zeros((n_log, len(self.midi_notes)))
        for j, m in enumerate(self.midi_notes):
            for h in range(1, self.n_harmonics + 1):
                pos = (m + 12.0 * np.log2(h) - self.spec_min_midi) * self.bps
                i0 = int(np.floor(pos))
                frac = pos - i0
                if i0 + 1 >= n_log:
                    break
                amp = self.harmonic_decay ** (h - 1)
                D[i0, j] += amp * (1.0 - frac)
                D[i0 + 1, j] += amp * frac
        D /= np.maximum(np.linalg.norm(D, axis=0, keepdims=True), 1e-12)
        self._dict = D
        self._DtD = D.T @ D
        self._built_tuning = tuning_cents

    def _chroma_weights(self):
        m = self.midi_notes.astype(float)

        # Raised-cosine windows over the treble (chord) and bass registers. The
        # treble window deliberately fades out the lowest notes: at full weight
        # the roots and fifths of guitar bass strings swamp the thirds and
        # sevenths that decide the chord quality.
        def window(lo, hi):
            w = np.zeros_like(m)
            inside = (m >= lo) & (m <= hi)
            w[inside] = 0.5 - 0.5 * np.cos(2 * np.pi * (m[inside] - lo) / (hi - lo))
            return w
        treble = window(44, 90)   # G#2 .. F#6, peak around G4
        bass = window(24, 58)     # C1 .. A#3, peak around F2
        return treble, bass

    # -- tuning ------------------------------------------------------------
    def _update_tuning(self, mag: np.ndarray):
        lo = int(np.searchsorted(self._fft_freqs, 80.0))
        hi = int(np.searchsorted(self._fft_freqs, 1800.0))
        seg = mag[lo:hi]
        if len(seg) < 5 or seg.max() <= 0:
            return
        interior = (seg[1:-1] > seg[:-2]) & (seg[1:-1] >= seg[2:]) & (seg[1:-1] > 0.1 * seg.max())
        idx = np.nonzero(interior)[0] + 1
        if len(idx) == 0:
            return
        idx = idx[np.argsort(seg[idx])[-12:]]
        a = np.log(seg[idx - 1] + 1e-12)
        b = np.log(seg[idx] + 1e-12)
        c = np.log(seg[idx + 1] + 1e-12)
        denom = a - 2 * b + c
        offset = np.where(np.abs(denom) > 1e-12, 0.5 * (a - c) / denom, 0.0)
        freqs = (lo + idx + np.clip(offset, -0.5, 0.5)) * self.sample_rate / self.window
        cents = 1200.0 * np.log2(freqs / 440.0)
        phasor = np.sum(seg[idx] * np.exp(2j * np.pi * cents / 100.0)) / np.sum(seg[idx])
        self._tuning_phasor = 0.97 * self._tuning_phasor + 0.03 * phasor
        if abs(self._tuning_phasor) > 0.3:
            est = float(np.angle(self._tuning_phasor) * 100.0 / (2 * np.pi))
            self.tuning_cents = est
            if abs(est - self._built_tuning) > 4.0:
                self._build(est)

    # -- per-frame ---------------------------------------------------------
    def log_spectrum(self, frame: np.ndarray) -> np.ndarray:
        if len(frame) != self.window:
            raise ValueError(f"frame must have {self.window} samples, got {len(frame)}")
        x = np.asarray(frame, dtype=np.float64)
        x = x - x.mean()
        mag = np.abs(np.fft.rfft(x * self._hann)) * (2.0 / self._hann_gain)
        if self.auto_tuning:
            self._update_tuning(mag)
        return self._logmap @ mag[self._fft_lo:self._fft_hi]

    def whiten(self, spec: np.ndarray) -> np.ndarray:
        width = 12 * self.bps + 1  # one octave
        kernel = np.ones(width) / width
        pad = width // 2
        padded = np.pad(spec, pad, mode='edge')
        mean = np.convolve(padded, kernel, mode='valid')
        sq = np.convolve(padded * padded, kernel, mode='valid')
        std = np.sqrt(np.maximum(sq - mean * mean, 1e-18))
        out = (spec - mean) / np.sqrt(std)
        out[out < 0] = 0.0
        # Ignore bins that are only numerical noise (digital silence).
        out[spec < 1e-7] = 0.0
        return out

    def process(self, frame: np.ndarray) -> Features:
        level = rms_dbfs(frame)
        white = self.whiten(self.log_spectrum(frame))
        if not np.any(white):
            acts = np.zeros(len(self.midi_notes))
            tonality = 0.0
        else:
            acts = _nnls_mu(self._dict, self._DtD, white, self._activations,
                            self.nnls_iterations)
            residual = np.sum((self._dict @ acts - white) ** 2) / np.sum(white * white)
            tonality = float(max(0.0, 1.0 - residual))
        self._activations = acts.copy()
        chroma = np.zeros(12)
        bass = np.zeros(12)
        pcs = self.midi_notes % 12
        np.add.at(chroma, pcs, acts * self._treble_w)
        np.add.at(bass, pcs, acts * self._bass_w)
        energy = float(np.sum(acts))
        if chroma.max() > 0:
            chroma /= chroma.max()
        if bass.max() > 0:
            bass /= bass.max()
        return Features(level, acts, chroma, bass, energy, self.tuning_cents, tonality)
