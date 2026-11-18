#!/usr/bin/env python3
"""Day in One Picture - a make.fun news-image entry.

Renders a newspaper-style front page that sums up the world news of
Tuesday 17 November 2026 into a single 1024x1024 PNG written to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).

Pure Python 3 standard library: the headlines live in headlines.json
beside this file, the type is a hand-drawn 5x7 pixel font below, and
the PNG is encoded with zlib/struct. No network, no third-party code,
fully deterministic: the same headlines.json always gives the same
bytes out.
"""

import binascii
import json
import os
import struct
import zlib

# ---------------------------------------------------------------- PNG out

def save_png(path, width, height, pixels):
    """Write an RGB pixel buffer (list of bytearray rows) as a PNG file."""
    raw = bytearray()
    for row in pixels:
        raw.append(0)  # filter type 0 (none) for every scanline
        raw.extend(row)
    compressed = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        out += struct.pack(">I", binascii.crc32(tag + payload) & 0xFFFFFFFF)
        return out

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", header)
    data += chunk(b"IDAT", compressed)
    data += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(data)


# ---------------------------------------------------------------- canvas

class Canvas:
    """A tiny RGB raster with the few primitives a poster needs."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.rows = [bytearray(colour * width) for _ in range(height)]

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            row = self.rows[y]
            row[x * 3] = colour[0]
            row[x * 3 + 1] = colour[1]
            row[x * 3 + 2] = colour[2]

    def fill_rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                row = self.rows[yy]
                for xx in range(max(x, 0), min(x + w, self.w)):
                    row[xx * 3] = colour[0]
                    row[xx * 3 + 1] = colour[1]
                    row[xx * 3 + 2] = colour[2]

    def frame(self, x, y, w, h, colour, thick):
        self.fill_rect(x, y, w, thick, colour)
        self.fill_rect(x, y + h - thick, w, thick, colour)
        self.fill_rect(x, y, thick, h, colour)
        self.fill_rect(x + w - thick, y, thick, h, colour)

    def line(self, x0, y0, x1, y1, colour, thick=1):
        """Bresenham line with a square brush of the given thickness."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        off = thick // 2
        while True:
            self.fill_rect(x0 - off, y0 - off, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            span = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.fill_rect(cx - span, yy, span * 2 + 1, 1, colour)

    def ring(self, cx, cy, r, colour, thick=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - thick < d <= r:
                    self.set(xx, yy, colour)


# ---------------------------------------------------------------- the font
# A 5x7 pixel typeface drawn for this poster, one string per row,
# '#' for ink and ' ' for paper. Text is set in capitals throughout.

GLYPHS = {
    "A": [" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "B": ["#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "],
    "C": [" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"],
    "D": ["###  ", "#  # ", "#   #", "#   #", "#   #", "#  # ", "###  "],
    "E": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"],
    "F": ["#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "],
    "G": [" ####", "#    ", "#    ", "#  ##", "#   #", "#   #", " ### "],
    "H": ["#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"],
    "I": [" ### ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "J": ["  ###", "    #", "    #", "    #", "    #", "#   #", " ### "],
    "K": ["#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"],
    "L": ["#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"],
    "M": ["#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"],
    "N": ["#   #", "#   #", "##  #", "# # #", "#  ##", "#   #", "#   #"],
    "O": [" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "P": ["#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "],
    "Q": [" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## # "],
    "R": ["#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"],
    "S": [" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "],
    "T": ["#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "],
    "U": ["#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "],
    "V": ["#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "],
    "W": ["#   #", "#   #", "#   #", "# # #", "# # #", "# # #", " # # "],
    "X": ["#   #", " # # ", " # # ", "  #  ", " # # ", " # # ", "#   #"],
    "Y": ["#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "],
    "Z": ["#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"],
    "0": [" ### ", "#  ##", "# # #", "# # #", "##  #", "#   #", " ### "],
    "1": ["  #  ", " ##  ", "# #  ", "  #  ", "  #  ", "  #  ", " ### "],
    "2": [" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"],
    "3": ["#### ", "    #", "    #", " ### ", "    #", "    #", "#### "],
    "4": ["   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "],
    "5": ["#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "],
    "6": [" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "],
    "7": ["#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "],
    "8": [" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "],
    "9": [" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "],
    ".": ["     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "],
    ",": ["     ", "     ", "     ", "     ", " ##  ", " ##  ", "#    "],
    "'": [" ##  ", " ##  ", "#    ", "     ", "     ", "     ", "     "],
    "-": ["     ", "     ", "     ", "#####", "     ", "     ", "     "],
    ":": ["     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "],
    ";": ["     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "#    "],
    "!": [" ##  ", " ##  ", " ##  ", " ##  ", " ##  ", "     ", " ##  "],
    "?": [" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "],
    "/": ["    #", "    #", "   # ", "   # ", "  #  ", " #   ", " #   "],
    "(": ["   ##", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   ##"],
    ")": ["##   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", "##   "],
    "+": ["     ", "     ", "  #  ", "#####", "  #  ", "     ", "     "],
    "%": ["##  #", "## # ", "   # ", "  #  ", " #   ", " # ##", "#  ##"],
    "$": [" ####", "# #  ", "# #  ", " ### ", "  # #", "  # #", "#### "],
    " ": ["     ", "     ", "     ", "     ", "     ", "     ", "     "],
}

CELL_W = 6  # glyph advance in font units: 5 px of glyph + 1 px of air
CELL_H = 7


def text_width(text, scale):
    """Pixel width of a line of text at the given integer scale."""
    if not text:
        return 0
    return (len(text) * CELL_W - 1) * scale


def draw_text(cv, x, y, text, scale, colour):
    """Draw one line of text with its top-left corner at (x, y)."""
    text = text.upper()
    for i, ch in enumerate(text):
        glyph = GLYPHS.get(ch)
        if glyph is None:
            # Unknown character: a hollow block, so a typo is visible.
            cv.frame(x + i * CELL_W * scale, y, 5 * scale, 7 * scale,
                     colour, max(1, scale // 2))
            continue
        gx = x + i * CELL_W * scale
        for r, row in enumerate(glyph):
            for c, cell in enumerate(row):
                if cell == "#":
                    cv.fill_rect(gx + c * scale, y + r * scale,
                                 scale, scale, colour)
    return CELL_H * scale


def wrap(text, scale, max_width):
    """Greedy word wrap: split text into lines that fit max_width."""
    lines = []
    current = ""
    for word in text.upper().split():
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_block(cv, x, y, text, scale, colour, max_width, pitch):
    """Draw wrapped text; returns the height it occupied."""
    lines = wrap(text, scale, max_width)
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * pitch, line, scale, colour)
    return len(lines) * pitch


def draw_centred(cv, y, text, scale, colour, width):
    x = (width - text_width(text, scale)) // 2
    draw_text(cv, x, y, text, scale, colour)
    return CELL_H * scale


# ---------------------------------------------------------------- icons
# Small geometric pictograms, drawn in a box of about 54x40 px at (x, y).

def icon_rings(cv, x, y, colour):
    """Three overlapping rings: three powers around one table."""
    cv.ring(x + 16, y + 20, 13, colour, 3)
    cv.ring(x + 38, y + 20, 13, colour, 3)
    cv.ring(x + 27, y + 32, 13, colour, 3)


def icon_bridge(cv, x, y, colour):
    """A suspension bridge: two towers, a deck and hanging cables."""
    cv.fill_rect(x + 10, y + 4, 4, 32, colour)
    cv.fill_rect(x + 40, y + 4, 4, 32, colour)
    cv.fill_rect(x, y + 34, 54, 4, colour)
    cv.line(x + 12, y + 4, x + 27, y + 18, colour, 2)
    cv.line(x + 27, y + 18, x + 42, y + 4, colour, 2)
    cv.fill_rect(x + 18, y + 10, 2, 24, colour)
    cv.fill_rect(x + 26, y + 18, 2, 16, colour)
    cv.fill_rect(x + 36, y + 10, 2, 24, colour)


def icon_tent(cv, x, y, colour):
    """An aid tent under a medical cross: shelter for the displaced."""
    cv.fill_rect(x + 25, y, 4, 11, colour)
    cv.fill_rect(x + 21, y + 3, 12, 4, colour)
    cv.line(x + 4, y + 40, x + 27, y + 14, colour, 3)
    cv.line(x + 27, y + 14, x + 50, y + 40, colour, 3)
    cv.fill_rect(x + 2, y + 40, 50, 3, colour)


def icon_leaf(cv, x, y, colour):
    """A leaf on a stem: the climate talks."""
    cv.line(x + 10, y + 40, x + 44, y + 6, colour, 3)
    cv.line(x + 10, y + 40, x + 12, y + 18, colour, 3)
    cv.line(x + 12, y + 18, x + 30, y + 8, colour, 3)
    cv.line(x + 44, y + 6, x + 34, y + 30, colour, 3)
    cv.line(x + 34, y + 30, x + 16, y + 38, colour, 3)
    cv.line(x + 14, y + 36, x + 36, y + 12, colour, 1)


ICONS = {
    "rings": icon_rings,
    "bridge": icon_bridge,
    "tent": icon_tent,
    "leaf": icon_leaf,
}


# ---------------------------------------------------------------- the page

PAPER = (246, 241, 227)
CARD = (255, 254, 249)
INK = (22, 24, 29)
SOFT = (52, 55, 62)
RED = (190, 18, 44)
FAINT = (203, 196, 178)

W = 1024
H = 1024
MARGIN = 36
CW = W - 2 * MARGIN  # 952 px of content width


def panel(cv, x, y, w, h, story, headline_scale, body_scale,
          headline_pitch, body_pitch, icon=None):
    """One news card: tag, optional icon, headline, then the essence."""
    cv.fill_rect(x, y, w, h, CARD)
    cv.frame(x, y, w, h, INK, 3)
    pad = 16
    draw_text(cv, x + pad, y + 14, story["tag"], 3, RED)
    if icon is not None:
        ICONS[icon](cv, x + w - 70, y + 8, INK)
    ty = y + 14 + CELL_H * 3 + 7
    head_w = w - 2 * pad - (60 if icon is not None else 0)
    used = draw_block(cv, x + pad, ty, story["headline"], headline_scale,
                      INK, head_w, headline_pitch)
    by = ty + used + 8
    draw_block(cv, x + pad, by, story["body"], body_scale, SOFT,
               w - 2 * pad, body_pitch)


def compose(data):
    cv = Canvas(W, H, PAPER)

    # Masthead: red rule, strap line, the date in the biggest type on
    # the page, then the weekday between two rules. The judge is not
    # told the day, so the date has to shout.
    cv.fill_rect(MARGIN, 24, CW, 12, RED)
    draw_centred(cv, 50, data["strap"], 3, INK, W)
    draw_centred(cv, 82, data["date"], 9, INK, W)
    wy = 158
    label = data["weekday"]
    lw = text_width(label, 4)
    lx = (W - lw) // 2
    cv.fill_rect(MARGIN, wy + 12, lx - MARGIN - 24, 4, INK)
    cv.fill_rect(lx + lw + 24, wy + 12, W - MARGIN - lx - lw - 24, 4, INK)
    draw_text(cv, lx, wy, label, 4, RED)

    # The lead story, full width.
    lead_y = 202
    lead_h = 254
    cv.fill_rect(MARGIN, lead_y, CW, lead_h, CARD)
    cv.frame(MARGIN, lead_y, CW, lead_h, INK, 4)
    lead = data["lead"]
    draw_text(cv, MARGIN + 20, lead_y + 16, lead["tag"], 3, RED)
    used = draw_block(cv, MARGIN + 20, lead_y + 42, lead["headline"], 8,
                      INK, CW - 40, 64)
    draw_block(cv, MARGIN + 20, lead_y + 42 + used + 12, lead["body"], 4,
               SOFT, CW - 40, 33)

    # Four more stories in a two-by-two grid.
    grid_y = lead_y + lead_h + 14
    cell_w = (CW - 14) // 2
    cell_h = 168
    for i, story in enumerate(data["panels"]):
        px = MARGIN + (i % 2) * (cell_w + 14)
        py = grid_y + (i // 2) * (cell_h + 12)
        panel(cv, px, py, cell_w, cell_h, story, 4, 3, 34, 26,
              icon=story.get("icon"))

    # Bottom band: the sport story and a list of shorter items.
    band_y = grid_y + 2 * cell_h + 12 + 14
    band_h = H - band_y - 16
    sport_w = 300
    panel(cv, MARGIN, band_y, sport_w, band_h, data["sport"], 4, 3, 34, 26)
    ax = MARGIN + sport_w + 14
    aw = W - MARGIN - ax
    cv.fill_rect(ax, band_y, aw, band_h, CARD)
    cv.frame(ax, band_y, aw, band_h, INK, 3)
    draw_text(cv, ax + 16, band_y + 12, data["also_heading"], 3, RED)
    iy = band_y + 12 + CELL_H * 3 + 11
    for item in data["also"]:
        cv.fill_rect(ax + 16, iy + 6, 10, 10, RED)
        used = draw_block(cv, ax + 38, iy, item, 3, INK, aw - 54, 26)
        iy += used + 9
    return cv


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "headlines.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    cv = compose(data)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    save_png(os.path.join(out_dir, "entry.png"), W, H, cv.rows)


if __name__ == "__main__":
    main()
