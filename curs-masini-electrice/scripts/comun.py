"""Stil comun pentru figuri și funcția de salvare."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

FIGURI = Path(__file__).resolve().parent.parent / "figuri"
FIGURI.mkdir(exist_ok=True)

# Paleta categorială (ordine fixă) și culorile de text / grilă
C1, C2, C3, C4, C5 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#6250d6"
SERII = [C1, C2, C3, C4, C5]
TEXT, TEXT2, GRILA, FUNDAL = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": FUNDAL,
    "axes.facecolor": FUNDAL,
    "savefig.facecolor": FUNDAL,
    "font.size": 10,
    "font.family": "DejaVu Sans",
    "axes.edgecolor": TEXT2,
    "axes.labelcolor": TEXT,
    "axes.titlesize": 11,
    "axes.titleweight": "bold",
    "axes.titlecolor": TEXT,
    "axes.grid": True,
    "grid.color": GRILA,
    "grid.linewidth": 0.8,
    "grid.linestyle": "-",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": TEXT2,
    "ytick.color": TEXT2,
    "lines.linewidth": 2.0,
    "lines.solid_capstyle": "round",
    "legend.frameon": False,
    "svg.fonttype": "path",
    "svg.hashsalt": "curs-masini-electrice",   # SVG reproductibil
    "axes.formatter.use_locale": False,
})


def virgula(ax, axe="xy"):
    """Virgulă zecimală pe axe (convenția românească)."""
    f = FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    if "x" in axe:
        ax.xaxis.set_major_formatter(f)
    if "y" in axe:
        ax.yaxis.set_major_formatter(f)


def salveaza(fig, nume):
    cale = FIGURI / f"{nume}.svg"
    fig.savefig(cale, format="svg", bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)
    print(f"  figura {cale.name}")
    return cale


def sageata(ax, z0, z1, culoare, eticheta=None, offset=(0, 0), lw=2.0, ha="left", va="bottom", fs=10, t=0.5):
    """Desenează un fazor de la z0 la z1 (numere complexe) cu etichetă opțională."""
    ax.annotate("", xy=(z1.real, z1.imag), xytext=(z0.real, z0.imag),
                arrowprops=dict(arrowstyle="-|>", color=culoare, lw=lw, mutation_scale=14,
                                shrinkA=0, shrinkB=0))
    if eticheta:
        zm = z0 + t * (z1 - z0)
        ax.annotate(eticheta, xy=(zm.real, zm.imag), xytext=offset, textcoords="offset points",
                    color=TEXT, ha=ha, va=va, fontsize=fs)
