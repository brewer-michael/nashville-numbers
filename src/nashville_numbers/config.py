"""Configuration: defaults, JSON loading with deep merge, legacy key migration.

Every setting has a default, so a config file only needs the values you want
to change, e.g.::

    {"display": {"type": "ht16k33"}, "audio": {"device": "USB"}}
"""

import copy
import json
import logging
import math
from typing import Any, Dict, Optional

from .analysis.pipeline import AnalyzerSettings
from .theory import NUMBERING_STYLES, VOCABULARIES

log = logging.getLogger(__name__)

DISPLAY_TYPES = ('console', 'lcd', 'ht16k33', 'tm1637', 'max7219')

DEFAULTS: Dict[str, Any] = {
    'audio': {
        'device': None,          # None = system default; an index or part of the device name
        'sample_rate': None,     # None = the device's default rate
        'channels': None,        # None = 1 if the device allows it, else its channel count
        'channel': None,         # None = mix all channels to mono; or pick one (0-based)
        'block_size': 1024,
        'backend': 'auto',       # 'auto', 'sounddevice' or 'pyaudio'
    },
    'analysis': {
        'window_seconds': 0.35,  # rounded to a power-of-two number of samples
        'hop_seconds': 0.1,      # how often the display updates
        'gate_open_dbfs': -50.0,  # input level that starts analysis
        'gate_close_dbfs': -56.0,  # input level that stops it (hysteresis)
        'auto_tuning': True,     # follow instruments tuned away from A440
        'tuning_cents': 0.0,     # starting / fixed tuning offset
        'chord_vocabulary': 'sevenths',  # triads | basic | sevenths | full
        'chord_hold_seconds': 0.5,  # higher = steadier chords, slower changes
        'no_chord_score': 0.62,
    },
    'key': {
        'numbering': 'relative_major',   # relative_major (Am = 6m) | minor_tonic (Am = 1m)
        'window_seconds': 60.0,  # how much recent music decides the key
        'switch_seconds': 6.0,   # how long a new key must win before switching
        'min_events': 4,         # chords heard before the first key is shown
        'silence_reset_seconds': 0.0,  # >0: forget the key after this much silence
    },
    'display': {
        'type': 'console',
        'lcd': {'cols': 16, 'rows': 2, 'address': '0x27', 'expander': 'PCF8574', 'port': 1,
                'charmap': 'A00'},
        'ht16k33': {'address': '0x70', 'bus': 1, 'brightness': 15},
        'tm1637': {'clk_pin': 23, 'dio_pin': 24, 'brightness': 7},
        'max7219': {'port': 0, 'device': 0, 'digits': 8, 'brightness': 8, 'reverse': True},
    },
    'controls': {
        'enabled': True,
        'button_pin': 17,        # BCM; None disables
        'footswitch_pin': 27,    # BCM; None disables
        'hold_seconds': 1.5,     # hold: lock / unlock key
        'shutdown_seconds': 6.0,  # long hold on the panel button: shut down
        'allow_shutdown': True,
    },
    'logging': {'level': 'INFO'},
}


class ConfigError(ValueError):
    pass


def _merge(base: dict, override: dict, path: str = ''):
    for key, value in override.items():
        where = f"{path}{key}"
        if key not in base:
            log.warning("Unknown config setting '%s' (ignored - typo?)", where)
            continue
        if isinstance(base[key], dict):
            if not isinstance(value, dict):
                raise ConfigError(f"'{where}' must be an object")
            _merge(base[key], value, where + '.')
        else:
            base[key] = value


def _migrate_legacy(data: dict) -> dict:
    """Accept config files written for version 1."""
    data = copy.deepcopy(data)
    if not isinstance(data, dict):
        raise ConfigError("the config file must contain a JSON object")
    display = data.get('display', {})
    audio = data.get('audio', {})
    if not isinstance(display, dict) or not isinstance(audio, dict):
        return data            # _merge reports the type error
    if display.get('type') == 'led':
        led = display.pop('led', {}) or {}
        chip = str(led.get('display_type', 'TM1637')).lower()
        display['type'] = chip if chip in DISPLAY_TYPES else 'tm1637'
        if display['type'] == 'tm1637':
            display.setdefault('tm1637', {})
            for old, new in (('clk_pin', 'clk_pin'), ('dio_pin', 'dio_pin'),
                             ('brightness', 'brightness')):
                if led.get(old) is not None:
                    display['tm1637'][new] = led[old]
        log.warning("Config: 'display.type: led' is deprecated; using '%s'", display['type'])
    elif 'led' in display:
        display.pop('led')
    if isinstance(display.get('lcd'), dict) and 'i2c_address' in display['lcd']:
        display['lcd']['address'] = display['lcd'].pop('i2c_address')
    if 'device_index' in audio:
        audio['device'] = audio.pop('device_index')
    for key in ('chunk_size',):
        audio.pop(key, None)
    if 'detection' in data:
        data.pop('detection')
        log.warning("Config: the 'detection' section from version 1 is no longer used; "
                    "see 'analysis' and 'key'")
    if 'system' in data:
        system = data.pop('system')
        if system.get('simulation_mode'):
            display['type'] = 'console'
        if system.get('verbose'):
            data.setdefault('logging', {})['level'] = 'DEBUG'
    return data


def validate(cfg: dict):
    a, k, d = cfg['analysis'], cfg['key'], cfg['display']
    if a['chord_vocabulary'] not in VOCABULARIES:
        raise ConfigError(f"analysis.chord_vocabulary must be one of {sorted(VOCABULARIES)}")
    if k['numbering'] not in NUMBERING_STYLES:
        raise ConfigError(f"key.numbering must be one of {list(NUMBERING_STYLES)}")
    if d['type'] not in DISPLAY_TYPES:
        raise ConfigError(f"display.type must be one of {list(DISPLAY_TYPES)}")
    if a['gate_close_dbfs'] > a['gate_open_dbfs']:
        raise ConfigError("analysis.gate_close_dbfs must not be above gate_open_dbfs")
    if not 0.02 <= a['hop_seconds'] <= 1.0:
        raise ConfigError("analysis.hop_seconds must be between 0.02 and 1.0")
    if not 0.05 <= a['window_seconds'] <= 2.0:
        raise ConfigError("analysis.window_seconds must be between 0.05 and 2.0")


def load_config(path: Optional[str] = None, overrides: Optional[dict] = None) -> dict:
    """Defaults, then the JSON file at `path` (if any), then `overrides`."""
    cfg = copy.deepcopy(DEFAULTS)
    if path:
        try:
            with open(path, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{path}: invalid JSON ({exc})") from exc
        _merge(cfg, _migrate_legacy(data))
    if overrides:
        _merge(cfg, overrides)
    validate(cfg)
    return cfg


def save_config(cfg: dict, path: str):
    with open(path, 'w', encoding='utf-8') as fh:
        json.dump(cfg, fh, indent=4)
        fh.write('\n')


def analyzer_settings(cfg: dict, sample_rate: int) -> AnalyzerSettings:
    a, k = cfg['analysis'], cfg['key']
    window = 1 << max(10, int(round(math.log2(a['window_seconds'] * sample_rate))))
    return AnalyzerSettings(
        window=window, hop_seconds=a['hop_seconds'],
        gate_open_dbfs=a['gate_open_dbfs'], gate_close_dbfs=a['gate_close_dbfs'],
        auto_tuning=a['auto_tuning'], tuning_cents=a['tuning_cents'],
        chord_vocabulary=a['chord_vocabulary'], chord_hold_seconds=a['chord_hold_seconds'],
        no_chord_score=a['no_chord_score'], key_window_seconds=k['window_seconds'],
        key_switch_seconds=k['switch_seconds'], key_min_events=k['min_events'],
        numbering=k['numbering'], silence_reset_seconds=k['silence_reset_seconds'])
