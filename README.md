# Bazele electronicii de putere — curs introductiv

Un curs introductiv, în limba română, despre conversia energiei electrice cu
dispozitive semiconductoare: redresoare, convertoare DC-DC, invertoare,
dispozitive de putere, pierderi și calcul termic.

**Principiul cursului: nicio formulă nu este „crezută pe cuvânt”.**

1. **Derivare.** Relațiile sunt derivate în text, pornind de la principii
   (bilanțul volt-secundă, bilanțul de sarcină, integrale de medie și valoare
   efectivă, serii Fourier). Excepție: amplitudinile armonicilor PWM exprimate
   prin funcții Bessel, a căror derivare (analiza Fourier dublă) depășește
   nivelul cursului. Ele sunt citate din [B4] și verificate numeric.
2. **Verificare numerică independentă**: simularea exactă a circuitului,
   integrarea directă a formei de undă sau o a treia cale analitică. Rămân fără
   verificare numerică, și sunt marcate ca atare, doar relațiile pentru
   flyback/forward și formula inductanței unui fir drept (din literatură).
3. **Aproximările sunt marcate explicit**, cu eroarea măsurată. De exemplu,
   formula uzuală a ondulației filtrului capacitiv supraestimează cu 5–36 %, în
   funcție de $C$, iar cursul arată din ce două cauze provine diferența.

Starea curentă a verificărilor: **199 / 199 trecute**
(`python3 verificari/ruleaza_toate.py`).

## Cuprins

| # | Modul | Conținut |
|---|---|---|
| 1 | [Introducere](curs/01-introducere.md) | de ce comutație; regulator liniar vs. convertor în comutație; PWM; clasificarea convertoarelor |
| 2 | [Mărimi și relații fundamentale](curs/02-fundamente.md) | medie și RMS; putere, factor de putere, THD; bilanțul volt-secundă și de sarcină |
| 3 | [Dispozitive semiconductoare de putere](curs/03-dispozitive.md) | diodă, tiristor, MOSFET, IGBT, SiC, GaN; pierderi de conducție și comutație; comanda pe grilă |
| 4 | [Redresoare](curs/04-redresoare.md) | monofazat, trifazat, necomandat și comandat; filtru capacitiv; factor de putere; suprapunerea comutației |
| 5 | [Convertoare DC-DC](curs/05-convertoare-dc-dc.md) | buck, boost, buck-boost; CCM/DCM; dimensionarea L și C; limitele reale ale boost-ului; flyback/forward |
| 6 | [Invertoare](curs/06-invertoare.md) | semipunte, punte H, trifazat; undă dreptunghiulară; SPWM; bipolar/unipolar; injecția armonicii a 3-a |
| 7 | [Pierderi, termic, aspecte practice](curs/07-pierderi-termic-practica.md) | bilanț complet de pierderi; calcul termic; paraziți și layout; EMI; control; protecții; siguranță |
| 8 | [Exerciții rezolvate](curs/08-exercitii.md) | 12 probleme rezolvate; răspunsurile numerice sunt recalculate și, unde se poate, confirmate prin simulare |
| — | [Bibliografie](curs/bibliografie.md) | manuale, standarde și sursele datelor despre dispozitive |

**Cunoștințe necesare:** circuite electrice (legile lui Kirchhoff, R, L, C,
regim sinusoidal), noțiuni de analiză matematică (integrale, serii Fourier la
nivel de utilizare). **Ordinea recomandată:** 1 → 2 → 3 → 4/5/6 (pot fi
parcurse în orice ordine) → 7 → 8.

## Verificările numerice

Directorul [`verificari/`](verificari/) conține scripturile Python (doar
**numpy** este obligatoriu):

| Fișier | Ce verifică | Metoda independentă |
|---|---|---|
| `comun.py` | utilitare: medie, RMS, FFT, THD, $e^{A}$, funcții Bessel | — |
| `simulator_dcdc.py` | — | simulator exact pe porțiuni liniare (buck/boost/buck-boost), pornit din repaus până la regim permanent, cu detecția DCM |
| `v02_fundamente.py` | Modulul 2 | integrarea directă a formelor de undă |
| `v04_redresoare.py` | Modulul 4 | soluție exactă + simulare RK4 (filtru C), simularea tiristoarelor, construcția numerică a punții trifazate |
| `v05_dc_dc.py` | Modulul 5 | simulatorul exact; bilanțuri volt-secundă, de sarcină și de putere |
| `v06_invertoare.py` | Modulul 6 | FFT + coeficienți Fourier exacți din momentele de comutație + funcții Bessel |
| `v07_pierderi.py` | Modulele 1, 3, 7 | integrarea lui $v \cdot i$; simularea curenților; rețea termică tranzitorie |
| `v08_exercitii.py` | Modulul 8 | recalcul + simulare pentru fiecare exercițiu |
| `ruleaza_toate.py` | toate | rezumat; cod de ieșire ≠ 0 la orice eșec |
| `genereaza_figuri.py` | — | generează figurile din `figuri/` (necesită matplotlib) |

```bash
pip install -r requirements.txt        # numpy (+ matplotlib pentru figuri)
python3 verificari/ruleaza_toate.py    # ~25 s; afișează fiecare comparație
python3 verificari/genereaza_figuri.py # regenerează figurile
```

Fiecare linie de ieșire are forma

```
[OK  ] Vo = D*Vin: obținut = 12, așteptat = 12, eroare relativă = 1.01e-11
```

unde „obținut” vine din metoda independentă (simulare/integrare), iar
„așteptat” din formula din curs. Eroarea efectivă este afișată la fiecare
comparație. Toleranțele reflectă precizia metodei numerice: de exemplu
10⁻⁴ … 10⁻⁵ pentru forme de undă eșantionate care au discontinuități,
2·10⁻³ pentru simulările cu pas fix ale tiristoarelor și 10⁻⁶ … 10⁻¹² acolo
unde metoda este practic exactă. Pentru formulele aproximative (de exemplu
ondulația mică), toleranțele sunt mai largi și sunt comentate în cod.

## Limitele cursului

- Este un curs de **bază**: modelarea dinamică și proiectarea buclelor de
  reglare, convertoarele rezonante, componentele magnetice și topologiile
  multinivel sunt doar menționate.
- Simulările folosesc **componente ideale**, cu trei excepții introduse
  deliberat: rezistența bobinei (analiza boost-ului), rezistența sursei la
  redresorul cu filtru capacitiv (0,01 Ω și 0,5 Ω) și inductanța rețelei
  (suprapunerea comutației). Ele verifică matematica formulelor, nu
  comportamentul unei plăci reale. Pentru aceasta este nevoie de măsurători.
- Datele despre dispozitive (tensiuni maxime, proprietăți de material) provin
  din surse publice citate în bibliografie și se schimbă în timp.
