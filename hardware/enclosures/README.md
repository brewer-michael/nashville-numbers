# Nashville Numbers - 3D Printed Enclosures

Professional enclosures for your Nashville Numbers system. All designs are OpenSCAD parametric models that can be customized and 3D printed.

## Table of Contents

1. [Enclosure Options](#enclosure-options)
2. [Printing Guide](#printing-guide)
3. [Assembly Instructions](#assembly-instructions)
4. [Bill of Materials](#bill-of-materials)
5. [Customization](#customization)

## Enclosure Options

### 1. Raspberry Pi + LCD Case (`raspberry_pi_lcd_case.scad`)

**Best for:** Desktop use, practice rooms, detailed monitoring

**Features:**
- Houses Raspberry Pi 3B+/4 with mounted LCD display
- Top-mounted 16x2 LCD window
- Full access to all Raspberry Pi ports
- Ventilation holes for cooling
- Two-part design (base + lid)
- Professional appearance

**Dimensions:** 101mm × 68mm × 40mm (L×W×H)

**Print time:** ~8 hours (both parts)

**Material needed:** ~80g PLA/PETG

![LCD Case Preview](https://via.placeholder.com/400x300?text=LCD+Case)

---

### 2. Stage LED Display Case (`stage_led_case.scad`)

**Best for:** Stage performance, floor mounting, high visibility

**Features:**
- 30° viewing angle optimized for floor placement
- Large LED digit window
- Rugged construction for stage use
- Cable strain relief
- Rubber feet mounting points
- Optional red acrylic filter

**Dimensions:**
- TM1637: 62mm × 37mm × 45mm (front height)
- MAX7219: 148mm × 45mm × 45mm

**Print time:** ~4-6 hours

**Material needed:** ~60g PETG

![Stage Case Preview](https://via.placeholder.com/400x300?text=Stage+LED+Case)

---

### 3. Compact All-in-One Case (`compact_allinone_case.scad`)

**Best for:** Pedalboard mounting, minimal desk space, portable setups

**Features:**
- Vertical orientation saves space
- Raspberry Pi and LED display in one unit
- Front-facing LED display
- Passive chimney-effect cooling
- VESA mount compatible
- Pedalboard-ready

**Dimensions:** 93mm × 64mm × 80mm

**Print time:** ~7 hours

**Material needed:** ~110g PLA/PETG

![Compact Case Preview](https://via.placeholder.com/400x300?text=Compact+All-in-One)

---

### 4. Mounting Accessories (`mounting_accessories.scad`)

**Includes:**
- **Microphone Stand Mount** - Attach to standard mic stand
- **Desktop Stand** - 15° angled stand for optimal viewing
- **Cable Clips** - Organize wires (various sizes)
- **VESA Adapter** - 75mm mount for monitor arms/walls
- **Pedalboard Mount** - Low-profile velcro mount

## Printing Guide

### Software Requirements

1. **OpenSCAD** (Free, open-source)
   - Download: [openscad.org](https://openscad.org/)
   - Used to customize and export models

2. **Slicer Software**
   - Cura, PrusaSlicer, or your preferred slicer
   - Converts STL to G-code for your printer

### Recommended Print Settings

#### General Settings

| Setting | Value | Notes |
|---------|-------|-------|
| Layer Height | 0.2mm | Good balance of quality/speed |
| Wall Thickness | 1.2mm | 3 walls minimum |
| Infill | 20-30% | Higher for stage cases |
| Supports | Case dependent | See per-model notes |
| Bed Adhesion | Brim recommended | Especially for larger parts |

#### Material Selection

**PLA**
- ✓ Easy to print
- ✓ Good for indoor/desktop use
- ✓ Lower cost
- ✗ Not heat resistant
- ✗ Less durable

**PETG**
- ✓ More durable
- ✓ Better for stage use
- ✓ Temperature resistant
- ✓ Slightly flexible
- ✗ Needs higher temps
- ✗ Strings more

**TPU** (for specific parts)
- Rubber feet
- Anti-vibration mounts
- Cable grommets

### Per-Model Print Instructions

#### Raspberry Pi + LCD Case

**Base:**
- Supports: None needed
- Orientation: Print as shown
- Print time: ~5 hours
- Notes: Print walls first for better strength

**Lid:**
- Supports: Yes (for LCD standoffs)
- Orientation: Upside down (as shown in model)
- Print time: ~3 hours
- Notes: Support only needed under standoffs

#### Stage LED Case

- Supports: Tree supports under angled face
- Orientation: As shown (angled back)
- Print time: ~4-6 hours
- Material: PETG recommended for durability
- Notes: Use 3+ walls for impact resistance

#### Compact All-in-One

**Body:**
- Supports: None needed
- Orientation: Print as shown
- Print time: ~5 hours

**Front Panel:**
- Supports: Yes (for LED standoffs)
- Orientation: Face down
- Print time: ~1.5 hours

**Back Panel:**
- Supports: None
- Orientation: Face down
- Print time: ~1 hour

### Exporting for Printing

1. Open model in OpenSCAD
2. Set configuration variables at top of file
3. Press F5 to preview
4. Press F6 to render (may take time)
5. Export as STL: File → Export → Export as STL
6. Import STL into your slicer
7. Apply settings and generate G-code

## Assembly Instructions

### Raspberry Pi + LCD Case

**Required Hardware:**
- 4× M2.5 × 8mm screws (Pi mounting)
- 4× M2.5 × 6mm screws (LCD mounting)
- 4× M2 × 8mm screws (lid attachment)
- Raspberry Pi 3B+ or 4
- 16×2 LCD with I2C backpack

**Assembly Steps:**

1. **Mount Raspberry Pi to Base**
   - Place Pi on standoffs in base
   - Align mounting holes
   - Secure with M2.5 × 8mm screws
   - Route cables through side openings

2. **Wire LCD to Pi**
   - Connect I2C wires (VCC, GND, SDA, SCL)
   - Route wires neatly inside case
   - Test connections before final assembly

3. **Mount LCD to Lid**
   - Place LCD on standoffs (printed into lid)
   - Align screen with window
   - Secure with M2.5 × 6mm screws from inside

4. **Attach Lid**
   - Place lid on case (lip fits into base)
   - Align screw holes with corner posts
   - Secure with 4× M2 × 8mm screws

5. **Final Check**
   - Verify all ports accessible
   - Test power-on
   - Check display visibility

**Total assembly time:** ~15 minutes

---

### Stage LED Display Case

**Required Hardware:**
- 4× M2.5 × 8mm screws (LED mounting)
- 4× Rubber feet (adhesive or screw-mount)
- TM1637 or MAX7219 LED module
- 1× Zip tie (cable strain relief)
- Optional: 2mm red acrylic sheet for filter

**Assembly Steps:**

1. **Prepare Display Module**
   - Test LED module before installation
   - Pre-solder wires if needed
   - Heat-shrink or tape connections

2. **Mount LED Module**
   - Place module on angled platform
   - Route wires through platform hole
   - Secure with M2.5 × 8mm screws

3. **Cable Management**
   - Feed cable through back hole
   - Use zip tie at strain relief point
   - Trim excess zip tie

4. **Install Rubber Feet**
   - Clean bottom of case
   - Apply adhesive rubber feet to corners
   - Or screw-mount feet into pre-drilled holes
   - Press firmly for 30 seconds

5. **Optional: Install Red Filter**
   - Cut 2mm red acrylic using filter template
   - Test fit in window recess
   - Glue from inside with clear adhesive
   - Let cure 24 hours

**Total assembly time:** ~10 minutes

---

### Compact All-in-One Case

**Required Hardware:**
- 4× M2.5 × 10mm screws (Pi mounting - vertical)
- 4× M2.5 × 8mm screws (LED mounting)
- 4× M2 × 8mm screws (back panel)
- Raspberry Pi Zero W/2W, or Pi 3A+ (compact)
- TM1637 LED module

**Assembly Steps:**

1. **Mount Raspberry Pi Vertically**
   - Align Pi with vertical mounting pillars
   - Note orientation: USB ports face right
   - Secure with M2.5 × 10mm screws
   - Route power/audio cables down

2. **Mount LED to Front Panel**
   - Place LED on front panel standoffs
   - Align digits with window
   - Secure with M2.5 × 8mm screws
   - Wire to Pi GPIO pins

3. **Wire Connections**
   - Connect LED to Pi GPIO
   - Connect USB audio (if used)
   - Keep wires neat and short
   - Use zip ties if needed

4. **Install Front Panel**
   - Align front panel lip with body
   - Press firmly until clips engage
   - Check LED visibility through window

5. **Attach Back Panel**
   - Route remaining cables
   - Place back panel on body
   - Secure with 4× M2 × 8mm screws

6. **Add Mounting Method**
   - Adhesive velcro for pedalboard
   - VESA adapter for monitor arm
   - Rubber feet for desktop

**Total assembly time:** ~20 minutes

## Bill of Materials

### For Raspberry Pi + LCD Case

| Item | Quantity | Source | Cost (USD) |
|------|----------|--------|------------|
| 3D printed base | 1 | Self-print | ~$2 |
| 3D printed lid | 1 | Self-print | ~$1 |
| M2.5 × 8mm screws | 8 | Hardware store | $1 |
| M2 × 8mm screws | 4 | Hardware store | $0.50 |
| Raspberry Pi 4 (2GB) | 1 | Adafruit/Amazon | $45 |
| 16×2 LCD I2C | 1 | Amazon | $10 |
| USB Audio Interface | 1 | Amazon | $30 |
| microSD Card (16GB) | 1 | Amazon | $8 |
| Power Supply (5V 3A) | 1 | Adafruit | $8 |
| **Total** | | | **~$105** |

### For Stage LED Case

| Item | Quantity | Source | Cost (USD) |
|------|----------|--------|------------|
| 3D printed case | 1 | Self-print | ~$2 |
| TM1637 LED display | 1 | Amazon/AliExpress | $5 |
| Rubber feet (adhesive) | 4 | Hardware store | $2 |
| M2.5 × 8mm screws | 4 | Hardware store | $0.50 |
| Zip ties | 2 | Hardware store | $0.25 |
| Red acrylic (optional) | 1 sheet | Craft store | $3 |
| **Total** | | | **~$13** |

### For Compact All-in-One

| Item | Quantity | Source | Cost (USD) |
|------|----------|--------|------------|
| 3D printed body | 1 | Self-print | ~$3 |
| 3D printed panels | 2 | Self-print | ~$0.50 |
| Raspberry Pi Zero 2 W | 1 | Adafruit | $15 |
| TM1637 LED | 1 | Amazon | $5 |
| M2.5 × 10mm screws | 4 | Hardware store | $0.50 |
| M2.5 × 8mm screws | 4 | Hardware store | $0.50 |
| M2 × 8mm screws | 4 | Hardware store | $0.50 |
| USB Mini Microphone | 1 | Amazon | $15 |
| microSD Card (16GB) | 1 | Amazon | $8 |
| USB Power adapter | 1 | Amazon | $6 |
| **Total** | | | **~$54** |

## Customization

All OpenSCAD models are parametric and can be customized.

### Common Modifications

#### Change Case Dimensions

Edit these variables at the top of the file:

```openscad
// Example: Make case 10mm longer
case_length = pi_length + wall * 2 + 20;  // Was + 10
```

#### Adjust Ventilation

```openscad
// More/larger vent holes
vent_hole_dia = 4;  // Was 3
vent_spacing = 4;   // Was 5 (closer together)
```

#### Add Custom Text/Branding

```openscad
// Add your band name to lid
translate([case_length/2, panel_thickness - 0.5, 10])
    rotate([90, 0, 0])
    linear_extrude(height=0.6)
    text("MY BAND", size=5, halign="center");
```

#### Support Different Raspberry Pi Models

```openscad
// For Raspberry Pi 3A+ (smaller)
pi_length = 65;
pi_width = 56;
// Adjust case dimensions accordingly
```

### Remix and Share

These designs are open-source under MIT license. Feel free to:
- Modify for your specific needs
- Share your remixes
- Use commercially
- Print and sell assembled units

If you create cool modifications, consider sharing them with the community!

## Troubleshooting

### Print Issues

**Warping corners:**
- Use brim or raft
- Increase bed temperature
- Ensure level bed
- Try glue stick on bed

**Supports hard to remove:**
- Use tree supports
- Adjust support density to 10-15%
- Enable "support interface"
- Print support at 5°C cooler

**Weak layer adhesion:**
- Increase printing temperature
- Slow down print speed
- Increase flow rate 2-3%
- Check nozzle isn't clogged

### Assembly Issues

**Screws don't fit:**
- Pilot holes may need drilling out
- Use 2.5mm drill bit for M2.5
- Print at 101% scale if consistent issue

**Parts don't align:**
- Check you printed correct version
- Verify printer calibration
- Small gaps OK, can file/sand
- Lid should fit snug but not tight

**LCD/LED doesn't fit window:**
- Measure your specific module
- Adjust window size in OpenSCAD
- Re-export and re-print lid/panel only

## Resources

- [OpenSCAD Documentation](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)
- [Thingiverse Nashville Numbers](https://thingiverse.com/) (search for remixes)
- [r/3Dprinting](https://reddit.com/r/3Dprinting) - Printing help
- [Project GitHub](https://github.com/your-repo) - Report issues

## Gallery

Share your builds! Tag with #NashvilleNumbers on social media.

---

**Happy printing! 🎵🎸🖨️**
