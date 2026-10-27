"""Capitolul 9 – Automatizarea stațiilor: funcții de calcul comune problemelor și figurilor.

Toate timpii sunt în secunde, debitele în bit/s, lungimile cadrelor în octeți.
"""

import numpy as np

# Pe fir, fiecare cadru Ethernet mai ocupă preambulul cu delimitatorul de început (8 octeți)
# și pauza minimă dintre cadre (12 octeți) – IEEE 802.3.
SUPLIMENT_FIR = 8 + 12


# ---------------------------------------------------------------------------
# 9.1 – eroarea de sincronizare a timpului: unghi și TVE
# ---------------------------------------------------------------------------

def unghi_din_timp(dt, f=50.0):
    """Eroarea de fază [rad] produsă de o eroare de timp dt la frecvența f."""
    return 2 * np.pi * f * dt


def tve_faza(theta):
    """TVE pentru o eroare pur de fază (amplitudinea exactă): |e^{jθ} − 1| = 2·sin(θ/2)."""
    return 2 * np.sin(np.asarray(theta) / 2)


def tve_dft(dt, f=50.0, fs=4000.0, phi=0.3, cicluri=1, amplitudine=1.0):
    """Calea numerică: semnalul √2·A·cos(ωt + φ) este eșantionat cu un ceas decalat cu dt
    (eșantionul n este luat la n·Ts + dt, dar etichetat cu n·Ts). Fazorul se estimează cu
    transformata Fourier discretă pe un număr întreg de cicluri; se întoarce TVE și eroarea de fază."""
    N = int(round(fs / f)) * cicluri
    n = np.arange(N)
    tn = n / fs
    x = np.sqrt(2) * amplitudine * np.cos(2 * np.pi * f * (tn + dt) + phi)
    X_est = np.sqrt(2) / N * np.sum(x * np.exp(-1j * 2 * np.pi * f * tn))
    X_ref = amplitudine * np.exp(1j * phi)
    return abs(X_est - X_ref) / abs(X_ref), np.angle(X_est / X_ref)


# ---------------------------------------------------------------------------
# 9.2 – traficul de valori eșantionate (SV) pe magistrala de proces
# ---------------------------------------------------------------------------

def debit_sv(esantioane_pe_s, asdu_pe_cadru, L_cadru):
    """Cadre pe secundă și debitul pe fir [bit/s] al unui flux SV."""
    cadre = esantioane_pe_s / asdu_pe_cadru
    return cadre, cadre * (L_cadru + SUPLIMENT_FIR) * 8


def simuleaza_port(N, cadre_pe_s, L_cadru, C=100e6, durata=1.0, decalaje=None):
    """Simulare pe evenimente a portului de ieșire al unui comutator (coadă FIFO) spre care
    trimit N unități de îmbinare. Fiecare cadru ocupă linia (L + 20)·8/C secunde.
    decalaje: decalajul de fază al fiecărui flux în intervalul dintre cadre (None = toate
    eșantionează în același moment, cum se întâmplă când sunt sincronizate).
    Întoarce gradul de încărcare (timp ocupat / durată) și întârzierea maximă în coadă."""
    Tc = 1.0 / cadre_pe_s
    t_cadru = (L_cadru + SUPLIMENT_FIR) * 8 / C
    if decalaje is None:
        decalaje = np.zeros(N)
    sosiri = np.sort(np.concatenate([np.arange(0, durata, Tc) + decalaje[k] * Tc for k in range(N)]))
    liber = 0.0          # momentul în care linia devine liberă
    ocupat = 0.0
    intarziere_max = 0.0
    for ts in sosiri:
        start = max(ts, liber)
        sfarsit = start + t_cadru
        intarziere_max = max(intarziere_max, sfarsit - ts)
        ocupat += t_cadru
        liber = sfarsit
    return ocupat / durata, intarziere_max, t_cadru


# ---------------------------------------------------------------------------
# 9.3 – mesajele GOOSE: programul de retransmisie și supravegherea
# ---------------------------------------------------------------------------

def intervale_goose(T_min=0.002, T0=1.0, n=14):
    """Intervalele dintre mesajele care urmează unei schimbări de stare (exemplu de configurare):
    primul interval T_min, apoi dublare până la T0 (intervalul de „bătaie de inimă”)."""
    iv = []
    T = T_min
    while len(iv) < n:
        iv.append(min(T, T0))
        T *= 2
    return np.array(iv)


def momente_goose(T_min=0.002, T0=1.0, n=14):
    """Momentele de emisie după eveniment (primul mesaj la t = 0)."""
    return np.concatenate(([0.0], np.cumsum(intervale_goose(T_min, T0, n))))


def sosire_dupa_pierderi(k, t_pub, t_retea, t_sub, T_min=0.002, T0=1.0):
    """Momentul în care abonatul primește informația dacă primele k mesaje s-au pierdut
    (măsurat de la apariția informației la publicator)."""
    return t_pub + momente_goose(T_min, T0, k + 2)[k] + t_retea + t_sub


def simuleaza_pierderi(p, t_pub, t_retea, t_sub, incercari, rng, T_min=0.002, T0=1.0, n=40):
    """Monte Carlo: fiecare mesaj se pierde independent cu probabilitatea p; se întoarce
    momentul primirii primului mesaj reușit, pentru fiecare încercare."""
    t_emis = momente_goose(T_min, T0, n)
    pierdut = rng.random((incercari, len(t_emis))) < p
    primul = np.argmax(~pierdut, axis=1)            # indicele primului mesaj primit
    return t_pub + t_emis[primul] + t_retea + t_sub


def detectie_pierdere_legatura(t_cadere, T0, TAL):
    """Abonatul declară informația invalidă dacă nu primește niciun mesaj timp de TAL de la ultimul
    mesaj primit. În regim staționar mesajele vin la multipli de T0. Se întoarce întârzierea
    detecției față de momentul căderii legăturii."""
    ultimul = np.floor(t_cadere / T0) * T0
    return ultimul + TAL - t_cadere


# ---------------------------------------------------------------------------
# 9.4 – disponibilitatea căilor de comunicație
# ---------------------------------------------------------------------------

def indisponibilitate(MTBF, MTTR):
    return MTTR / (MTBF + MTTR)


def intervale_defect(MTBF, MTTR, T, rng):
    """Proces de reînnoire alternant (timpi exponențiali): intervalele de defect [început, sfârșit)
    pe orizontul T [h]."""
    n = int(T / MTBF * 1.2) + 100
    sus = rng.exponential(MTBF, n)
    jos = rng.exponential(MTTR, n)
    inceput = np.cumsum(sus + np.concatenate(([0.0], jos[:-1])))
    sfarsit = inceput + jos
    m = inceput < T
    return inceput[m], np.minimum(sfarsit[m], T)


def intersectie(a0, a1, b0, b1):
    """Intervalele în care ambele procese sunt în defect (fiecare listă e sortată și disjunctă)."""
    out0, out1 = [], []
    i = j = 0
    while i < len(a0) and j < len(b0):
        s = max(a0[i], b0[j])
        e = min(a1[i], b1[j])
        if s < e:
            out0.append(s)
            out1.append(e)
        if a1[i] < b1[j]:
            i += 1
        else:
            j += 1
    return np.array(out0), np.array(out1)


def reuniune_lungime(a0, a1, b0, b1):
    """Lungimea totală a reuniunii a două mulțimi de intervale."""
    s = np.concatenate((a0, b0))
    e = np.concatenate((a1, b1))
    ordine = np.argsort(s)
    s, e = s[ordine], e[ordine]
    total = 0.0
    cs, ce = s[0], e[0]
    for x0, x1 in zip(s[1:], e[1:]):
        if x0 > ce:
            total += ce - cs
            cs, ce = x0, x1
        else:
            ce = max(ce, x1)
    return total + ce - cs
