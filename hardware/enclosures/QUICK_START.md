# Quick Start - 3D Printed Enclosures

## 5-Minute Guide to Printing Your First Case

### Step 1: Choose Your Enclosure (1 min)

**For practice room/desktop:**
→ Print `raspberry_pi_lcd_case.scad`

**For stage use:**
→ Print `stage_led_case.scad`

**For pedalboard:**
→ Print `compact_allinone_case.scad`

### Step 2: Download OpenSCAD (2 min)

1. Go to [openscad.org/downloads.html](https://openscad.org/downloads.html)
2. Download for your OS (Windows/Mac/Linux)
3. Install (takes ~1 minute)

### Step 3: Export STL Files (1 min)

1. Open OpenSCAD
2. Open your chosen `.scad` file
3. **For multi-part cases:**
   ```openscad
   // Edit these lines at top of file:
   render_base = true;
   render_lid = false;
   ```
4. Press **F5** (Preview) - wait for it
5. Press **F6** (Render) - be patient!
6. **File → Export → Export as STL**
7. Name it `base.stl`
8. Repeat with `render_lid = true` for `lid.stl`

### Step 4: Slice and Print (1 min setup)

1. Open your slicer (Cura, PrusaSlicer, etc.)
2. Import the STL file
3. Use these settings:
   ```
   Layer Height: 0.2mm
   Infill: 20%
   Supports: Auto (if needed)
   ```
4. Slice and save G-code
5. Print!

### Step 5: Gather Hardware

While printing, order these parts:

**For LCD case:**
- [ ] Raspberry Pi 4 (2GB+)
- [ ] 16×2 I2C LCD display
- [ ] USB audio interface
- [ ] 16GB microSD card
- [ ] M2.5 screws (pack of 50)

**For LED stage case:**
- [ ] TM1637 4-digit display (red)
- [ ] 4 rubber feet (adhesive)
- [ ] M2.5 screws

## Print Time Estimates

| Case | Print Time | Material |
|------|------------|----------|
| LCD Base | ~5 hours | 60g |
| LCD Lid | ~3 hours | 20g |
| Stage LED | ~4 hours | 60g |
| Compact Body | ~5 hours | 80g |
| Compact Panels | ~2 hours | 30g |

## Assembly Time

- LCD Case: 15 minutes
- Stage LED: 10 minutes
- Compact All-in-One: 20 minutes

## Cost Breakdown

### Just the Enclosure
- Filament: $1-3
- Screws: $1
- **Total: $2-4**

### Complete System
- Enclosure + hardware: $4
- Raspberry Pi 4: $45
- Display: $10
- Audio: $30
- Power/SD: $16
- **Total: ~$105**

## Common Questions

**Q: I don't have a 3D printer!**

A: Many options:
- Local library (often free!)
- Makerspace membership
- Online services (Shapeways, Craftcloud)
- Friend with printer
- Local print shop

**Q: Can I modify the design?**

A: Yes! All files are MIT licensed.
- Edit variables at top of `.scad` file
- Add your branding
- Share your remix!

**Q: What if screws don't fit?**

A: Pilot holes might need widening:
- Use 2.5mm drill bit for M2.5 screws
- Or print at 101% scale

**Q: My printer bed is too small!**

A: Some options:
- Print in sections and glue
- Scale down slightly (95%)
- Try the compact case (smallest)

**Q: PLA or PETG?**

A:
- Desktop use: PLA is fine
- Stage use: PETG is better
- Either works for most cases

## Printing Tips

### For Best Results

✓ **Level your bed** - This is #1 issue
✓ **Use brim** - Prevents corner lifting
✓ **Clean nozzle** - Old filament causes problems
✓ **Calibrate e-steps** - Better dimensional accuracy

### Common Fixes

**Warping:**
- Add brim or raft
- Increase bed temp +5°C
- Close enclosure/reduce drafts

**Stringing:**
- Enable retraction
- Lower print temp -5°C
- Increase retraction speed

**Weak parts:**
- Increase wall count to 3-4
- Raise infill to 30%
- Slow down print speed

## Next Steps

1. While printing, read the full [README.md](README.md)
2. Get your hardware (see [HARDWARE_SETUP.md](../../docs/HARDWARE_SETUP.md))
3. Install software (see [INSTALLATION.md](../../docs/INSTALLATION.md))
4. Assemble everything
5. Rock out! 🎸

## Need Help?

- Full documentation: `hardware/enclosures/README.md`
- Hardware setup: `docs/HARDWARE_SETUP.md`
- Installation: `docs/INSTALLATION.md`
- GitHub issues: [Report a problem](https://github.com/your-repo/issues)

---

**Print time: ~4-8 hours**
**Assembly time: ~15 minutes**
**Total cost: ~$2-4 in filament**

Go make some music! 🎵
