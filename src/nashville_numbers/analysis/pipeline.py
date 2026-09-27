"""The analysis pipeline: audio frame in, chord / key / Nashville number out."""

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional, Tuple

import numpy as np

from ..theory import Chord, Key, NashvilleNumber, to_nashville
from .chords import ChordRecognizer
from .features import FeatureExtractor, rms_dbfs
from .key import KeyTracker


@dataclass
class AnalyzerSettings:
    window: int = 16384
    hop_seconds: float = 0.1
    gate_open_dbfs: float = -50.0
    gate_close_dbfs: float = -56.0
    auto_tuning: bool = True
    tuning_cents: float = 0.0
    chord_vocabulary: str = 'sevenths'
    chord_hold_seconds: float = 0.5
    no_chord_score: float = 0.62
    min_tonality: float = 0.4          # below this a frame is noise/percussion, not a chord
    key_window_seconds: float = 60.0
    key_switch_seconds: float = 6.0
    key_min_events: int = 4
    numbering: str = 'relative_major'
    silence_reset_seconds: float = 0.0
    history_length: int = 8
    history_min_seconds: float = 0.4   # chords shorter than this are left out of the history


@dataclass
class AnalysisState:
    level_dbfs: float = -120.0
    signal: bool = False
    chord: Optional[Chord] = None
    chord_confidence: float = 0.0
    key: Optional[Key] = None
    key_strength: float = 0.0
    key_locked: bool = False
    number: Optional[NashvilleNumber] = None
    chord_changed: bool = False
    key_changed: bool = False
    tuning_cents: float = 0.0
    history: Tuple[Chord, ...] = field(default_factory=tuple)            # recent chords
    history_numbers: Tuple[NashvilleNumber, ...] = field(default_factory=tuple)

    def chord_name(self) -> Optional[str]:
        if self.chord is None:
            return None
        flats = self.key.uses_flats if self.key is not None else False
        return self.chord.name(flats)


class Analyzer:
    """Stateful analyser. Call `process()` once per hop with the latest
    `settings.window` samples."""

    def __init__(self, sample_rate: int, settings: Optional[AnalyzerSettings] = None):
        self.sample_rate = int(sample_rate)
        self.settings = s = settings or AnalyzerSettings()
        self.features = FeatureExtractor(self.sample_rate, s.window, auto_tuning=s.auto_tuning,
                                         tuning_cents=s.tuning_cents)
        self.chords = ChordRecognizer(s.chord_vocabulary, hop_seconds=s.hop_seconds,
                                      hold_seconds=s.chord_hold_seconds,
                                      no_chord_score=s.no_chord_score)
        self.keys = KeyTracker(window_seconds=s.key_window_seconds,
                               min_events=s.key_min_events,
                               switch_seconds=s.key_switch_seconds,
                               numbering=s.numbering,
                               silence_reset_seconds=s.silence_reset_seconds)
        self._gate_open = False
        self._history: Deque = deque(maxlen=s.history_length)
        self._held_chord: Optional[Chord] = None
        self._held_seconds = 0.0
        self.state = AnalysisState()

    @property
    def window(self) -> int:
        return self.settings.window

    def reset(self):
        """New song: forget chords and key (lock state is kept)."""
        self.chords.reset()
        self.keys.reset()
        self._history.clear()
        self._held_chord, self._held_seconds = None, 0.0

    def toggle_lock(self) -> bool:
        self.keys.set_locked(not self.keys.locked)
        return self.keys.locked

    def process(self, frame: np.ndarray) -> AnalysisState:
        s = self.settings
        level = rms_dbfs(frame)
        if self._gate_open:
            self._gate_open = level >= s.gate_close_dbfs
        else:
            self._gate_open = level >= s.gate_open_dbfs

        if self._gate_open:
            feats = self.features.process(frame)
            tonal = feats.energy > 0 and feats.tonality >= s.min_tonality
            est = self.chords.update(feats.chroma if tonal else None,
                                     feats.bass_chroma if tonal else None)
            chroma = feats.chroma if tonal else None
        else:
            est = self.chords.update(None, silent=True)
            chroma = None

        key_est = self.keys.update(est.chord, chroma if est.chord is not None else None,
                                   s.hop_seconds)
        number = None
        if est.chord is not None and key_est.key is not None:
            number = to_nashville(est.chord, key_est.key, s.numbering)
        # History: chords that were held long enough (skips transitional blips).
        if est.chord != self._held_chord:
            self._held_chord, self._held_seconds = est.chord, 0.0
        self._held_seconds += s.hop_seconds
        if (est.chord is not None and self._held_seconds >= s.history_min_seconds
                and (not self._history or self._history[-1] != est.chord)):
            self._history.append(est.chord)
        history = tuple(self._history)
        numbers = tuple(to_nashville(c, key_est.key, s.numbering) for c in history) \
            if key_est.key is not None else ()

        self.state = AnalysisState(
            level_dbfs=level, signal=self._gate_open, chord=est.chord,
            chord_confidence=est.confidence, key=key_est.key,
            key_strength=key_est.strength, key_locked=key_est.locked, number=number,
            chord_changed=est.changed, key_changed=key_est.changed,
            tuning_cents=self.features.tuning_cents, history=history,
            history_numbers=numbers)
        return self.state

    def process_signal(self, audio: np.ndarray):
        """Analyse a whole recording offline; yields (time_seconds, state)."""
        hop = int(round(self.settings.hop_seconds * self.sample_rate))
        w = self.window
        if len(audio) < w:
            audio = np.pad(audio, (0, w - len(audio)))
        for start in range(0, len(audio) - w + 1, hop):
            yield (start + w) / self.sample_rate, self.process(audio[start:start + w])
