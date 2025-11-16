/*
 * Nashville Numbers - Raspberry Pi + LCD Display Enclosure
 *
 * Complete enclosure for Raspberry Pi (3B+/4) with 16x2 LCD display
 * mounted on top. Perfect for desktop/practice room use.
 *
 * Features:
 * - Mounts for Raspberry Pi with standoffs
 * - Top-mounted LCD display window
 * - Ventilation holes for cooling
 * - Access to all Pi ports
 * - Cable management channels
 * - Two-part design (base + lid)
 *
 * Print Settings:
 * - Layer height: 0.2mm
 * - Infill: 20%
 * - Supports: Only for lid
 * - Material: PLA or PETG
 */

// ========================================
// CONFIGURATION
// ========================================

// What to render
render_base = true;      // Base with Pi mounts
render_lid = true;       // Lid with LCD window
render_assembled = false; // Show assembly view

// Dimensions
wall = 2;                // Wall thickness
bottom = 2;              // Bottom thickness
top = 2;                 // Top thickness

// Raspberry Pi 3/4 dimensions
pi_length = 85;
pi_width = 56;
pi_height = 18;          // With components
pi_hole_spacing_length = 58;
pi_hole_spacing_width = 49;
pi_hole_offset_x = 3.5;
pi_hole_offset_y = 3.5;
pi_hole_dia = 2.75;      // M2.5 mounting holes
pi_standoff_height = 4;

// LCD 16x2 dimensions (with I2C backpack)
lcd_length = 80;
lcd_width = 36;
lcd_pcb_thickness = 1.6;
lcd_screen_length = 64;
lcd_screen_width = 16;
lcd_screen_offset_x = (lcd_length - lcd_screen_length) / 2;
lcd_screen_offset_y = 10;  // From bottom of LCD
lcd_mount_hole_spacing_length = 75;
lcd_mount_hole_spacing_width = 31;
lcd_mount_hole_dia = 2.5; // M2.5

// Case dimensions
case_length = pi_length + wall * 2 + 10;  // Extra space for cables
case_width = pi_width + wall * 2 + 6;
case_height = pi_height + pi_standoff_height + bottom + 2;
lid_height = lcd_pcb_thickness + top + 8;  // Room for LCD components

// Ventilation
vent_hole_dia = 3;
vent_spacing = 5;

// ========================================
// MODULES
// ========================================

module rounded_box(length, width, height, radius) {
    hull() {
        for (x = [radius, length - radius]) {
            for (y = [radius, width - radius]) {
                translate([x, y, 0])
                    cylinder(h=height, r=radius, $fn=30);
            }
        }
    }
}

module pi_mounting_holes(height) {
    // Raspberry Pi mounting hole pattern
    hole_positions = [
        [pi_hole_offset_x, pi_hole_offset_y],
        [pi_hole_offset_x + pi_hole_spacing_length, pi_hole_offset_y],
        [pi_hole_offset_x, pi_hole_offset_y + pi_hole_spacing_width],
        [pi_hole_offset_x + pi_hole_spacing_length, pi_hole_offset_y + pi_hole_spacing_width]
    ];

    for (pos = hole_positions) {
        translate([pos[0], pos[1], 0])
            cylinder(h=height, d=pi_hole_dia, $fn=20);
    }
}

module pi_standoffs(height) {
    hole_positions = [
        [pi_hole_offset_x, pi_hole_offset_y],
        [pi_hole_offset_x + pi_hole_spacing_length, pi_hole_offset_y],
        [pi_hole_offset_x, pi_hole_offset_y + pi_hole_spacing_width],
        [pi_hole_offset_x + pi_hole_spacing_length, pi_hole_offset_y + pi_hole_spacing_width]
    ];

    for (pos = hole_positions) {
        difference() {
            translate([pos[0], pos[1], 0])
                cylinder(h=height, d=6, $fn=20);
            translate([pos[0], pos[1], -0.1])
                cylinder(h=height + 0.2, d=pi_hole_dia, $fn=20);
        }
    }
}

module ventilation_grid(rows, cols, hole_dia, spacing) {
    for (i = [0:rows-1]) {
        for (j = [0:cols-1]) {
            translate([j * spacing, i * spacing, -0.1])
                cylinder(h=wall + 0.2, d=hole_dia, $fn=15);
        }
    }
}

module base() {
    difference() {
        // Main box
        rounded_box(case_length, case_width, case_height, 3);

        // Hollow interior
        translate([wall, wall, bottom])
            rounded_box(case_length - wall*2, case_width - wall*2, case_height, 2);

        // USB ports cutout (Raspberry Pi side)
        translate([wall + 7, -0.1, bottom + pi_standoff_height + 2])
            cube([60, wall + 0.2, 16]);

        // HDMI/Power/Audio cutout (opposite side)
        translate([wall + 20, case_width - wall - 0.1, bottom + pi_standoff_height + 2])
            cube([55, wall + 0.2, 14]);

        // SD card slot (bottom end)
        translate([-0.1, wall + 15, bottom + pi_standoff_height + 2])
            cube([wall + 0.2, 20, 4]);

        // Ethernet port (if using Pi with ethernet)
        translate([wall + 70, -0.1, bottom + pi_standoff_height + 2])
            cube([18, wall + 0.2, 14]);

        // Ventilation holes on sides
        translate([wall + 10, wall, bottom + pi_standoff_height])
            rotate([90, 0, 0])
            ventilation_grid(3, 12, vent_hole_dia, vent_spacing);

        translate([wall + 10, case_width - wall, bottom + pi_standoff_height])
            rotate([90, 0, 0])
            ventilation_grid(3, 12, vent_hole_dia, vent_spacing);

        // Cable management channel
        translate([case_length - wall - 8, wall + case_width/2 - 5, bottom])
            cube([10, 10, pi_standoff_height]);
    }

    // Raspberry Pi standoffs
    translate([wall + 5, wall + 3, bottom])
        pi_standoffs(pi_standoff_height);

    // Lid mounting posts
    post_height = case_height - bottom - 2;
    post_positions = [
        [wall + 3, wall + 3],
        [case_length - wall - 3, wall + 3],
        [wall + 3, case_width - wall - 3],
        [case_length - wall - 3, case_width - wall - 3]
    ];

    for (pos = post_positions) {
        difference() {
            translate([pos[0], pos[1], bottom])
                cylinder(h=post_height, d=6, $fn=20);
            translate([pos[0], pos[1], post_height - 8])
                cylinder(h=10, d=2.2, $fn=15);  // M2 screw hole
        }
    }
}

module lid() {
    difference() {
        union() {
            // Main lid
            rounded_box(case_length, case_width, lid_height, 3);

            // Lip to fit into base
            translate([wall, wall, -2])
                rounded_box(case_length - wall*2 - 0.5, case_width - wall*2 - 0.5, 2.1, 2);
        }

        // Hollow interior
        translate([wall, wall, bottom])
            rounded_box(case_length - wall*2, case_width - wall*2, lid_height, 2);

        // LCD screen window
        lcd_x = (case_length - lcd_screen_length) / 2;
        lcd_y = (case_width - lcd_screen_width) / 2 + 2;
        translate([lcd_x - 1, lcd_y - 1, -0.1])
            cube([lcd_screen_length + 2, lcd_screen_width + 2, top + 0.2]);

        // LCD mounting holes
        lcd_mount_x = (case_length - lcd_mount_hole_spacing_length) / 2;
        lcd_mount_y = (case_width - lcd_mount_hole_spacing_width) / 2;

        mount_positions = [
            [lcd_mount_x, lcd_mount_y],
            [lcd_mount_x + lcd_mount_hole_spacing_length, lcd_mount_y],
            [lcd_mount_x, lcd_mount_y + lcd_mount_hole_spacing_width],
            [lcd_mount_x + lcd_mount_hole_spacing_length, lcd_mount_y + lcd_mount_hole_spacing_width]
        ];

        for (pos = mount_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=top + 0.2, d=lcd_mount_hole_dia, $fn=20);
        }

        // Screw holes for lid attachment
        post_positions = [
            [wall + 3, wall + 3],
            [case_length - wall - 3, wall + 3],
            [wall + 3, case_width - wall - 3],
            [case_length - wall - 3, case_width - wall - 3]
        ];

        for (pos = post_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=lid_height + 0.2, d=2.4, $fn=15);  // M2 clearance hole
        }

        // Ventilation slots on top
        for (i = [0:6]) {
            translate([case_length/2 - 30 + i*10, case_width - 8, -0.1])
                cube([2, 5, top + 0.2]);
        }
    }

    // LCD mounting standoffs (printed upside down)
    lcd_mount_x = (case_length - lcd_mount_hole_spacing_length) / 2;
    lcd_mount_y = (case_width - lcd_mount_hole_spacing_width) / 2;

    mount_positions = [
        [lcd_mount_x, lcd_mount_y],
        [lcd_mount_x + lcd_mount_hole_spacing_length, lcd_mount_y],
        [lcd_mount_x, lcd_mount_y + lcd_mount_hole_spacing_width],
        [lcd_mount_x + lcd_mount_hole_spacing_length, lcd_mount_y + lcd_mount_hole_spacing_width]
    ];

    for (pos = mount_positions) {
        difference() {
            translate([pos[0], pos[1], top])
                cylinder(h=4, d=5, $fn=20);
            translate([pos[0], pos[1], top - 0.1])
                cylinder(h=4.2, d=lcd_mount_hole_dia, $fn=20);
        }
    }
}

// ========================================
// RENDERING
// ========================================

if (render_assembled) {
    // Show assembled view
    color("lightblue")
        base();

    color("lightgreen", 0.7)
        translate([0, 0, case_height - 0.1])
        lid();

    // Show Raspberry Pi outline
    color("green", 0.3)
        translate([wall + 5, wall + 3, bottom + pi_standoff_height])
        cube([pi_length, pi_width, pi_height]);

    // Show LCD outline
    color("blue", 0.3)
        translate([(case_length - lcd_length)/2, (case_width - lcd_width)/2, case_height + top])
        cube([lcd_length, lcd_width, lcd_pcb_thickness]);

} else {
    // Print layout
    if (render_base) {
        base();
    }

    if (render_lid) {
        translate([case_length + 10, 0, lid_height])
            rotate([180, 0, 0])
            lid();
    }
}
