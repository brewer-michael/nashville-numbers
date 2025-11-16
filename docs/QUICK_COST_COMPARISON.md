# Quick Cost Comparison - Nashville Numbers

## TL;DR - Recommended Path Forward

**Replace Raspberry Pi with ESP32-S3 custom PCB assembled by JLCPCB**
- **Cost:** $10-12 per unit (batches of 10-50)
- **Savings:** 78-91% vs. current design
- **Next step:** Design PCB, order 5-10 prototypes (~$100-150)

---

## Current vs. Proposed Costs

| Item | Current Design | ESP32-S3 Custom PCB | Savings |
|------|----------------|---------------------|---------|
| **Processor** | Pi 4 2GB: $45 | ESP32-S3 chip: $3 | **$42** |
| **Audio** | USB interface: $30 | INMP441 I2S mic: $1.50 | **$28.50** |
| **Storage** | microSD 16GB: $8 | Flash (built-in): $0.50 | **$7.50** |
| **Display** | TM1637 module: $5 | TM1637 on PCB: $1.10 | **$3.90** |
| **Power** | 5V 3A PSU: $8 | USB-C adapter: $3 | **$5** |
| **Enclosure** | 3D printed: $3 | 3D printed: $3 | $0 |
| | | |
| **TOTAL** | **$99** | **$12** | **$87 (88%)** |

---

## Why ESP32-S3 Works for Chord Detection

1. **Fast enough for FFT:** 10x faster than original ESP32
2. **Proven in audio:** Used in countless audio spectrum analyzers
3. **Real-time capable:** FFT uses <16% CPU at 44kHz sampling
4. **Official DSP library:** Espressif's optimized FFT functions
5. **Low power:** <100mA vs. Pi's 500-900mA

---

## Manufacturing Comparison

### JLCPCB (RECOMMENDED) ✓
- **10 units:** $11-12 each
- **50 units:** $10 each
- **Pros:** Cheapest, fastest, easiest (30k+ components in stock)
- **Cons:** Limited to standard components

### PCBWay
- **10 units:** $21-23 each
- **Pros:** More component options, better support
- **Cons:** ~2x cost vs. JLCPCB

### DIY Hand Assembly
- **10 units:** $8.30 each
- **Pros:** Absolute cheapest
- **Cons:** 1-2 hrs/board, requires soldering skills, QFN-48 package is hard!

---

## Action Plan

1. **Week 1-2:** Design PCB schematic & layout
2. **Week 3:** Order 5-10 prototypes from JLCPCB (~$100)
3. **Week 3-6:** Port software to ESP32-S3 (Arduino framework)
4. **Week 7-8:** Test prototypes, iterate if needed
5. **Production:** Order larger batches (50-100 units @ $10 each)

---

## Risk Assessment

| What could go wrong? | How likely? | Mitigation |
|---------------------|-------------|------------|
| ESP32 too slow | ⬜ Low | Already proven in similar projects |
| Mic quality poor | ⬜⬜ Medium | INMP441 is well-tested; can upgrade |
| Assembly issues | ⬜⬜ Medium | Stick to JLCPCB basic parts library |
| Software porting hard | ⬜⬜ Medium | Arduino has good libraries |

---

## Full Details

See `/home/user/nashville-numbers/docs/COST_REDUCTION_RESEARCH.md` for:
- Complete BOM with part numbers
- Detailed manufacturing comparison
- Alternative approaches
- Software porting strategy
- PCB design recommendations
- Enclosure options
