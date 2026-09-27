// Nashville Numbers enclosures - "ghost" models of the parts the cases hold.
//
// Each ghost is the part's envelope plus the free space it needs to be used:
// plug bodies in front of ports, Dupont jumpers above the GPIO header, wires
// behind displays, buttons and jacks. The fit checks (tools/check_cad.py)
// require that no printed part intersects any ghost.
//
// Dimensions come from the official Raspberry Pi mechanical drawings and
// common module datasheets, rounded outwards. Vendor-variable modules are
// parameters - measure yours (see README.md).

include <common.scad>

// ---------------------------------------------------------------------------
// Raspberry Pi 4 Model B / Pi 5, board coordinates:
//   x along the 85 mm edge (x = 0 microSD edge, x = 85 USB/Ethernet edge)
//   y along the 56 mm edge (y = 0 power/HDMI edge, y = 56 GPIO edge)
//   z = 0 is the PCB top surface
// ---------------------------------------------------------------------------
pi_len = 85;
pi_wid = 56;
pi_pcb_t = 1.4;
pi_holes = [[3.5, 3.5], [61.5, 3.5], [3.5, 52.5], [61.5, 52.5]];
pi_standoff_h = 5;          // PCB bottom above the base plate
pi_standoff_d = 6.0;        // = keep-out pad diameter around the holes

function pi_usb_y(model) = model == 5 ? [29.1, 47.0] : [9.0, 27.0];
function pi_eth_y(model) = model == 5 ? 10.2 : 45.75;
function pi_hdmi_x(model) = model == 5 ? [25.8, 39.2] : [26.0, 39.5];

module pi_ghost(model = 4, plugs = true, wiring = true, cooling = true) {
    // board and underside components (standoff pads excluded)
    translate([0, 0, -pi_pcb_t]) rbox([pi_len, pi_wid, pi_pcb_t], 3);
    difference() {
        translate([0, 0, -pi_pcb_t - 2.0]) rbox([pi_len, pi_wid, 2.0], 3);
        for (h = pi_holes) translate([h[0], h[1], -10]) cylinder(d = pi_standoff_d + 0.4, h = 20);
    }
    // microSD card (underside, protrudes 2.5 mm)
    translate([-2.5, 21.5, -pi_pcb_t - 1.8]) cube([15, 13, 1.8]);
    // long edge (y = 0): USB-C, 2x micro-HDMI, Pi 4 audio jack
    translate([11.2 - 4.6, -1.3, 0]) cube([9.2, 7.8, 3.4]);
    for (x = pi_hdmi_x(model)) translate([x - 3.9, -1.5, 0]) cube([7.8, 8.0, 3.7]);
    if (model == 4) translate([54 - 3.5, -2.5, 0]) cube([7, 14.5, 6.2]);
    // short edge (x = 85): stacked USB-A pairs and RJ45
    for (y = pi_usb_y(model)) translate([69.4, y - 7.3, 0]) cube([18.1, 14.6, 16.2]);
    translate([65.5, pi_eth_y(model) - 8.0, 0]) cube([22.0, 16.0, 13.9]);
    // GPIO header, PoE / fan headers
    translate([7.1, 49.9, 0]) cube([50.8, 5.2, 8.6]);
    translate([58.5, 45.5, 0]) cube([7.5, 9, 9]);
    // camera / display FFC connectors (5.5 mm tall)
    translate([1.0, 16, 0]) cube([5, 24, 5.5]);
    translate([43.5, 0.5, 0]) cube([5, 22, 5.5]);
    if (cooling) {
        if (model == 5) translate([3, 12, 0]) cube([60, 40, 16]);   // Active Cooler + air gap
        else translate([21.5, 24.5, 0]) cube([15, 15, 10]);         // stick-on heatsink
    }
    if (wiring) translate([6, 48.5, 0]) cube([53, 8.5, 22]);        // Dupont jumpers on the header
    if (plugs) pi_plugs(model);
}

// Plug bodies in front of each external port (25 mm long).
module pi_plugs(model = 4) {
    // USB-C and micro-HDMI overmolds
    translate([11.2 - 6.5, -27, 1.7 - 4.0]) cube([13, 25.5, 8.0]);
    for (x = pi_hdmi_x(model)) translate([x - 6.0, -27, 1.8 - 4.0]) cube([12, 25.3, 8.0]);
    if (model == 4) translate([54, -2.4, 3.1]) rotate([90, 0, 0]) cylinder(d = 10, h = 25);
    // USB-A plugs (both of each stacked pair) and the RJ45 plug
    for (y = pi_usb_y(model)) translate([87.4, y - 8.3, -0.6]) cube([25, 16.6, 17.6]);
    translate([87.4, pi_eth_y(model) - 7.8, 0]) cube([25, 15.6, 15.5]);
}

// ---------------------------------------------------------------------------
// 16x2 character LCD (HD44780) with PCF8574 I2C backpack.
// LCD coordinates (seen from the front, header row at the top):
//   x along 80 (x = 0 left edge), y along 36 (y = 0 bottom edge),
//   z = 0 is the PCB front surface, the bezel faces +z, the backpack -z.
// ---------------------------------------------------------------------------
lcd_pcb = [80, 36, 1.6];
lcd_bezel = [71.2, 24.2, 7.0];
lcd_va = [64.5, 14.5];              // viewing area (centred on the bezel)
lcd_backpack = [41.6, 19.1, 11.0];  // incl. header spacer and contrast trimmer
lcd_backpack_pos = [5, 16.4];       // lower-left corner of the backpack on the PCB

module lcd1602_ghost(header_side = "both", wiring = true) {
    translate([0, 0, -lcd_pcb[2]]) cube(lcd_pcb);
    translate([(lcd_pcb[0] - lcd_bezel[0]) / 2, (lcd_pcb[1] - lcd_bezel[1]) / 2, 0]) cube(lcd_bezel);
    translate([lcd_backpack_pos[0], lcd_backpack_pos[1], -lcd_pcb[2] - lcd_backpack[2]])
        cube(lcd_backpack);
    if (wiring) {
        // the backpack's 4-pin I2C header points sideways; Dupont housings + bend
        if (header_side == "left" || header_side == "both")
            translate([-20, 18, -lcd_pcb[2] - lcd_backpack[2]]) cube([25, 16, lcd_backpack[2]]);
        if (header_side == "right" || header_side == "both")
            translate([75, 18, -lcd_pcb[2] - lcd_backpack[2]]) cube([25, 16, lcd_backpack[2]]);
    }
}

// ---------------------------------------------------------------------------
// 7-segment modules. Module coordinates: x/y as seen from the front (origin at
// the lower-left corner of the module outline), z = 0 is the display's front
// surface, the module extends to -z.
// ---------------------------------------------------------------------------
// [outline w, outline h, depth to PCB back, digit window w, digit window h, wiring depth]
function sevenseg_dims(kind) =
    kind == "ht16k33_12" ? [120.0, 50.0, 13.0, 110.0, 40.0, 20] :   // Adafruit 1270 (1.2")
    kind == "tm1637_056" ? [50.5, 25.0, 10.0, 48.0, 17.0, 22] :     // 0.56" module
                           [42.0, 24.0, 9.0, 29.0, 13.0, 22];       // tm1637_036

module sevenseg_ghost(kind = "ht16k33_12", wiring = true) {
    d = sevenseg_dims(kind);
    translate([0, 0, -d[2]]) cube([d[0], d[1], d[2]]);
    // header + jumpers behind the module, clear of a 5 mm edge margin that
    // the clamp tabs press on
    if (wiring) translate([5, 5, -d[2] - d[5]]) cube([d[0] - 10, d[1] - 10, d[5]]);
}

// ---------------------------------------------------------------------------
// Panel parts. Local coordinates: the panel's outer surface is z = 0, the
// part's axis is z, the case interior is -z.
// ---------------------------------------------------------------------------
button_hole_d = 16.2;
button_nut_d = 22;      // flat area needed around the hole inside

module button16_ghost(panel_t) {
    translate([0, 0, -panel_t - 3.5]) cylinder(d = button_nut_d, h = 3.5);          // nut
    translate([0, 0, -panel_t - 38]) cylinder(d = 18.5, h = 38 - panel_t + eps);    // body, lugs, wires
    translate([0, 0, 0]) cylinder(d = 20, h = 12);                                   // head + finger
}

jack_hole_d = 9.6;

module jack_ts_ghost(panel_t) {
    // open-frame 1/4" jack with R1/C1 soldered on its lugs, wires behind
    translate([-11, -9, -panel_t - 40]) cube([22, 18, 40 - panel_t + eps]);
    translate([0, 0, 0]) cylinder(d = 15, h = 42);                                   // plug + nut
}

// BSS138 4-channel level shifter with jumpers standing up from its headers.
module level_shifter_ghost() {
    cube([21, 17, 18]);
}

// What the button and jack look like from outside, for the renders only.
module button16_visual() {
    color("Silver") cylinder(d = 19, h = 2);                            // bezel
    color("FireBrick") translate([0, 0, 2 - eps]) cylinder(d = 12, h = 2.5);   // cap
}

module jack_visual() {
    color("Silver") {
        cylinder(d = 14, h = 2.4, $fn = 6);                             // nut
        cylinder(d = 9.4, h = 4);                                       // threaded bush
    }
}
