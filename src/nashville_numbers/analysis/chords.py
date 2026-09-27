"""Chord recognition from chroma features.

Each frame is scored against a template for every chord in the vocabulary
(cosine similarity with the treble chroma, plus a bonus when the bass note is
the chord root, minus a small penalty for four-note chords so a plain triad is
not reported as a seventh chord). Scores become likelihoods that drive a
forward (HMM) filter with a "stay" probability, so the reported chord only
changes when the evidence for a new chord outweighs the old one for a couple of
frames. A "no chord" state absorbs silence, noise and unpitched sounds.
"""

from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

from ..theory import Chord, QUALITIES, VOCABULARIES


@dataclass
class ChordEstimate:
    chord: Optional[Chord]    # None = no chord
    confidence: float         # posterior probability of the reported state, 0..1
    score: float              # raw template similarity of the reported chord
    changed: bool             # True on the frame where the reported chord changed


class ChordRecognizer:
    def __init__(self, vocabulary: str = 'sevenths', hop_seconds: float = 0.1,
                 hold_seconds: float = 0.5, no_chord_score: float = 0.62,
                 bass_weight: float = 0.2, seventh_penalty: float = 0.02,
                 seventh_weight: float = 0.8, sharpness: float = 25.0,
                 min_switch_frames: int = 2):
        if vocabulary not in VOCABULARIES:
            raise ValueError(f"unknown chord vocabulary {vocabulary!r}; "
                             f"choose from {sorted(VOCABULARIES)}")
        self.vocabulary = vocabulary
        self.no_chord_score = no_chord_score
        self.bass_weight = bass_weight
        self.sharpness = sharpness
        self.min_switch_frames = max(1, int(min_switch_frames))
        # Probability of staying in the same state from one frame to the next.
        self.p_stay = float(np.exp(-hop_seconds / max(hold_seconds, 1e-3)))

        self.chords = []
        rows, penalties = [], []
        for q in VOCABULARIES[vocabulary]:
            quality = QUALITIES[q]
            for root in range(12):
                t = np.zeros(12)
                for k, interval in enumerate(quality.intervals):
                    t[(root + interval) % 12] = seventh_weight if k == 3 else 1.0
                rows.append(t / np.linalg.norm(t))
                penalties.append(seventh_penalty if quality.is_seventh else 0.0)
                self.chords.append(Chord(root, q))
        self._templates = np.array(rows)
        self._penalty = np.array(penalties)
        self._roots = np.array([c.root for c in self.chords])
        self.n_states = len(self.chords) + 1   # last state = no chord
        self.reset()

    def reset(self):
        self._posterior = np.full(self.n_states, 1.0 / self.n_states)
        self._current = self.n_states - 1
        self._candidate = None
        self._candidate_frames = 0

    def scores(self, chroma: np.ndarray, bass_chroma: Optional[np.ndarray] = None) -> np.ndarray:
        """Similarity of every chord (plus the no-chord state, last) to a frame."""
        norm = np.linalg.norm(chroma)
        s = np.empty(self.n_states)
        if norm <= 0:
            s[:-1] = 0.0
            s[-1] = 1.0
            return s
        s[:-1] = self._templates @ (chroma / norm) - self._penalty
        if bass_chroma is not None and np.max(bass_chroma) > 0:
            s[:-1] += self.bass_weight * bass_chroma[self._roots]
        s[-1] = self.no_chord_score
        return s

    def update(self, chroma: Optional[np.ndarray], bass_chroma: Optional[np.ndarray] = None,
               silent: bool = False) -> ChordEstimate:
        """Advance one frame.

        chroma=None means "no pitched content in this frame". With silent=True
        (input below the noise gate) the chord is dropped at once; otherwise
        (a drum hit, a strum's attack) it only counts as evidence for "no
        chord" and is debounced like any other change.
        """
        if chroma is None:
            s = np.zeros(self.n_states)
            s[-1] = 1.0
        else:
            s = self.scores(chroma, bass_chroma)
        likelihood = np.exp(self.sharpness * (s - s.max()))
        prior = self.p_stay * self._posterior + (1.0 - self.p_stay) / self.n_states
        post = likelihood * prior
        post /= post.sum()
        self._posterior = post

        best = int(np.argmax(post))
        changed = False
        if best == self._current:
            self._candidate, self._candidate_frames = None, 0
        else:
            if best == self._candidate:
                self._candidate_frames += 1
            else:
                self._candidate, self._candidate_frames = best, 1
            # Silence is reported immediately; everything else is debounced.
            if (silent and best == self.n_states - 1) or \
                    self._candidate_frames >= self.min_switch_frames:
                self._current = best
                self._candidate, self._candidate_frames = None, 0
                changed = True

        chord = None if self._current == self.n_states - 1 else self.chords[self._current]
        return ChordEstimate(chord, float(post[self._current]), float(s[self._current]), changed)

    def identify(self, chroma: np.ndarray, bass_chroma: Optional[np.ndarray] = None
                 ) -> Optional[Chord]:
        """Stateless single-frame classification (no smoothing)."""
        s = self.scores(chroma, bass_chroma)
        best = int(np.argmax(s))
        return None if best == self.n_states - 1 else self.chords[best]

    @property
    def labels(self) -> Sequence[Chord]:
        return tuple(self.chords)
