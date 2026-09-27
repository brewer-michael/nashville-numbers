// Nashville Numbers - stage floor wedge
//
// Raspberry Pi 5 or 4 + 7-segment display behind a red acrylic filter +
// 16 mm push button + 1/4" footswitch jack, in a floor wedge you read from
// standing height.
//
// display = "ht16k33_12"  Adafruit 1.2" 4-digit, HT16K33 backpack (stage build)
//           "tm1637_056"  0.56" TM1637 module (budget build)
//           "tm1637_036"  0.36" TM1637 module
//
// Printed parts (all without supports, PETG recommended):
//   shell     face-down (display face on the bed)
//   base      flat, bumper/hook-and-loop recesses down
//   clamps    display clamp tabs, flat
// Laser-cut or hand-cut: filter (2 mm red transparent acrylic), see cut/.
//
// `part` selects what to render; tools/build.py renders every part.

include <lib/wedge.scad>

part = "assembly";  // assembly | cutaway | exploded | print_layout
                    // | shell | base | clamps | filter
                    // | shell_asm | base_asm | clamps_asm | filter_asm
                    // | ghosts_pi4 | ghosts_pi5 | ghost_display | ghost_controls
display = "ht16k33_12";

// ---- enclosure parameters -----------------------------------------------------
W = 142;
D = 108;
H = 42;
angle = 25;
wall = 3.0;
face_t = 4.0;
base_t = 3.0;
corner_r = 5;
post_d = 10;

// ---- display ----------------------------------------------------------------------
dd = sevenseg_dims(display);          // [w, h, depth, window w, window h, wiring]
disp_x = W / 2;
disp_s = 34;                          // centre up the slope from the front edge
filter_t = 2.0;                       // red acrylic
filter_pocket = 2.0;                  // pocket depth = filter thickness (glue or tape it in)
filter_margin = 3.0;                  // filter overlap around the window
filter_size = [dd[3] + 2 * filter_margin, dd[4] + 2 * filter_margin];
disp_clamp_depth = dd[2];             // face underside to the module back
// tabs press the long edges (TM1637 headers may exit left or right, and the
// 1.2" module nearly fills the width)
disp_tabs = display == "ht16k33_12"
    ? [["top", -35], ["top", 35], ["bottom", -35], ["bottom", 35]]
    : [["top", 0], ["bottom", 0]];

// ---- controls ----------------------------------------------------------------------
jack_x = 88;       // on the back wall, right of the Pi port notch
jack_z = 45;
button_x = 120;    // on the face, near the back-right corner
button_s = 82;

module disp_place() { on_face(disp_x, disp_s) children(); }

module ghost_display() {
    disp_place() translate([-dd[0] / 2, -dd[1] / 2, -face_t]) sevenseg_ghost(display);
    if (display != "ht16k33_12") disp_place()      // sideways header wiring on either end
        for (sx = [-1, 1]) translate([sx > 0 ? dd[0] / 2 : -dd[0] / 2 - 22, -dd[1] / 2, -face_t - dd[2]])
            cube([22, dd[1], dd[2]]);
}

module ghost_controls() {
    translate([jack_x, D, jack_z]) rotate([-90, 0, 0]) jack_ts_ghost(wall);
    on_face(button_x, button_s) button16_ghost(face_t);
}

// ---- parts ------------------------------------------------------------------------------
module shell_vents() {
    // exhaust above the Pi, intake low on the front and right walls
    on_face(40, 90) translate([0, 0, -face_t - 1]) rotate([0, 0, 90]) slot_row(3, 50, 2.4, 6, face_t + 2);
    translate([W / 2, -1, 12]) rotate([-90, 0, 0]) slot_row(14, 10, 2.4, 6, wall + 2);
    translate([W + 1, 60, 12]) rotate([0, -90, 0]) rotate([0, 0, 90]) slot_row(8, 10, 2.4, 6, wall + 2);
}

module shell_asm() {
    difference() {
        union() {
            difference() { shell_outer(); shell_cavity(); }
            closure_posts();
            disp_place() clamp_bosses(dd[0], dd[1], disp_clamp_depth, disp_tabs);
            // stiffening rib across the back of the face, above the display,
            // stopping short of the button's nut
            disp_place() translate([-dd[0] / 2, dd[1] / 2 + 12, -face_t - 4])
                cube([button_x - disp_x + dd[0] / 2 - button_nut_d / 2 - 2, 2.4, 4 + eps]);
        }
        closure_holes();
        pi_port_notches();
        // display window and the filter pocket behind it
        disp_place() translate([-dd[3] / 2, -dd[4] / 2, -face_t - 1])
            linear_extrude(face_t + 2) rrect([dd[3], dd[4]], 1.5, $fn = 16);
        disp_place() translate([-filter_size[0] / 2 - tol, -filter_size[1] / 2 - tol, -face_t - 1])
            cube([filter_size[0] + 2 * tol, filter_size[1] + 2 * tol, filter_pocket + 1]);
        disp_place() clamp_boss_holes(dd[0], dd[1], disp_clamp_depth, disp_tabs);
        // back wall: footswitch jack. After rotate([90, 0, 0]) local x = X and
        // local y = Z; printed face-down, "up" along the back wall is towards
        // the rim (case -Z), so the teardrop points down.
        translate([jack_x, D + 1, jack_z]) rotate([90, 0, 0])
            teardrop_hole(jack_hole_d, wall + 2, up = [0, -1], clip_r = 5.6);
        // face: panel button
        on_face(button_x, button_s) translate([0, 0, -face_t - 1]) cylinder(d = button_hole_d, h = face_t + 2);
        shell_vents();
        on_face(disp_x, 7) translate([0, 0, -0.6]) linear_extrude(1)
            text("NASHVILLE NUMBERS", size = 4.6, halign = "center", valign = "center",
                 font = "Liberation Sans:style=Bold");
    }
}

module base_asm() {
    difference() {
        union() {
            base_plate_body();
            pi_standoffs();
        }
        pi_standoff_holes();
        base_closure_holes();
        bumper_recesses(18);
        // hook-and-loop / Dual Lock recesses for pedalboards
        for (x = [W / 2 - 38, W / 2 + 38]) translate([x - 12.5, D / 2 - 30, -eps]) cube([25, 60, 0.8 + eps]);
        at_pi() translate([32.5, 28, -10]) rotate([0, 0, 90]) slot_row(6, 26, 2.6, 6.5, 20);
    }
}

module clamps_asm() { disp_place() for (t = disp_tabs) clamp_tab(dd[0], dd[1], disp_clamp_depth, t); }

module filter_2d() { rrect(filter_size, 1.0, $fn = 16); }
module filter_asm() {
    disp_place() translate([-filter_size[0] / 2, -filter_size[1] / 2, -face_t - (filter_t - filter_pocket)])
        linear_extrude(filter_t) filter_2d();
}

module controls_visual() {
    on_face(button_x, button_s) button16_visual();
    translate([jack_x, D, jack_z]) rotate([-90, 0, 0]) jack_visual();
}

module display_module() {
    disp_place() translate([-dd[0] / 2, -dd[1] / 2, -face_t]) sevenseg_ghost(display, false);
}

// ---- render -----------------------------------------------------------------------------------
if (part == "shell") face_down() shell_asm();
else if (part == "base") base_asm();
else if (part == "clamps") clamp_tabs_print(dd[0], dd[1], disp_clamp_depth, disp_tabs);
else if (part == "filter") filter_2d();
else if (part == "shell_asm") shell_asm();
else if (part == "base_asm") base_asm();
else if (part == "clamps_asm") clamps_asm();
else if (part == "filter_asm") filter_asm();
else if (part == "ghosts_pi4") at_pi() pi_ghost(4);
else if (part == "ghosts_pi5") at_pi() pi_ghost(5);
else if (part == "ghost_display") ghost_display();
else if (part == "ghost_controls") ghost_controls();
else if (part == "exploded") {
    // assembly order: Pi on the base; filter, display and clamp tabs into
    // the shell; shell over the base
    color("SteelBlue") base_asm();
    color("ForestGreen") at_pi() pi_ghost(pi_model, plugs = false, wiring = false);
    translate([0, 0, 160]) {
        color("DarkSlateGray") shell_asm();
        controls_visual();
        translate(-75 * face_n) color("Red", 0.8) filter_asm();
        translate(-95 * face_n) color("Black") display_module();
        translate(-125 * face_n) color("DimGray") clamps_asm();
    }
}
else if (part == "print_layout") {
    // every printed part in its print orientation on a (large) bed
    color("Gainsboro") translate([-15, -slope_len - 15, -1]) cube([2 * W + 45, slope_len + 60, 1 - eps]);
    color("DarkSlateGray") face_down() shell_asm();
    color("SteelBlue") translate([W + 12, -slope_len, 0]) base_asm();
    color("DimGray") translate([W + 22, -slope_len + D + 12, 0])
        clamp_tabs_print(dd[0], dd[1], disp_clamp_depth, disp_tabs);
}
else {
    assert(part == "assembly" || part == "cutaway", str("unknown part: ", part));
    color("SteelBlue") base_asm();
    color("DimGray") clamps_asm();
    color("Red", 0.8) filter_asm();
    color("ForestGreen") at_pi() pi_ghost(pi_model, plugs = false, wiring = part == "cutaway");
    color("Black") display_module();
    if (part == "cutaway") {
        color("Gold") ghost_controls();
        color("DarkSlateGray") difference() { shell_asm(); translate([disp_x, -1, -1]) cube([W, D + 2, 200]); }
    } else {
        color("DarkSlateGray") shell_asm();
        controls_visual();
    }
}
