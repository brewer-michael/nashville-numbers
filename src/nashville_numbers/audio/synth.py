"""Additive synthesis of chords and progressions.

Used for the demo mode (`--demo`), for `--test-display` style checks and by the
test suite. The timbres are deliberately harmonic-rich (inharmonic partials,
per-partial decay, strumming, bass line, optional drums and noise) so that
tests exercise the same problems real instruments cause.
"""

from dataclasses import dataclass
from typing import List, Optional, Sequence

import numpy as np

from ..theory import Chord, QUALITIES


def midi_to_hz(midi, a4: float = 440.0):
    return a4 * 2.0 ** ((np.asarray(midi, dtype=float) - 69.0) / 12.0)


@dataclass(frozen=True)
class Timbre:
    n_partials: int
    rolloff: float        # partial amplitude ~ h ** -rolloff
    inharmonicity: float  # B in f_h = h f0 sqrt(1 + B h^2)
    decay: float          # seconds for the fundamental to fall 60 dB (0 = sustained)
    decay_slope: float    # higher partials decay this much faster per partial
    pluck: Optional[float] = None  # pluck position (fraction of string) -> comb filter


TIMBRES = {
    'sine': Timbre(1, 0.0, 0.0, 0.0, 0.0),
    'guitar': Timbre(18, 1.1, 1.2e-4, 3.0, 0.25, pluck=0.14),
    'piano': Timbre(24, 1.0, 3.5e-4, 4.0, 0.15),
    'organ': Timbre(12, 1.0, 0.0, 0.0, 0.0),       # sawtooth-like, sustained
    'pad': Timbre(6, 1.6, 0.0, 0.0, 0.0),
}


def render_note(midi: float, duration: float, sr: int, timbre: str = 'guitar',
                velocity: float = 1.0, rng: Optional[np.random.Generator] = None,
                a4: float = 440.0, detune_cents: float = 0.0) -> np.ndarray:
    """Render one note as float32 samples."""
    t_spec = TIMBRES[timbre]
    rng = rng if rng is not None else np.random.default_rng()
    n = int(round(duration * sr))
    t = np.arange(n) / sr
    f0 = float(midi_to_hz(midi, a4)) * 2.0 ** (detune_cents / 1200.0)
    out = np.zeros(n)
    for h in range(1, t_spec.n_partials + 1):
        fh = h * f0 * np.sqrt(1.0 + t_spec.inharmonicity * h * h)
        if fh >= 0.45 * sr:
            break
        amp = h ** -t_spec.rolloff
        if t_spec.pluck:
            amp *= abs(np.sin(np.pi * h * t_spec.pluck)) + 0.05
        if t_spec.decay > 0:
            t60 = t_spec.decay / (1.0 + t_spec.decay_slope * (h - 1))
            env = np.exp(-6.91 * t / t60)
        else:
            env = 1.0
        out += amp * env * np.sin(2 * np.pi * fh * t + rng.uniform(0, 2 * np.pi))
    # 5 ms attack, 30 ms release to avoid clicks
    attack = min(n, int(0.005 * sr))
    release = min(n, int(0.03 * sr))
    if attack:
        out[:attack] *= np.linspace(0, 1, attack)
    if release:
        out[-release:] *= np.linspace(1, 0, release)
    peak = np.max(np.abs(out)) or 1.0
    return (velocity * out / peak).astype(np.float32)


def voice_chord(chord: Chord, style: str = 'guitar', inversion: int = 0) -> List[int]:
    """Return MIDI notes for a playable voicing of `chord`.

    'guitar': root in E2..D#3 with the chord stacked above it (5-6 notes).
    'piano' : left-hand octave on the bass note, right-hand close voicing
              around middle C, optionally inverted.
    'close' : a close-position chord around C4.
    """
    intervals = QUALITIES[chord.quality].intervals
    if style == 'guitar':
        root = 40 + (chord.root - 4) % 12              # E2 .. D#3
        notes = [root, root + 7, root + 12]
        notes += [root + 12 + i for i in intervals[1:]]
        notes.append(root + 24)
        return sorted(set(notes))
    if style == 'piano':
        bass_pc = chord.bass if chord.bass is not None else chord.root
        bass = 36 + (bass_pc % 12)                     # C2 .. B2
        rh_root = 60 + (chord.root % 12)
        rh = [rh_root + i for i in intervals]
        for _ in range(inversion % len(rh)):
            rh = rh[1:] + [rh[0] + 12]
        rh = [n - 12 if n > 76 else n for n in rh]
        return sorted(set([bass, bass + 12] + rh))
    if style == 'close':
        return [60 + chord.root % 12 + i for i in intervals]
    raise ValueError(f"unknown voicing style {style!r}")


def render_chord(chord: Chord, duration: float, sr: int, timbre: str = 'guitar',
                 style: Optional[str] = None, strum_ms: float = 12.0,
                 rng: Optional[np.random.Generator] = None, inversion: int = 0,
                 a4: float = 440.0) -> np.ndarray:
    rng = rng if rng is not None else np.random.default_rng()
    style = style or ('guitar' if timbre == 'guitar' else 'piano')
    notes = voice_chord(chord, style, inversion)
    n = int(round(duration * sr))
    out = np.zeros(n, dtype=np.float32)
    for i, m in enumerate(notes):
        offset = int(i * strum_ms * 1e-3 * sr)
        if offset >= n:
            break
        vel = rng.uniform(0.6, 1.0)
        note = render_note(m, (n - offset) / sr, sr, timbre, vel, rng, a4,
                           detune_cents=rng.normal(0, 3))
        out[offset:offset + len(note)] += note[:n - offset]
    return out


def render_progression(chords: Sequence[Chord], seconds_per_chord: float = 2.0,
                       sr: int = 44100, timbre: str = 'guitar', strums_per_chord: int = 2,
                       bass: bool = True, drums: bool = False,
                       noise_db: Optional[float] = None, level_db: float = -12.0,
                       rng: Optional[np.random.Generator] = None, a4: float = 440.0,
                       ) -> np.ndarray:
    """Render a chord progression (re-strummed `strums_per_chord` times).

    Returns float32 audio peaking at `level_db` dBFS.
    """
    rng = rng if rng is not None else np.random.default_rng()
    seg = int(round(seconds_per_chord * sr))
    out = np.zeros(seg * len(chords), dtype=np.float32)
    strum_len = seg // strums_per_chord
    for ci, chord in enumerate(chords):
        start = ci * seg
        for s in range(strums_per_chord):
            dur = (seg - s * strum_len) / sr if timbre in ('organ', 'pad') else strum_len / sr + 0.4
            audio = render_chord(chord, dur, sr, timbre, rng=rng, a4=a4)
            a = start + s * strum_len
            b = min(len(out), a + len(audio))
            if timbre in ('organ', 'pad') and s > 0:
                break
            out[a:b] += audio[:b - a]
        if bass:
            root = 28 + (chord.root - 4) % 12          # E1 .. D#2
            line = render_note(root, seconds_per_chord, sr, 'guitar', 0.8, rng, a4)
            out[start:start + len(line)] += 0.8 * line
    if drums:
        beat = int(sr * seconds_per_chord / 4)
        click = rng.normal(0, 1, int(0.04 * sr)) * np.exp(-np.arange(int(0.04 * sr)) / (0.006 * sr))
        for pos in range(0, len(out) - len(click), beat):
            out[pos:pos + len(click)] += 0.5 * click
    peak = np.max(np.abs(out)) or 1.0
    out = out / peak * 10 ** (level_db / 20.0)
    if noise_db is not None:
        out = out + rng.normal(0, 10 ** (noise_db / 20.0), len(out))
    return out.astype(np.float32)
