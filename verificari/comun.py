"""Utilitare comune pentru verificările numerice ale cursului.

Toate funcțiile folosesc doar numpy, ca verificările să poată fi rulate
oriunde există Python 3 + numpy.
"""
import math

import numpy as np

# Rezultatele tuturor verificărilor din sesiunea curentă: (descriere, ok).
REZULTATE = []


def verifica(descriere, obtinut, asteptat, tol_rel=1e-3, tol_abs=0.0):
    """Compară o valoare obținută numeric cu una așteptată (analitică).

    Testul trece dacă |obtinut - asteptat| <= max(tol_abs, tol_rel*|asteptat|).
    """
    eroare = abs(obtinut - asteptat)
    ok = eroare <= max(tol_abs, tol_rel * abs(asteptat))
    REZULTATE.append((descriere, ok))
    stare = "OK  " if ok else "EȘEC"
    if asteptat == 0 or (tol_abs > 0 and abs(asteptat) * tol_rel < tol_abs):
        err = f"eroare absolută = {eroare:.2e} (toleranță {tol_abs:g})"
    else:
        err = f"eroare relativă = {eroare / abs(asteptat):.2e}"
    print(f"  [{stare}] {descriere}: obținut = {obtinut:.6g}, "
          f"așteptat = {asteptat:.6g}, {err}")
    return ok


def verifica_conditie(descriere, conditie, detalii=""):
    """Înregistrează o verificare de tip adevărat/fals (ex. o inegalitate)."""
    REZULTATE.append((descriere, bool(conditie)))
    stare = "OK  " if conditie else "EȘEC"
    print(f"  [{stare}] {descriere}{': ' + detalii if detalii else ''}")
    return bool(conditie)


def titlu(text):
    print()
    print("=" * 78)
    print(text)
    print("=" * 78)


# ---------------------------------------------------------------------------
# Mărimi periodice: medie, efectiv (RMS), armonici
# ---------------------------------------------------------------------------
# Convenție: x conține N eșantioane uniforme pe EXACT o perioadă, fără
# punctul final (t_k = k*T/N, k = 0..N-1). Cu această convenție media
# aritmetică a eșantioanelor este regula dreptunghiului, iar FFT-ul are
# armonica n exact în binul n.

def medie(x):
    return float(np.mean(x))


def efectiv(x):
    """Valoarea efectivă (RMS) pe o perioadă."""
    return float(np.sqrt(np.mean(np.square(x))))


def armonici(x, nmax):
    """Amplitudinile (de vârf) ale armonicilor 0..nmax. Indexul 0 = media."""
    X = np.fft.rfft(np.asarray(x, float))
    N = len(x)
    amp = 2.0 * np.abs(X[: nmax + 1]) / N
    amp[0] = abs(X[0].real) / N
    return amp


def faza_armonica(x, n):
    """Faza armonicii n, pentru componenta scrisă ca A*cos(n*w*t + faza)."""
    X = np.fft.rfft(np.asarray(x, float))
    return float(np.angle(X[n]))


def thd(x, nmax=None):
    """THD față de fundamentală, folosind toate armonicile 2..nmax."""
    N = len(x)
    if nmax is None:
        nmax = N // 2 - 1
    a = armonici(x, nmax)
    return float(np.sqrt(np.sum(a[2:] ** 2)) / a[1])


def esantioane_perioada(N):
    """Unghiuri theta_k = 2*pi*k/N, k = 0..N-1 (o perioadă, fără capăt)."""
    return 2.0 * np.pi * np.arange(N) / N


# ---------------------------------------------------------------------------
# Exponențiala matricială (fără scipy)
# ---------------------------------------------------------------------------

def expm(M):
    """exp(M) prin scalare și ridicare la pătrat + serie Taylor de ordin 30.

    După scalare ||M/2^s||_inf <= 0.5, deci restul seriei Taylor este sub
    0.5^31/31! ~ 1e-43: practic exact în dublă precizie.
    """
    M = np.asarray(M, float)
    n = M.shape[0]
    norma = np.linalg.norm(M, ord=np.inf)
    s = 0
    if norma > 0.5:
        s = int(math.ceil(math.log2(norma / 0.5)))
    A = M / (2.0 ** s)
    E = np.eye(n)
    termen = np.eye(n)
    for k in range(1, 31):
        termen = termen @ A / k
        E = E + termen
    for _ in range(s):
        E = E @ E
    return E


def bessel_j(n, x, puncte=20001):
    """Funcția Bessel de speța I, J_n(x), din reprezentarea integrală
    J_n(x) = (1/pi) * integrala_0^pi cos(n*tau - x*sin(tau)) dtau.
    Integrare cu metoda trapezelor (integrand neted -> convergență rapidă).
    """
    tau = np.linspace(0.0, np.pi, puncte)
    f = np.cos(n * tau - x * np.sin(tau))
    return float(np.trapezoid(f, tau) / np.pi)
