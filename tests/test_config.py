import json

import pytest

from nashville_numbers.config import (ConfigError, DEFAULTS, analyzer_settings, load_config,
                                      save_config)


def write(tmp_path, data):
    p = tmp_path / 'config.json'
    p.write_text(json.dumps(data))
    return str(p)


def test_defaults_are_valid_and_not_shared():
    a = load_config()
    a['display']['tm1637']['clk_pin'] = 99
    assert load_config()['display']['tm1637']['clk_pin'] == 23
    assert DEFAULTS['display']['tm1637']['clk_pin'] == 23


def test_partial_file_merges_over_defaults(tmp_path):
    data = {'display': {'type': 'ht16k33', 'ht16k33': {'brightness': 4}}}
    cfg = load_config(write(tmp_path, data))
    assert cfg['display']['type'] == 'ht16k33'
    assert cfg['display']['ht16k33']['brightness'] == 4
    assert cfg['display']['ht16k33']['address'] == '0x70'


def test_unknown_keys_warn_not_crash(tmp_path, caplog):
    load_config(write(tmp_path, {'audio': {'devcie': 'USB'}}))
    assert 'devcie' in caplog.text


def test_version1_config_is_migrated(tmp_path):
    v1 = {'audio': {'sample_rate': 44100, 'chunk_size': 4096, 'channels': 1, 'device_index': 2},
          'detection': {'min_chord_confidence': 0.3},
          'display': {'type': 'led', 'lcd': {'i2c_address': 63, 'rows': 2, 'cols': 16},
                      'led': {'display_type': 'TM1637', 'clk_pin': 5, 'dio_pin': 6,
                              'cs_pin': None, 'brightness': 3}},
          'system': {'update_interval': 0.2, 'simulation_mode': False, 'verbose': True}}
    cfg = load_config(write(tmp_path, v1))
    assert cfg['display']['type'] == 'tm1637'
    assert (cfg['display']['tm1637']['clk_pin'], cfg['display']['tm1637']['dio_pin']) == (5, 6)
    assert cfg['display']['lcd']['address'] == 63
    assert cfg['audio']['device'] == 2
    assert cfg['logging']['level'] == 'DEBUG'


@pytest.mark.parametrize('bad', [
    {'display': {'type': 'oled'}},
    {'analysis': {'chord_vocabulary': 'jazz'}},
    {'key': {'numbering': 'roman'}},
    {'analysis': {'gate_open_dbfs': -60, 'gate_close_dbfs': -50}},
    {'display': 'lcd'},
])
def test_invalid_settings_rejected(tmp_path, bad):
    with pytest.raises(ConfigError):
        load_config(write(tmp_path, bad))


def test_invalid_json_reports_file(tmp_path):
    p = tmp_path / 'bad.json'
    p.write_text('{"display": ')
    with pytest.raises(ConfigError, match='bad.json'):
        load_config(str(p))


def test_save_round_trip(tmp_path):
    cfg = load_config(overrides={'key': {'numbering': 'minor_tonic'}})
    p = tmp_path / 'out.json'
    save_config(cfg, str(p))
    assert load_config(str(p)) == cfg


@pytest.mark.parametrize('rate,window', [(44100, 16384), (48000, 16384), (96000, 32768),
                                         (22050, 8192)])
def test_window_scales_with_sample_rate(rate, window):
    assert analyzer_settings(load_config(), rate).window == window
