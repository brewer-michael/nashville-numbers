# User Guide

How to use the Nashville Numbers chord detection system effectively for practice and performance.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Understanding the Display](#understanding-the-display)
3. [Best Practices](#best-practices)
4. [Using in Practice](#using-in-practice)
5. [Using on Stage](#using-on-stage)
6. [Tips and Techniques](#tips-and-techniques)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)

## Quick Start

### Starting the System

**From terminal:**
```bash
cd ~/nashville-numbers
python3 main.py
```

**If auto-start is enabled:**
- System starts automatically on boot
- Wait 30 seconds after powering on
- Display will show "Listening..."

### Basic Operation

1. **Position your audio source**
   - Microphone 1-2 feet from instrument/amp
   - Or connect line-in from mixer/amp

2. **Play a chord**
   - Play cleanly and let ring
   - Wait 1-2 seconds for detection

3. **Watch the display**
   - Display shows detected chord and Nashville number
   - Key appears after detecting 2-3 chords

4. **Continue playing**
   - System tracks chord changes in real-time
   - Key updates if progression changes

### Stopping the System

Press **Ctrl+C** in terminal or power off Raspberry Pi.

## Understanding the Display

### LCD Display (16x2)

```
Chord: 1     C
Key: C Maj  95%
```

**Line 1:**
- `Chord:` Current chord detected
- `1` Nashville number
- `C` Actual chord name

**Line 2:**
- `Key:` Current musical key
- `C Maj` Key name and quality (Maj/Min)
- `95%` Detection confidence (higher is better)

### LED Display (TM1637/MAX7219)

```
┌──────────┐
│    1     │  ← Nashville number only
└──────────┘
```

Shows only the Nashville number in large digits for stage visibility.

**Display states:**
- `----` Listening, no chord detected
- `1` Major chord (plain number)
- `2m` Minor chord (number + 'm')
- `7°` Diminished chord (number + '°')

### Nashville Number System Reference

| Number | Major Key | Minor Key | Typical Quality |
|--------|-----------|-----------|----------------|
| 1      | I         | i         | Major/Minor    |
| 2      | ii        | ii°       | Minor          |
| 3      | iii       | III       | Minor/Major    |
| 4      | IV        | iv        | Major/Minor    |
| 5      | V         | v/V       | Major          |
| 6      | vi        | VI        | Minor/Major    |
| 7      | vii°      | VII       | Diminished     |

**Additional symbols:**
- `7` Dominant 7th
- `M7` Major 7th
- `m7` Minor 7th
- `°7` Diminished 7th

## Best Practices

### Audio Input

**For best detection accuracy:**

1. **Clean signal**
   - Minimize background noise
   - Single instrument is best
   - Or well-balanced mix

2. **Proper gain staging**
   - Set input so peaks are -6dB to -12dB
   - Use `python3 main.py --test-audio` to check levels
   - Avoid clipping (distortion)

3. **Instrument considerations**
   - Guitar: Play full chords, let ring
   - Piano: Play clear voicings
   - Bass: Works better with other instruments
   - Vocals: Not suitable for chord detection

### Environmental Setup

**Practice room:**
- Place system on desk/table
- LCD display close to you
- Microphone positioned toward sound source
- Quiet environment

**Stage:**
- LED display on floor in line of sight
- Bright red LEDs work best in low light
- Microphone or line-in from mixer
- Consider backup power supply

## Using in Practice

### Learning Progressions

**Scenario**: Learning a new song's chord progression

1. **Start the system**
   ```bash
   python3 main.py --verbose
   ```

2. **Play through the song**
   - Play each chord clearly
   - Hold for 2-3 seconds
   - Watch Nashville numbers appear

3. **Write down the progression**
   - Note the sequence: `1 - 4 - 5 - 6m`
   - Now you can transpose easily!

4. **Practice in different keys**
   - Play same Nashville numbers in new key
   - System will detect and confirm

### Ear Training

**Scenario**: Improving chord recognition skills

1. **Listen to recorded song**
2. **Try to play along**
3. **Check your work**
   - System shows what you're actually playing
   - Compare to what you think you hear
   - Improve recognition over time

### Improvisation Practice

**Scenario**: Jamming with a group

1. **Let system detect the key**
   - Play a few chords of the progression
   - System identifies key automatically
   - Confirms you're all in the same key!

2. **Follow the changes**
   - Watch Nashville numbers
   - Anticipate common progressions
   - Experiment with variations

## Using on Stage

### Setup Considerations

1. **Placement**
   - LED display on stage floor
   - In your line of sight
   - Not in audience view (if desired)

2. **Power**
   - Use reliable power supply
   - Consider backup battery
   - Test before performance

3. **Audio**
   - Line-in from mixer is most reliable
   - Or dedicated mic on your amp
   - Avoid picking up other instruments

### Performance Tips

1. **Soundcheck**
   - Test detection with full band
   - Adjust input levels
   - Verify display visibility

2. **Key Changes**
   - System adapts automatically
   - Play new key clearly for 2-3 chords
   - Display updates when confident

3. **Complex Chords**
   - System detects: maj, min, dim, aug, 7ths
   - Extended chords (9th, 11th, 13th) show as base chord
   - Use as harmonic guide, not absolute truth

### Stage Etiquette

- Position display for your view only
- Don't rely 100% on system during performance
- Use as a safety net, not a crutch
- Practice with it before gigging

## Tips and Techniques

### Improving Detection Accuracy

**If chords aren't detected:**
1. Play louder or increase gain
2. Let chords ring longer (2-3 seconds)
3. Play cleaner (avoid string noise)
4. Reduce background noise

**If wrong chords detected:**
1. Check tuning
2. Play cleaner voicings
3. Increase `min_chord_confidence` in config
4. Enable `chord_smoothing`

**If key detection is unstable:**
1. Play standard progressions initially
2. Increase `key_detection_history`
3. Avoid chromatic chords at first
4. Let system "lock in" to key before experimenting

### Configuration Tweaks

**For faster response (sacrifice accuracy):**
```json
"detection": {
    "min_chord_confidence": 0.2,
    "chord_smoothing": false
},
"system": {
    "update_interval": 0.1
}
```

**For more stable/accurate (slower):**
```json
"detection": {
    "min_chord_confidence": 0.4,
    "chord_smoothing": true,
    "key_detection_history": 10
},
"system": {
    "update_interval": 0.3
}
```

### Working with Different Genres

**Folk/Country/Pop:**
- Standard progressions work best
- Diatonic chords (in-key) detect easily
- System excels here

**Blues:**
- Dominant 7th chords detected
- 12-bar progressions work well
- May show key as major even for blues

**Jazz:**
- Complex voicings may simplify to basic chord
- Rapid changes challenging
- Use as harmonic reference

**Rock:**
- Power chords may not detect (no 3rd)
- Full barre chords work best
- Distortion can affect accuracy

## Common Scenarios

### Scenario 1: Playing in a Jam Session

**Problem**: Different players in different keys

**Solution**:
1. One player starts
2. System detects key
3. Display shows: "Key: G Maj"
4. Others join in G major
5. Everyone in sync!

### Scenario 2: Transposing a Song

**Original**: Song in C (chords: C, Am, F, G)

**Process**:
1. Play in C, system shows: `1, 6m, 4, 5`
2. Want to play in D instead
3. Play same Nashville numbers in D
4. New chords: D, Bm, G, A
5. System confirms you're in D

### Scenario 3: Learning Progressions by Ear

**Listening to**: Unknown song

**Process**:
1. Try to play along on instrument
2. Watch display for Nashville numbers
3. Write down: `1 - 5 - 6m - 4`
4. Recognize as "I-V-vi-IV" progression
5. Play in any key you want

### Scenario 4: Checking Band Members

**Problem**: Bass player sounds off

**Solution**:
1. Point mic at bass amp
2. Have bassist play their progression
3. Display shows what they're actually playing
4. Identify the discrepancy
5. Fix and move on

## Troubleshooting

### Display Issues

**No display:**
- Check power to Raspberry Pi
- Verify display connections
- Run `sudo i2cdetect -y 1` for LCD
- Try simulation mode to test software

**Garbled display:**
- Check I2C address (LCD)
- Verify wiring
- Adjust contrast pot (LCD)

**Display frozen:**
- Check if system is running
- Restart service: `sudo systemctl restart nashville-numbers`

### Detection Issues

**No chords detected:**
1. Run audio test: `python3 main.py --test-audio`
2. Check if meter responds to sound
3. Increase gain if levels too low
4. Verify audio device in config

**Wrong chords:**
1. Check instrument tuning
2. Play cleaner
3. Reduce background noise
4. Adjust confidence threshold

**Erratic key detection:**
1. Play more predictable progressions initially
2. Increase key detection history
3. Enable chord smoothing
4. Let system stabilize (5-10 chords)

### System Issues

**High latency:**
- Reduce chunk_size in config
- Decrease update_interval
- Close other programs
- Use Raspberry Pi 4

**System crashes:**
- Check logs: `sudo journalctl -u nashville-numbers`
- Verify all libraries installed
- Check power supply adequate
- Test in simulation mode

**Auto-start not working:**
- Check service status: `sudo systemctl status nashville-numbers`
- View errors: `sudo journalctl -u nashville-numbers -e`
- Verify config file path
- Check file permissions

## Advanced Usage

### Verbose Mode

See detailed detection information:
```bash
python3 main.py --verbose
```

Output example:
```
RMS: 0.0523, Chord: C, Confidence: 0.87
RMS: 0.0612, Chord: F, Confidence: 0.82
RMS: 0.0598, Chord: G, Confidence: 0.79
```

### Custom Configuration

Create specific configs for different scenarios:

**Practice (accurate):**
```bash
python3 main.py --config config.practice.json
```

**Stage (fast):**
```bash
python3 main.py --config config.stage.json
```

### Integration with Other Tools

**Recording for analysis:**
- System can run while you record
- Review Nashville numbers in your DAW notes
- Helps with music notation later

**Teaching tool:**
- Students play, display shows what they played
- Immediate feedback
- Learn Nashville system hands-on

## Getting the Most Out of the System

### Do's

✓ Use for learning and practice
✓ Verify with your ears
✓ Experiment with settings
✓ Use as a teaching aid
✓ Practice in different keys
✓ Build musical understanding

### Don'ts

✗ Rely completely without listening
✗ Use as only method of learning
✗ Ignore your musical intuition
✗ Expect 100% accuracy on complex chords
✗ Use with badly out-of-tune instruments
✗ Expect it to work in very noisy environments

## Additional Resources

### Nashville Number System

- [Wikipedia - Nashville Number System](https://en.wikipedia.org/wiki/Nashville_Number_System)
- Books: "The Nashville Number System" by Chas Williams
- Online tutorials and courses

### Music Theory

Understanding music theory helps interpret the system's output:
- Scale degrees and chord functions
- Diatonic vs. chromatic chords
- Common progressions by genre
- Key relationships

### Community

Share tips and get help:
- GitHub issues for bugs/features
- Music forums for technique discussion
- Online communities of Nashville Number users

---

**Remember**: This system is a tool to enhance your musicianship, not replace it. Use it to learn, practice, and grow as a musician!
