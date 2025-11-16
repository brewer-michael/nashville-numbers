/*
 * Nashville Numbers - Compact All-in-One Enclosure
 *
 * Compact vertical enclosure with Raspberry Pi inside and
 * TM1637 LED display on the front face. Perfect for minimalist
 * desktop setup or pedalboard mounting.
 *
 * Features:
 * - Vertical orientation saves desk space
 * - Front-facing LED display
 * - Side access to Pi ports
 * - Passive cooling with chimney effect
 * - VESA mount compatible (75mm)
 * - Optional pedalboard velcro strips
 *
 * Print Settings:
 * - Layer height: 0.2mm
 * - Infill: 25%
 * - Material: PLA or PETG
 */

// ========================================
// CONFIGURATION
// ========================================

// What to render
render_body = true;
render_front_panel = true;
render_back_panel = false;
render_assembled = false;

// Dimensions
wall = 2.5;
corner_radius = 3;

// Raspberry Pi dimensions
pi_length = 85;
pi_width = 56;
pi_height = 18;
pi_standoff = 4;

// TM1637 display
display_length = 42;
display_width = 24;
digit_length = 30;
digit_width = 13;

// Case dimensions - vertical orientation
case_width = pi_length + wall * 2 + 4;   // 93mm
case_depth = pi_width + wall * 2 + 4;    // 64mm
case_height = 80;                         // Tall enough for Pi + clearance

// Panel dimensions
panel_thickness = 2;
panel_lip = 1.5;

// ========================================
// MODULES
// ========================================

module rounded_cube(x, y, z, r) {
    hull() {
        for (ix = [r, x-r]) {
            for (iy = [r, y-r]) {
                translate([ix, iy, 0])
                    cylinder(h=z, r=r, $fn=30);
            }
        }
    }
}

module body() {
    difference() {
        // Main body
        rounded_cube(case_width, case_depth, case_height, corner_radius);

        // Hollow interior
        translate([wall, wall, wall])
            rounded_cube(
                case_width - wall*2,
                case_depth - wall*2,
                case_height,
                corner_radius - wall
            );

        // Front panel recess
        translate([-0.1, -0.1, -0.1])
            rounded_cube(
                case_width + 0.2,
                panel_thickness + panel_lip + 0.1,
                case_height + 0.2,
                corner_radius
            );

        // Back panel recess
        translate([-0.1, case_depth - panel_thickness - panel_lip, -0.1])
            rounded_cube(
                case_width + 0.2,
                panel_thickness + panel_lip + 0.2,
                case_height + 0.2,
                corner_radius
            );

        // USB ports access (right side when facing front)
        translate([case_width - wall - 0.1, case_depth/2 - 30, 25])
            cube([wall + 0.2, 60, 18]);

        // HDMI/Power access (left side)
        translate([-0.1, case_depth/2 - 25, 25])
            cube([wall + 0.2, 50, 16]);

        // Top ventilation slots (chimney effect)
        for (i = [0:8]) {
            translate([wall + 10 + i*8, wall + 5, case_height - wall - 0.1])
                cube([3, case_depth - wall*2 - 10, wall + 0.2]);
        }

        // Bottom ventilation (intake)
        vent_grid_x = 6;
        vent_grid_y = 5;
        for (i = [0:vent_grid_x-1]) {
            for (j = [0:vent_grid_y-1]) {
                translate([
                    wall + 8 + i*10,
                    wall + 8 + j*8,
                    -0.1
                ])
                    cylinder(h=wall + 0.2, d=4, $fn=20);
            }
        }

        // Cable exit hole (bottom rear)
        translate([case_width/2, case_depth - wall - 8, -0.1])
            cylinder(h=wall + 0.2, d=10, $fn=30);
    }

    // Raspberry Pi mounting pillars (vertical orientation)
    pi_x_offset = (case_width - pi_length) / 2;
    pi_z_offset = 15;  // Height from bottom

    // Pi is mounted vertically on the back wall
    pi_holes = [
        [3.5, 3.5],
        [3.5 + 58, 3.5],
        [3.5, 3.5 + 49],
        [3.5 + 58, 3.5 + 49]
    ];

    translate([pi_x_offset, case_depth - wall - panel_thickness - panel_lip - 3, pi_z_offset]) {
        for (hole = pi_holes) {
            difference() {
                translate([hole[0], 0, hole[1]])
                    rotate([90, 0, 0])
                    cylinder(h=pi_standoff, d=6, $fn=20);

                translate([hole[0], 1, hole[1]])
                    rotate([90, 0, 0])
                    cylinder(h=pi_standoff + 2, d=2.75, $fn=15);
            }
        }
    }

    // Front panel clips
    clip_positions = [
        [wall + 5, panel_thickness + panel_lip - 0.3, case_height/2 - 10],
        [case_width - wall - 5, panel_thickness + panel_lip - 0.3, case_height/2 - 10],
        [wall + 5, panel_thickness + panel_lip - 0.3, case_height/2 + 10],
        [case_width - wall - 5, panel_thickness + panel_lip - 0.3, case_height/2 + 10]
    ];

    for (pos = clip_positions) {
        translate([pos[0], pos[1], pos[2]])
            rotate([90, 0, 0])
            difference() {
                cylinder(h=1.5, d=4, $fn=20);
                translate([0, 0, -0.1])
                    cylinder(h=1.7, d=2.2, $fn=15);
            }
    }

    // Back panel screw posts
    post_positions = [
        [wall + 5, case_depth - panel_thickness - panel_lip - 3, wall + 5],
        [case_width - wall - 5, case_depth - panel_thickness - panel_lip - 3, wall + 5],
        [wall + 5, case_depth - panel_thickness - panel_lip - 3, case_height - wall - 5],
        [case_width - wall - 5, case_depth - panel_thickness - panel_lip - 3, case_height - wall - 5]
    ];

    for (pos = post_positions) {
        difference() {
            translate([pos[0], pos[1], pos[2]])
                rotate([90, 0, 0])
                cylinder(h=3, d=6, $fn=20);

            translate([pos[0], pos[1] + 0.1, pos[2]])
                rotate([90, 0, 0])
                cylinder(h=3.2, d=2.2, $fn=15);
        }
    }
}

module front_panel() {
    difference() {
        // Main panel
        union() {
            // Panel face
            rounded_cube(case_width, panel_thickness, case_height, corner_radius);

            // Lip that fits into body
            translate([wall, panel_thickness, wall])
                rounded_cube(
                    case_width - wall*2 - 0.3,
                    panel_lip - 0.15,
                    case_height - wall*2 - 0.3,
                    corner_radius - wall
                );
        }

        // LED display window
        display_x = (case_width - digit_length) / 2;
        display_y = case_height / 2 - digit_width / 2;

        translate([display_x - 2, -0.1, display_y - 2])
            cube([digit_length + 4, panel_thickness + 0.2, digit_width + 4]);

        // LED module mounting holes
        led_mount_x = (case_width - display_length) / 2;
        led_mount_y = case_height / 2 - display_width / 2;

        led_holes = [
            [led_mount_x + 3, led_mount_y + 3],
            [led_mount_x + display_length - 3, led_mount_y + 3],
            [led_mount_x + 3, led_mount_y + display_width - 3],
            [led_mount_x + display_length - 3, led_mount_y + display_width - 3]
        ];

        for (hole = led_holes) {
            translate([hole[0], -0.1, hole[1]])
                rotate([-90, 0, 0])
                cylinder(h=panel_thickness + 0.2, d=2.5, $fn=20);
        }

        // Panel clip holes
        clip_positions = [
            [wall + 5, case_height/2 - 10],
            [case_width - wall - 5, case_height/2 - 10],
            [wall + 5, case_height/2 + 10],
            [case_width - wall - 5, case_height/2 + 10]
        ];

        for (pos = clip_positions) {
            translate([pos[0], panel_thickness + panel_lip - 0.5, pos[1]])
                rotate([90, 0, 0])
                cylinder(h=panel_lip, d=2.4, $fn=15);
        }

        // Branding text (optional)
        translate([case_width/2, panel_thickness - 0.5, case_height - 8])
            rotate([90, 0, 0])
            linear_extrude(height=0.6)
            text("NASHVILLE", size=4, halign="center", font="Arial:style=Bold");
    }

    // LED standoffs (on back of panel)
    led_mount_x = (case_width - display_length) / 2;
    led_mount_y = case_height / 2 - display_width / 2;

    led_holes = [
        [led_mount_x + 3, led_mount_y + 3],
        [led_mount_x + display_length - 3, led_mount_y + 3],
        [led_mount_x + 3, led_mount_y + display_width - 3],
        [led_mount_x + display_length - 3, led_mount_y + display_width - 3]
    ];

    for (hole = led_holes) {
        difference() {
            translate([hole[0], panel_thickness, hole[1]])
                rotate([-90, 0, 0])
                cylinder(h=5, d=5, $fn=20);

            translate([hole[0], panel_thickness - 0.1, hole[1]])
                rotate([-90, 0, 0])
                cylinder(h=5.2, d=2.5, $fn=20);
        }
    }
}

module back_panel() {
    difference() {
        union() {
            // Panel face
            rounded_cube(case_width, panel_thickness, case_height, corner_radius);

            // Lip
            translate([wall, 0, wall])
                rounded_cube(
                    case_width - wall*2 - 0.3,
                    panel_lip - 0.15,
                    case_height - wall*2 - 0.3,
                    corner_radius - wall
                );
        }

        // Screw holes
        post_positions = [
            [wall + 5, wall + 5],
            [case_width - wall - 5, wall + 5],
            [wall + 5, case_height - wall - 5],
            [case_width - wall - 5, case_height - wall - 5]
        ];

        for (pos = post_positions) {
            translate([pos[0], -0.1, pos[1]])
                rotate([-90, 0, 0])
                cylinder(h=panel_thickness + 0.2, d=2.4, $fn=15);
        }

        // Ventilation holes
        for (i = [0:6]) {
            for (j = [0:8]) {
                translate([wall + 10 + i*10, -0.1, wall + 10 + j*7])
                    rotate([-90, 0, 0])
                    cylinder(h=panel_thickness + 0.2, d=3, $fn=15);
            }
        }
    }
}

// ========================================
// RENDERING
// ========================================

if (render_assembled) {
    color("lightblue")
        body();

    color("white", 0.9)
        front_panel();

    color("gray", 0.7)
        translate([0, case_depth - panel_thickness, 0])
        rotate([0, 0, 0])
        back_panel();

    // Show Pi outline (vertical mount)
    color("green", 0.3)
        translate([
            (case_width - pi_length)/2,
            case_depth - wall - panel_thickness - panel_lip - 3 - pi_standoff - pi_height,
            15
        ])
        cube([pi_length, pi_height, pi_width]);

} else {
    // Print layout
    if (render_body) {
        body();
    }

    if (render_front_panel) {
        translate([case_width + 10, 0, 0])
            front_panel();
    }

    if (render_back_panel) {
        translate([case_width + 10, panel_thickness + 5, 0])
            back_panel();
    }
}

// ========================================
// NOTES
// ========================================

/*
ASSEMBLY NOTES:

1. Pi Mounting (Vertical):
   - Pi mounts vertically on back wall
   - USB ports face right side
   - HDMI/Power face left side
   - Use M2.5 x 10mm screws

2. LED Display:
   - Mounts on inside of front panel
   - Use M2.5 x 8mm screws with standoffs
   - Digits visible through window

3. Cooling:
   - Bottom holes intake cool air
   - Top slots exhaust (chimney effect)
   - Passive cooling sufficient for normal use

4. Mounting Options:
   - VESA 75mm pattern on back (drill holes)
   - Adhesive velcro for pedalboard
   - Rubber feet for desktop

DIMENSIONS:
- Width: 93mm (3.66")
- Depth: 64mm (2.52")
- Height: 80mm (3.15")
- Compact enough for pedalboard or desk
*/
