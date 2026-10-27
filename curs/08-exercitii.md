# Modulul 8 — Exerciții rezolvate

Încearcă fiecare problemă înainte de a deschide soluția. Toate răspunsurile
numerice sunt recalculate de `verificari/v08_exercitii.py`. Acolo unde se poate,
sunt confirmate și independent, prin simulare (rezultatele simulării sunt date
la sfârșitul fiecărei soluții).

---

### Exercițiul 1 — Valori efective (Modulul 2)

Tranzistorul unui buck conduce un curent trapezoidal: $I_o$ = 5 A,
$\Delta i_L$ = 2 A, $D$ = 0,4. Calculează curentul mediu, curentul efectiv și
pierderile de conducție pentru $R_{DS(on)}$ = 20 mΩ.

<details><summary>Soluție</summary>

$I_{med} = D I_o = 2$ A.

$I_{rms} = \sqrt{D\,(I_o^2 + \Delta i_L^2/12)} = \sqrt{0{,}4\,(25 + 0{,}333)} = 3{,}183$ A.

$P_{cond} = R_{DS(on)} I_{rms}^2 = 0{,}02 \cdot 10{,}133 = 202{,}7$ mW.

*Verificare:* integrarea numerică a formei de undă dă același $I_{rms}$
(eroare 5·10⁻⁷).
</details>

---

### Exercițiul 2 — Punte monofazată (Modulul 4)

O punte de diode este alimentată de la 230 V / 50 Hz și debitează pe
$R$ = 100 Ω. Calculează $V_{dc}$, $I_{dc}$, curentul efectiv prin sarcină,
puterea, curentul mediu printr-o diodă și tensiunea inversă pe care trebuie să
o suporte fiecare diodă.

<details><summary>Soluție</summary>

$V_m = 325{,}3$ V; $V_{dc} = 2V_m/\pi = 207{,}07$ V; $I_{dc} = 2{,}071$ A.

$V_{o,rms} = V_s = 230$ V, deci $I_{rms} = 2{,}30$ A și $P = V_s^2/R = 529$ W
(atenție: **nu** $V_{dc} I_{dc}$ = 429 W, pentru că sarcina rezistivă disipă și
pe armonici).

Fiecare diodă conduce o alternanță din două: $I_{D,med} = I_{dc}/2 = 1{,}035$ A.
Tensiunea inversă: $V_{RRM} \ge V_m = 325{,}3$ V, plus o marjă (tipic se alege o
diodă de 600 V, din cauza supratensiunilor din rețea).

*Verificare:* integrare numerică ($V_{dc}$ și $P$ identice, eroare ≤ 3·10⁻¹²).
</details>

---

### Exercițiul 3 — Filtru capacitiv (Modulul 4)

Un transformator dă 18 V RMS / 50 Hz unei punți cu filtru capacitiv. Sarcina
consumă ≈ 1 A, iar ondulația trebuie să fie ≤ 2 V vârf-vârf. Alege $C$ dintr-o
valoare standard și verifică rezultatul.

<details><summary>Soluție</summary>

$V_m = 25{,}46$ V. Cu formula acoperitoare:
$C \ge I_o/(2 f \Delta V) = 1/(2\cdot50\cdot2) = 5000$ µF. Alegem **5600 µF**
(valoare standard din seria E12).

Verificare cu soluția exactă ($R$ = 24 Ω, ca să rezulte ≈ 1 A): $\Delta V$ =
1,617 V ≤ 2 V, $V_{dc}$ = 24,67 V, $I_o$ = 1,028 A. Simularea în timp dă
$\Delta V$ = 1,606 V (diferență 0,7 %).

De reținut în practică: diodele trebuie să suporte $V_m$ (plus marjă), iar
condensatorul trebuie ales și după **curentul de ondulație** admis (curentul
lui efectiv este mare, din cauza impulsurilor de încărcare).
</details>

---

### Exercițiul 4 — Punte trifazată comandată (Modulul 4)

O punte trifazată cu tiristoare, la $V_{LL}$ = 400 V, trebuie să dea
$V_{dc}$ = 400 V (curent continuu, $L$ mare). Ce unghi $\alpha$ trebuie și ce
factor de putere rezultă?

<details><summary>Soluție</summary>

$V_{d0} = 1{,}35\,V_{LL} = 540{,}19$ V;
$\cos\alpha = 400/540{,}19 = 0{,}7405$, deci $\alpha = 42{,}23°$.

$\mathrm{PF} = (3/\pi)\cos\alpha = 0{,}7071$.

*Verificare:* construcția numerică a formei de undă cu $\alpha$ = 42,23° dă
$V_{dc}$ = 400,00 V (eroare 1,3·10⁻⁶).
</details>

---

### Exercițiul 5 — Proiectarea unui buck (Modulul 5)

12 V → 5 V, 2 A, $f_s$ = 200 kHz. Cerințe: $\Delta i_L \le 30\ \%\ I_o$,
$\Delta v_o \le 1\ \%\ V_o$. Alege $L$ și $C$ (valori standard), calculează
ondulațiile reale și sarcina minimă pentru CCM.

<details><summary>Soluție</summary>

$D = 5/12 = 0{,}4167$.

$L \ge \dfrac{V_o(1-D)}{f_s \cdot 0{,}3 I_o} = \dfrac{5 \cdot 0{,}5833}{2\cdot10^5 \cdot 0{,}6} = 24{,}31$ µH,
deci alegem **27 µH**. Atunci $\Delta i_L = 0{,}540$ A.

$C \ge \dfrac{\Delta i_L}{8 f_s \Delta v_o} = \dfrac{0{,}540}{8\cdot2\cdot10^5\cdot0{,}05} = 6{,}75$ µF,
deci alegem **10 µF** (ideal). Atunci $\Delta v_o = 33{,}8$ mV.

$L_{crit} = (1-D)R/(2f_s) = 3{,}65$ µH, iar CCM se păstrează pentru
$I_o > \Delta i_L/2 = 0{,}270$ A.

*Verificare prin simulare:* $V_o$ = 5,000 V, $\Delta i_L$ = 0,541 A,
$\Delta v_o$ = 33,8 mV (erori ≤ 0,2 %). Notă: un condensator real trebuie să
aibă $\mathrm{ESR} \ll 33{,}8\text{ mV}/0{,}54\text{ A} \approx 60$ mΩ, de
exemplu un condensator ceramic.
</details>

---

### Exercițiul 6 — Boost (Modulul 5)

5 V → 12 V, 0,5 A, $f_s$ = 500 kHz, $L$ = 10 µH. Calculează $D$, curentul mediu
și de vârf prin bobină și $C$ minim pentru $\Delta v_o \le 60$ mV.

<details><summary>Soluție</summary>

$D = 1 - 5/12 = 0{,}5833$; $I_L = I_o/(1-D) = 1{,}200$ A (verificare prin
puteri: $5 \cdot 1{,}2 = 12 \cdot 0{,}5 = 6$ W).

$\Delta i_L = V_{in}D/(Lf_s) = 0{,}583$ A, $I_{L,max} = 1{,}492$ A.

$C \ge I_o D/(f_s \Delta v_o) = 9{,}72$ µF, deci alegem **10 µF**.

*Verificare prin simulare:* $V_o$ = 11,998 V, $I_L$ = 1,1995 A,
$\Delta v_o$ = 58,3 mV ≤ 60 mV.
</details>

---

### Exercițiul 7 — Sarcină mică: DCM (Modulul 5)

Buck-ul de la Exercițiul 5 ($L$ = 27 µH) lucrează la $I_o$ = 0,1 A
($R$ = 50 Ω). (a) Este în CCM sau în DCM? (b) Ce tensiune ar da cu $D$
neschimbat (buclă deschisă)? (c) Ce $D$ trebuie pentru 5 V?

<details><summary>Soluție</summary>

(a) $K = 2L f_s/R = 0{,}216 < 1 - D = 0{,}583$, deci **DCM**.

(b) $M = \dfrac{2}{1+\sqrt{1+4K/D^2}} = 0{,}5806$, deci $V_o = 6{,}97$ V, cu
39 % peste valoarea dorită.

(c) Din $KM^2 + D^2M - D^2 = 0$ rezultă $D = M\sqrt{K/(1-M)}$. Cu
$M$ = 5/12 se obține $D = 0{,}2535$.

*Verificare prin simulare:* DCM confirmat; $V_o$ = 6,972 V cu $D$ = 0,4167,
respectiv 5,003 V cu $D$ = 0,2535. Concluzia: la sarcină mică, bucla de reglare
trebuie să reducă mult $D$.
</details>

---

### Exercițiul 8 — Invertor monofazat (Modulul 6)

O punte H alimentată la 400 V trebuie să dea 230 V RMS (fundamentală) cu SPWM.
Ce $m_a$ trebuie? Dar dacă $V_{dc}$ scade la 350 V? Care este tensiunea maximă
posibilă la 400 V?

<details><summary>Soluție</summary>

$\hat V_1 = m_a V_{dc}$, deci $m_a = \sqrt2 \cdot 230/400 = 0{,}8132$, iar la
350 V: $m_a = 0{,}9293$ (încă în zona liniară).

Maximul (undă dreptunghiulară): $V_{1,rms} = \frac{4}{\pi}\frac{400}{\sqrt2} = 360{,}1$ V.

*Verificare:* SPWM unipolar simulat cu $m_a$ = 0,8132 dă $V_{1,rms}$ = 230,00 V
(eroare 1,6·10⁻⁵).
</details>

---

### Exercițiul 9 — Invertor trifazat (Modulul 6)

Un invertor trifazat este alimentat la 600 V. Care este tensiunea de linie
maximă (RMS, fundamentală) cu SPWM liniar, cu injecția armonicii a 3-a și în
șase trepte? Se pot obține 400 V în zona liniară?

<details><summary>Soluție</summary>

- SPWM, $m_a$ = 1: $\frac{\sqrt3}{2\sqrt2}\cdot 600 = 0{,}6124 \cdot 600 = 367{,}4$ V;
- cu injecție, $m_a = 2/\sqrt3$: $367{,}4 \cdot 1{,}1547 = 424{,}3$ V;
- șase trepte: $\frac{\sqrt6}{\pi}\cdot 600 = 0{,}7797 \cdot 600 = 467{,}8$ V.

Pentru 400 V: $m_a = 400/367{,}4 = 1{,}0887$. Valoarea este peste 1, deci SPWM
simplu ar intra în supramodulație, dar este sub 1,1547, deci **cu injecția
armonicii a 3-a** se rămâne în zona liniară.

*Verificare:* simularea cu injecție și $m_a$ = 1,0887 dă $V_{LL1,rms}$ =
399,99 V.
</details>

---

### Exercițiul 10 — Radiator (Modulul 7)

Un tranzistor disipă 3 W. $R_{th,jc}$ = 1,2 K/W, $R_{th,cs}$ = 0,3 K/W,
$T_a$ = 50 °C, iar $T_j$ trebuie să rămână ≤ 125 °C. Ce rezistență termică
maximă poate avea radiatorul?

<details><summary>Soluție</summary>

$R_{th,sa} \le \dfrac{T_j - T_a}{P} - R_{th,jc} - R_{th,cs} = \dfrac{75}{3} - 1{,}5 = 23{,}5$ K/W.

*Verificare inversă:* $50 + 3\,(1{,}2 + 0{,}3 + 23{,}5) = 125$ °C.
</details>

---

### Exercițiul 11 — Conducție vs. comutație (Modulele 3 și 7)

Tranzistorul de la Exercițiul 1 lucrează la $V_{in}$ = 12 V, cu timpi de
comutație totali de 20 ns la pornire și 20 ns la blocare (model liniar). La ce
frecvență pierderile de comutație devin egale cu cele de conducție?

<details><summary>Soluție</summary>

Pornirea are loc la curentul minim, $I_o - \Delta i_L/2 = 4$ A, iar blocarea la
curentul maxim, $6$ A:

$E_{sw} = \tfrac12 \cdot 12 \cdot (4 \cdot 20 + 6 \cdot 20)\cdot10^{-9} = 1{,}2$ µJ pe perioadă.

$f_s = P_{cond}/E_{sw} = 0{,}2027/1{,}2\cdot10^{-6} = 168{,}9$ kHz.

Peste această frecvență domină comutația, așa că merită un tranzistor mai
rapid, chiar dacă are $R_{DS(on)}$ ceva mai mare.
</details>

---

### Exercițiul 12 — Alegerea dispozitivului (Modulul 3, calitativ)

Ce tip de dispozitiv ai alege pentru: (a) un încărcător USB-C compact de 65 W
alimentat din rețea; (b) un invertor de tracțiune de 800 V c.c. pentru un
vehicul electric; (c) o stație HVDC; (d) un convertor 12 V → 1 V / 30 A pentru
un procesor?

<details><summary>Răspuns orientativ</summary>

(a) GaN HEMT sau MOSFET superjunction de ~650 V: frecvență mare, deci
componente magnetice mici. (b) SiC MOSFET de 1200 V: pierderi mici la tensiune
mare (alternativ IGBT, cu randament mai mic). (c) Tiristoare de înaltă
tensiune (clasa 8,5 kV), înseriate în valve. (d) MOSFET-uri de Si de joasă
tensiune (~25–30 V), cu $R_{DS(on)}$ foarte mic, în buck sincron multifazat.
Justificarea fiecărei alegeri este în tabelul din secțiunea 3.10. Alegerea
finală depinde de cost, de disponibilitate și de cataloagele actuale.
</details>

---

[← Modulul 7](07-pierderi-termic-practica.md) · [Cuprins](../README.md) · [Bibliografie →](bibliografie.md)
