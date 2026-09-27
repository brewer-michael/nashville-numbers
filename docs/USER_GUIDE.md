# User Guide

Nashville Numbers listens to the music, works out the key, and shows every
chord as its Nashville number: **1 4 5 6m** instead of **G C D Em**. Play or
jam along and you always know where you are in the key.

## Contents

1. [Reading the display](#reading-the-display)
2. [Controls](#controls)
3. [How it decides the key](#how-it-decides-the-key)
4. [Getting a good signal](#getting-a-good-signal)
5. [Settings](#settings)
6. [What it can and can't hear](#what-it-can-and-cant-hear)
7. [Nashville Number System primer](#nashville-number-system-primer)

## Reading the display

### 16x2 LCD (desktop build)

```
┌────────────────┐
│6m   Em        G│   number · chord · key (🔒 before the key when locked)
│1 5 6m 4 1 5 6m │   the progression so far, newest on the right
└────────────────┘
```

Before the key is known the top line shows the chord name and `key?`, the
bottom line `finding key...`. With no sound it shows `waiting for sound`.
A 20x4 LCD adds the full key name (`Key G major locked`) and the input level
and tuning offset.

### 7-segment LED (stage and budget builds)

The degree is always in the second digit so it doesn't jump around; the
quality follows it:

| Display | Means | Nashville |
|---|---|---|
| ` 1  ` | major | 1 |
| ` 6- ` | minor (Nashville "dash" notation) | 6m |
| ` 7° ` | diminished | 7° |
| ` 5⁷ ` (small raised 7) | dominant seventh | 57 |
| ` 2-⁷` | minor seventh | 2m7 |
| ` 4M⁷` | major seventh | 4maj7 |
| `b7  ` | chord on the flat seven | b7 |
| `#4° ` | sharp-four diminished | #4° |
| ` A- ` (letters) | chord *name* (Am) - shown until the key is known | |
| `----` | listening, no chord | |
| colon lit | key is locked | |

Status messages: `HELO` starting, `noAu` no audio interface, `nEU` new song
(key cleared), `LOC` / `FrEE` key locked / unlocked, `OFF` shutting down,
`Err` error (details in the log).

An 8-digit MAX7219 display shows the number and the chord name side by side:
` 6-  E- `.

## Controls

| Action | Panel button | Footswitch |
|---|---|---|
| **New song** - forget the key and the progression | short press | short stomp |
| **Lock / unlock the key** - keep the current key through a bridge or solo | hold 1.5 s | hold 1.5 s |
| **Shut down** safely before unplugging | hold 6 s | - |

The footswitch jack takes any momentary footswitch or keyboard sustain pedal;
normally-open and normally-closed pedals both work (the polarity is learned
when the Pi starts, and again if you plug a pedal in later).

Without a button: `sudo systemctl restart nashville-numbers` starts a new
song.

## How it decides the key

* It needs about **four chords** (usually 5-9 seconds) before it shows a key.
  Until then the display shows chord names. If the evidence is clear it
  commits after three.
* It uses the **chord changes**, how long each chord lasts, which chord
  sounds like home (the song's first chord, V→I and IV→I resolutions), and
  the overall pitch content. A chord you hold for a long time doesn't
  outweigh the rest of the progression.
* Once the key is set it **stays put** through borrowed chords, secondary
  dominants, blues sevenths and bVII rock changes. It switches only when
  another key has clearly fitted the music better for several seconds: about
  4 seconds when the song really modulates (the classic last-chorus key
  change), 6 seconds otherwise.
* **Lock** the key (hold the button) during a solo or a bridge you don't want
  it to follow; **new song** (short press) when the next song starts.
* Minor keys: by default a minor song is numbered from its relative major,
  the most common Nashville practice (A minor charted in C: Am F C G = 6m 4 1
  5). Set `key.numbering` to `minor_tonic` if you prefer 1m-based charts
  (Am F C G = 1m b6 b3 b7).

## Getting a good signal

Detection is only as good as what it hears. From best to worst:

1. **Line or DI feed** of one harmonic instrument - keys or guitar from a
   mixer aux send, a DI's thru, a pedalboard output (use a buffered output or
   splitter so the guitar tone isn't loaded).
2. **Guitar/bass straight into a Hi-Z interface input** (Behringer UM2,
   UMC22, UCG102).
3. **A microphone** close to one amp or acoustic instrument.
4. A room microphone hearing the whole band: works on clear, sustained chords,
   gets confused by loud drums and busy bass lines.

Use `nashville-numbers --test-audio` to set the gain: strummed chords should
peak around −20 to −10 dBFS, silence should stay below −50 dBFS (the gate).
The meter also shows the chord it hears and the tuning offset; the analyser
follows instruments tuned up to about ±50 cents away from A440.

## Settings

Put only what you change in `~/.config/nashville-numbers/config.json`, e.g.

```json
{ "display": { "type": "ht16k33" }, "key": { "numbering": "minor_tonic" } }
```

and restart the service. All settings with their defaults:

| Setting | Default | Meaning |
|---|---|---|
| `audio.device` | `null` | input device: `null` = system default, a number from `--list-devices`, or part of its name (`"USB"`) |
| `audio.sample_rate` | `null` | `null` = the device's own rate (usually 48000) |
| `audio.channels` / `audio.channel` | `null` | channels to open / which one to analyse (`null` = mix to mono) |
| `audio.backend` | `"auto"` | `sounddevice`, `pyaudio` or `auto` |
| `analysis.window_seconds` | `0.35` | analysis window (longer = better low-note resolution, slower response) |
| `analysis.hop_seconds` | `0.1` | how often the display updates |
| `analysis.gate_open_dbfs` / `gate_close_dbfs` | `-50` / `-56` | input level that starts / stops analysis |
| `analysis.auto_tuning` | `true` | follow instruments tuned away from A440 |
| `analysis.chord_vocabulary` | `"sevenths"` | `triads` (maj, min), `basic` (+ dim, 7), `sevenths` (+ maj7, m7), `full` (+ aug, sus2, sus4, m7b5) |
| `analysis.chord_hold_seconds` | `0.5` | higher = steadier chords, slower changes |
| `analysis.no_chord_score` | `0.62` | higher = more willing to show `--` for unclear sounds |
| `key.numbering` | `"relative_major"` | `relative_major` (Am = 6m) or `minor_tonic` (Am = 1m) |
| `key.min_events` | `4` | chords heard before the first key is shown |
| `key.switch_seconds` | `6` | how long another key must win before switching |
| `key.window_seconds` | `60` | how much recent music is considered |
| `key.silence_reset_seconds` | `0` | if > 0, forget the key after this much silence (automatic "new song") |
| `display.type` | `"console"` | `lcd`, `ht16k33`, `tm1637`, `max7219` or `console` |
| `display.lcd` | 16x2 at `0x27` | `cols`, `rows`, `address`, `expander` (`PCF8574`, `MCP23008`), `port`, `charmap` (`A00`/`A02`) |
| `display.ht16k33` | `0x70` | `address`, `bus`, `brightness` (0-15) |
| `display.tm1637` | GPIO 23/24 | `clk_pin`, `dio_pin`, `brightness` (0-7) |
| `display.max7219` | SPI 0.0 | `port`, `device`, `digits`, `brightness` (0-15), `reverse` (digit order) |
| `controls.enabled` | `true` | use the button/footswitch (off with `--simulate`) |
| `controls.button_pin` / `footswitch_pin` | `17` / `27` | BCM GPIO numbers; `null` disables |
| `controls.hold_seconds` | `1.5` | hold time for lock/unlock |
| `controls.shutdown_seconds` / `allow_shutdown` | `6` / `true` | long hold on the panel button shuts down |
| `logging.level` | `"INFO"` | `DEBUG` logs every chord change |

## What it can and can't hear

* **Chords**: major, minor, diminished and dominant/major/minor sevenths by
  default; augmented, sus2/sus4 and half-diminished with the `full`
  vocabulary. Ninths, elevenths and thirteenths show as the seventh or triad
  underneath them.
* **Power chords** (root and fifth only) show as major - there is no third to
  tell them apart.
* **Inversions** show the chord's root (C/E shows as 1, not 1/3).
* **Single-note melodies** are not chords; it shows whatever the notes imply,
  or `--`.
* **Accuracy**: on the bundled benchmark (10 common progressions × 12 keys ×
  guitar, piano and organ timbres, solo and with bass, drums and noise;
  `python tools/benchmark.py`) it gets 99.9 % of Nashville numbers right and
  the key right in every case, without changing key mid-song. Real
  instruments in real rooms are harder than synthesised ones: treat it as a
  very good assistant, not an oracle.

## Nashville Number System primer

Each chord is numbered by the scale degree of its root in the song's key, so
a chart works in any key:

| Key | 1 | 2m | 3m | 4 | 5 | 6m | 7° |
|---|---|---|---|---|---|---|---|
| C | C | Dm | Em | F | G | Am | B° |
| G | G | Am | Bm | C | D | Em | F#° |
| D | D | Em | F#m | G | A | Bm | C#° |
| A | A | Bm | C#m | D | E | F#m | G#° |
| E | E | F#m | G#m | A | B | C#m | D#° |
| F | F | Gm | Am | Bb | C | Dm | E° |

Chords outside the key get a flat or sharp: in G, F is **b7**, Bb is **b3**,
Eb is **b6**. Minor is written `m` or `-`, diminished `°`, a dominant seventh
`57` (on paper a small raised 7). Further reading:
[Nashville Number System on Wikipedia](https://en.wikipedia.org/wiki/Nashville_Number_System).
