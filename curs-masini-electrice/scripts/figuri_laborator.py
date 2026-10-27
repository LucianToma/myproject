"""Schemele de montaj pentru îndrumarul de laborator."""

import schemdraw
import schemdraw.elements as elm
from schemdraw.elements.sources import Source
from schemdraw.segments import SegmentText, SegmentCircle
from comun import FUNDAL, FIGURI, TEXT2, salveaza_schema

schemdraw.use("matplotlib")
schemdraw.config(fontsize=12, bgcolor=FUNDAL, lw=1.6)


class Wattmetru(Source):
    """Wattmetru: bobina de curent în serie (elementul), bobina de tensiune legată separat."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.segments.append(SegmentText((0.5, 0), "W"))


class Cerc(elm.Element):
    def __init__(self, r=0.9, **kw):
        super().__init__(**kw)
        self.segments.append(SegmentCircle((0, 0), r))


def intrare(d, ypus=3.0):
    """Sursa reglabilă, ampermetrul, wattmetrul și voltmetrul de pe partea alimentată."""
    d.add(elm.SourceSin().at((0, 0)).up(ypus))
    d.add(elm.Label().at((-1.6, ypus / 2)).label("sursă\nreglabilă\n(AT)", fontsize=10))
    d.add(elm.MeterA().at((0, ypus)).right(2.4).label("$I$", loc="top", ofst=0.15))
    d.add(Wattmetru().at((2.4, ypus)).right(2.4).label("$P$", loc="top", ofst=0.15))
    d.add(elm.Line().at((3.6, ypus - 0.5)).to((3.6, 0)).linestyle("--"))
    d.add(elm.Label().at((3.75, 1.2)).label("bobina de\ntensiune a W", fontsize=9, color=TEXT2, halign="left"))
    d.add(elm.Dot().at((3.6, 0)))
    d.add(elm.Line().at((4.8, ypus)).to((6.0, ypus)))
    d.add(elm.Dot().at((6.0, ypus)))
    d.add(elm.MeterV().at((6.0, ypus)).down(ypus).label("$U$", loc="bottom", ofst=0.15))
    d.add(elm.Dot().at((6.0, 0)))
    d.add(elm.Line().at((0, 0)).to((7.5, 0)))


def transformator(d, ypus=3.0, x=8.0):
    d.add(elm.Line().at((6.0, ypus)).to((7.5, ypus)))
    d.add(elm.Line().at((7.5, ypus)).to((7.5, 2.3)))
    d.add(elm.Line().at((7.5, 2.3)).to((x, 2.3)))
    d.add(elm.Line().at((7.5, 0)).to((7.5, 0.7)))
    d.add(elm.Line().at((7.5, 0.7)).to((x, 0.7)))
    d.add(elm.Transformer(t1=4, t2=4).at((x, 0.7)))


# --- L1: încercarea de mers în gol ------------------------------------------
with schemdraw.Drawing(show=False) as d:
    intrare(d)
    transformator(d)
    d.add(elm.Label().at((7.85, 0.3)).label("JT", fontsize=10))
    d.add(elm.Label().at((9.15, 0.3)).label("ÎT", fontsize=10))
    d.add(elm.Line().at((9.0, 2.3)).to((10.5, 2.3)))
    d.add(elm.Line().at((9.0, 0.7)).to((10.5, 0.7)))
    d.add(elm.MeterV().at((10.5, 2.3)).down(1.6).label("$U_{20}$", loc="bottom", ofst=0.15))
    d.add(elm.Label().at((5.0, -0.9)).label("Secundarul este în gol (doar voltmetrul $V_2$, de impedanță mare).",
                                          fontsize=10, color=TEXT2))
    salveaza_schema(d, "fL-1-incercare-gol")

# --- L1: încercarea de scurtcircuit ---------------------------------------------
with schemdraw.Drawing(show=False) as d:
    intrare(d)
    transformator(d)
    d.add(elm.Label().at((7.85, 0.3)).label("ÎT", fontsize=10))
    d.add(elm.Label().at((9.15, 0.3)).label("JT", fontsize=10))
    d.add(elm.Line().at((9.0, 2.3)).to((10.5, 2.3)))
    d.add(elm.Line().at((9.0, 0.7)).to((10.5, 0.7)))
    d.add(elm.MeterA().at((10.5, 2.3)).down(1.6).label("$I_{2sc}$", loc="bottom", ofst=0.15))
    d.add(elm.Label().at((5.0, -0.9)).label("Secundarul este scurtcircuitat prin ampermetru; se pornește de la U = 0!",
                                          fontsize=10, color=TEXT2))
    salveaza_schema(d, "fL-2-incercare-scurtcircuit")

# --- Metoda celor două wattmetre (Aron) pentru motorul trifazat --------------------
with schemdraw.Drawing(show=False) as d:
    y = {"L1": 4.0, "L2": 2.5, "L3": 1.0}
    for L, yy in y.items():
        d.add(elm.Label().at((-0.5, yy)).label(L))
    d.add(elm.MeterA().at((0, 4.0)).right(2.4).label("$I$", loc="top", ofst=0.15))
    d.add(Wattmetru().at((2.4, 4.0)).right(2.4).label("$W_1$", loc="top", ofst=0.15))
    d.add(elm.Line().at((4.8, 4.0)).to((9.0, 4.0)))
    d.add(elm.Line().at((0, 2.5)).to((9.0, 2.5)))
    d.add(elm.Line().at((0, 1.0)).to((2.4, 1.0)))
    d.add(Wattmetru().at((2.4, 1.0)).right(2.4).label("$W_2$", loc="bottom", ofst=0.15))
    d.add(elm.Line().at((4.8, 1.0)).to((9.0, 1.0)))
    # bobinele de tensiune ale wattmetrelor sunt legate la faza L2
    d.add(elm.Line().at((3.6, 3.5)).to((3.6, 2.5)).linestyle("--"))
    d.add(elm.Dot().at((3.6, 2.5)))
    d.add(elm.Line().at((3.6, 1.5)).to((3.6, 2.5)).linestyle("--"))
    d.add(elm.Dot().at((6.0, 4.0)))
    d.add(elm.MeterV().at((6.0, 4.0)).down(1.5).label("$U$", loc="bottom", ofst=0.15))
    d.add(elm.Dot().at((6.0, 2.5)))
    for yy in (4.0, 2.5, 1.0):
        d.add(elm.Line().at((9.0, yy)).to((10.2, 2.5 + (yy - 2.5) * 0.35)))
    d.add(Cerc().at((11.0, 2.5)))
    d.add(elm.Label().at((11.0, 2.5)).label("M\n3~"))
    d.add(elm.Label().at((5.0, -0.9)).label("P = P$_{W1}$ + P$_{W2}$ (rețea cu trei conductoare, orice sarcină)",
                                          fontsize=10, color=TEXT2))
    salveaza_schema(d, "fL-3-metoda-aron")
