#!/usr/bin/env python3
"""Checks for the scene-asset module and the values lines."""

from __future__ import annotations

import importlib.util
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STYLES = ROOT / "styles.css"
HTML = ROOT / "index.html"
LINES = [
    "stay curious",
    "be kind",
    "build small",
    "make waves",
]


def fail(message: str) -> None:
    print(f"FAIL {message}")
    sys.exit(1)


def webp_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[12:16] == b"VP8X":
        width = 1 + int.from_bytes(data[24:27], "little")
        height = 1 + int.from_bytes(data[27:30], "little")
        return width, height
    if data[12:16] == b"VP8 ":
        width, height = struct.unpack_from("<HH", data, 26)
        return width & 0x3FFF, height & 0x3FFF
    if data[12:16] == b"VP8L":
        b0, b1, b2, b3 = data[21:25]
        width = 1 + (((b1 & 0x3F) << 8) | b0)
        height = 1 + (((b3 & 0xF) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
        return width, height
    fail(f"{path.name} is not a webp frame")
    raise AssertionError


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or b"IEND" not in data:
        fail(f"{path.name} is not a complete png")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    styles = STYLES.read_text()
    html = HTML.read_text()
    urls = re.findall(r"url\((\"|')?((?:background|logo|ui)/[^)\"']+)", styles)
    if len(urls) != 4:
        fail(f"scene asset map has {len(urls)} urls, expected 4")
    for _quote, rel in urls:
        path = (ROOT / rel).resolve()
        if not path.is_file():
            fail(f"missing scene asset {rel}")
    if "mark-mobile" in styles or "values-sign.webp" in styles or "values-sign.png" in styles:
        fail("scene asset map still names a retired file")
    srcs = re.findall(r"\bsrc\s*=\s*[\"']([^\"']+)", html)
    analytics = "https://analytics.manaiakalani.info/api/script.js?siteId=8e29cd0f40e2"
    if srcs != [analytics, "parallax.js"]:
        fail(f"homepage sources are {srcs}")

    desktop = webp_size(ROOT / "background" / "hero-desktop-3840x2160.webp")
    mobile = webp_size(ROOT / "background" / "hero-mobile-1440x2560.webp")
    if desktop != (3840, 2160):
        fail(f"desktop background is {desktop}")
    if mobile != (1440, 2560):
        fail(f"mobile background is {mobile}")

    items = re.findall(r"<li>(.*?)</li>", html, flags=re.S)
    if [item.strip() for item in items] != LINES:
        fail(f"values lines are {items}")

    mail = re.search(r'href="mailto:([^"]+)"', html)
    shown = re.search(r'class="contact-address">([^<]+)', html)
    if mail is None or shown is None or mail.group(1) != shown.group(1).strip():
        fail("email text does not match the mailto address")

    portrait = re.search(
        r"@media\s*\(\s*max-width:\s*720px\s*\)\s*\{((?:[^{}]|\{[^{}]*\})*)\}",
        styles,
    )
    if portrait is None:
        fail("portrait breakpoint is missing")
    body = portrait.group(1)
    for banned in ("top:", "left:", "right:", "bottom:", "width:", "font-size:", "content:"):
        if banned in body:
            fail(f"breakpoint restates placement via {banned}")
    if "background-image" not in body:
        fail("breakpoint does not swap the background")

    favicon_builder = load_module(ROOT / "logo" / "build_favicon.py", "build_favicon")
    favicon_path = ROOT / "favicon.svg"
    if not favicon_path.is_file() or favicon_path.read_text() != favicon_builder.favicon_svg():
        fail("favicon drifted from the emblem; run logo/build_favicon.py")
    if "<rect" in favicon_path.read_text():
        fail("favicon should stay transparent")

    script = (ROOT / "parallax.js").read_text()
    if ".brand-mark" not in script or any(
        name in script for name in (".values-sign", ".wordmark", ".contact-pill", ".scene-bg")
    ):
        fail("parallax should move only the logo")

    if (ROOT / "logo" / "mark-mobile.svg").exists():
        fail("mobile emblem file still duplicates the mark")
    mark = (ROOT / "logo" / "mark-desktop.svg").read_text()
    lockup_path = ROOT / "logo" / "full-lockup.svg"
    lockup = lockup_path.read_text()
    if 'id="emblem"' not in mark:
        fail("emblem module has no emblem id")
    lockup_builder = load_module(ROOT / "logo" / "build_lockup.py", "build_lockup")
    if lockup != lockup_builder.lockup_svg():
        fail("lockup drifted from the emblem; run logo/build_lockup.py")
    mark_paths = re.findall(r'\sd="([^"]+)"', mark)
    lock_paths = re.findall(r'\sd="([^"]+)"', lockup)
    if mark_paths != lock_paths:
        fail("lockup paths are not the emblem paths")

    frame = load_module(ROOT / "ui" / "build_values_frame.py", "build_values_frame")
    css_path = ROOT / "values-lines.css"
    if css_path.read_text() != frame.line_css():
        fail("values line positions drifted from the glyph bounds")
    painted = png_size(ROOT / "ui" / "values-sign.png")
    if painted != (1230, 1278):
        fail(f"painted sign is {painted}")
    master = png_size(ROOT / "ui" / "values-sign-2x.png")
    if master != (2460, 2556):
        fail(f"painted master is {master}")
    webp_size(ROOT / "ui" / "values-sign-frame.webp")
    print("ok")


if __name__ == "__main__":
    main()
