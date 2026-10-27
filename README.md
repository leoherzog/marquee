# Marquee Letters

## What is this?

This project uses OpenSCAD to generate open-backed shell like the vacuum-formed original letters that are no longer sold. They rest on a theatre marquee sign's rails. [OpenSCAD](https://openscad.org/) builds the geometry + a small Python script renders whole character sets and splits anything too big for your 3D printer.

### Features

- 🔤 Any TrueType or OpenType font, from a file or by installed name
- 📏 Single (9 in) or double (18 in) line height, scaled so a capital H fills the line
- 🪝 Hook notches placed by the sign's rail spacing, so every letter hangs level with its neighbors
- ✂️ Letters bigger than your print bed split into pieces, with splice plates to glue them back together
- 🖨️ Prints face down with no supports
- 🎛️ Every dimension is a parameter, from the command line or OpenSCAD's Customizer

## Usage

You'll need:

- An [OpenSCAD development snapshot](https://openscad.org/downloads.html#snapshots). The 2021.01 release can't measure text, which this depends on. Drop the AppImage in this folder, put `openscad` on your `PATH`, or point `$OPENSCAD` at it.
- [uv](https://docs.astral.sh/uv/) to run the script. There are no other Python dependencies.
- fontconfig, for reading font files. Most Linux desktops already have it.

Then:

```bash
uv run marquee.py                                   # A-Z, 0-9 and punctuation, single height
uv run marquee.py HELLO --height double --bed 250   # 18 in letters, split for a 250 mm bed
uv run marquee.py E --font "Montserrat:style=Bold"  # an installed font by name
```

STLs land in `out/single/` and `out/double/`. The font defaults to the first file in `fonts/`, and [Barlow Semi Condensed Bold](https://github.com/jpt/barlow) is included. Pick a heavy weight if you swap it, since thin strokes lose the groove.

A letter larger than `--bed` (380 mm by default) comes out as numbered pieces plus splice plates, like `T-1.stl`, `T-2.stl`, and `T-splice-1-2.stl`. Glue each splice inside the face across its seam. A textured PEI sheet gives the face a pebbled finish like the originals.

To tweak one letter by hand, open `marquee.scad` in OpenSCAD and use the Customizer. Start OpenSCAD with `OPENSCAD_FONT_PATH=fonts` so it can find the fonts in this folder.

### Fitting your sign

The rail spacing, hook profile, and letter depth were estimated from photos of one sign. Measure yours before printing a full set, and override anything that differs:

```bash
uv run marquee.py --set rail_pitch=180 --set rail_first=40 --set "depth=[15, 24]"
```

[PLAN.md](PLAN.md) lists every parameter with its default and where it came from.

## Special Thanks

This project wouldn't be possible without the fantastic work of:

- [OpenSCAD](https://github.com/openscad/openscad) and contributors, for `textmetrics()` and the Manifold backend
- [@jpt](https://github.com/jpt) and the Barlow Project Authors, for [Barlow](https://github.com/jpt/barlow)

## License

The MIT License (MIT)

Copyright © 2026 Leo Herzog

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Barlow, in `fonts/`, is licensed separately under the [SIL Open Font License](fonts/OFL.txt).

## About Me

<a href="https://herzog.tech/" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/link-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/link.svg.png">
    <img src="https://herzog.tech/signature/link.svg.png" width="32px">
  </picture>
</a>
<a href="https://mastodon.social/@herzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/mastodon-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/mastodon.svg.png">
    <img src="https://herzog.tech/signature/mastodon.svg.png" width="32px">
  </picture>
</a>
<a href="https://github.com/leoherzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/github-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/github.svg.png">
    <img src="https://herzog.tech/signature/github.svg.png" width="32px">
  </picture>
</a>
<a href="https://keybase.io/leoherzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/keybase-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/keybase.svg.png">
    <img src="https://herzog.tech/signature/keybase.svg.png" width="32px">
  </picture>
</a>
<a href="https://www.linkedin.com/in/leoherzog" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/linkedin-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/linkedin.svg.png">
    <img src="https://herzog.tech/signature/linkedin.svg.png" width="32px">
  </picture>
</a>
<a href="https://hope.edu/directory/people/herzog-leo/" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/anchor-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/anchor.svg.png">
    <img src="https://herzog.tech/signature/anchor.svg.png" width="32px">
  </picture>
</a>
<br />
<a href="https://herzog.tech/$" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://herzog.tech/signature/mug-tea-saucer-solid-light.svg.png">
    <source media="(prefers-color-scheme: light)" srcset="https://herzog.tech/signature/mug-tea-saucer-solid.svg.png">
    <img src="https://herzog.tech/signature/mug-tea-saucer-solid.svg.png" alt="Buy Me A Tea" width="32px">
  </picture>
  Found this helpful? Buy me a tea!
</a>
