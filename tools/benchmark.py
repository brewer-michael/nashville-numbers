#!/usr/bin/env python3
"""Accuracy benchmark: synthesised progressions in all 12 keys.

For every progression x timbre x condition it renders the progression three
times through, runs the analyser exactly as the device does (0.1 s hops) and
reports how many chords (after the first pass, which is spent finding the
key) got the right Nashville number, whether the final key is right, how
often the reported key changed mid-song, and how long the first key took.

    python tools/benchmark.py                      # everything (~10 min, uses all cores)
    python tools/benchmark.py --quick              # guitar only, solo
    python tools/benchmark.py --vocabulary triads
"""

import argparse
import os
import sys
import time
from collections import Counter
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))

from nashville_numbers.analysis.pipeline import Analyzer, AnalyzerSettings  # noqa: E402
from nashville_numbers.audio.sources import demo_chords  # noqa: E402
from nashville_numbers.audio.synth import render_progression  # noqa: E402
from nashville_numbers.theory import Key, to_nashville  # noqa: E402

SR = 44100
SECONDS_PER_CHORD = 2.0
PASSES = 3
PROGRESSIONS = {
    'pop 1 5 6m 4': '1 5 6m 4',
    'doo-wop 1 6m 4 5': '1 6m 4 5',
    'country 1 4 1 5': '1 4 1 5',
    'jazz 2m7 57 1maj7': '2m7 57 1maj7 1maj7',
    'blues 17 47 57': '17 17 47 17 57 47 17 57',
    'minor 6m 4 1 5': '6m 4 1 5',
    'harmonic minor 6m 2m 3 6m': '6m 2m 3 6m',
    'mixolydian 1 b7 4 1': '1 b7 4 1',
    'folk 1 4 5 4': '1 4 5 4',
    'royal road 4 5 3m 6m': '4 5 3m 6m',
}


def run(args):
    tonic, progression, timbre, band, vocabulary = args
    key = Key(tonic, 'major')
    one_pass = demo_chords(progression, key)
    chords = one_pass * PASSES
    audio = render_progression(chords, SECONDS_PER_CHORD, SR, timbre, bass=band, drums=band,
                               noise_db=-45 if band else None,
                               rng=np.random.default_rng(100 + tonic))
    analyzer = Analyzer(SR, AnalyzerSettings(chord_vocabulary=vocabulary))
    votes = [[] for _ in chords]
    first_key, groups = None, []
    for t, st in analyzer.process_signal(audio):
        seg = int((t - 0.05) // SECONDS_PER_CHORD)
        if seg >= len(chords):
            break
        if st.key is not None:
            first_key = first_key or t
            if not groups or groups[-1] != st.key.relative_major_tonic:
                groups.append(st.key.relative_major_tonic)
        if t - seg * SECONDS_PER_CHORD > 0.5 * SECONDS_PER_CHORD:
            votes[seg].append(str(st.number) if st.number else None)
    expected = [str(to_nashville(c, key)) for c in chords]
    scored = range(len(one_pass), len(chords))
    right = sum(Counter(votes[i]).most_common(1)[0][0] == expected[i] for i in scored if votes[i])
    key_ok = analyzer.state.key is not None and analyzer.state.key.relative_major_tonic == tonic
    return right, len(scored), key_ok, max(0, len(groups) - 1), first_key or float('nan')


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('--quick', action='store_true')
    p.add_argument('--vocabulary', default='sevenths')
    args = p.parse_args()
    conditions = ['solo'] if args.quick else ['solo', 'band']
    timbres = ['guitar'] if args.quick else ['guitar', 'piano', 'organ']
    totals = [0, 0, 0, 0, 0]
    start = time.time()
    print(f"{'condition':9} {'timbre':7} {'progression':27} {'numbers':>9} {'keys':>6} "
          f"{'switches':>8} {'1st key':>7}")
    with Pool(os.cpu_count()) as pool:
        for cond in conditions:
            for timbre in timbres:
                for name, prog in PROGRESSIONS.items():
                    res = pool.map(run, [(k, prog, timbre, cond == 'band', args.vocabulary)
                                         for k in range(12)])
                    right = sum(r[0] for r in res)
                    total = sum(r[1] for r in res)
                    keys = sum(r[2] for r in res)
                    switches = sum(r[3] for r in res)
                    first = np.nanmean([r[4] for r in res])
                    totals = [totals[0] + right, totals[1] + total, totals[2] + keys,
                              totals[3] + 12, totals[4] + switches]
                    print(f"{cond:9} {timbre:7} {name:27} {right:4d}/{total:<4d} {keys:3d}/12 "
                          f"{switches:8d} {first:6.1f}s", flush=True)
    print(f"\nNashville numbers correct: {totals[0]}/{totals[1]} "
          f"({100 * totals[0] / totals[1]:.2f}%)  keys correct: {totals[2]}/{totals[3]}  "
          f"mid-song key changes: {totals[4]}  ({time.time() - start:.0f} s)")


if __name__ == '__main__':
    main()
