// Nashville Numbers enclosures - shared helpers.
// Units: mm. OpenSCAD 2021.01 compatible, no external libraries.

$fn = 48;
eps = 0.01;

tol = 0.2;    // clearance for holes and pockets
fit = 0.3;    // clearance between mating printed parts

// M3 heat-set insert for a 4.0 mm hole, up to 5.7 long (CNC Kitchen / Ruthex
// "M3 x 5.7"); the hole is a little deeper for the displaced plastic
insert_d     = 4.0;
insert_depth = 6.0;
selftap_m3_d = 2.6;   // pilot for M3 self-tapping screws (closure = "selftap")
m3_clear_d   = 3.4;
m3_head_d    = 6.2;   // ISO 7380 button head is 5.7
m3_head_h    = 2.0;
m25_pilot_d  = 2.2;   // M2.5 self-tapping (or machine screw cut into the plastic)
m25_clear_d  = 2.9;

// Rounded rectangle prism, origin at the min corner.
module rbox(size, r) {
    r = max(min(r, size[0] / 2 - eps, size[1] / 2 - eps), eps);
    hull() for (x = [r, size[0] - r], y = [r, size[1] - r])
        translate([x, y, 0]) cylinder(r = r, h = size[2]);
}

// 2D rounded rectangle, origin at the min corner.
module rrect(size, r) {
    r = max(min(r, size[0] / 2 - eps, size[1] / 2 - eps), eps);
    hull() for (x = [r, size[0] - r], y = [r, size[1] - r])
        translate([x, y]) circle(r = r);
}

// Hole for a screw coming from below: counterbore for the head, clearance hole.
module counterbored_hole(len, d = m3_clear_d, head_d = m3_head_d, head_h = m3_head_h) {
    translate([0, 0, -eps]) cylinder(d = d, h = len + 2 * eps);
    translate([0, 0, -eps]) cylinder(d = head_d, h = head_h + eps);
}

// Round hole that prints cleanly in a wall: a truncated teardrop whose point
// faces `up` (2D direction in the hole's local x/y plane, i.e. the direction
// that will be "up" on the printer), clipped at radius `clip_r` so a nut or
// button head still covers it. Local z is the hole axis.
module teardrop_hole(d, depth, up = [0, 1], clip_r = undef) {
    r = d / 2;
    cr = clip_r == undef ? r * 1.2 : clip_r;
    a = atan2(up[1], up[0]);
    translate([0, 0, -eps]) linear_extrude(depth + 2 * eps)
        rotate(a - 90) intersection() {
            union() {
                circle(r = r);
                polygon([[-r * cos(45), r * sin(45)], [r * cos(45), r * sin(45)], [0, r * sqrt(2)]]);
            }
            translate([-r, -r]) square([2 * r, r + cr]);
        }
}

// Row of rounded slots along X, centred on the origin, cut through `depth` along Z.
module slot_row(n, len, width, pitch, depth) {
    for (i = [0:n - 1])
        translate([(i - (n - 1) / 2) * pitch, 0, -eps])
            hull() for (y = [-(len - width) / 2, (len - width) / 2])
                translate([0, y, 0]) cylinder(d = width, h = depth + 2 * eps, $fn = 20);
}
