// marquee.scad - one changeable marquee letter: a hollow, open-backed shell
// with an inset groove on the face and wedge notches in the side walls that
// hang it on the sign rails. Sized for a single or double line; print face down.
// Needs an OpenSCAD development snapshot (textmetrics). Drive it from
// marquee.py, or set the parameters in the Customizer.

/* [Letter] */
char = "A";
// Fontconfig name. Fonts in other folders are found when OPENSCAD_FONT_PATH points there.
font = "Liberation Sans:style=Bold";
height = "single"; // [single, double]

/* [Size: single, double] */
// Height of a capital H.
cap_height = [228.6, 457.2];
// Face to back edge.
depth = [14, 22];
wall = [2.0, 2.4];
face = [2.4, 3.0];

/* [Face groove: single, double] */
// Distance from the outline to the groove.
groove_inset = [7, 13];
groove_width = [1.6, 2.4];
groove_depth = [0.8, 1.2];

/* [Rails and hooks] */
// Vertical spacing of the sign rails.
rail_pitch = 184;
// Height of the lowest hook tip above the baseline.
rail_first = 38;
// Hook tips stay at least this far below the cap line.
row_margin = 15;
// How far a notch tip reaches from the back toward the face: single, double.
hook_reach = [7, 11];
// Notch opening along the back edge, below the tip: single, double.
hook_open = [10, 16];

/* [Print splitting] */
// A splice is a flat plate glued inside the face across a cut between pieces.
part = "letter"; // [letter, splice]
// Keep only the rectangle [x0, y0, x1, y1]; [] keeps everything. A splice needs one.
region = [];
splice_thickness = 2.5;
// Clearance between a splice plate and the walls.
splice_fit = 0.3;

/* [Hidden] */
$fs = 0.5;
$fa = 3;

i = height == "double" ? 1 : 0;
H = cap_height[i];
D = depth[i];
W = wall[i];
F = face[i];
GI = groove_inset[i];
GW = groove_width[i];
GD = groove_depth[i];
R = hook_reach[i];
O = hook_open[i];
assert(D - R > F, "hook_reach must stop short of the face plate");

S = 100 * H / textmetrics(text = "H", font = font, size = 100).size.y;
tm = textmetrics(text = char, font = font, size = S, halign = "center", valign = "baseline");
// Ink box [x0, y0, x1, y1] of the mirrored glyph.
box = [-(tm.position.x + tm.size.x), tm.position.y, -tm.position.x, tm.position.y + tm.size.y];

// Hook tip heights above the baseline, one per rail behind the letter.
rows = [for (y = [rail_first : rail_pitch : H - row_margin]) y];
hooked = len([for (r = rows) if (r > box[1] && r < box[3] - 2 * W) r]) > 0;

// OpenSCAD silently substitutes a fallback for a font it cannot find.
used = fontmetrics(font = font).font;
echo(box = box, notches = [for (r = rows) [r - O, r]], hooked = hooked,
     font_used = str(used.family, ":style=", used.style));
if (!hooked) echo(str("WARNING: no hook row crosses \"", char, "\"; it will not hang on the rails"));

// Mirrored so it reads correctly from the face, which is the side on the print bed.
module glyph() mirror([1, 0]) text(char, size = S, font = font, halign = "center", valign = "baseline");

module groove() difference() {
  offset(r = -GI) glyph();
  offset(r = -(GI + GW)) glyph();
}

// Wedge cut through every wall at hook height y: square top edge, lower edge
// slanting out to the opening on the back.
module notch(y) {
  e = 1;
  rotate([90, 0, 90]) linear_extrude(2e4, center = true)
    polygon([[y, D - R], [y, D + e], [y - O * (1 + e / R), D + e]]);
}

module shell() {
  if (GD > 0) linear_extrude(GD) difference() { glyph(); groove(); }
  translate([0, 0, GD]) linear_extrude(F - GD) glyph();
  difference() {
    translate([0, 0, F]) linear_extrude(D - F) difference() {
      glyph();
      offset(r = -W) glyph();
    }
    for (y = rows) notch(y);
  }
}

module region_2d() translate([region[0], region[1]]) square([region[2] - region[0], region[3] - region[1]]);

module splice_plate() {
  assert(len(region) == 4, "a splice needs a region");
  linear_extrude(splice_thickness) intersection() {
    offset(r = -(W + splice_fit)) glyph();
    region_2d();
  }
}

if (part == "splice") splice_plate();
else if (len(region) == 4) intersection() {
  shell();
  translate([0, 0, -1]) linear_extrude(D + 2) region_2d();
}
else shell();
