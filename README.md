# Nashville Numbers

A Raspberry Pi that listens to live music, works out the key, and shows every
chord as its **Nashville number** (1, 4, 5, 6m ...) on an LCD or a big red
LED display, so you always know where you are in the key while you play,
practise or improvise.

```
┌────────────────┐        ┌───┬───┬───┬───┐
│6m   Em        G│        │   │ 6 │ - │   │   6m, in big 30 mm red digits
│1 5 6m 4 1 5 6m │        └───┴───┴───┴───┘
└────────────────┘
  desktop build              stage build
```

## What it does

* **Chords**: major, minor, diminished and seventh chords from a line, DI or
  microphone signal, several times a second.
* **Key**: found from the chord progression within about four chords, held
  steady through borrowed chords and bVII rock changes, and updated within
  seconds when the song modulates. Lock it with a button or footswitch.
* **Numbers**: Nashville notation with flats for chromatic chords (b7, b3),
  minor songs charted from the relative major (6m) or from 1m, your choice.
* **Hands-free**: button or footswitch for "new song" and "lock key",
  safe shutdown, runs as a service that survives unplugged cables.

On the bundled benchmark - 10 common progressions in all 12 keys, played by
synthetic guitar, piano and organ, solo and with bass, drums and noise - it
names **99.9 % of chords with the right Nashville number and gets every key
right without ever changing key mid-song** (`python tools/benchmark.py`).

## Try it now, no hardware needed

```bash
git clone https://github.com/brewer-michael/nashville-numbers.git
cd nashville-numbers
pip install .
nashville-numbers --simulate --demo                  # synthesised "1 5 6m 4" in G
nashville-numbers --analyze my-song.wav              # chords and key of a recording
```

## Build one

| Build | Display | Enclosure | For |
|---|---|---|---|
| **Desktop** | 16x2 LCD: number, chord, key, progression | desktop LCD case | practice, lessons |
| **Stage** | Adafruit 1.2" red 7-segment + footswitch jack | floor wedge | gigs, rehearsals |
| **Budget** | TM1637 0.56" red 7-segment | floor wedge | lowest cost |

All builds use a Raspberry Pi 5 or Pi 4 (1 GB is plenty for either), a USB
audio interface and one push button.

* [Hardware overview and build order](hardware/README.md)
* [Bill of materials](hardware/bom/README.md)
* [Wiring diagrams](hardware/wiring/README.md)
* [3D-printable enclosures](hardware/enclosures/README.md)
* [Design spec](hardware/SPEC.md)

On the Pi: `./deploy/install.sh --build stage` installs everything and starts
the service. See [Installation](docs/INSTALLATION.md).

## Documentation

* [Installation](docs/INSTALLATION.md): Raspberry Pi setup, service,
  read-only mode for gigs, troubleshooting
* [User Guide](docs/USER_GUIDE.md): reading the display, controls, how the
  key is chosen, every setting, limitations, a Nashville Number primer

## How it works

1. **Spectrum**: a 0.35 s window every 0.1 s is mapped onto a log-frequency
   axis (3 bins per semitone), whitened, and auto-tuned to the band.
2. **Notes**: non-negative least squares fits harmonic note templates to the
   spectrum, so overtones count for the note that made them instead of
   looking like extra notes (after Mauch & Dixon, *Approximate Note
   Transcription for the Improved Identification of Difficult Chords*,
   ISMIR 2010). How well the fit explains the spectrum tells music from noise
   and drums.
3. **Chords**: treble and bass chroma are matched against chord templates; a
   forward (HMM) filter and a short debounce keep the display steady.
4. **Key**: chord changes are weighted by duration and recency and scored
   against all 24 keys (diatonic fit, tonic and cadence cues, pitch profile);
   hysteresis on two timescales keeps it stable yet quick to follow real
   modulations.
5. **Display**: numbers go to an HD44780 LCD (RPLCD), an HT16K33, TM1637 or
   MAX7219 7-segment display, or the terminal.

The analysis needs only NumPy and runs in about a millisecond per frame on a
desktop CPU, comfortably real time on a Raspberry Pi.

## Repository layout

```
src/nashville_numbers/   the application (analysis, audio, displays, controls, CLI)
tests/                   180 tests; display hardware is simulated
tools/benchmark.py       accuracy benchmark
deploy/                  Raspberry Pi installer and systemd unit
examples/                ready-made configs per build
hardware/                spec, BOM, wiring diagrams, 3D-printable enclosures
docs/                    installation and user guide
```

## Development

```bash
pip install -e ".[dev]"
pytest -q                      # tests
ruff check .                   # lint
python tools/benchmark.py      # accuracy, ~10 min on 4 cores
```

CI runs the tests on Python 3.9, 3.11 and 3.13 (Raspberry Pi OS Bullseye,
Bookworm, Trixie), checks the wiring diagrams against the spec, and renders
and fit-checks the enclosures.

## License

MIT - see [LICENSE](LICENSE).
