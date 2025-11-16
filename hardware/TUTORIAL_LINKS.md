# Tutorial Resources for ESP32-S3 Nashville Numbers PCB Design

**Curated list of tutorials, guides, and resources for building the ESP32-S3 custom PCB**

This document provides links to external tutorials that will help you learn everything needed to design, manufacture, and program the Nashville Numbers ESP32-S3 custom PCB.

---

## Table of Contents

1. [PCB Design with EasyEDA](#1-pcb-design-with-easyeda)
2. [PCB Design Fundamentals](#2-pcb-design-fundamentals)
3. [JLCPCB Assembly Service](#3-jlcpcb-assembly-service)
4. [ESP32-S3 Development](#4-esp32-s3-development)
5. [I2S Audio & INMP441 Microphone](#5-i2s-audio--inmp441-microphone)
6. [FFT & Audio Processing](#6-fft--audio-processing)
7. [Component Selection & Sourcing](#7-component-selection--sourcing)
8. [Troubleshooting & Community](#8-troubleshooting--community)

---

## 1. PCB Design with EasyEDA

### 🎥 Video Tutorials (Highly Recommended!)

**"Custom PCB Design Tutorial - From Schematic to Manufacturing in EasyEDA"** by Robert Feranec
- **Duration:** ~2 hours
- **Level:** Beginner
- **Content:** Complete walkthrough of designing a USB-C power supply PCB from scratch
- **Link:** https://www.classcentral.com/course/youtube-how-to-make-a-custom-pcb-in-2-hours-full-tutorial-easyeda-277120
- **Why watch:** Best single resource for learning EasyEDA end-to-end

**"From Circuit Diagram to PCB - Part 1"** by Ralph S Bacon
- **Level:** Absolute beginner
- **Content:** Schematic creation, parts selection, BOM generation
- **Uses:** EasyEDA + LCSC + JLCPCB integration
- **Link:** https://www.classcentral.com/course/youtube-164-from-circuit-diagram-to-pcb-part-1-schematic-parts-bom-easyeda-tutorial-130696
- **Why watch:** Perfect for first-time PCB designers

**"EasyEda Tutorial - Absolute Beginners"** (Official)
- **Source:** Design n Techie
- **Link:** https://docs.easyeda.com/en/Videos/Demo-Video/
- **Content:** Official tutorial videos from EasyEDA
- **Why watch:** Straight from the source

### 📚 Written Tutorials

**EasyEDA Online PCB Design Tutorial for IoT Projects (2025)**
- **Link:** https://iotdunia.com/easyeda-online-pcb-design/
- **Updated:** 2025
- **Content:** Comprehensive guide covering schematic creation, PCB layout, and circuit simulation
- **Best for:** Understanding EasyEDA's interface and workflow

**How to Use EasyEDA to design PCB Schematic Step By Step**
- **Link:** https://www.wellpcb.com/blog/pcb-manufacturing/easyeda/
- **Updated:** May 2025
- **Quote:** "The perfect PCB design software for beginners"
- **Best for:** Step-by-step schematic design

**PCB Designing Using EasyEDA** (Instructables)
- **Link:** https://www.instructables.com/PCB-Designing-Using-EasyEDA/
- **Format:** Picture-based step-by-step guide
- **Best for:** Visual learners who prefer screenshots

**PCB Design Tutorial Using EasyEDA & JLCPCB**
- **Link:** https://maker.pro/pcb/tutorial/pcb-design-tutorial-using-easyeda-jlcpcb
- **Content:** End-to-end process including ordering from JLCPCB
- **Best for:** Understanding the complete workflow

### 🆓 Free Courses

**Learn EasyEDA Design Tool** (Udemy - Free)
- **Link:** https://www.udemy.com/course/getting-started-with-easyeda-electronics-design-tool/
- **Content:** Create schematic symbols, explore simulation, transform schematics into PCB designs
- **Duration:** Self-paced
- **Best for:** Structured learning path

**EasyEDA Tutorial PDF** (Official)
- **Link:** https://image.easyeda.com/files/EasyEDA-Tutorial_v6.4.32.pdf
- **Format:** Comprehensive PDF guide
- **Best for:** Offline reference

### 🔄 Importing from KiCad (If Needed)

**Import KiCAD Files to EasyEDA** (Official Docs)
- **EasyEDA Standard:** https://docs.easyeda.com/en/Import/Import-KiCAD/
- **EasyEDA Pro:** https://prodocs.easyeda.com/en/import-export/import-kicad/
- **Supports:** KiCAD v4.06 and greater
- **Format:** ZIP file containing schematic + symbols
- **Best for:** Porting existing KiCad designs

---

## 2. PCB Design Fundamentals

### Ground Planes, Vias, and Trace Width

**Basics of PCB Layout: Components, Traces, and Ground Planes**
- **Link:** https://www.viasion.com/blog/pcb-layout-components-traces-and-ground-planes/
- **Content:** Comprehensive overview of PCB layout fundamentals
- **Topics:** Component placement, trace routing, ground plane benefits
- **Best for:** Understanding the "why" behind PCB design rules

**PCB Designing Tutorial for Beginners (2025)**
- **Link:** https://www.bestpcbs.com/blog/2025/06/pcb-designing-tutorial-for-beginners/
- **Updated:** June 2025
- **Content:** Trace width guidelines, clearances, modern best practices
- **Best for:** 2025 standards and recommendations

**PCB Design Basics: A Comprehensive Guide for Beginners**
- **Link:** https://www.andwinpcb.com/pcb-design-basics-a-comprehensive-guide-for-beginners/
- **Content:** Complete beginner's guide to PCB design concepts
- **Topics:** Layer stack-up, design rules, manufacturing constraints
- **Best for:** Theoretical foundation

**Beginner's Guide to PCB Design: From Schematic to Gerbers**
- **Link:** https://www.allpcb.com/allelectrohub/beginners-guide-to-pcb-design-from-schematic-to-gerbers/
- **Content:** Complete workflow from schematic to manufacturing files
- **Best for:** Understanding the entire process

### Stack Exchange Discussions (Real-world Q&A)

**Understanding the basics of a ground plane and vias on a 2 layer PCB**
- **Link:** https://electronics.stackexchange.com/questions/681061/understanding-the-basics-of-a-ground-plane-and-vias-to-it-on-a-2-layer-pcb
- **Best for:** Practical questions answered by experts

**How to correctly design ground planes simple circuit PCB's?**
- **Link:** https://electronics.stackexchange.com/questions/676410/how-to-correctly-design-ground-planes-simple-circuit-pcbs
- **Best for:** Real-world design challenges and solutions

### Design Guidelines Reference

**The PCB Ground Plane and How it is Used in Your Design** (Cadence)
- **Link:** https://resources.pcb.cadence.com/blog/2020-the-pcb-ground-plane-and-how-it-is-used-in-your-design
- **Content:** In-depth technical explanation of ground plane design
- **Best for:** Advanced understanding

**Key Takeaways:**
- Minimum trace width: 0.2mm (8 mil) for standard designs
- Minimum spacing: 0.2mm (8 mil) between traces
- Ground plane coverage: Aim for 70%+ on bottom layer
- Via size: Typically 0.3-0.5mm for through-hole

---

## 3. JLCPCB Assembly Service

### Official JLCPCB Resources

**How do I place a PCBA order?** (Official FAQ)
- **Link:** https://jlcpcb.com/help/article/how-do-i-place-a-pcba-order
- **Content:** Step-by-step official guide
- **Best for:** Authoritative reference

**Build Your First Custom PCBA Successfully in 5 Key Steps**
- **Link:** https://jlcpcb.com/blog/build-your-first-custom-pcba
- **Content:** Official blog post with detailed workflow
- **Best for:** Understanding JLCPCB's process

**The Comprehensive Guide to PCB Assembly Process at JLCPCB**
- **Link:** https://jlcpcb.com/blog/the-ultimate-guide-to-pcb-assembly-process
- **Content:** Complete overview of JLCPCB's assembly capabilities
- **Topics:** MOQ, lead times, capabilities, pricing
- **Best for:** Understanding what JLCPCB can do

**PCB Assembly FAQs**
- **Link:** https://jlcpcb.com/help/article/pcb-assembly-faqs
- **Content:** Comprehensive FAQ section
- **Best for:** Quick answers to common questions

**PCB Layout Tutorial: A Step-by-Step Guide to Ordering with JLCPCB**
- **Link:** https://jlcpcb.com/blog/pcb-layout-tutorial-order-with-jlcpcb
- **Content:** Complete ordering workflow
- **Best for:** First-time JLCPCB users

### Community Tutorials

**How to Order PCBA on JLCPCB - It's Easy** (ElCircuit)
- **Link:** https://www.elcircuit.com/2023/10/how-to-order-pcba-on-jlcpcb-its-easy.html
- **Updated:** October 2023
- **Content:** Step-by-step with screenshots
- **Best for:** Visual walkthrough

**JLCPCB SMT Assembly Service - Complete Guide** (Hackaday.io)
- **Link:** https://hackaday.io/project/184378-jlcpcb-smt-assembly-service-complete-guide
- **Content:** Community project documenting the full process
- **Best for:** Tips and tricks from experienced users

**How to order Full PCB Assembly Service** (Electronoobs)
- **Link:** https://electronoobs.com/eng_blogs.php?id=194
- **Content:** Detailed tutorial with examples
- **Best for:** Practical examples

**JLCPCB SMT Assembly: A Guide to Utilizing JLCPCB's SMT Assembly Services**
- **Link:** https://prototypepcbassembly.com/jlcpcb-smt-assembly/
- **Content:** Third-party comprehensive guide
- **Best for:** Independent perspective

### Component Orientation Fix

**JLCPCB SMT Assembly Components Orientation Fix** (GitHub)
- **Link:** https://github.com/JLCPCB/JLCPCB-SMT-Assembly-Components-orientation-fix
- **Content:** Official guide for fixing component placement issues
- **Best for:** Troubleshooting BOM/CPL problems

**Key Information:**
- **Files needed:** Gerber, BOM (XLS/XLSX/CSV), CPL (XLS/XLSX/CSV)
- **Parts library:** 40,000+ components (698 basic, 300k+ extended)
- **MOQ:** As low as 2 pieces
- **Lead time:** 90% finished within 24 hours after PCB fabrication
- **Turn-around:** Total 7-10 days including shipping

---

## 4. ESP32-S3 Development

### Getting Started Guides (2025)

**Getting Started with ESP32 Arduino** (Official Espressif - October 2025)
- **Link:** https://developer.espressif.com/blog/2025/10/arduino-get-started/
- **Updated:** October 2025
- **Content:** Official guide from Espressif for ESP32 Arduino Core setup
- **Topics:** Arduino IDE installation, board package setup, dual-core programming
- **Best for:** Most current official guide

**ESP32-S3 Getting Started** (Official Docs)
- **Link:** https://esp32s3.com/getting-started.html
- **Content:** Complete getting started guide for ESP32-S3
- **Best for:** ESP32-S3 specific information

**Installing the ESP32 Board in Arduino IDE** (Random Nerd Tutorials)
- **Link:** https://randomnerdtutorials.com/installing-the-esp32-board-in-arduino-ide-windows-instructions/
- **Platforms:** Windows, Mac OS X, Linux
- **Best for:** Platform-specific installation instructions

**ESP32-S3 Geek and Arduino IDE - Getting Started Tutorial** (April 2025)
- **Link:** https://www.electroniclinic.com/esp32-s3-geek-and-arduino-ide-getting-started-tutorial/
- **Updated:** April 2025
- **Content:** Waveshare ESP32-S3 Geek Development board specific
- **Best for:** Library installation and setup

**ESP32-S3 YOUTH #1 - Getting Started** (Instructables - January 2025)
- **Link:** https://www.instructables.com/ESP32-S3-YOUTH-1-Getting-Started/
- **Updated:** January 2025
- **Content:** Step-by-step setup with screenshots
- **Key settings:** USB CDC On Boot: Enable
- **Best for:** Beginners with pictures

**Programming ESP32-S3 Box-3 with Arduino IDE** (October 2025)
- **Link:** https://circuitdigest.com/microcontrollers-projects/programming-esp32-s3-box3-with-arduino-ide-rgb-led-control-interface
- **Updated:** October 2025
- **Content:** Interactive RGB LED controller project
- **Topics:** PWM, touchscreen interface, LovyanGFX library
- **Best for:** Practical project examples

### Official Documentation

**Arduino ESP32 Documentation**
- **Link:** https://docs.espressif.com/projects/arduino-esp32/en/latest/getting_started.html
- **Content:** Complete Arduino-ESP32 documentation
- **Best for:** Comprehensive reference

**ESP-IDF Programming Guide for ESP32-S3**
- **Link:** https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/get-started/index.html
- **Content:** Official ESP-IDF (native framework) documentation
- **Best for:** Advanced development with C/C++

### Additional Tutorials

**Hello Arduino on ESP32-S3** (Hutscape)
- **Link:** https://hutscape.com/tutorials/hello-arduino-esp32s3
- **Content:** Simple "hello world" tutorial
- **Best for:** Verifying your setup works

**Arduino IDE Setup - Adafruit QT Py ESP32-S3**
- **Link:** https://learn.adafruit.com/adafruit-qt-py-esp32-s3/arduino-ide-setup-99bba7be-288a-490d-b27b-1e63d17882fc
- **Content:** Setup guide for Adafruit board (8MB Flash/No PSRAM)
- **Best for:** Adafruit hardware users

**Setup Instructions:**
1. Add board URL: `https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json`
2. Install "ESP32 by Espressif Systems" from Boards Manager
3. Select "ESP32S3 Dev Module"
4. Set "USB CDC On Boot" to "Enable"
5. Upload your first sketch!

---

## 5. I2S Audio & INMP441 Microphone

### Comprehensive Tutorials

**Sound with ESP32 - I2S Protocol** (DroneBot Workshop)
- **Link:** https://dronebotworkshop.com/esp32-i2s/
- **Content:** Complete I2S tutorial for ESP32
- **Topics:** I2S protocol, microphone input, audio output
- **Hardware:** INMP441 microphone examples
- **Best for:** Understanding I2S from the ground up

**ESP32 Mic Testing With INMP441 and DumbDisplay** (Instructables)
- **Link:** https://www.instructables.com/ESP32-Mic-Testing-With-INMP441-and-DumbDisplay/
- **Format:** Step-by-step with pictures
- **Content:** Testing INMP441 microphone with visualization
- **Best for:** Verifying your mic is working

**Inputting audio to an ESP32 from an INMP441 I2S microphone: success** (ESP32 Forum)
- **Link:** https://esp32.com/viewtopic.php?t=15185
- **Content:** Forum discussion with working code examples
- **Best for:** Troubleshooting and community solutions

### GitHub Projects (Code Examples)

**esp32-mic-fft** by squix78
- **Link:** https://github.com/squix78/esp32-mic-fft
- **Content:** Sample code for I2S microphone with FFT analysis
- **Hardware:** ESP-EYE board (adaptable to any I2S mic)
- **Best for:** FFT implementation example

**ESP32-Audio-Analyzer-Loudness-and-Frequency-Detection**
- **Link:** https://github.com/ElectroPrashant/ESP32-Audio-Analyzer-Loudness-and-Frequency-Detection
- **Content:** Real-time audio loudness measurement and frequency detection
- **Hardware:** ESP32 + INMP441
- **Topics:** Audio analysis, dominant frequency detection
- **Best for:** Complete working project

**ESP32-AudioInI2S** by sheaivey
- **Link:** https://github.com/sheaivey/ESP32-AudioInI2S
- **Content:** Simple MEMS I2S microphone and audio processing library
- **Features:** Robust audio processing classes, FFT compute on I2S samples
- **Best for:** Ready-to-use library

**More INMP441 Projects** (GitHub Topics)
- **Link:** https://github.com/topics/inmp441
- **Content:** Collection of INMP441-related projects
- **Best for:** Browsing examples and inspiration

### Component Documentation

**How to Use INMP441 FRONT MIC: Pinouts, Specs, and Examples**
- **Link:** https://docs.cirkitdesigner.com/component/f5a2b2c1-1830-47a0-bebd-4ccef6a7babd/inmp441-front-mic
- **Content:** Complete INMP441 documentation
- **Topics:** Pinouts, electrical specs, connection examples
- **Best for:** Technical reference

### IoT Project Examples

**Smart door bell and noise meter using FFT on ESP32**
- **Link:** https://iotassistant.io/esp32/smart-door-bell-noise-meter-using-fft-esp32/
- **Content:** Practical IoT project using FFT for sound detection
- **Best for:** Real-world application example

**INMP441 Key Specs:**
- **Interface:** I2S digital
- **Frequency response:** 60 Hz - 15 kHz
- **SNR:** >60 dB
- **Connections:** VDD, GND, SD, WS, SCK, L/R
- **Power:** 3.3V, ~1.4mA

---

## 6. FFT & Audio Processing

### ESP-DSP Library (Official Espressif)

**ESP-DSP Library Documentation**
- **Link:** https://docs.espressif.com/projects/esp-dsp/en/latest/esp32/
- **Content:** Official Espressif DSP library documentation
- **Chips:** ESP32, ESP32-S3, ESP32-P4
- **Best for:** Official FFT implementation

**ESP-DSP Library Examples**
- **Link:** https://docs.espressif.com/projects/esp-dsp/en/latest/esp32/esp-dsp-examples.html
- **Content:** Working examples for FFT and other DSP operations
- **Best for:** Copy-paste starting code

**ESP-DSP GitHub Repository**
- **Link:** https://github.com/espressif/esp-dsp
- **Content:** Source code, examples, benchmarks
- **Best for:** Exploring the library code

**ESP-DSP FFT Example README**
- **Link:** https://github.com/espressif/esp-dsp/blob/master/examples/fft/README.md
- **Content:** Specific FFT example documentation
- **Best for:** Understanding FFT usage

**ESP-DSP API Reference**
- **Link:** https://docs.espressif.com/projects/esp-dsp/en/latest/esp32/esp-dsp-apis.html
- **Content:** Complete API documentation
- **Best for:** Function reference

### Community Discussions

**Advice using FFT on the ESP32 - ESP-DSP Component**
- **Link:** https://www.esp32.com/viewtopic.php?t=11849
- **Content:** Forum discussion with practical FFT advice
- **Best for:** Tips from experienced users

**ESP-DSP: The official DSP library for the ESP32** (Hiveeyes Community)
- **Link:** https://community.hiveeyes.org/t/esp-dsp-the-official-dsp-library-for-the-esp32/1556
- **Content:** Community discussion and overview
- **Best for:** Understanding ESP-DSP capabilities

### Alternative FFT Tutorials

**FFT on the ESP32** by Robin Scheibler
- **Link:** http://www.robinscheibler.org/2017/12/12/esp32-fft.html
- **Content:** Vanilla FFT implementation
- **Note:** Classic tutorial, still relevant
- **Best for:** Understanding FFT fundamentals

**Fast Fourier Transform (FFT) on the ESP32 Development Board** (Elektor)
- **Link:** https://www.elektormagazine.com/articles/fast-fourier-transform-fft-on-the-esp32
- **Content:** Detailed FFT article
- **Best for:** Theory and implementation

**HackerBox 0079: Audio DSP** (Instructables)
- **Link:** https://www.instructables.com/HackerBox-0079-Audio-DSP/
- **Content:** Complete audio DSP project
- **Best for:** Hands-on project

### Advanced: DSP with Faust

**DSP on the ESP-32 With Faust**
- **Link:** https://faustdoc.grame.fr/tutorials/esp32/
- **Content:** Using Faust programming language for DSP
- **Best for:** Advanced audio processing

**ESP-DSP Performance:**
- **ESP32-S3:** ~10x faster than original ESP32
- **FFT processing:** <16% CPU time at 44.1kHz/2048 samples
- **Optimization:** Hardware vector math acceleration

---

## 7. Component Selection & Sourcing

### LCSC Component Database

**LCSC Electronics Components**
- **Website:** https://www.lcsc.com
- **Content:** 300,000+ electronic components
- **Integration:** Direct integration with JLCPCB assembly
- **Best for:** Finding parts for your BOM

**LCSC Component Search Tips:**
- Filter by "JLCPCB Assembly" to see only assemblable parts
- Look for "Basic Parts" (lowest assembly cost)
- Check stock levels before finalizing design
- Compare similar parts for best price/availability

### Finding Components in EasyEDA

**EasyEDA Component Library:**
- Built-in LCSC component library
- Search directly in the schematic editor
- Shows real-time stock levels
- Links to datasheets

**How to search:**
1. Open EasyEDA schematic editor
2. Click "LCSC Components" in left sidebar
3. Search by part number or description
4. Filter by "Basic Parts"
5. Drag component to schematic

### Alternative Distributors (For comparison/backup)

**Mouser Electronics**
- **Website:** https://www.mouser.com
- **Best for:** US-based sourcing, datasheets
- **Shipping:** Worldwide

**Digi-Key Electronics**
- **Website:** https://www.digikey.com
- **Best for:** Largest selection, parametric search
- **Tools:** Excellent parametric filters

**Newark/Element14**
- **Website:** https://www.newark.com
- **Best for:** Europe/US sourcing

### Datasheets (Used in This Project)

**ESP32-S3-WROOM-1 Datasheet**
- **Link:** https://www.espressif.com/sites/default/files/documentation/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf
- **Content:** Complete module specifications, pinout, reference design

**INMP441 Datasheet**
- **Link:** https://invensense.tdk.com/wp-content/uploads/2015/02/INMP441.pdf
- **Content:** MEMS microphone specifications, electrical characteristics

**TM1637 Datasheet**
- **Link:** https://www.mcielectronics.cl/website_MCI/static/documents/Datasheet_TM1637.pdf
- **Content:** LED driver IC specifications, command set

**CP2102N Datasheet**
- **Link:** https://www.silabs.com/documents/public/data-sheets/cp2102n-datasheet.pdf
- **Content:** USB-to-UART bridge specifications

**AMS1117 Datasheet**
- **Link:** http://www.advanced-monolithic.com/pdf/ds1117.pdf
- **Content:** LDO voltage regulator specifications

---

## 8. Troubleshooting & Community

### Forums & Communities

**ESP32 Forum (Official)**
- **Link:** https://esp32.com
- **Content:** Official Espressif forum
- **Best for:** ESP32-specific questions and support

**r/PrintedCircuitBoard (Reddit)**
- **Link:** https://reddit.com/r/PrintedCircuitBoard
- **Content:** PCB design community
- **Best for:** Design review, layout advice

**r/esp32 (Reddit)**
- **Link:** https://reddit.com/r/esp32
- **Content:** ESP32 community projects and help
- **Best for:** ESP32 programming and project ideas

**EasyEDA Forum**
- **Link:** https://easyeda.com/forum
- **Content:** EasyEDA-specific questions
- **Best for:** Software issues, tips and tricks

**Electrical Engineering Stack Exchange**
- **Link:** https://electronics.stackexchange.com
- **Content:** Professional electronics Q&A
- **Best for:** Theoretical questions, expert answers

**Arduino Forum**
- **Link:** https://forum.arduino.cc
- **Content:** Arduino IDE and programming help
- **Best for:** Arduino-specific questions

### YouTube Channels

**DroneBot Workshop**
- **Link:** https://www.youtube.com/c/Dronebotworkshop
- **Content:** ESP32 tutorials, I2S audio, electronics projects
- **Best for:** Video tutorials on ESP32

**Phil's Lab**
- **Link:** https://www.youtube.com/c/PhilsLab
- **Content:** PCB design, hardware engineering
- **Best for:** Professional PCB design techniques

**Robert Feranec**
- **Link:** https://www.youtube.com/c/RobertFeranec
- **Content:** PCB design tutorials, EasyEDA, KiCad
- **Best for:** PCB design best practices

**Andreas Spiess**
- **Link:** https://www.youtube.com/c/AndreasSpiess
- **Content:** ESP32 projects, IoT, sensors
- **Best for:** ESP32 project ideas and reviews

**GreatScott!**
- **Link:** https://www.youtube.com/c/greatscottlab
- **Content:** Electronics projects, tutorials
- **Best for:** General electronics knowledge

### Nashville Numbers Project Resources

**Nashville Numbers GitHub**
- **Link:** (Add your repository link here)
- **Content:** Project source code, documentation
- **Best for:** Project-specific issues and updates

**Nashville Numbers Discord/Slack**
- **Link:** (Add your community link here)
- **Content:** Real-time chat with other builders
- **Best for:** Quick questions, sharing progress

---

## Quick Start Path (Recommended Learning Order)

### Week 1: PCB Design Basics
1. ✅ Watch: "Custom PCB Design Tutorial" by Robert Feranec (2 hours)
2. ✅ Read: "PCB Designing Tutorial for Beginners" (Best PCBs)
3. ✅ Practice: Sign up for EasyEDA, explore interface
4. ✅ Follow: "From Circuit Diagram to PCB - Part 1" by Ralph S Bacon

### Week 2: ESP32-S3 Development
1. ✅ Read: "Getting Started with ESP32 Arduino" (Espressif Oct 2025)
2. ✅ Follow: "ESP32-S3 YOUTH #1 - Getting Started" (Instructables)
3. ✅ Practice: Install Arduino IDE, upload blink sketch to ESP32
4. ✅ Experiment: Run example code, modify and test

### Week 3: Audio Processing
1. ✅ Watch/Read: "Sound with ESP32 - I2S Protocol" (DroneBot Workshop)
2. ✅ Clone: esp32-mic-fft GitHub repository
3. ✅ Read: ESP-DSP documentation and examples
4. ✅ Test: Run FFT examples on ESP32 dev board

### Week 4: PCB Design & Ordering
1. ✅ Design: Create schematic in EasyEDA using this project's guides
2. ✅ Layout: Convert to PCB, add ground pour, run DRC
3. ✅ Read: "How do I place a PCBA order?" (JLCPCB)
4. ✅ Order: Submit PCB + assembly order to JLCPCB

---

## Additional Learning Resources

### Books

**"Designing Audio Effect Plugins in C++"** by Will Pirkle
- Great for understanding audio DSP concepts
- Applicable to ESP32 audio processing

**"The Scientist and Engineer's Guide to Digital Signal Processing"** by Steven W. Smith
- Free online book
- Excellent FFT and DSP fundamentals
- Link: http://www.dspguide.com/

### Online Courses

**Coursera: PCB Design for Manufacture**
- University of Colorado Boulder
- Professional PCB design course

**Udemy: PCB Design with EasyEDA**
- Multiple courses available
- Look for recent (2024-2025) courses

### Tools & Calculators

**Trace Width Calculator**
- **Link:** https://www.4pcb.com/trace-width-calculator.html
- Calculate trace width for current requirements

**Via Current Calculator**
- **Link:** https://www.saturncircuits.com/resources/via-current-calculator/
- Determine via current capacity

**PCB Impedance Calculator**
- **Link:** https://www.eeweb.com/tools/microstrip-impedance/
- Calculate impedance for USB differential pairs

---

## Troubleshooting Quick Links

### Common Issues & Solutions

**"ESP32 not recognized on USB"**
- Install CP210x drivers: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- Try different USB cable (data cable, not charge-only)
- Enable "USB CDC On Boot" in Arduino IDE

**"JLCPCB can't find my components"**
- Use LCSC part numbers in BOM
- Filter for "Basic Parts" in EasyEDA
- Check component orientation in CPL file

**"I2S microphone not working"**
- Verify connections: SD, WS, SCK pins
- Check L/R pin (must be GND or VDD, not floating)
- Add 100nF capacitor near VDD pin

**"FFT results look wrong"**
- Apply windowing (Hamming or Hann)
- Check sample rate configuration
- Verify I2S buffer size (512-2048 typical)

**"PCB design rule check fails"**
- Increase trace width (minimum 0.2mm)
- Increase clearance (minimum 0.2mm)
- Check for isolated copper areas
- Run "rebuild" on ground pour

---

## Staying Current

### Official Blogs to Follow

**JLCPCB Blog**
- **Link:** https://jlcpcb.com/blog
- Updates on services, capabilities, tutorials

**Espressif Blog**
- **Link:** https://blog.espressif.com
- ESP32 updates, new features, case studies

**EasyEDA News**
- **Link:** https://easyeda.com/forum/topic/News-fad75f75ea194a8892ee2509fc6b7a0e
- Software updates, new features

### Social Media

**Twitter/X:**
- @espressif (Espressif Systems)
- @JLCPCB (JLCPCB updates)

**LinkedIn:**
- Follow "Espressif Systems" for professional updates

---

## Summary

This curated list provides everything you need to:
- ✅ Learn PCB design with EasyEDA
- ✅ Order professional assembly from JLCPCB
- ✅ Program ESP32-S3 in Arduino IDE
- ✅ Implement I2S audio input with INMP441
- ✅ Perform FFT analysis with ESP-DSP
- ✅ Troubleshoot common issues
- ✅ Connect with the community

**Recommended starting point:** Watch the 2-hour Robert Feranec video, then follow the 4-week learning path.

**Questions?** Check the forums and Stack Exchange links - chances are someone has already solved your problem!

---

**Last Updated:** 2025-11-16
**Maintained by:** Nashville Numbers Project
**Contributions:** Submit a PR to add helpful tutorials you've found!

---

*Good luck with your PCB design! Remember: Everyone's first PCB design is a learning experience. Don't be afraid to make mistakes - that's how you learn!* 🎸🎵
