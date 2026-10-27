# Protecții în rețelele electrice

Curs de master, orientat spre aplicații industriale: de la curentul de defect la fișa de reglaje.
Fiecare modul are patru tab-uri, în română și engleză:

- **Laborator**: simulator al rețelei-exemplu, cu calcul pas cu pas;
- **Reglaje**: fișa de calcul industrială (regula de reglaj, sursa ei, valoarea, verificarea), cu tabel de copiat în Excel;
- **Teorie**: relațiile numerotate, ipotezele modelului, sursele;
- **Test**: grile cu explicații și probleme numerice cu alte valori la fiecare încercare.

## Stare

| Modul | Subiect | Stare |
|---|---|---|
| M01 | Curenții de defect pentru reglaje (IEC 60909-0, componente simetrice, tratarea neutrului MT) | gata |
| M02 | Transformatoare de curent pentru protecții (F_a real, saturația tranzitorie, dimensionarea) | gata |
| M03 | Protecția maximală de curent 50/51: reglaje și coordonare pe patru relee | gata |
| M04 | Protecția maximală direcțională 67/67N: unghiul caracteristic, bucla închisă | gata |
| M05–M14 | Punerea la pământ în MT, generare distribuită, distanță, teleprotecție, automatizări, transformatoare, generatoare, bare și motoare, relee numerice, proiectul stației | urmează |

Toate modulele lucrează pe aceeași rețea-exemplu: stația 110/20 kV cu transformatorul T1 de 25 MVA
(tipul standard pandapower „25 MVA 110/20 kV”), neutrul de 20 kV tratat prin rezistor de 300 A și plecarea F1
în LEA Ol-Al 70/12 mm², 20 km. Puterile de scurtcircuit și datele neutrului sunt valori de exemplu.

## Structura

```
site/                 paginile, gata de urcat pe server (HTML/CSS/JS static, fără build)
  index.html          cuprinsul cursului
  assets/             stilurile, funcțiile comune (limba, tab-uri, teste), numere complexe
  m01…m04/            câte un modul: index.html (pagina), engine.js (calculele), page.js (interfața)
verify/               verificările independente ale motoarelor de calcul (Python)
tests/                verificări în browser (Playwright) și ale formulelor (KaTeX)
```

Motorul de calcul al fiecărui modul (`engine.js`) rulează și în pagină, și în Node, așa că testele
verifică exact codul pe care îl folosesc studenții.

## Cum se verifică

```
pip install numpy scipy pandapower
verify/run_all.sh
```

Ce compară fiecare script:

| Script | Calea independentă |
|---|---|
| `m01_line_params.py` | parametrii homopolari ai liniilor: formulele Carson simplificate față de integrala Carson evaluată numeric (abatere sub 1 %) |
| `m01_verify.py` | 576 de cazuri (4 tipuri de defect × 4 tratări ale neutrului × 3 linii × max/min × poziții × R_f): analiză nodală în coordonate de fază (abatere 6·10⁻⁹); curenții 3F/2F față de pandapower (IEC 60909-0); tiparele 1-1-2 și 1-1-0 pe 110 kV |
| `m02_verify.py` | ecuația TC integrată cu scipy (Radau) față de motor (abatere RMS 0,23 % din vârf); formula IEEE C37.110 a timpului până la saturație față de fluxul calculat exact; calibrarea erorii compuse la ALF |
| `m03_verify.py` | curbele IEC/IEEE față de valorile de referință la 10·I>; reglajele recalculate cu curenții din pandapower; 328 de scenarii de defect (cine declanșează primul și marja); minimalitatea fiecărui TMS |
| `m04_verify.py` | 128 de cazuri ale elementului direcțional prin analiză nodală în coordonate de fază; reglajele buclei recalculate; 152 de defecte în bucla închisă simulate independent (secvența de declanșare, izolarea corectă, rezerva ≥ Δt) |

Verificarea în browser (toate paginile, RO și EN, desktop și telefon, temele deschisă și întunecată):

```
node tests/browser_check.cjs
```

## Publicare

Conținutul folderului `site/` se urcă așa cum este într-un folder al serverului (de exemplu `gridwise.ro/protectii/`).
Paginile încarcă fonturile de pe Google Fonts și KaTeX 0.16.9 de pe cdnjs; restul e local.

## Surse

Fiecare modul își listează sursele în tab-ul Teorie. Regulile de reglaj sunt citate din standarde
(IEC 60909-0, IEC 60255-151, IEEE C37.112, IEC 61869-2, IEEE C37.110), din manuale și ghiduri ale producătorilor
(ABB, GE, SEL) și din cursuri românești de protecții. Unde o valoare e doar un exemplu sau o estimare, pagina o spune.
