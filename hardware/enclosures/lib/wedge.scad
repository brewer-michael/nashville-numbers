// Nashville Numbers enclosures - the wedge case both enclosures are built on.
//
//   * shell: four walls and a sloped display face in one piece, printed
//            FACE-DOWN (no supports: the side walls stand vertical, the front
//            and back walls lean by `angle`, port notches open at the rim).
//   * base:  a flat plate that drops into the shell's open bottom; the Pi sits
//            on it. Three M3 screws go up through it into heat-set inserts in
//            corner posts of the shell (the fourth corner holds the Pi's
//            USB/Ethernet ports).
//
// Case coordinates: X right, Y back, Z up; origin at the outer front-left
// corner of the bottom rim. The face is the plane z = H + y * tan(angle).
//
// A file using this library sets the parameters below (after the include)
// and provides the build-specific features.

include <ghosts.scad>

// ---- parameters (overridden by the enclosure file) -------------------------
W = 120;            // outer width
D = 80;             // outer depth
H = 35;             // outer height of the face's front edge
angle = 25;         // face tilt from horizontal (degrees)
wall = 2.5;
face_t = 3.0;       // face plate thickness (perpendicular to the face)
base_t = 3.0;       // base plate thickness
corner_r = 4;
post_d = 9;
closure = "insert"; // "insert" (M3 heat-set) or "selftap" (M3 thread-forming)
pi_model = 4;       // ghost used for the preview; the case fits 4 and 5

// ---- derived -----------------------------------------------------------------
function face_z(y) = H + y * tan(angle);           // outer face height at depth y
H_back = face_z(D);
slope_len = D / cos(angle);
face_n = [0, -sin(angle), cos(angle)];             // outward face normal

// Pi: USB/Ethernet end against the left wall, power/HDMI edge against the
// back wall (board rotated 180 degrees about Z).
pi_X0 = wall + pi_len + 0.5;          // board x = 0 edge (microSD end)
pi_Y0 = D - wall - 0.5;               // board y = 0 edge (power/HDMI)
pi_z_top = base_t + pi_standoff_h + pi_pcb_t;

module at_pi() {
    translate([pi_X0, pi_Y0, pi_z_top]) rotate([0, 0, 180]) children();
}

// Face frame: x along X, y up the slope from the front edge, z = outward
// normal; z = 0 is the outer face surface, -face_t its underside.
module on_face(x, s) {
    translate([x, 0, H]) rotate([angle, 0, 0]) translate([0, s, 0]) children();
}

// Everything below the (optionally offset) face plane.
module below_face(offset = 0, big = 2000) {
    translate([0, 0, H - offset / cos(angle)]) rotate([angle, 0, 0])
        translate([-big / 2, -big / 2, -big]) cube([big, big, big]);
}

// Closure post positions (front-left, front-right, back-right).
function post_xy() = [
    [wall + post_d / 2 - 1, wall + post_d / 2 - 1],
    [W - wall - post_d / 2 + 1, wall + post_d / 2 - 1],
    [W - wall - post_d / 2 + 1, D - wall - post_d / 2 + 1]];

module shell_outer() {
    intersection() {
        rbox([W, D, H_back + 1], corner_r);
        below_face();
    }
}

module shell_cavity() {
    intersection() {
        translate([wall, wall, -1]) rbox([W - 2 * wall, D - 2 * wall, H_back + 2], corner_r - wall / 2);
        below_face(face_t);
    }
}

module closure_posts() {
    intersection() {
        union() for (p = post_xy()) {
            // post merged into the corner so it prints as part of the walls
            cx = p[0] < W / 2 ? wall - eps : W - wall + eps;
            cy = p[1] < D / 2 ? wall - eps : D - wall + eps;
            hull() {
                translate([p[0], p[1], base_t]) cylinder(d = post_d, h = H_back);
                translate([min(p[0], cx), min(p[1], cy), base_t])
                    cube([abs(p[0] - cx), abs(p[1] - cy), H_back]);
            }
        }
        below_face();
    }
}

module closure_holes() {
    for (p = post_xy()) translate([p[0], p[1], base_t - eps]) {
        if (closure == "insert") {
            cylinder(d = insert_d, h = insert_depth + eps);
            cylinder(d = m3_clear_d, h = insert_depth + 4);   // room for the screw tip
        } else cylinder(d = selftap_m3_d, h = 10);
    }
}

// Print direction "up" of the face-down shell, expressed in case coordinates:
// (0, sin(angle), -cos(angle)). Used to orient teardrop holes in the walls.
function print_up_yz() = [sin(angle), -cos(angle)];

// U-notches (open at the rim) for the Pi's ports, sized for Pi 4 and Pi 5.
module pi_port_notches() {
    // left wall: USB-A pairs and RJ45 (both layouts), up to the plug tops
    translate([-1, pi_Y0 - 55.8, -1])
        cube([wall + 2, 55.8 - 0.2, pi_z_top + 18.5 + 1]);
    // back wall: USB-C, micro-HDMI x2, Pi 4 audio jack
    translate([pi_X0 - 59.5, D - wall - 1, -1])
        cube([59.5 - 4.2, wall + 2, pi_z_top + 9.0 + 1]);
}

// Clamp tabs hold a display module against the face regardless of where the
// module's own mounting holes are. A module (outline w x h, centred on the
// face point it is placed at, its back `depth` below the face underside) gets
// tabs = [[edge, offset], ...] with edge "left" | "right" | "top" | "bottom"
// and offset the tab position along that edge from the module centre. Each
// tab is a small plate screwed to a boss beside the module, pressing
// `tab_overlap` onto the module's back.
tab_w = 10;
tab_t = 3.2;
tab_overlap = 3.5;
boss_d = 7;

function tab_boss(w, h, tab) =
    tab[0] == "left"  ? [-w / 2 - boss_d / 2 - 0.6, tab[1]] :
    tab[0] == "right" ? [ w / 2 + boss_d / 2 + 0.6, tab[1]] :
    tab[0] == "top"   ? [tab[1],  h / 2 + boss_d / 2 + 0.6] :
                        [tab[1], -h / 2 - boss_d / 2 - 0.6];

module clamp_bosses(w, h, depth, tabs) {
    // 0.3 mm short of the module back, so the tab clamps before it bottoms out
    for (t = tabs) let(p = tab_boss(w, h, t))
        translate([p[0], p[1], -face_t - depth + 0.3]) cylinder(d = boss_d, h = depth - 0.3 + 0.2);
}

module clamp_boss_holes(w, h, depth, tabs) {
    for (t = tabs) let(p = tab_boss(w, h, t))
        translate([p[0], p[1], -face_t - depth - 1]) cylinder(d = m25_pilot_d, h = 8 + 1);
}

// Tab in face coordinates (assembled position).
module clamp_tab(w, h, depth, tab) {
    p = tab_boss(w, h, tab);
    z0 = -face_t - depth - tab_t;
    horiz = tab[0] == "left" || tab[0] == "right";
    // from the far side of the boss to tab_overlap inside the module edge
    inner = horiz ? sign(p[0]) * (w / 2 - tab_overlap) : sign(p[1]) * (h / 2 - tab_overlap);
    outer = horiz ? p[0] + sign(p[0]) * (boss_d / 2 + 0.5) : p[1] + sign(p[1]) * (boss_d / 2 + 0.5);
    difference() {
        translate([0, 0, z0]) linear_extrude(tab_t)
            if (horiz) translate([min(inner, outer), p[1] - tab_w / 2]) square([abs(outer - inner), tab_w]);
            else translate([p[0] - tab_w / 2, min(inner, outer)]) square([tab_w, abs(outer - inner)]);
        translate([p[0], p[1], z0 - 1]) cylinder(d = m25_clear_d, h = tab_t + 2);
    }
}

// All tabs laid flat on z = 0 in a row, for printing.
module clamp_tabs_print(w, h, depth, tabs) {
    for (i = [0:len(tabs) - 1]) translate([i * 22, 0, 0]) {
        p = tab_boss(w, h, tabs[i]);
        translate([-p[0], -p[1], face_t + depth + tab_t]) clamp_tab(w, h, depth, tabs[i]);
    }
}

// Base plate: fits inside the shell rim, carries the Pi standoffs.
module base_plate_body() {
    translate([wall + fit, wall + fit, 0])
        rbox([W - 2 * wall - 2 * fit, D - 2 * wall - 2 * fit, base_t], corner_r - wall / 2);
}

module pi_standoffs() {
    at_pi() for (h = pi_holes)
        translate([h[0], h[1], -pi_pcb_t - pi_standoff_h - eps])
            cylinder(d = pi_standoff_d, h = pi_standoff_h + eps);
}

module pi_standoff_holes() {
    at_pi() for (h = pi_holes)
        translate([h[0], h[1], -pi_pcb_t - pi_standoff_h - base_t + 1.0])
            cylinder(d = m25_pilot_d, h = pi_standoff_h + base_t);
}

module base_closure_holes() {
    for (p = post_xy()) translate([p[0], p[1], 0]) counterbored_hole(base_t);
}

bumper_d = 13.5;
module bumper_recesses(inset = 16) {
    for (x = [inset, W - inset], y = [inset, D - inset])
        translate([x, y, -eps]) cylinder(d = bumper_d, h = 0.8 + eps);
}

// Rotate the shell so its face lies on z = 0 (outward normal pointing down)
// for printing: rotating by 180 - angle about X maps the normal
// (0, -sin a, cos a) to (0, 0, -1) and the face plane onto z = 0.
module face_down() {
    rotate([180 - angle, 0, 0]) translate([0, 0, -H]) children();
}
