import json

import numpy as np

from nashville_numbers.audio.sources import demo_chords, write_wav
from nashville_numbers.audio.synth import render_progression
from nashville_numbers.cli import main
from nashville_numbers.theory import Key


def test_analyze_prints_progression(tmp_path, capsys):
    sr = 22050
    chords = demo_chords('1 4 5 1', Key.parse('A')) * 3
    audio = render_progression(chords, 2.0, sr, 'guitar', rng=np.random.default_rng(4))
    path = tmp_path / 'song.wav'
    write_wav(str(path), audio, sr)
    assert main(['--analyze', str(path)]) == 0
    out = capsys.readouterr().out
    assert 'key A major' in out
    assert 'Progression:' in out and '1 4 5 1' in out.split('Progression:')[1]


def test_write_config(tmp_path):
    path = tmp_path / 'cfg.json'
    assert main(['--display', 'tm1637', '--write-config', str(path)]) == 0
    assert json.loads(path.read_text())['display']['type'] == 'tm1637'


def test_bad_config_exit_code(tmp_path, capsys):
    path = tmp_path / 'cfg.json'
    path.write_text('{"display": {"type": "oled"}}')
    assert main(['--config', str(path), '--write-config', str(tmp_path / 'x.json')]) == 2
    assert 'display.type' in capsys.readouterr().err


def test_simulated_demo_runs(capsys):
    assert main(['--simulate', '--demo', '1 4 5 1', '--demo-key', 'E', '--duration', '1.5']) == 0
