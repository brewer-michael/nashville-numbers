// Nashville Numbers - desktop LCD case
//
// Raspberry Pi 5 or 4 + 16x2 character LCD (PCF8574 backpack) + BSS138 level
// shifter + 16 mm push button, in a 30-degree desk wedge.
//
// Printed parts (all without supports):
//   shell     face-down (the LCD face on the bed)          PLA or PETG
//   base      flat, bumper recesses down                    PLA or PETG
//   clamps    three LCD clamp tabs, flat                    PLA or PETG
//
// Hardware: 3x M3 heat-set insert + 3x M3 x 8 (closure), 4x M2.5 x 8 (Pi),
// 3x M2.5 x 8 (LCD clamp tabs), 16 mm momentary button, 4 rubber bumpers,
// foam tape for the level shifter. See README.md.
//
// `part` selects what to render; tools/build.py renders every part.

include <lib/wedge.scad>

part = "assembly";  // assembly | interior | cutaway | exploded | print_layout
                    // | shell | base | clamps | shell_asm | base_asm | clamps_asm
                    // | ghosts_pi4 | ghosts_pi5 | ghost_display | ghost_controls

// ---- enclosure parameters -----------------------------------------------------
W = 125;
D = 82;
H = 38;
angle = 30;
wall = 2.5;
face_t = 3.0;
base_t = 3.0;

// ---- LCD ------------------------------------------------------------------------
lcd_x = W / 2;                  // LCD centre across the face
lcd_s = 28;                     // LCD centre up the slope from the front edge
lcd_header_side = "both";       // I2C header side: "left", "right" or "both" (reserve both)
// clamp tabs: bottom-left and bottom-right edges (below the backpack's I2C
// header, which may exit on either side), and the top edge right of the
// 16-pin header row
lcd_tabs = [["left", -10], ["right", -10], ["top", 16]];
lcd_clamp_depth = lcd_bezel[2] + lcd_pcb[2];      // face underside to PCB back
lcd_window = [lcd_va[0] + 1.5, lcd_va[1] + 2.0];

// ---- button (right side wall) ---------------------------------------------------
button_y = 58;
button_z = 48;

// ---- level shifter (foam-taped to the base plate) -------------------------------
shifter_pos = [92, 5];

// ---- vents --------------------------------------------------------------------------
module shell_vents() {
    // exhaust: slots in the face above the Pi, behind the LCD
    on_face(lcd_x, 70) translate([0, 0, -face_t - 1]) rotate([0, 0, 90])
        slot_row(3, 60, 2.4, 6, face_t + 2);
    // intake: low on the front wall and the right wall
    translate([W / 2, -1, 11]) rotate([-90, 0, 0]) slot_row(12, 10, 2.4, 6, wall + 2);
    translate([W + 1, 42, 11]) rotate([0, -90, 0]) rotate([0, 0, 90]) slot_row(6, 10, 2.4, 6, wall + 2);
}

module base_vents() {
    at_pi() translate([32.5, 28, -10]) rotate([0, 0, 90]) slot_row(6, 26, 2.6, 6.5, 20);
}

// ---- parts ----------------------------------------------------------------------------
module lcd_place() { on_face(lcd_x, lcd_s) children(); }

module lcd_ghost_placed() {
    lcd_place() translate([-lcd_pcb[0] / 2, -lcd_pcb[1] / 2, -face_t - lcd_bezel[2]])
        lcd1602_ghost(lcd_header_side);
}

module shell_asm() {
    difference() {
        union() {
            difference() { shell_outer(); shell_cavity(); }
            closure_posts();
            lcd_place() clamp_bosses(lcd_pcb[0], lcd_pcb[1], lcd_clamp_depth, lcd_tabs);
            // locating ridge around the LCD bezel
            lcd_place() translate([0, 0, -face_t - 1.5]) linear_extrude(1.5 + eps)
                difference() {
                    square([lcd_bezel[0] + 0.8 + 2.4, lcd_bezel[1] + 0.8 + 2.4], center = true);
                    square([lcd_bezel[0] + 0.8, lcd_bezel[1] + 0.8], center = true);
                }
        }
        closure_holes();
        pi_port_notches();
        lcd_place() translate([-lcd_window[0] / 2, -lcd_window[1] / 2, -face_t - 1])
            linear_extrude(face_t + 2) rrect([lcd_window[0], lcd_window[1]], 1.0, $fn = 16);
        lcd_place() clamp_boss_holes(lcd_pcb[0], lcd_pcb[1], lcd_clamp_depth, lcd_tabs);
        // right wall: local x = -Z, y = Y after rotate([0, -90, 0]); print-up is (+Y, -Z)
        translate([W + 1, button_y, button_z]) rotate([0, -90, 0])
            teardrop_hole(button_hole_d, wall + 2, up = [-cos(angle), sin(angle)], clip_r = 9.4);
        shell_vents();
        // name on the face, below the LCD (engraved 0.6 mm)
        on_face(lcd_x, 6) translate([0, 0, -0.6]) linear_extrude(1)
            text("NASHVILLE NUMBERS", size = 4.2, halign = "center", valign = "center",
                 font = "Liberation Sans:style=Bold");
    }
}

module base_asm() {
    difference() {
        union() {
            base_plate_body();
            pi_standoffs();
            // locating ridge for the level shifter (foam-taped)
            translate([shifter_pos[0] - 1.6, shifter_pos[1] - 1.6, base_t - eps]) difference() {
                cube([21 + 3.2, 17 + 3.2, 1.2]);
                translate([1.2, 1.2, -1]) cube([21 + 0.8, 17 + 0.8, 3.4]);
            }
        }
        pi_standoff_holes();
        base_closure_holes();
        bumper_recesses();
        base_vents();
    }
}

module clamps_asm() {
    lcd_place() for (t = lcd_tabs) clamp_tab(lcd_pcb[0], lcd_pcb[1], lcd_clamp_depth, t);
}

// ---- ghosts (parts the case holds, and the space they need) ---------------------------
module ghost_display() { lcd_ghost_placed(); }
module ghost_controls() {
    translate([W, button_y, button_z]) rotate([0, 90, 0]) button16_ghost(wall);
    translate([shifter_pos[0], shifter_pos[1], base_t]) level_shifter_ghost();
}

module ghosts_pi(model) { at_pi() pi_ghost(model); }

// ---- print orientation ------------------------------------------------------------------
module shell_print() { face_down() shell_asm(); }
module base_print() { base_asm(); }
module clamps_print() { clamp_tabs_print(lcd_pcb[0], lcd_pcb[1], lcd_clamp_depth, lcd_tabs); }

// ---- render ----------------------------------------------------------------------------------
if (part == "shell") shell_print();
else if (part == "base") base_print();
else if (part == "clamps") clamps_print();
else if (part == "shell_asm") shell_asm();
else if (part == "base_asm") base_asm();
else if (part == "clamps_asm") clamps_asm();
else if (part == "ghosts_pi4") ghosts_pi(4);
else if (part == "ghosts_pi5") ghosts_pi(5);
else if (part == "ghost_display") ghost_display();
else if (part == "ghost_controls") ghost_controls();
else if (part == "cutaway") {
    // the shell cut at the LCD centre line, to show how everything fits
    color("SteelBlue") base_asm();
    color("DimGray") clamps_asm();
    color("ForestGreen") at_pi() pi_ghost(pi_model, plugs = false, wiring = true);
    color("MidnightBlue") lcd_ghost_placed();
    color("Gold") ghost_controls();
    color("LightSteelBlue") difference() { shell_asm(); translate([lcd_x, -1, -1]) cube([W, D + 2, 200]); }
}
else if (part == "exploded") {
    // assembly order: Pi and level shifter on the base; LCD and clamp tabs
    // into the shell; shell over the base
    color("SteelBlue") base_asm();
    color("ForestGreen") at_pi() pi_ghost(pi_model, plugs = false, wiring = false);
    color("Gold") translate([shifter_pos[0], shifter_pos[1], base_t]) level_shifter_ghost();
    translate([0, 0, 130]) {
        color("LightSteelBlue") shell_asm();
        translate([W, button_y, button_z]) rotate([0, 90, 0]) button16_visual();
        translate(-85 * face_n) color("MidnightBlue") lcd_place()
            translate([-lcd_pcb[0] / 2, -lcd_pcb[1] / 2, -face_t - lcd_bezel[2]]) lcd1602_ghost(wiring = false);
        translate(-112 * face_n) color("DimGray") clamps_asm();
    }
}
else if (part == "print_layout") {
    // every printed part in its print orientation on a (large) bed
    color("Gainsboro") translate([-15, -slope_len - 15, -1]) cube([2 * W + 45, slope_len + 60, 1 - eps]);
    color("LightSteelBlue") shell_print();
    color("SteelBlue") translate([W + 12, -slope_len, 0]) base_print();
    color("DimGray") translate([W + 22, -slope_len + D + 12, 0]) clamps_print();
}
else {
    assert(part == "assembly" || part == "interior", str("unknown part: ", part));
    color("SteelBlue") base_asm();
    color("DimGray") clamps_asm();
    color("ForestGreen") at_pi() pi_ghost(pi_model, plugs = false, wiring = false);
    color("MidnightBlue") lcd_ghost_placed();
    if (part != "interior") {
        color("LightSteelBlue") shell_asm();
        translate([W, button_y, button_z]) rotate([0, 90, 0]) button16_visual();
    }
}
