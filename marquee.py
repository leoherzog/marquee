# /// script
# requires-python = ">=3.11"
# ///
"""marquee.py - batch driver for marquee.scad: renders STLs for a set of
characters at single or double line height, splitting letters larger than the
print bed into tiles plus splice plates.

    uv run marquee.py ABC --font fonts/MyFont.ttf --height double
"""
import argparse
import json
import math
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCAD = ROOT / "marquee.scad"
DEFAULT_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789&@#$%?!.,:;'\"-+=/*()"
NAMES = {
    ".": "period", ",": "comma", ":": "colon", ";": "semicolon", "!": "exclam",
    "?": "question", "'": "apostrophe", '"': "quote", "-": "hyphen", "+": "plus",
    "=": "equals", "/": "slash", "&": "ampersand", "@": "at", "#": "hash",
    "$": "dollar", "%": "percent", "*": "asterisk", "(": "lparen", ")": "rparen",
}


def file_stem(ch: str) -> str:
    """Filesystem-safe name; lowercase letters get a prefix so they survive case-insensitive filesystems."""
    if ch.isascii() and (ch.isupper() or ch.isdigit()):
        return ch
    if ch.isascii() and ch.islower():
        return f"lc_{ch}"
    return NAMES.get(ch, f"u{ord(ch):04X}")


def find_openscad() -> list[str]:
    """$OPENSCAD, else the newest OpenSCAD-*.AppImage beside this script, else openscad on PATH."""
    if env := os.environ.get("OPENSCAD"):
        cmd = shlex.split(env)
    elif images := sorted(ROOT.glob("OpenSCAD-*.AppImage")):
        cmd = [str(images[-1])]
    elif exe := shutil.which("openscad"):
        cmd = [exe]
    else:
        sys.exit("OpenSCAD not found: set OPENSCAD or put a development snapshot AppImage here")
    version = subprocess.run([*cmd, "--version"], capture_output=True, text=True)
    year = re.search(r"(\d{4})\.", version.stdout + version.stderr)
    if not year or int(year[1]) < 2025:
        sys.exit(f"{cmd[0]} is too old: marquee.scad needs a development snapshot with textmetrics()")
    return cmd


def resolve_font(arg: str | None) -> tuple[str, dict[str, str]]:
    """Fontconfig name for a font file or name, plus the env that lets OpenSCAD find a file."""
    if arg is None:
        files = sorted(p for p in (ROOT / "fonts").iterdir() if p.suffix.lower() in (".ttf", ".otf"))
        if not files:
            return "Liberation Sans:style=Bold", {}
        arg = str(files[0])
    path = Path(arg).expanduser()
    if not path.is_file():
        return arg, {}
    scan = subprocess.run(["fc-scan", "--format", "%{family[0]}\t%{style[0]}\n", str(path)],
                          capture_output=True, text=True, check=True)
    family, style = scan.stdout.splitlines()[0].split("\t")
    family = re.sub(r"([-:,\\])", r"\\\1", family)
    return f"{family}:style={style}", {"OPENSCAD_FONT_PATH": str(path.resolve().parent)}


def scad_value(v) -> str:
    """OpenSCAD literal for a Python value; JSON escapes are valid OpenSCAD string escapes."""
    return json.dumps(v)


def stl_x_extent(path: Path) -> tuple[float, float]:
    """Min and max x of an ASCII STL."""
    xs = [float(l.split()[1]) for l in path.read_text().splitlines() if l.lstrip().startswith("vertex")]
    return min(xs), max(xs)


def row_cuts(lo: float, hi: float, notches: list[list[float]], bed: float, clear: float = 15) -> list[float]:
    """Fewest horizontal cuts leaving no band taller than `bed`, each `clear` mm away from every notch.

    Cuts start evenly spaced and move to the nearest allowed height.
    """
    zones = [(a - clear, b + clear) for a, b in notches]
    allowed = lambda c: all(not z0 < c < z1 for z0, z1 in zones)
    for n in range(math.ceil((hi - lo) / bed), math.ceil((hi - lo) / bed) + 4):
        cuts = []
        for k in range(1, n):
            ideal = lo + k * (hi - lo) / n
            options = [c for c in (ideal, *(e for z in zones for e in z)) if allowed(c)]
            cuts.append(min(options, key=lambda c: abs(c - ideal)))
        edges = [lo, *cuts, hi]
        if all(0 < b - a <= bed for a, b in zip(edges, edges[1:])):
            return cuts
    return [lo + k * (hi - lo) / n for k in range(1, n)]


def echo_value(log: str, name: str):
    """Parse `name = <value>` from OpenSCAD echo output; vectors print as JSON arrays."""
    start = log.index(f"{name} = ") + len(name) + 3
    return json.JSONDecoder().raw_decode(log, start)[0]


class Renderer:
    def __init__(self, cmd, font, env, bed, splice_width, overrides, out):
        self.cmd, self.font, self.bed, self.splice_width, self.out = cmd, font, bed, splice_width, out
        self.env = {**os.environ, **env}
        self.overrides = overrides

    def run(self, output: Path, **params) -> str:
        args = [*self.cmd, "-o", str(output)]
        for k, v in params.items():
            args += ["-D", f"{k}={scad_value(v)}"]
        for o in self.overrides:
            args += ["-D", o]
        proc = subprocess.run([*args, str(SCAD)], capture_output=True, text=True, env=self.env)
        log = proc.stdout + proc.stderr
        if output.suffix == ".echo" and output.exists():
            log += output.read_text()
        if "top level object is empty" in log:
            output.unlink(missing_ok=True)
            return log
        if proc.returncode != 0 or "ERROR" in log:
            raise RuntimeError(next((l for l in log.splitlines() if "ERROR" in l), log.strip()[-300:]))
        return log

    def check_font(self) -> str:
        """Exit unless OpenSCAD resolves the requested family; return what it resolved to."""
        with tempfile.TemporaryDirectory(dir=self.out) as tmp:
            log = self.run(Path(tmp) / "font.echo", char="H", font=self.font)
        used = re.search(r'font_used = "([^"]*)"', log)[1]
        want = re.sub(r"\\(.)", r"\1", re.split(r"(?<!\\):", self.font)[0])
        if want.casefold() != used.split(":")[0].casefold():
            sys.exit(f"font {self.font!r} not found; OpenSCAD would substitute {used!r}")
        return used

    def fit(self, out: Path, y0: float, y1: float, **params) -> list[float]:
        """Render the band y0..y1, splitting it into equal columns if wider than the bed.

        Returns the x positions of the column cuts.
        """
        self.run(out, **params, region=[-1e4, y0, 1e4, y1])
        if not out.exists():
            return []
        x0, x1 = stl_x_extent(out)
        n = math.ceil((x1 - x0) / self.bed)
        if n <= 1:
            return []
        out.unlink()
        xs = [x0 + k * (x1 - x0) / n for k in range(n + 1)]
        for k in range(n):
            self.run(out.with_stem(f"{out.stem}{chr(ord('a') + k)}"), **params, region=[xs[k], y0, xs[k + 1], y1])
        return xs[1:-1]

    def letter(self, ch: str, height: str) -> str:
        base = {"char": ch, "font": self.font, "height": height}
        dest = self.out / height
        dest.mkdir(parents=True, exist_ok=True)
        stem = file_stem(ch)
        with tempfile.TemporaryDirectory(dir=self.out) as tmp:
            info = self.run(Path(tmp) / "info.echo", **base)
        notes = sorted({l.removeprefix("WARNING: ") for l in info.splitlines() if l.startswith("WARNING: ")})
        if "hooked = false" in info:
            notes.insert(0, "no hook row crosses this glyph; it will not hang")

        x0, y0, x1, y1 = echo_value(info, "box")
        if self.bed <= 0 or max(x1 - x0, y1 - y0) <= self.bed:
            self.run(dest / f"{stem}.stl", **base)
            return "; ".join(notes)

        # Bands bottom to top, each split into columns as needed; splices bridge every cut.
        cuts = row_cuts(y0, y1, echo_value(info, "notches"), self.bed)
        edges = [y0 - 1, *cuts, y1 + 1]
        half = self.splice_width / 2
        pieces = 0
        for j in range(len(edges) - 1):
            lo, hi = edges[j], edges[j + 1]
            columns = self.fit(dest / f"{stem}-{j + 1}.stl", lo, hi, **base)
            pieces += len(columns) + 1
            trim_lo = lo + half if j > 0 else lo
            trim_hi = hi - half if j < len(edges) - 2 else hi
            for k, cx in enumerate(columns):
                pair = chr(ord("a") + k) + chr(ord("b") + k)
                self.run(dest / f"{stem}-splice-{j + 1}{pair}.stl", **base,
                         part="splice", region=[cx - half, trim_lo, cx + half, trim_hi])
        for j, cy in enumerate(cuts):
            self.fit(dest / f"{stem}-splice-{j + 1}-{j + 2}.stl", cy - half, cy + half, **base, part="splice")
        notes.insert(0, f"{pieces} pieces")
        return "; ".join(notes)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render marquee letters to STL.")
    ap.add_argument("chars", nargs="?", default=DEFAULT_SET, help="characters to render (default: A-Z, 0-9 and common punctuation)")
    ap.add_argument("--font", help="font file or fontconfig name (default: first file in fonts/)")
    ap.add_argument("--height", choices=["single", "double", "both"], default="single")
    ap.add_argument("--bed", type=float, default=250, help="largest printable piece in mm; 0 never splits")
    ap.add_argument("--splice-width", type=float, default=40, help="width of the plates that bridge cuts, mm")
    ap.add_argument("--set", action="append", default=[], metavar="NAME=VALUE",
                    help="override a marquee.scad parameter, e.g. --set rail_pitch=180")
    ap.add_argument("--out", type=Path, default=ROOT / "out")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) // 2))
    args = ap.parse_args()

    font, env = resolve_font(args.font)
    args.out.mkdir(parents=True, exist_ok=True)
    renderer = Renderer(find_openscad(), font, env, args.bed, args.splice_width, args.set, args.out.resolve())
    heights = ["single", "double"] if args.height == "both" else [args.height]
    chars = list(dict.fromkeys(c for c in args.chars if not c.isspace()))
    print(f"font: {renderer.check_font()}\nout:  {args.out}")

    def job(ch: str, height: str):
        try:
            return ch, height, "ok", renderer.letter(ch, height)
        except Exception as exc:  # report and keep going with the batch
            return ch, height, "FAIL", str(exc)

    failed = 0
    with ThreadPoolExecutor(args.jobs) as pool:
        for ch, height, status, note in pool.map(lambda j: job(*j), [(c, h) for h in heights for c in chars]):
            failed += status == "FAIL"
            print(f"  {status:4} {height:6} {ch!r:5} {note}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
