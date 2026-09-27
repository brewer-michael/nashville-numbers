"""Command line interface: `nashville-numbers` (or `python -m nashville_numbers`)."""

import argparse
import logging
import sys
import time
from typing import List, Optional

from . import __version__
from .config import ConfigError, DISPLAY_TYPES, analyzer_settings, load_config, save_config

log = logging.getLogger('nashville_numbers')


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog='nashville-numbers',
        description='Listen to live music and show the chords as Nashville numbers.')
    p.add_argument('-c', '--config', help='JSON config file (only the settings you change)')
    p.add_argument('-d', '--display', choices=DISPLAY_TYPES, help='display type (overrides config)')
    p.add_argument('-s', '--simulate', action='store_true',
                   help='print to the terminal instead of display hardware; no buttons')
    p.add_argument('--device', help='audio input device: index or part of its name')
    p.add_argument('--input-file', metavar='WAV', help='play a WAV file instead of live input')
    p.add_argument('--demo', nargs='?', const='1 5 6m 4', metavar='PROGRESSION',
                   help="synthesise a looping progression instead of live input "
                        "(default '1 5 6m 4')")
    p.add_argument('--demo-key', default='G', help='key for --demo (default G)')
    p.add_argument('--analyze', metavar='WAV', help='analyse a recording and print its chords')
    p.add_argument('--list-devices', action='store_true', help='list audio input devices')
    p.add_argument('--test-audio', nargs='?', type=float, const=15.0, metavar='SECONDS',
                   help='show the input level (dBFS) and detected chord for a while')
    p.add_argument('--test-display', action='store_true',
                   help='cycle example numbers on the configured display, then exit')
    p.add_argument('--duration', type=float, help='stop after this many seconds')
    p.add_argument('--write-config', metavar='PATH', help='write the full configuration and exit')
    p.add_argument('-v', '--verbose', action='store_true', help='debug logging')
    p.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    return p


def _overrides(args) -> dict:
    o: dict = {}
    if args.display:
        o.setdefault('display', {})['type'] = args.display
    if args.simulate:
        o.setdefault('display', {})['type'] = 'console'
        o.setdefault('controls', {})['enabled'] = False
    if args.device is not None:
        o.setdefault('audio', {})['device'] = int(args.device) if args.device.isdigit() \
            else args.device
    return o


def cmd_analyze(cfg: dict, path: str) -> int:
    from .analysis.pipeline import Analyzer
    from .audio.sources import read_wav
    from .displays.base import nashville_text
    audio, rate = read_wav(path)
    analyzer = Analyzer(rate, analyzer_settings(cfg, rate))
    print(f"{path}: {len(audio) / rate:.1f} s at {rate} Hz")
    key_shown = None
    for t, st in analyzer.process_signal(audio):
        if st.key is not None and st.key != key_shown:
            print(f"{t:7.1f}s  key {st.key.long_name()}")
            key_shown = st.key
        if st.chord_changed:
            name = st.chord_name() or '--'
            num = nashville_text(st.number) if st.number else ''
            print(f"{t:7.1f}s  {name:<7} {num}")
    if analyzer.state.history_numbers:
        print("Progression:", ' '.join(nashville_text(n) for n in analyzer.state.history_numbers))
    return 0


def cmd_test_audio(cfg: dict, seconds: float) -> int:
    from .analysis.pipeline import Analyzer
    from .audio.sources import make_source
    source = make_source(cfg)
    source.start()
    analyzer = Analyzer(source.sample_rate, analyzer_settings(cfg, source.sample_rate))
    gate = cfg['analysis']['gate_open_dbfs']
    print(f"Input: {source.description}. Gate opens at {gate:.0f} dBFS. Ctrl+C to stop.")
    end = time.monotonic() + seconds
    try:
        while time.monotonic() < end:
            time.sleep(cfg['analysis']['hop_seconds'])
            frame = source.latest(analyzer.window)
            if frame is None:
                continue
            st = analyzer.process(frame)
            bar = '#' * max(0, min(40, int((st.level_dbfs + 80) / 2)))
            chord = st.chord_name() or '--'
            print(f"\r{st.level_dbfs:6.1f} dBFS |{bar:<40}| {'ON ' if st.signal else 'off'} "
                  f"{chord:<6} tune {st.tuning_cents:+4.0f}c", end='', flush=True)
    except KeyboardInterrupt:
        pass
    finally:
        source.stop()
        print()
    return 0


def cmd_test_display(cfg: dict) -> int:
    from .analysis.pipeline import AnalysisState
    from .displays import create_display
    from .theory import Chord, Key, to_nashville
    display = create_display(cfg)
    display.open()
    key = Key.parse('G')
    try:
        display.message('hello')
        time.sleep(1.5)
        history = []
        for sym in ['G', 'Am', 'Bm', 'C', 'D7', 'Em', 'F#dim', 'F', 'Cmaj7', 'Am7']:
            chord = Chord.parse(sym)
            history.append(chord)
            num = to_nashville(chord, key)
            display.show(AnalysisState(level_dbfs=-20, signal=True, chord=chord, key=key,
                                       key_strength=0.9, number=num, chord_changed=True,
                                       history=tuple(history),
                                       history_numbers=tuple(to_nashville(c, key)
                                                             for c in history)))
            print(f"showing {num} ({sym} in G)")
            time.sleep(1.2)
        display.message('locked', key.long_name())
        time.sleep(1.5)
    finally:
        display.close()
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.config, _overrides(args))
    except (ConfigError, OSError) as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    configured = getattr(logging, str(cfg['logging']['level']).upper(), logging.INFO)
    level = logging.DEBUG if args.verbose else configured
    logging.basicConfig(level=level, format='%(asctime)s %(levelname)-7s %(name)s: %(message)s')

    if args.write_config:
        save_config(cfg, args.write_config)
        print(f"Wrote {args.write_config}")
        return 0
    if args.list_devices:
        from .audio.sources import list_input_devices
        for line in list_input_devices(cfg['audio']['backend']):
            print(line)
        return 0
    if args.analyze:
        return cmd_analyze(cfg, args.analyze)
    if args.test_audio is not None:
        return cmd_test_audio(cfg, args.test_audio)
    if args.test_display:
        return cmd_test_display(cfg)

    from .app import App
    from .audio.sources import make_source
    from .displays import create_display
    display = create_display(cfg)
    controls = None
    c = cfg['controls']
    if c['enabled'] and cfg['display']['type'] != 'console':
        from .controls import Controls
        controls = Controls(c['button_pin'], c['footswitch_pin'], c['hold_seconds'],
                            c['shutdown_seconds'], c['allow_shutdown'])
    demo = (args.demo, args.demo_key) if args.demo is not None else None
    app = App(cfg, display, lambda: make_source(cfg, args.input_file, demo), controls)
    app.install_signal_handlers()
    log.info("Nashville Numbers %s - display: %s", __version__, cfg['display']['type'])
    return app.run(duration=args.duration)


if __name__ == '__main__':
    sys.exit(main())
