// Buddy desk figure for R.O.B. Vision
// Units: millimetres. Front faces negative Y. Print with the base on the bed.
// Run build.py for the printable STL and the multipart, multi-color 3MF.

$fn = 56;
part = "all"; // all, six-color names, or shell4/navy4

shell = "#ECEAE4";
navy = "#182A42";
navy_light = "#34465D";
cyan = "#4DE5EE";
orange = "#EF765E";
white = "#FFFFFF";

function pigment(name) =
    name == "shell" ? shell :
    name == "navy" ? navy :
    name == "navy_light" ? navy_light :
    name == "cyan" ? cyan :
    name == "orange" ? orange : white;

module paint(name) {
    if (part == "all" || part == name ||
        (part == "shell4" && (name == "shell" || name == "white")) ||
        (part == "navy4" && (name == "navy" || name == "navy_light")))
        color(pigment(name)) children();
}

module oval(size) {
    scale(size) sphere(r = 1);
}

module bar(a, b, radius) {
    hull() {
        translate(a) sphere(r = radius);
        translate(b) sphere(r = radius);
    }
}

module soft_box(size, radius) {
    // Smooth rectangular block, centered about its origin.
    hull()
        for (x = [-1, 1], y = [-1, 1], z = [-1, 1])
            translate([x * (size[0]/2-radius),
                       y * (size[1]/2-radius),
                       z * (size[2]/2-radius)])
                sphere(r = radius, $fn = 32);
}

module foot() {
    paint("navy") union() {
        cylinder(h = 5.5, r1 = 36.5, r2 = 37.5);
        translate([0, 0, 5.4]) cylinder(h = 10.8, r1 = 37.5, r2 = 34.5);
        translate([0, 0, 16]) cylinder(h = 4, r1 = 34.5, r2 = 26.5);
    }
    paint("cyan") translate([0, 0, 8.3])
        difference() {
            cylinder(h = 1.8, r = 37.1);
            translate([0, 0, -0.1]) cylinder(h = 2, r = 36.0);
        }
    paint("shell") translate([0, 0, 14.2])
        difference() {
            cylinder(h = 8, r1 = 35.8, r2 = 30.2);
            translate([0, 0, -0.1]) cylinder(h = 8.2, r1 = 25.8, r2 = 25.5);
        }
    paint("navy_light") translate([0, -34.4, 11.4])
        soft_box([27, 3.6, 10], 1.6);
    for (x = [-9, 0, 9])
        paint("cyan") translate([x, -36.1, 11.5])
            soft_box([4.5, 1.8, 4.5], 0.6);
}

module body() {
    paint("navy") translate([0, 0, 19.5])
        cylinder(h = 9, r1 = 19, r2 = 16);

    paint("navy") translate([0, 0, 49]) oval([25, 21, 27]);
    paint("shell") translate([0, -1.0, 53]) oval([24.6, 20.6, 27.5]);

    // The lower shell leaves the dark waist visible; the orange accent
    // echoes Buddy's illustrated side panel.
    paint("orange") translate([-19, -8.3, 38]) rotate([0, 19, -15])
        oval([3.4, 7.3, 13]);

    paint("navy") translate([0, 0, 78])
        cylinder(h = 13, r1 = 11.5, r2 = 9.7);
    paint("cyan") translate([0, 0, 82.5])
        cylinder(h = 1.5, r = 11.8);
}

module face() {
    // All head details share one tilted coordinate system.
    paint("shell") oval([37.5, 24, 23.5]);
    paint("navy") translate([0, -15.5, -2.2])
        oval([34.8, 10.7, 17.0]);

    // Cyan iris rings sit proud of the visor, with dark pupils and highlights.
    for (x = [-15.0, 15.0]) {
        paint("cyan") translate([x, -24.6, -1.8])
            oval([8.2, 2.7, 10.0]);
        paint("navy") translate([x+0.4, -26.5, -2.0])
            oval([4.5, 1.35, 6.8]);
        paint("white") translate([x-1.1, -27.5, 1.3])
            sphere(r = 1.65, $fn = 24);
    }

    for (x = [-1, 1]) {
        paint("navy") translate([x*36.1, 1.0, 2.0])
            rotate([0, 90, 0]) cylinder(h = 3.3, r = 10, center = true);
        paint("cyan") translate([x*38.0, 1.0, 2.0])
            rotate([0, 90, 0])
                difference() {
                    cylinder(h = 1.2, r = 7.1, center = true);
                    cylinder(h = 1.4, r = 4.8, center = true);
                }
        paint("orange") translate([x*32.2, 1.4, 14.5])
            rotate([0, x*20, 0]) oval([5.5, 7.7, 13]);
    }

    paint("orange") translate([-30, -15, -7.2])
        rotate([0, -27, 0]) oval([2.5, 3.6, 6.8]);
}

module head() {
    translate([0, -1.8, 106]) rotate([0, -8, 5]) face();
}

module arm(side) {
    // Open elbows frame the block; the two hands cup its left/right sides.
    paint("navy") translate([side*24, -0.5, 72])
        oval([9.2, 10.5, 9.5]);
    paint("navy_light") bar([side*25.8, -2.5, 72],
                          [side*25, -20.0, 58.5], 5.8);
    paint("navy") translate([side*25, -20, 58.5])
        oval([7.2, 7.2, 7.2]);
    paint("navy_light") bar([side*24.7, -21.7, 58.6],
                          [side*15.0, -39.0, 57.0], 5.5);
    paint("shell") translate([side*14.0, -40.4, 57])
        oval([8.5, 8.0, 7.0]);
    paint("cyan") translate([side*22.1, -41.0, 55.7])
        oval([1.25, 2.2, 2.8]);

    paint("navy_light") translate([side*26.2, -0.8, 72])
        rotate([0, 90, 0]) cylinder(h = 3.0, r = 5.8, center = true);
    paint("cyan") translate([side*28.1, -0.8, 72])
        rotate([0, 90, 0]) cylinder(h = 1.0, r = 3.2, center = true);
}

module carried_block() {
    paint("cyan") translate([0, -42, 58])
        soft_box([18, 18, 18], 2.0);
    // Pixel marks echo the illustrated block; each mark is at least 2 mm.
    for (x = [-4, 4])
        paint("white") translate([x, -51.15, 60])
            soft_box([2.2, 1.7, 2.2], 0.35);
}

// The "all" selection is one connected solid for the monochrome STL.
// build.py selects each named material and makes non-overlapping 3MF volumes.
union() {
    foot();
    body();
    arm(-1);
    arm(1);
    carried_block();
    head();
}
