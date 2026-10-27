# Mașini electrice și acționări electrice

**Curs pentru studenții de la specializările de inginerie non-electrică** (mecanică, energetică, mecatronică etc.): transformatorul, mașina asincronă, generatorul sincron, motorul sincron și acționările electrice, cu probleme rezolvate, întrebări de autoevaluare și îndrumar de laborator.

## Cuprins

| Capitol | Conținut |
|---|---|
| [0. Noțiuni fundamentale](00-notiuni-fundamentale.md) | circuitul magnetic, inducția, forța electromagnetică, fazori și puteri, sisteme trifazate, câmpul învârtitor, pierderi și încălzire, plăcuța indicatoare |
| [1. Transformatorul](01-transformatorul.md) | construcție, transformatorul ideal, schema echivalentă, încercările de gol și scurtcircuit, căderea de tensiune, randamentul, transformatorul trifazat, grupa de conexiuni, funcționarea în paralel, transformatoare speciale |
| [2. Mașina asincronă](02-masina-asincrona.md) | construcție, alunecare, schema echivalentă, bilanțul puterilor, caracteristica mecanică, formula lui Kloss, pornirea, reglarea vitezei, frânarea, clasele de randament IE |
| [3. Generatorul sincron](03-generatorul-sincron.md) | construcție (poli înecați/aparenți), reacția indusului, reactanța sincronă, caracteristici, puterea și stabilitatea, sincronizarea, reglajul P și Q, statismul |
| [4. Motorul sincron](04-motorul-sincron.md) | principiu, diagrama fazorială, cuplul de desprindere, curbele în V, compensarea factorului de putere, pornirea, motoare cu magneți permanenți |
| [5. Acționări electrice](05-actionari-electrice.md) | ecuația mișcării, raportarea la arbore, caracteristicile mașinilor de lucru, stabilitatea, cele patru cadrane, pornirea, alegerea motorului, convertorul de frecvență, eficiența energetică, scheme de comandă |
| [Îndrumar de laborator](06-indrumar-laborator.md) | securitatea muncii și lucrările L1–L7 |

Ordinea capitolelor este cea pedagogică uzuală: **transformatorul** introduce schema echivalentă și încercările de gol și scurtcircuit, reluate apoi la **mașina asincronă**; **generatorul sincron** precede **motorul sincron** (aceeași mașină, convenții diferite); **acționările** folosesc toate capitolele anterioare.

## Structura fiecărui capitol

1. **Obiective** – ce trebuie să știe studentul la final.
2. **Teorie** – cu figuri și formule; formulele esențiale sunt încadrate.
3. **Probleme rezolvate** – pas cu pas, fiecare cu o **verificare pe o cale independentă**.
4. **Întrebări de autoevaluare** – cu răspunsuri ascunse (se deschid cu un clic).
5. **Bibliografie** pentru capitol.

Pentru unitate, problemele folosesc câteva **mașini de referință**, reluate de la un capitol la altul:

| Mașină | Date principale | Folosită în |
|---|---|---|
| transformator 20 kVA | 2400/240 V, $u_{sc}$ = 4 % | cap. 1 |
| transformator 400 kVA | 20/0,4 kV, Dyn11, $u_{sc}$ = 4 % | cap. 1 |
| motorul asincron **M15** | 15 kW, 400 V Δ, 4 poli, 1466 rot/min, IE3 | cap. 2 și 5 |
| generatorul **G10** | 10 MVA, 6,3 kV, $\cos\varphi$ = 0,8 | cap. 3 |
| motorul sincron **MS1000** | 1000 kW, 6 kV, 8 poli, $\cos\varphi$ = 0,9 capacitiv | cap. 4 |

Datele acestor mașini sunt construite pentru curs, cu valori în domeniile uzuale; nu reproduc un produs comercial anume.

## Cum au fost verificate calculele și figurile

Toate rezultatele numerice din probleme și toate figurile (cu excepția schițelor constructive) sunt **calculate de scripturile Python** din [`scripts/`](scripts/), din aceleași modele:

- `modele.py` – modelele comune (transformator, mașina asincronă cu schema în T, inclusiv varianta cu colivie dublă, formula lui Kloss, mașina sincronă);
- `probleme_cap00.py` … `probleme_cap05.py` – rezolvă problemele fiecărui capitol și **verifică fiecare rezultat pe cel puțin două căi independente** (de exemplu: bilanțul puterilor față de calculul direct, formula aproximativă față de soluția exactă, soluția analitică față de integrarea numerică). Orice nepotrivire oprește scriptul cu eroare;
- `figuri_cap00.py` … `figuri_cap05.py`, `figuri_laborator.py` – generează figurile SVG din [`figuri/`](figuri/);
- `ruleaza_tot.py` – rulează tot.

```bash
cd curs-masini-electrice/scripts
pip install -r requirements.txt
python ruleaza_tot.py
```

La ultima rulare: 13 scripturi, 88 de verificări, toate trecute.

Afirmațiile care nu rezultă din calcul (date normative, valori tipice, proprietăți constructive) sunt însoțite de trimiteri la bibliografie și standarde.

## Plan orientativ (un semestru de 14 săptămâni)

| Săpt. | Curs (2 h) | Laborator (2 h la două săptămâni) |
|---|---|---|
| 1 | Cap. 0 – noțiuni fundamentale (§ 0.1–0.6) | instructaj de securitate |
| 2 | Cap. 0 – trifazat, câmp învârtitor, pierderi (§ 0.7–0.10) | |
| 3 | Cap. 1 – construcție, principiu, schema echivalentă | L1 |
| 4 | Cap. 1 – încercări, sarcină, trifazat, paralel | |
| 5 | Cap. 2 – principiu, schema echivalentă, bilanț | L2 |
| 6 | Cap. 2 – caracteristica mecanică, Kloss | |
| 7 | Cap. 2 – pornire, reglarea vitezei, frânare, clase IE | L3 |
| 8 | Cap. 3 – construcție, reactanța sincronă, caracteristici | |
| 9 | Cap. 3 – putere, stabilitate, funcționarea la rețea, statism | L4 |
| 10 | Cap. 4 – motorul sincron | |
| 11 | Cap. 5 – ecuația mișcării, raportare, stabilitate, cadrane | L5 |
| 12 | Cap. 5 – pornire, alegerea motorului | |
| 13 | Cap. 5 – convertorul de frecvență, eficiență, scheme | L6, L7 |
| 14 | Recapitulare, probleme | recuperări, evaluare |

## Notații și convenții

- Fazorii (numere complexe) sunt subliniați: $\underline{U}$, $\underline{I}$; valorile efective nu: $U$, $I$.
- Mărimile raportate la primar (stator) au apostrof: $R_2'$, $I_2'$.
- Indicii: $n$ – nominal, $f$ – de fază, $l$ – de linie, $0$ – mers în gol, $sc$ – scurtcircuit, $p$ – pornire.
- $M$ – cuplu [N·m], $\Omega$ – viteză unghiulară [rad/s], $n$ – turație [rot/min]; $\Omega = 2\pi n/60$, iar $M\,[\text{N·m}] = 9550\,P\,[\text{kW}]/n\,[\text{rot/min}]$.
- Virgula este separatorul zecimal (convenția românească).

## Bibliografie

**Manuale**

1. A. E. Fitzgerald, C. Kingsley Jr., S. D. Umans – *Electric Machinery*, ed. 6, McGraw-Hill, 2003.
2. S. J. Chapman – *Electric Machinery Fundamentals*, ed. 5, McGraw-Hill, 2012.
3. Al. Fransua, R. Măgureanu – *Mașini și acționări electrice. Elemente de execuție*, Editura Tehnică, București, 1986.
4. I. Boldea, S. A. Nasar – *The Induction Machine Handbook*, CRC Press, 2002.
5. N. Mohan, T. M. Undeland, W. P. Robbins – *Power Electronics: Converters, Applications, and Design*, ed. 3, Wiley, 2003.
6. B. K. Bose – *Modern Power Electronics and AC Drives*, Prentice Hall, 2002.
7. W. Leonhard – *Control of Electrical Drives*, ed. 3, Springer, 2001.
8. P. Kundur – *Power System Stability and Control*, McGraw-Hill, 1994.

**Standarde și reglementări**

- [S1] IEC 60034-1 – *Rotating electrical machines – Part 1: Rating and performance* (regimurile S1–S10, datele nominale).
- [S2] IEC 60034-30-1:2014 – *Efficiency classes of line operated AC motors (IE code)*. A apărut ediția a 2-a (2025); valorile citate în curs sunt din ediția 2014.
- [S3] IEC 60076-1 – *Power transformers – Part 1: General*.
- [S4] IEC 60085 – *Electrical insulation – Thermal evaluation and designation* (clasele termice 130 (B), 155 (F), 180 (H) etc.).
- [S5] IEC 60529 – *Degrees of protection provided by enclosures (IP Code)*.
- [S6] Regulamentul (UE) 2019/1781 privind cerințele de proiectare ecologică pentru motoarele electrice și variatoarele de viteză (modificat prin Regulamentul (UE) 2021/341).
- [S7] Regulamentul (UE) nr. 548/2014 privind cerințele de proiectare ecologică pentru transformatoarele de putere mică, medie și mare (modificat prin Regulamentul (UE) 2019/1783).
- [S8] IEC 60034-12 – *Starting performance of single-speed three-phase cage induction motors*.
- [S9] Legea nr. 319/2006 a securității și sănătății în muncă.
- [S10] IEC 60034-2-1 – *Standard methods for determining losses and efficiency from tests*.
