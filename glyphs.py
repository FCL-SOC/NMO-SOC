"""Texto in formas mutatum (litterae ut viae), ut imagines ubique eodem modo appareant."""
import os
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
HERE = os.path.dirname(os.path.abspath(__file__))
class Face:
    def __init__(self, path, tag):
        self.f = TTFont(os.path.join(HERE, "fonts", path)); self.gs = self.f.getGlyphSet(); self.cm = self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm; self.tag = tag; self.used = {}
    def _g(self, ch):
        name = self.cm.get(ord(ch))
        if name is None: return None, 0
        adv = self.gs[name].width
        if ch not in self.used:
            pen = SVGPathPen(self.gs); self.gs[name].draw(pen)
            self.used[ch] = (f"{self.tag}{ord(ch):x}", pen.getCommands())
        return self.used[ch][0], adv
    def width(self, text, size, ls=0):
        return sum(self._g(c)[1] for c in text) * size / self.upm + ls * max(len(text) - 1, 0)
    def text(self, text, x, y, size, fill, anchor="start", ls=0, bold=0, extra=""):
        """Textus ad (x,y) lineam basalem; bold = crassitudo lineae in pixelis."""
        sc = size / self.upm; w = self.width(text, size, ls)
        x0 = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
        st = f' stroke="{fill}" stroke-width="{bold / sc:.1f}" stroke-linejoin="round"' if bold else ""
        o = ""; cx = 0
        for c in text:
            gid, adv = self._g(c)
            if gid: o += f'<use href="#{gid}" x="{cx:.0f}"/>'
            cx += adv + ls / sc
        return f'<g transform="translate({x0:.1f},{y:.1f}) scale({sc:.5f},{-sc:.5f})" fill="{fill}"{st}{extra}>{o}</g>'
    def defs(self):
        return "".join(f'<path id="{gid}" d="{d}"/>' for gid, d in self.used.values())
