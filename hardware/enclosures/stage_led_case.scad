/*
 * Nashville Numbers - Stage LED Display Enclosure
 *
 * Floor-mountable enclosure for TM1637 or MAX7219 LED display.
 * Designed for stage use with angled viewing and sturdy construction.
 *
 * Features:
 * - 30-degree viewing angle for floor placement
 * - Large LED display window
 * - Cable management with strain relief
 * - Anti-slip rubber feet mounts
 * - Impact-resistant design
 * - Red filter insert option
 *
 * Print Settings:
 * - Layer height: 0.2mm
 * - Infill: 30% (stronger for stage use)
 * - Material: PETG (more durable than PLA)
 */

// ========================================
// CONFIGURATION
// ========================================

// Display type
display_type = "TM1637";  // "TM1637" or "MAX7219"

// What to render
render_case = true;
render_filter = false;
render_assembled = false;

// Dimensions
wall = 3;                // Thicker walls for stage use
bottom = 3;
viewing_angle = 30;      // Degrees from horizontal

// TM1637 4-digit display dimensions
tm1637_length = 42;
tm1637_width = 24;
tm1637_height = 12;
tm1637_digit_length = 30;
tm1637_digit_width = 13;
tm1637_mount_hole_spacing = 38;
tm1637_mount_hole_dia = 2.5;

// MAX7219 8-digit display dimensions
max7219_length = 128;
max7219_width = 32;
max7219_height = 12;
max7219_digit_length = 100;
max7219_digit_width = 18;

// Select dimensions based on display type
display_length = (display_type == "TM1637") ? tm1637_length : max7219_length;
display_width = (display_type == "TM1637") ? tm1637_width : max7219_width;
display_height = (display_type == "TM1637") ? tm1637_height : max7219_height;
digit_length = (display_type == "TM1637") ? tm1637_digit_length : max7219_digit_length;
digit_width = (display_type == "TM1637") ? tm1637_digit_width : max7219_digit_width;

// Case dimensions (with padding)
case_length = display_length + 20;
case_width = display_width + wall * 2 + 10;
case_height = 25;  // Front height
case_back_height = case_height + case_length * tan(viewing_angle);

// Cable management
cable_dia = 8;  // For cables with strain relief

// ========================================
// MODULES
// ========================================

module rounded_box_angled(length, width, front_height, back_height, radius) {
    hull() {
        // Front corners
        for (y = [radius, width - radius]) {
            translate([radius, y, 0])
                cylinder(h=front_height, r=radius, $fn=30);
        }
        // Back corners
        for (y = [radius, width - radius]) {
            translate([length - radius, y, 0])
                cylinder(h=back_height, r=radius, $fn=30);
        }
    }
}

module stage_case() {
    difference() {
        // Main angled enclosure
        rounded_box_angled(case_length, case_width, case_height, case_back_height, 4);

        // Hollow interior
        translate([wall, wall, bottom])
            rounded_box_angled(
                case_length - wall*2,
                case_width - wall*2,
                case_height - bottom,
                case_back_height - bottom,
                2
            );

        // Display window - angled to match case
        window_x = (case_length - digit_length) / 2;
        window_y = (case_width - digit_width) / 2;
        window_z = case_height * 0.4;  // Position on angled face

        translate([window_x - 2, window_y - 2, -0.1])
            linear_extrude(height = wall + 5)
            offset(r=2)
            square([digit_length + 4, digit_width + 4]);

        // Cable entry hole (back, bottom)
        translate([case_length - 15, case_width/2, -0.1])
            cylinder(h=bottom + 0.2, d=cable_dia, $fn=30);

        // Strain relief channel
        translate([case_length - 20, case_width/2 - cable_dia/2, bottom])
            cube([15, cable_dia, 8]);

        // Rubber feet mounting holes (bottom corners)
        feet_positions = [
            [8, 8],
            [case_length - 8, 8],
            [8, case_width - 8],
            [case_length - 8, case_width - 8]
        ];

        for (pos = feet_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=bottom + 0.2, d=3, $fn=20);
        }

        // Ventilation slots on sides
        for (i = [0:3]) {
            translate([-0.1, wall + 8 + i*8, case_height * 0.5])
                cube([wall + 0.2, 4, 6]);

            translate([case_length - wall - 0.1, wall + 8 + i*8, case_height * 0.5 + (case_length - wall) * tan(viewing_angle)])
                cube([wall + 0.2, 4, 6]);
        }
    }

    // Display mounting platform (angled)
    translate([wall + 5, wall + 3, bottom + 3]) {
        rotate([0, viewing_angle, 0]) {
            difference() {
                // Platform
                cube([display_length + 5, display_width + 4, 3]);

                // Wire pass-through holes
                if (display_type == "TM1637") {
                    translate([display_length/2, display_width/2, -0.1])
                        cylinder(h=3.2, d=6, $fn=20);
                }
            }

            // Mounting posts for display
            mount_positions = (display_type == "TM1637") ? [
                [3, 3],
                [display_length - 3, 3],
                [3, display_width - 3],
                [display_length - 3, display_width - 3]
            ] : [
                [5, 5],
                [display_length - 5, 5],
                [5, display_width - 5],
                [display_length - 5, display_width - 5]
            ];

            for (pos = mount_positions) {
                difference() {
                    translate([pos[0], pos[1], 3])
                        cylinder(h=4, d=5, $fn=20);
                    translate([pos[0], pos[1], 2.9])
                        cylinder(h=4.2, d=2.2, $fn=15);
                }
            }
        }
    }

    // Cable tie down points
    translate([case_length - 25, wall + 3, bottom + 1]) {
        difference() {
            cube([4, 8, 4]);
            translate([2, 4, -0.1])
                cylinder(h=6, d=3, $fn=20);
        }
    }
}

module red_filter() {
    // Optional red acrylic filter insert
    // Cut from 2mm red transparent acrylic
    difference() {
        offset(r=1)
            square([digit_length + 4, digit_width + 4]);

        // Corner mounting holes
        positions = [
            [2, 2],
            [digit_length + 2, 2],
            [2, digit_width + 2],
            [digit_length + 2, digit_width + 2]
        ];

        for (pos = positions) {
            translate([pos[0], pos[1]])
                circle(d=2.5, $fn=20);
        }
    }
}

module rubber_foot() {
    // Template for rubber feet (use adhesive rubber pads)
    // Or print in TPU
    difference() {
        cylinder(h=4, d=8, $fn=30);
        translate([0, 0, 2])
            cylinder(h=2.2, d=3.2, $fn=20);  // Screw hole
    }
}

// ========================================
// RENDERING
// ========================================

if (render_assembled) {
    // Show assembled view
    color("darkred")
        stage_case();

    // Show display outline
    color("black", 0.3)
        translate([wall + 8, wall + 5, bottom + 6])
        rotate([0, viewing_angle, 0])
        cube([display_length, display_width, display_height]);

    // Show filter
    if (render_filter) {
        color("red", 0.5)
            translate([
                (case_length - digit_length - 4) / 2,
                (case_width - digit_width - 4) / 2,
                case_height * 0.4
            ])
            linear_extrude(height=2)
            red_filter();
    }

} else {
    // Print layout
    if (render_case) {
        stage_case();
    }

    if (render_filter) {
        translate([case_length + 10, 0, 0])
            linear_extrude(height=0.2)  // Just the outline
            red_filter();
    }

    // Rubber feet (if printing in TPU)
    translate([case_length + 20, case_width/2, 0]) {
        for (i = [0:3]) {
            translate([i*12, 0, 0])
                rubber_foot();
        }
    }
}

// ========================================
// NOTES
// ========================================

/*
ASSEMBLY INSTRUCTIONS:

1. Print the case in PETG for durability
2. Print rubber feet in TPU, or use adhesive rubber pads

3. Mount LED display:
   - Place display on angled platform
   - Use M2.5 x 8mm screws through mounting posts
   - Route wires through platform hole

4. Cable management:
   - Feed cable through back hole
   - Use zip tie at tie-down point for strain relief

5. Install rubber feet:
   - Screw or adhesive mount to bottom corners
   - Ensures non-slip on stage floor

6. Optional red filter:
   - Cut 2mm red acrylic sheet using the filter template
   - Glue into display window from inside
   - Enhances LED visibility and aesthetics

PLACEMENT ON STAGE:
- Position on floor in your line of sight
- 30° angle optimized for viewing from standing position
- Cable runs to Raspberry Pi (can be 2+ meters away)
- Consider gaffer tape to secure cable to floor
*/
