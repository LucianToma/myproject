"""Figurile capitolului 9 – Automatizarea stațiilor."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, ZONA, salveaza, bloc, legatura, virgula
from calcul_cap09 import unghi_din_timp, tve_faza, momente_goose, SUPLIMENT_FIR

# --- Figura 9.1: nivelurile automatizării unei stații ------------------------
fig, ax = plt.subplots(figsize=(11, 7.2))
ax.set_xlim(0, 11)
ax.set_ylim(0, 7.4)
ax.axis("off")
niveluri = [(6.05, "Dispecer\n(centrul de\nconducere)"), (4.25, "Nivelul\nstației"), (2.3, "Nivelul\ncelulei"),
            (0.25, "Nivelul\nprocesului")]
for y, txt in niveluri:
    ax.text(0.15, y + 0.55, txt, ha="left", va="center", fontsize=9.5, color=TEXT, fontweight="bold")
for y in (5.75, 3.95, 2.05):
    ax.plot([0.1, 10.9], [y, y], color=GRILA, lw=1.2, ls="--")
# dispecer
bloc(ax, 3.2, 6.15, 3.0, 0.95, "SCADA / EMS / DMS\n(operatori, aplicații de rețea)", C1)
bloc(ax, 7.0, 6.15, 2.6, 0.95, "alte stații", TEXT2)
legatura(ax, (4.7, 6.15), (4.7, 5.3), stil="<|-|>")
ax.text(4.8, 5.85, "IEC 60870-5-104\n(TCP, port 2404)", ha="left", va="center", fontsize=8, color=TEXT2)
legatura(ax, (8.3, 6.15), (9.3, 5.3), stil="<|-|>")
ax.text(8.9, 5.85, "teleprotecție", ha="left", va="center", fontsize=8, color=TEXT2)
# stația
bloc(ax, 1.6, 4.3, 2.0, 1.0, "Calculatorul\nstației (HMI)", C5)
bloc(ax, 3.9, 4.3, 1.8, 1.0, "Poarta de\ncomunicație\n(gateway)", C5)
bloc(ax, 6.0, 4.3, 1.7, 1.0, "Sursa de timp\n(GNSS)\nPTP / IRIG-B", C4)
bloc(ax, 8.0, 4.3, 2.6, 1.0, "Teleprotecție, înregistrare\nde perturbații, acces la\ndistanță (prin firewall)", C5)
ax.plot([1.6, 10.6], [4.05, 4.05], color=C1, lw=3)
ax.text(10.6, 3.83, "magistrala stației (Ethernet): MMS, GOOSE", ha="right", va="top", fontsize=8.5, color=C1,
        bbox=dict(fc=FUNDAL, ec="none", pad=1.5), zorder=5)
for x in (2.6, 4.8, 6.85, 9.3):
    ax.plot([x, x], [4.3, 4.05], color=C1, lw=1.4)
# celula
for i, (txt, c) in enumerate((("IED protecție\nlinie (21, 79)", C2), ("IED protecție\ntrafo (87T)", C2),
                              ("Unitate de comandă\na celulei (CSWI)", C3), ("IED protecție\nfider (50/51)", C2))):
    x = 1.6 + i * 2.3
    bloc(ax, x, 2.35, 2.0, 1.0, txt, c)
    ax.plot([x + 1.0, x + 1.0], [3.35, 4.05], color=C1, lw=1.4)
ax.plot([1.6, 10.6], [1.85, 1.85], color=C3, lw=3)
ax.text(10.6, 1.63, "magistrala de proces: valori eșantionate (SV), GOOSE", ha="right", va="top", fontsize=8.5, color=C3,
        bbox=dict(fc=FUNDAL, ec="none", pad=1.5), zorder=5)
for i in range(4):
    x = 1.6 + i * 2.3 + 1.0
    ax.plot([x, x], [2.35, 1.85], color=C3, lw=1.4)
# procesul
bloc(ax, 1.6, 0.25, 2.6, 1.0, "Unitate de îmbinare (MU)\nTC, TT → eșantioane", C3)
bloc(ax, 4.6, 0.25, 2.6, 1.0, "Unitate de interfață\na întrerupătorului\n(poziții, comenzi)", C3)
bloc(ax, 7.6, 0.25, 3.0, 1.0, "Aparatajul primar: întrerupătoare,\nseparatoare, transformatoare\nde măsură", TEXT2)
for x in (2.9, 5.9):
    ax.plot([x, x], [1.25, 1.85], color=C3, lw=1.4)
legatura(ax, (7.2, 0.75), (7.6, 0.75), stil="<|-|>")
salveaza(fig, "f09-1-arhitectura")

# --- Figura 9.2: modelul de date IEC 61850 (exemplu ilustrativ) ---------------
fig, ax = plt.subplots(figsize=(12, 5.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.4)
ax.axis("off")
niv = ["Server\n(IED-ul fizic)", "Dispozitiv\nlogic (LD)", "Nod logic\n(LN)", "Obiect de\ndate (DO)", "Atribut de\ndate (DA)"]
for i, t in enumerate(niv):
    ax.text(0.95 + i * 2.15, 5.15, t, ha="center", va="center", fontsize=9, color=TEXT2, fontweight="bold")
bloc(ax, 0.2, 2.2, 1.5, 0.8, "IED_F1\n(releul R1)", C5)
noduri = {
    "PROT": (2.35, 3.35), "CTRL": (2.35, 1.0),
    "PTOC1": (4.5, 4.0), "PTRC1": (4.5, 2.75), "XCBR1": (4.5, 1.55), "CSWI1": (4.5, 0.35),
    "Str": (6.65, 4.3), "Op": (6.65, 3.55), "Pos": (6.65, 1.55),
    "general": (8.8, 4.3), "q, t": (8.8, 3.55), "stVal": (8.8, 1.85), "q, t ": (8.8, 1.2),
}
culori = {"PROT": C2, "CTRL": C3, "PTOC1": C2, "PTRC1": C2, "XCBR1": C3, "CSWI1": C3, "Str": C1, "Op": C1, "Pos": C1,
          "general": C4, "q, t": C4, "stVal": C4, "q, t ": C4}
for k, (x, y) in noduri.items():
    bloc(ax, x, y, 1.5, 0.55, k.strip(), culori[k], fs=9)
muchii = [((1.7, 2.6), "PROT"), ((1.7, 2.6), "CTRL"), ("PROT", "PTOC1"), ("PROT", "PTRC1"), ("CTRL", "XCBR1"),
          ("CTRL", "CSWI1"), ("PTOC1", "Str"), ("PTOC1", "Op"), ("XCBR1", "Pos"), ("Op", "general"), ("Op", "q, t"),
          ("Pos", "stVal"), ("Pos", "q, t ")]
for a, b in muchii:
    pa = a if isinstance(a, tuple) else (noduri[a][0] + 1.5, noduri[a][1] + 0.275)
    pb = (noduri[b][0], noduri[b][1] + 0.275)
    ax.plot([pa[0], pb[0]], [pa[1], pb[1]], color=TEXT2, lw=1.0)
ax.text(10.4, 4.57, "„declanșare”\n(adevărat/fals)", ha="left", va="center", fontsize=8, color=TEXT2)
ax.text(10.4, 2.12, "poziția\nîntrerupătorului", ha="left", va="center", fontsize=8, color=TEXT2)
ax.text(10.4, 1.47, "calitatea și\nmarca de timp", ha="left", va="center", fontsize=8, color=TEXT2)
ax.text(6.0, -0.05, "Exemple de referințe: IED_F1PROT/PTOC1.Op.general    IED_F1CTRL/XCBR1.Pos.stVal",
        ha="center", va="bottom", fontsize=9.5, color=TEXT, family="DejaVu Sans Mono")
salveaza(fig, "f09-2-model-date")

# --- Figura 9.4: fluxul de inginerie cu fișiere SCL --------------------------
fig, ax = plt.subplots(figsize=(11, 4.0))
ax.set_xlim(0, 11)
ax.set_ylim(0, 4.0)
ax.axis("off")
bloc(ax, 0.1, 2.7, 2.1, 0.9, "SSD\nspecificația stației\n(schemă, funcții)", C1, fs=8.5)
bloc(ax, 0.1, 0.4, 2.1, 0.9, "ICD / IID\ncapabilitățile fiecărui\ntip de IED (producător)", C2, fs=8.5)
bloc(ax, 3.0, 1.55, 2.2, 1.0, "Configuratorul\nde sistem", C5)
bloc(ax, 6.0, 1.6, 1.6, 0.9, "SCD\nconfigurația\ntotală", C1, fs=8.5)
bloc(ax, 8.4, 1.55, 2.4, 1.0, "Configuratorul IED-ului\n(instrumentul\nproducătorului)", C5)
bloc(ax, 8.6, 0.05, 2.0, 0.8, "CID → IED", C3, fs=9)
bloc(ax, 6.0, 3.0, 1.6, 0.7, "SED (schimb\nîntre proiecte)", TEXT2, fs=8)
legatura(ax, (2.2, 3.15), (3.0, 2.3))
legatura(ax, (2.2, 0.85), (3.0, 1.8))
legatura(ax, (5.2, 2.05), (6.0, 2.05))
legatura(ax, (7.6, 2.05), (8.4, 2.05))
legatura(ax, (9.6, 1.55), (9.6, 0.85))
legatura(ax, (6.8, 2.5), (6.8, 3.0), stil="<|-|>")
ax.plot([8.7, 8.7, 2.45], [1.55, 1.1, 1.1], color=TEXT2, lw=1.0, ls="--")
legatura(ax, (2.45, 1.1), (2.2, 1.1))
ax.text(5.6, 0.95, "IID: IED-ul configurat se întoarce în configuratorul de sistem", ha="center", va="top",
        fontsize=8, color=TEXT2)
salveaza(fig, "f09-4-flux-scl")

# --- Figura 9.3: programul de retransmisie GOOSE (exemplu de configurare) ------
emis = momente_goose(0.002, 1.0, 14)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 4.8), gridspec_kw=dict(height_ratios=[1, 1]))
# a1: imaginea de ansamblu – bătăi de inimă la 1 s, eveniment la t = 0
batai = np.arange(-3.0, 0.0, 1.0)
toate = np.concatenate((batai, emis[emis < 4.0]))
for t in toate:
    a1.plot([t, t], [0, 1], color=C1 if t >= 0 else TEXT2, lw=1.4)
a1.set_xlim(-3.2, 4.2)
a1.set_ylim(0, 1.5)
a1.set_yticks([])
a1.axvline(0, color=C2, lw=1.4, ls="--")
a1.text(0.04, 1.32, "schimbare de stare (stNum crește, sqNum = 0)", color=C2, fontsize=8.5, ha="left")
a1.text(-3.1, 1.22, "„bătăi de inimă” la T0 = 1 s\n(sqNum crește)", color=TEXT2, fontsize=8.5, ha="left", va="center")
a1.set_xlabel("timp [s]")
a1.grid(axis="y", visible=False)
virgula(a1, "x")
# a2: primele 300 ms
for i, t in enumerate(emis[emis < 0.3]):
    a2.plot([t * 1e3, t * 1e3], [0, 1], color=C1, lw=1.8)
    # etichetele primelor mesaje sunt așezate pe două rânduri, ca să nu se suprapună
    a2.text(t * 1e3, 1.05 if i % 2 == 0 else 1.3, f"{t * 1e3:.0f}", ha="center", va="bottom", fontsize=8,
            color=TEXT)
    if i % 2 == 1:
        a2.plot([t * 1e3, t * 1e3], [1.0, 1.28], color=GRILA, lw=0.8)
a2.set_xlim(-8, 300)
a2.set_ylim(0, 1.6)
a2.set_yticks([])
a2.set_xlabel("timp după eveniment [ms] – mesaje la 2 ms, apoi intervalul se dublează")
a2.grid(axis="y", visible=False)
fig.tight_layout()
salveaza(fig, "f09-3-goose-retransmisie")

# --- Figura 9.5: eroarea de fază și TVE în funcție de eroarea de timp ----------
dt = np.logspace(-7, -3, 300)
th = np.degrees(unghi_din_timp(dt))
tve = 100 * tve_faza(unghi_din_timp(dt))
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.loglog(dt * 1e6, th, color=C1, label="eroarea de fază [°]")
ax.loglog(dt * 1e6, tve, color=C2, label="TVE [%] (numai eroare de fază)")
for x, txt in ((1.0, "1 µs → 0,018°"), (31.83, "31,8 µs → TVE = 1 %"), (63.7, "63,7 µs → 2 %")):
    ax.axvline(x, color=TEXT2, lw=0.8, ls=":")
    ax.text(x * 1.08, 0.0012, txt, rotation=90, ha="left", va="bottom", fontsize=8, color=TEXT2)
ax.set_xlabel("eroarea de sincronizare a timpului Δt [µs]")
ax.set_ylabel("eroare")
ax.set_title("Efectul erorii de timp la 50 Hz")
ax.legend(loc="upper left")
ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
salveaza(fig, "f09-5-eroare-timp")

# --- Figura 9.6: bugetul de timp al blocării prin GOOSE (problema 9.3) ---------
t_porn, t_pub, t_sub, t_ciclu = 20.0, 1.0, 1.0, 1.0
t_retea = (3 * (150 + SUPLIMENT_FIR) * 8 / 100e6 + 2 * 5e-6) * 1e3
etape = [("pornirea releului R1", t_porn, C1), ("publicator", t_pub, C5), ("rețea", t_retea, C3),
         ("abonat", t_sub, TEXT2), ("ciclul logicii R0", t_ciclu, C4)]
fig, ax = plt.subplots(figsize=(10, 3.2))
x = 0.0
for nume, d_, c in etape:
    ax.barh(1, d_, left=x, height=0.5, color=c, edgecolor=FUNDAL)
    x += d_
ax.text(x + 1.5, 1, f"blocare aplicată la {x:.2f} ms".replace(".", ","), va="center", ha="left", fontsize=9, color=TEXT)
# mesajele repetate: dacă primele k mesaje se pierd
for k, t in enumerate(momente_goose(0.002, 1.0, 8)[:7]):
    tb = t_porn + t_pub + t * 1e3 + t_retea + t_sub + t_ciclu
    ax.plot([tb], [0.35], marker="v", color=C2 if tb <= 100 else TEXT2, ms=8)
    ax.text(tb, 0.12, f"{k}", ha="center", va="center", fontsize=8, color=TEXT2)
ax.text(0, 0.12, "mesaje pierdute:", ha="right", va="center", fontsize=8, color=TEXT2)
ax.axvline(100, color=C2, lw=1.6, ls="--")
ax.text(101, 1.45, "R0 ar declanșa la 100 ms", ha="left", va="center", fontsize=9, color=C2)
ax.set_xlim(-14, 160)
ax.set_ylim(-0.1, 1.7)
ax.spines["left"].set_visible(False)
ax.set_yticks([])
ax.set_xlabel("timp de la apariția defectului pe fider [ms]")
ax.grid(axis="y", visible=False)
for nume, d_, c in etape:
    ax.plot([], [], color=c, lw=8, label=nume)
ax.legend(loc="upper center", ncol=5, fontsize=8, bbox_to_anchor=(0.45, 1.25))
salveaza(fig, "f09-6-buget-blocare")
