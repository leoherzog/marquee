# Marquee letters

3D-printable replacements for changeable marquee sign letters, generated from
any font at single (9 in) or double (18 in) line height. Each letter is a
hollow, open-backed shell like the vacuum-formed originals: a face plate with
an inset decorative groove, side walls, and wedge notches in the walls that
hang it on the sign rails.

## Files

```
marquee.scad   the parametric letter model (OpenSCAD)
marquee.py     batch driver: font, character set, height, bed splitting
fonts/         font files to build from
out/           generated STLs, out/<single|double>/
OpenSCAD-*.AppImage   development snapshot that marquee.py runs
```

## Usage

`marquee.scad` uses `textmetrics()`, which only OpenSCAD development snapshots
have; 2021.01 cannot run it. `marquee.py` uses `$OPENSCAD`, else the newest
`OpenSCAD-*.AppImage` in this folder, else `openscad` on `PATH`.

```bash
uv run marquee.py                                  # A-Z, 0-9, punctuation; single height
uv run marquee.py ABC --font fonts/MyFont.ttf --height double
uv run marquee.py W --font "Montserrat:style=Bold" --height both
uv run marquee.py E --bed 250 --set rail_pitch=180 --set "depth=[15, 24]"
```

`--font` takes a font file or a fontconfig name and defaults to the first file
in `fonts/`. The driver stops if OpenSCAD cannot find the font, since OpenSCAD
otherwise substitutes another one silently. `--set` overrides any parameter in
`marquee.scad`. A run prints a warning for each glyph that no hook row crosses.

To edit a single letter interactively, open `marquee.scad` in the snapshot
and use the Customizer. Start it with `OPENSCAD_FONT_PATH=fonts` so it finds
the fonts in this folder.

## Model

The glyph is scaled so a capital H is exactly the line's cap height, then
mirrored so it reads correctly from the face, which prints on the bed. The
face plate carries a recessed groove at a fixed inset from the outline. The
walls are an inward offset of the outline, so strokes thinner than two walls
come out solid.

Hooks follow the rails, not the letter: a notch row sits at
`rail_first + k * rail_pitch` above the baseline, up to `row_margin` below the
cap line. Each row cuts a wedge through every wall it crosses, open at the
back, with a square top edge and a lower edge slanting to the opening. A
single letter gets one row; a double letter gets three.

Glyphs that sit between rows, such as `- + = * ' "` at single height, get no
hook. They need a carrier or adhesive.

## Printing

Print face down without supports. The notches widen toward the back, so they
need no supports either. A textured PEI sheet gives the face a pebbled finish
like the originals.

Pieces larger than `--bed` (default 380 mm; use 250 for a Bambu X1C) are
split. Horizontal cuts come first: the fewest that keep every band within the
bed, spaced evenly and moved at least 15 mm clear of any notch. Any band still
too wide is then split into equal columns. Each cut gets a splice plate, which
is glued inside the shell across the seam. Files are named `T-1.stl`, `T-2a.stl`, `T-2b.stl`, `T-splice-1-2.stl`
(between bands 1 and 2) and `T-splice-2ab.stl` (between 2a and 2b).

## Dimensions

Everything below was estimated from the reference photos. The rail values
decide whether letters hang at all, so measure them before printing a set.

| Parameter | Single | Double | Source |
|---|---|---|---|
| `cap_height` | 228.6 | 457.2 | 9 in D and 18 in T, measured |
| `depth` | 14 | 22 | side views |
| `wall`, `face` | 2.0, 2.4 | 2.4, 3.0 | chosen for printing |
| `groove_inset` / `width` / `depth` | 7 / 1.6 / 0.8 | 13 / 2.4 / 1.2 | face close-ups |
| `hook_reach` / `hook_open` | 7 / 10 | 11 / 16 | notch close-ups |
| `rail_pitch` | 184 | 184 | notch spacing on the 18 in T |
| `rail_first` | 38 | 38 | lowest notch on the D and the T |

## Status

- [x] Model: shell, groove, rail notches, single and double height.
- [x] Driver: font files or names, batch, bed splitting with splice plates.
- [x] Full A-Z, 0-9 and punctuation set renders as watertight solids at both heights.
- [ ] Measure the rail pitch, the lowest hook height, and one notch profile.
- [ ] Choose the final font and drop it in `fonts/`.
- [ ] Print one single letter and check the hook fit on a real rail.
- [ ] Print one split double letter and check the splice joint.
