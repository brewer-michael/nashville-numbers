"""Key tracking from recognised chords.

The key is inferred from the recent *chord changes* (not from frames: holding
one chord for a long time must not outweigh a whole progression):

* every chord event is weighted by how long it lasted (capped at 4 s) and by
  how recent it is (half-life 15 s), so after a modulation the new key wins
  instead of a "pivot" key that half-fits both sections;
* each of the 24 keys scores how well each chord fits it (diatonic chords
  score 1, common borrowed/secondary chords partial credit, anything else is
  penalised), with extra weight for the tonic chord, a bonus for V->I and
  IV->I cadences and a small, fading prior that the first chord of a song is
  its tonic;
* a slowly-averaged chroma is correlated with the Krumhansl-Kessler key
  profiles and added as a smaller vote that grows as the song goes on;
* the first key is only committed once the evidence is unambiguous, and the
  reported key only changes when another key has been clearly better for
  several seconds of music (hysteresis) - never while the key is locked.

With the default 'relative_major' numbering, a key and its relative minor
produce identical Nashville numbers, so the major/minor decision only affects
how the key is labelled.
"""

from collections import deque
from dataclasses import dataclass
from typing import Deque, List, Optional

import numpy as np

from ..theory import Chord, Key, QUALITIES

# Krumhansl-Kessler probe-tone profiles.
KK_MAJOR = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
KK_MINOR = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# How well a chord built on each scale step fits a key: {interval: {quality: fit}}.
_OUT_OF_KEY = -0.5
_MAJOR_FIT = {
    0: {'maj': 1.0, 'maj7': 1.0, '7': 0.9, 'sus2': 0.8, 'sus4': 0.8, 'aug': 0.3},
    2: {'min': 1.0, 'min7': 1.0, 'maj': 0.4, '7': 0.5, 'sus2': 0.6, 'sus4': 0.6},
    3: {'maj': 0.2},
    4: {'min': 1.0, 'min7': 1.0, 'maj': 0.3, '7': 0.4},
    5: {'maj': 1.0, 'maj7': 1.0, '7': 0.8, 'min': 0.4, 'sus2': 0.8, 'sus4': 0.6},
    7: {'maj': 1.0, '7': 1.0, 'sus4': 0.9, 'sus2': 0.6, 'min': 0.3},
    8: {'maj': 0.3, 'maj7': 0.3},
    9: {'min': 1.0, 'min7': 1.0, 'maj': 0.3, '7': 0.4},
    10: {'maj': 0.6, '7': 0.4},
    11: {'dim': 1.0, 'hdim7': 1.0, 'min': 0.2},
}
_MINOR_FIT = {
    0: {'min': 1.0, 'min7': 1.0, 'sus2': 0.6, 'sus4': 0.6, 'maj': 0.2},
    2: {'dim': 1.0, 'hdim7': 1.0, 'min': 0.3},
    3: {'maj': 1.0, 'maj7': 1.0, 'aug': 0.3},
    5: {'min': 1.0, 'min7': 1.0, 'maj': 0.4, '7': 0.3},
    7: {'min': 1.0, 'min7': 1.0, 'maj': 1.0, '7': 1.0, 'sus4': 0.8},
    8: {'maj': 1.0, 'maj7': 1.0},
    10: {'maj': 1.0, '7': 1.0},
    11: {'dim': 0.8},
}
# Tonic chord qualities per mode ('7' on the tonic is the blues I7).
_TONIC_QUALITIES = {'major': ('maj', 'maj7', '7', 'sus2', 'sus4'), 'minor': ('min', 'min7')}
_TONIC_WEIGHT = 1.6
_DOMINANT_WEIGHT = 1.15
_V_I_BONUS = 0.6
_IV_I_BONUS = 0.3
_FIRST_CHORD_PRIOR = 0.75     # "weighted seconds" of evidence for the first chord as tonic
_SUBSTANTIAL_EVENT = 0.75     # seconds a chord must last to count towards committing a key
_MAX_EVENT_SECONDS = 4.0

ALL_KEYS: List[Key] = [Key(t, m) for m in ('major', 'minor') for t in range(12)]
_QUALITY_NAMES = tuple(QUALITIES)
_CHORD_INDEX = {(r, q): qi * 12 + r for qi, q in enumerate(_QUALITY_NAMES) for r in range(12)}
_ALL_CHORDS = [Chord(r, q) for q in _QUALITY_NAMES for r in range(12)]


def chord_fit(chord: Chord, key: Key) -> float:
    table = _MAJOR_FIT if key.mode == 'major' else _MINOR_FIT
    interval = (chord.root - key.tonic) % 12
    return table.get(interval, {}).get(chord.quality, _OUT_OF_KEY)


def _is_tonic(chord: Chord, key: Key) -> bool:
    return chord.root == key.tonic and chord.quality in _TONIC_QUALITIES[key.mode]


def _is_dominant(chord: Chord, key: Key) -> bool:
    return (chord.root - key.tonic) % 12 == 7 and chord.quality in ('maj', '7', 'sus4')


def _is_subdominant(chord: Chord, key: Key) -> bool:
    return (chord.root - key.tonic) % 12 == 5 and \
        chord.quality in ('maj', 'maj7', '7', 'min', 'min7')


def _table(fn):
    return np.array([[fn(c, k) for c in _ALL_CHORDS] for k in ALL_KEYS], dtype=float)


_FIT = _table(chord_fit)
_TONIC = _table(_is_tonic).astype(bool)
_DOMINANT = _table(_is_dominant).astype(bool)
_SUBDOMINANT = _table(_is_subdominant).astype(bool)
_MULT = np.where(_TONIC, _TONIC_WEIGHT, np.where(_DOMINANT, _DOMINANT_WEIGHT, 1.0))


def _profiles():
    p = np.array([np.roll(KK_MAJOR if k.mode == 'major' else KK_MINOR, k.tonic)
                  for k in ALL_KEYS])
    p -= p.mean(axis=1, keepdims=True)
    return p / np.linalg.norm(p, axis=1, keepdims=True)


_PROFILES = _profiles()


@dataclass
class ChordEvent:
    chord: Chord
    duration: float = 0.0


@dataclass
class KeyEstimate:
    key: Optional[Key]
    strength: float      # 0..1, how well recent chords fit the reported key
    locked: bool
    changed: bool        # True on the frame where the reported key changed


class KeyTracker:
    def __init__(self, window_seconds: float = 60.0, max_events: int = 32,
                 min_events: int = 4, switch_seconds: float = 6.0,
                 switch_margin: float = 0.12, commit_margin: float = 0.08,
                 fast_commit_margin: float = 0.2,
                 commit_timeout: float = 16.0, chroma_weight: float = 0.25,
                 chroma_seconds: float = 20.0, numbering: str = 'relative_major',
                 silence_reset_seconds: float = 0.0, relabel_seconds: float = 3.0,
                 recency_half_life: float = 15.0, recent_seconds: float = 12.0,
                 fast_switch_margin: float = 0.3, fast_switch_seconds: float = 4.0):
        self.window_seconds = window_seconds
        self.max_events = max_events
        self.min_events = min_events
        self.switch_seconds = switch_seconds
        self.switch_margin = switch_margin
        self.commit_margin = commit_margin
        self.fast_commit_margin = fast_commit_margin
        self.commit_timeout = commit_timeout
        self.chroma_weight = chroma_weight
        self.chroma_seconds = chroma_seconds
        self.numbering = numbering
        self.silence_reset_seconds = silence_reset_seconds
        self.relabel_seconds = relabel_seconds
        self.recency_half_life = recency_half_life
        self.recent_seconds = recent_seconds
        self.fast_switch_margin = fast_switch_margin
        self.fast_switch_seconds = fast_switch_seconds
        # Keys that yield identical Nashville numbers share a group id.
        if numbering == 'relative_major':
            self._group = np.array([k.relative_major_tonic for k in ALL_KEYS])
        else:
            self._group = np.arange(len(ALL_KEYS))
        self.locked = False
        self.reset()

    # -- state ---------------------------------------------------------------
    def reset(self):
        """Forget everything (new song). Keeps the lock state."""
        self.events: Deque[ChordEvent] = deque(maxlen=self.max_events)
        self.key: Optional[Key] = None
        self._first_chord: Optional[Chord] = None
        self._chroma = np.zeros(12)
        self._active_seconds = 0.0
        self._silent_seconds = 0.0
        self._challenger: Optional[int] = None
        self._challenger_seconds = 0.0
        self._relabel_seconds = 0.0
        self._last_chord: Optional[Chord] = None
        self._strength = 0.0

    def set_locked(self, locked: bool):
        self.locked = bool(locked)

    def set_key(self, key: Optional[Key]):
        """Force a key (e.g. chosen by the user)."""
        self.key = key
        self._challenger, self._challenger_seconds = None, 0.0

    # -- scoring -------------------------------------------------------------
    def _trim(self):
        total = 0.0
        keep = 0
        for ev in reversed(self.events):
            total += min(ev.duration, _MAX_EVENT_SECONDS)
            keep += 1
            if total >= self.window_seconds:
                break
        while len(self.events) > keep:
            self.events.popleft()

    def _weights(self, events) -> np.ndarray:
        """Duration (capped) times recency decay for each event, oldest first."""
        durations = np.array([e.duration for e in events], dtype=float)
        # age = music played after the event ended
        age = np.concatenate((np.cumsum(durations[::-1])[::-1][1:], [0.0]))
        decay = 0.5 ** (age / self.recency_half_life) if self.recency_half_life else 1.0
        return np.minimum(durations, _MAX_EVENT_SECONDS) * decay

    @staticmethod
    def _score_events(events, w: np.ndarray, first_chord: Optional[Chord] = None) -> np.ndarray:
        idx = np.array([_CHORD_INDEX[(e.chord.root, e.chord.quality)] for e in events])
        total = (_FIT[:, idx] * _MULT[:, idx]) @ w
        if len(events) > 1:
            prev, cur = idx[:-1], idx[1:]
            wmin = np.minimum(w[:-1], w[1:])
            to_tonic = _TONIC[:, cur]
            total += (to_tonic & _DOMINANT[:, prev]) @ wmin * _V_I_BONUS
            total += (to_tonic & _SUBDOMINANT[:, prev]) @ wmin * _IV_I_BONUS
        norm = w.sum()
        if first_chord is not None:
            first = _CHORD_INDEX[(first_chord.root, first_chord.quality)]
            total += _FIRST_CHORD_PRIOR * _TONIC[:, first] * _TONIC_WEIGHT
            norm += _FIRST_CHORD_PRIOR
        return total / norm

    def key_scores(self) -> np.ndarray:
        """Long-term score for each key in ALL_KEYS (higher = better)."""
        events = [e for e in self.events if e.duration > 0]
        scores = np.zeros(len(ALL_KEYS))
        if events:
            scores = self._score_events(events, self._weights(events), self._first_chord)
        if np.any(self._chroma):
            c = self._chroma - self._chroma.mean()
            n = np.linalg.norm(c)
            if n > 0:
                ramp = min(1.0, self._active_seconds / self.chroma_seconds)
                scores = scores + self.chroma_weight * ramp * (_PROFILES @ (c / n))
        return scores

    def recent_scores(self) -> np.ndarray:
        """Scores from only the last `recent_seconds` of chords (no priors)."""
        events, total = [], 0.0
        for ev in reversed(self.events):
            if ev.duration <= 0:
                continue
            events.append(ev)
            total += ev.duration
            if total >= self.recent_seconds:
                break
        if not events:
            return np.zeros(len(ALL_KEYS))
        events.reverse()
        w = np.minimum([e.duration for e in events], _MAX_EVENT_SECONDS)
        return self._score_events(events, w)

    def _best_other_group(self, scores: np.ndarray, key_index: int) -> int:
        other = np.where(self._group != self._group[key_index], scores, -np.inf)
        return int(np.argmax(other))

    def _consider_switch(self, scores: np.ndarray, best: int, dt: float) -> bool:
        cur = ALL_KEYS.index(self.key)
        if self._group[best] == self._group[cur]:
            # Same numbers either way: only relabel major <-> relative minor.
            self._challenger, self._challenger_seconds = None, 0.0
            if best != cur and scores[best] > scores[cur] + 0.05:
                self._relabel_seconds += dt
                if self._relabel_seconds >= self.relabel_seconds:
                    self.key = ALL_KEYS[best]
                    self._relabel_seconds = 0.0
                    return True
            else:
                self._relabel_seconds = 0.0
            return False

        # A challenger must lead the *recent* chords (so a "pivot" key that
        # half-fits the old and the new section never wins), and beat the
        # current key either clearly in the long run (normal switch) or by a
        # wide margin recently (the current key no longer explains what is
        # being played, e.g. the last chorus moved up a step: fast switch).
        recent = self.recent_scores()
        cand = int(np.argmax(recent))
        if self._group[cand] == self._group[cur]:
            self._challenger, self._challenger_seconds = None, 0.0
            return False
        if recent[cand] - recent[cur] >= self.fast_switch_margin:
            needed = self.fast_switch_seconds
        elif scores[cand] - scores[cur] >= self.switch_margin:
            # Early in a song there is little evidence either way: switch sooner.
            needed = self.switch_seconds * float(np.clip(len(self.events) / 8.0, 0.35, 1.0))
        else:
            self._challenger, self._challenger_seconds = None, 0.0
            return False
        if self._challenger == cand:
            self._challenger_seconds += dt
        else:
            self._challenger, self._challenger_seconds = cand, dt
        if self._challenger_seconds >= needed:
            self.key = ALL_KEYS[cand]
            self._challenger, self._challenger_seconds = None, 0.0
            self._relabel_seconds = 0.0
            return True
        return False

    # -- per frame -----------------------------------------------------------
    def update(self, chord: Optional[Chord], chroma: Optional[np.ndarray], dt: float,
               ) -> KeyEstimate:
        """Advance by `dt` seconds. `chord` is the currently reported chord
        (None for silence / no chord), `chroma` the frame's treble chroma."""
        if chord is None and chroma is None:
            self._silent_seconds += dt
            if self.silence_reset_seconds and self._silent_seconds >= self.silence_reset_seconds \
                    and not self.locked and (self.events or self.key is not None):
                self.reset()
                return KeyEstimate(None, 0.0, self.locked, True)
            self._last_chord = None
            return KeyEstimate(self.key, self._strength, self.locked, False)
        self._silent_seconds = 0.0
        self._active_seconds += dt

        if chroma is not None and np.any(chroma):
            alpha = min(1.0, dt / self.chroma_seconds)
            self._chroma = (1 - alpha) * self._chroma + alpha * chroma

        if chord is not None:
            if self._first_chord is None:
                self._first_chord = chord
            if chord != self._last_chord or not self.events:
                self.events.append(ChordEvent(chord))
                self._trim()
            self.events[-1].duration += dt
        self._last_chord = chord

        changed = False
        scores = self.key_scores()
        best = int(np.argmax(scores))

        if self.key is None:
            # Commit after `min_events` solid chords if the leader is ahead, or one
            # chord earlier if it is far ahead; otherwise keep listening.
            solid = [e for e in self.events if e.duration >= _SUBSTANTIAL_EVENT]
            distinct = len({(e.chord.root, e.chord.quality) for e in solid})
            margin = scores[best] - scores[self._best_other_group(scores, best)]
            ready = distinct >= 2 and (
                (len(solid) >= self.min_events and margin >= self.commit_margin) or
                (len(solid) >= self.min_events - 1 and margin >= self.fast_commit_margin))
            timeout = self._active_seconds >= self.commit_timeout and self.events
            if not self.locked and (ready or timeout):
                self.key = ALL_KEYS[best]
                changed = True
        elif not self.locked:
            changed = self._consider_switch(scores, best, dt)

        if self.key is not None and self.events:
            ki = ALL_KEYS.index(self.key)
            idx = [_CHORD_INDEX[(e.chord.root, e.chord.quality)] for e in self.events]
            w = self._weights(list(self.events))
            fits = np.clip(_FIT[ki, idx], 0.0, 1.0)
            self._strength = float(fits @ w / w.sum()) if w.sum() > 0 else 0.0
        return KeyEstimate(self.key, self._strength, self.locked, changed)
