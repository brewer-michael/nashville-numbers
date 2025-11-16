/*
 * Nashville Numbers - Mounting Accessories
 *
 * Collection of useful mounting accessories for various setups:
 * - Microphone stand mount
 * - Desktop stand/riser
 * - Cable clips and organizers
 * - VESA adapter plate
 * - Pedalboard mount
 *
 * Print Settings:
 * - Layer height: 0.2mm
 * - Infill: 30%
 * - Material: PLA or PETG
 */

// ========================================
// CONFIGURATION
// ========================================

// What to render
render_mic_stand_mount = false;
render_desktop_stand = false;
render_cable_clips = false;
render_vesa_adapter = false;
render_pedalboard_mount = true;

// ========================================
// MICROPHONE STAND MOUNT
// ========================================

module mic_stand_mount() {
    /*
    Mounts Nashville Numbers case to microphone stand.
    Fits standard 5/8" mic stand threads.
    */

    stand_diameter = 25;  // For 5/8" thread insert
    clamp_width = 100;    // Width to clamp case
    clamp_depth = 65;     // Depth to clamp case
    wall = 3;

    difference() {
        union() {
            // Base plate
            translate([-clamp_width/2, -clamp_depth/2, 0])
                cube([clamp_width, clamp_depth, wall]);

            // Stand tube mount
            cylinder(h=30, d=stand_diameter + wall*2, $fn=50);

            // Reinforcement ribs
            for (angle = [0:90:270]) {
                rotate([0, 0, angle])
                    translate([-2, 0, 0])
                    linear_extrude(height=wall)
                    polygon([
                        [0, 0],
                        [4, 0],
                        [4, 30],
                        [0, 25]
                    ]);
            }
        }

        // Stand thread hole (for 5/8" thread insert)
        translate([0, 0, -0.1])
            cylinder(h=32, d=stand_diameter, $fn=50);

        // Case mounting screw holes (M4)
        mount_positions = [
            [-clamp_width/2 + 10, -clamp_depth/2 + 10],
            [clamp_width/2 - 10, -clamp_depth/2 + 10],
            [-clamp_width/2 + 10, clamp_depth/2 - 10],
            [clamp_width/2 - 10, clamp_depth/2 - 10]
        ];

        for (pos = mount_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=wall + 0.2, d=4.5, $fn=20);
            translate([pos[0], pos[1], wall - 1.5])
                cylinder(h=2, d=8, $fn=6);  // Hex countersink
        }
    }
}

// ========================================
// DESKTOP STAND
// ========================================

module desktop_stand() {
    /*
    Angled desktop stand for optimal viewing.
    15-degree angle, anti-slip pads.
    */

    stand_width = 100;
    stand_depth = 80;
    stand_height_front = 15;
    stand_height_back = 35;
    wall = 3;

    difference() {
        union() {
            // Angled platform
            hull() {
                // Front edge
                translate([0, 0, 0])
                    cube([stand_width, wall, stand_height_front]);

                // Back edge
                translate([0, stand_depth - wall, 0])
                    cube([stand_width, wall, stand_height_back]);

                // Bottom
                translate([0, 0, 0])
                    cube([stand_width, stand_depth, wall]);
            }

            // Side walls for stability
            translate([0, 0, 0])
                cube([wall, stand_depth, stand_height_back]);

            translate([stand_width - wall, 0, 0])
                cube([wall, stand_depth, stand_height_back]);
        }

        // Case mounting holes
        mount_spacing_x = 80;
        mount_spacing_y = 55;
        mount_x = (stand_width - mount_spacing_x) / 2;
        mount_y = (stand_depth - mount_spacing_y) / 2;

        mount_positions = [
            [mount_x, mount_y],
            [mount_x + mount_spacing_x, mount_y],
            [mount_x, mount_y + mount_spacing_y],
            [mount_x + mount_spacing_x, mount_y + mount_spacing_y]
        ];

        for (pos = mount_positions) {
            hull() {
                translate([pos[0], pos[1], -0.1])
                    cylinder(h=wall + 0.2, d=4.5, $fn=20);

                translate([pos[0], pos[1], stand_height_front - 5])
                    cylinder(h=wall + 0.2, d=4.5, $fn=20);
            }
        }

        // Rubber feet holes (bottom)
        feet_positions = [
            [wall + 8, wall + 8],
            [stand_width - wall - 8, wall + 8],
            [wall + 8, stand_depth - wall - 8],
            [stand_width - wall - 8, stand_depth - wall - 8]
        ];

        for (pos = feet_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=wall + 0.2, d=3, $fn=20);
        }

        // Cable management slot
        translate([stand_width/2 - 5, stand_depth - wall - 0.1, wall])
            cube([10, wall + 0.2, 15]);
    }
}

// ========================================
// CABLE CLIPS
// ========================================

module cable_clip(cable_diameter=6, mount_type="screw") {
    /*
    Cable clip for organizing wires.
    mount_type: "screw" or "adhesive"
    */

    clip_width = cable_diameter + 4;
    clip_height = cable_diameter + 6;

    difference() {
        union() {
            // Base
            if (mount_type == "screw") {
                cylinder(h=2, d=clip_width + 4, $fn=30);
            } else {
                cube([clip_width + 4, clip_width + 4, 2], center=true);
            }

            // Clip body
            translate([0, 0, 2])
                difference() {
                    cylinder(h=clip_height, d=clip_width, $fn=30);
                    translate([0, 0, -0.1])
                        cylinder(h=clip_height + 0.2, d=cable_diameter, $fn=30);

                    // Slot to insert cable
                    translate([-cable_diameter/2 - 0.5, 0, -0.1])
                        cube([cable_diameter + 1, clip_width, clip_height + 0.2]);
                }
        }

        // Mount hole
        if (mount_type == "screw") {
            translate([0, 0, -0.1])
                cylinder(h=2.2, d=3, $fn=20);
        }
    }
}

module cable_organizer_tray() {
    /*
    Tray that attaches to bottom of case for cable routing.
    */

    tray_length = 90;
    tray_width = 30;
    tray_height = 12;
    wall = 1.5;

    difference() {
        // Outer shell
        cube([tray_length, tray_width, tray_height]);

        // Hollow interior
        translate([wall, wall, wall])
            cube([tray_length - wall*2, tray_width - wall*2, tray_height]);

        // Cable entry/exit slots
        translate([5, -0.1, wall + 2])
            cube([15, wall + 0.2, 6]);

        translate([tray_length - 20, -0.1, wall + 2])
            cube([15, wall + 0.2, 6]);

        // Mounting screw holes
        for (x = [10, tray_length - 10]) {
            translate([x, tray_width/2, -0.1])
                cylinder(h=wall + 0.2, d=3, $fn=20);
        }
    }

    // Cable tie posts
    tie_positions = [
        [tray_length/3, tray_width/2],
        [tray_length*2/3, tray_width/2]
    ];

    for (pos = tie_positions) {
        translate([pos[0], pos[1], wall]) {
            difference() {
                cylinder(h=8, d=6, $fn=20);
                translate([0, 0, 2])
                    cylinder(h=7, d=3.5, $fn=20);
            }
        }
    }
}

// ========================================
// VESA ADAPTER PLATE
// ========================================

module vesa_adapter_plate() {
    /*
    VESA 75mm mount adapter for monitor arms or wall mounts.
    Attaches to back of case.
    */

    plate_size = 90;
    thickness = 3;
    vesa_spacing = 75;  // VESA 75mm standard

    difference() {
        union() {
            // Main plate
            translate([0, 0, 0])
                minkowski() {
                    cube([plate_size - 6, plate_size - 6, thickness/2]);
                    cylinder(r=3, h=thickness/2, $fn=30);
                }

            // Reinforcement ribs
            translate([plate_size/2 - 1, 5, thickness])
                cube([2, plate_size - 10, 3]);

            translate([5, plate_size/2 - 1, thickness])
                cube([plate_size - 10, 2, 3]);
        }

        // VESA mounting holes (M4)
        vesa_offset = (plate_size - vesa_spacing) / 2;
        vesa_positions = [
            [vesa_offset, vesa_offset],
            [vesa_offset + vesa_spacing, vesa_offset],
            [vesa_offset, vesa_offset + vesa_spacing],
            [vesa_offset + vesa_spacing, vesa_offset + vesa_spacing]
        ];

        for (pos = vesa_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=thickness + 6.2, d=4.5, $fn=20);

            // Countersink
            translate([pos[0], pos[1], thickness + 3])
                cylinder(h=3.2, d=9, $fn=30);
        }

        // Case mounting holes (corners)
        case_mount_positions = [
            [8, 8],
            [plate_size - 8, 8],
            [8, plate_size - 8],
            [plate_size - 8, plate_size - 8]
        ];

        for (pos = case_mount_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=thickness + 0.2, d=3.5, $fn=20);
        }
    }
}

// ========================================
// PEDALBOARD MOUNT
// ========================================

module pedalboard_mount() {
    /*
    Low-profile mount for guitar pedalboard.
    Uses velcro strips or dual-lock fasteners.
    */

    mount_length = 95;
    mount_width = 65;
    height = 8;
    wall = 2;

    difference() {
        union() {
            // Base platform
            minkowski() {
                cube([mount_length - 6, mount_width - 6, height/2]);
                cylinder(r=3, h=height/2, $fn=30);
            }

            // Raised edges to prevent sliding
            translate([0, 0, height])
                difference() {
                    minkowski() {
                        cube([mount_length - 6, mount_width - 6, wall]);
                        cylinder(r=3, h=wall, $fn=30);
                    }
                    translate([wall, wall, -0.1])
                        minkowski() {
                            cube([mount_length - 6 - wall*2, mount_width - 6 - wall*2, wall + 0.2]);
                            cylinder(r=2, h=wall, $fn=30);
                        }
                }
        }

        // Case mounting screw holes
        mount_positions = [
            [mount_length/2 - 35, mount_width/2 - 22],
            [mount_length/2 + 35, mount_width/2 - 22],
            [mount_length/2 - 35, mount_width/2 + 22],
            [mount_length/2 + 35, mount_width/2 + 22]
        ];

        for (pos = mount_positions) {
            translate([pos[0], pos[1], -0.1])
                cylinder(h=height + 0.2, d=3.5, $fn=20);

            translate([pos[0], pos[1], height - 2])
                cylinder(h=3, d=6.5, $fn=6);  // Hex countersink
        }

        // Velcro/dual-lock attachment zones (recessed areas)
        velcro_zones = [
            [mount_length/2 - 30, mount_width/2 - 15, 60, 10],
            [mount_length/2 - 30, mount_width/2 + 5, 60, 10]
        ];

        for (zone = velcro_zones) {
            translate([zone[0], zone[1], -0.1])
                cube([zone[2], zone[3], 1.2]);
        }
    }

    // Anti-slip texture on bottom
    for (i = [0:12]) {
        for (j = [0:8]) {
            translate([8 + i*6.5, 8 + j*6.5, -0.5])
                cylinder(h=0.6, d=2, $fn=6);
        }
    }
}

// ========================================
// RENDERING
// ========================================

if (render_mic_stand_mount) {
    mic_stand_mount();
}

if (render_desktop_stand) {
    translate([120, 0, 0])
        desktop_stand();
}

if (render_cable_clips) {
    translate([0, 100, 0]) {
        cable_clip(6, "screw");

        translate([20, 0, 0])
            cable_clip(8, "screw");

        translate([0, 20, 0])
            cable_organizer_tray();
    }
}

if (render_vesa_adapter) {
    translate([0, 200, 0])
        vesa_adapter_plate();
}

if (render_pedalboard_mount) {
    pedalboard_mount();
}

// ========================================
// NOTES
// ========================================

/*
ACCESSORY USAGE:

1. MICROPHONE STAND MOUNT
   - Install 5/8" threaded insert in center hole
   - Mount case using M4 screws through corners
   - Adjust angle with microphone boom

2. DESKTOP STAND
   - Provides 15° viewing angle
   - Install rubber feet in bottom holes
   - Secure case with M4 screws

3. CABLE CLIPS
   - Print multiple in desired cable diameter
   - Screw or adhesive mount to surfaces
   - Route cables through clips for clean setup
   - Cable tray mounts under case bottom

4. VESA ADAPTER
   - Standard 75mm VESA pattern
   - Compatible with monitor arms, wall mounts
   - Use M4 screws for VESA mount
   - M3 screws to attach to case

5. PEDALBOARD MOUNT
   - Apply heavy-duty velcro or dual-lock to recessed zones
   - Anti-slip texture prevents movement
   - Low profile doesn't interfere with pedals
   - Angle case slightly for better visibility

PRINT TIPS:
- Use PETG for outdoor/stage use (more durable)
- 30% infill for strength
- Print clips in batches
- Consider TPU for vibration dampening on pedalboard mount
*/
