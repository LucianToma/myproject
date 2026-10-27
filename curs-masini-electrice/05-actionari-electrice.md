# Capitolul 5. Acționări electrice

> **Obiective.** După acest capitol ar trebui să puteți: (1) descrie structura unei acționări electrice; (2) scrie și folosi ecuația fundamentală a mișcării; (3) raporta cuplurile și momentele de inerție la arborele motorului; (4) determina punctul de funcționare și stabilitatea lui; (5) calcula timpul de pornire; (6) alege și verifica motorul pentru un ciclu de sarcină; (7) explica funcționarea convertorului de frecvență și economia de energie la pompe și ventilatoare; (8) citi o schemă de pornire directă cu contactor.

Capitolele 1–4 au tratat mașinile; acest capitol tratează **sistemul**: mașina electrică împreună cu ce o alimentează și ce antrenează. Pentru un inginer mecanic, energetician sau mecatronist, aici se întâlnesc cel mai direct cele două lumi.

---

## 5.1. Structura unei acționări electrice

O **acționare electrică** este ansamblul care transformă energia electrică în lucru mecanic controlat:

```mermaid
flowchart LR
    R[Rețea] --> C[Convertor<br/>electronic de putere]
    C --> M[Motor<br/>electric]
    M --> T[Transmisie<br/>reductor, curea, cuplaj]
    T --> ML[Mașina de lucru<br/>pompă, macara, bandă]
    S[Comandă și reglare] -.-> C
    ML -. senzori: turație, poziție .-> S
    M -. curenți, tensiuni .-> S
```

- **Convertorul** (lipsește la acționările nereglabile, alimentate direct prin contactor) adaptează tensiunea și frecvența: convertor de frecvență, pornitor static, redresor comandat.
- **Motorul** – de regulă asincron cu colivie; pentru cerințe dinamice mari sau eficiență maximă, sincron cu magneți permanenți.
- **Transmisia** adaptează turația și cuplul motorului la cele ale mașinii de lucru.
- **Comanda și reglarea** – de la simpla pornire/oprire la reglarea turației, a cuplului sau a poziției.

## 5.2. Ecuația fundamentală a mișcării

Pentru un sistem rotativ cu momentul de inerție $J$ (raportat la arborele motorului), legea a doua a lui Newton pentru rotație este

$$\boxed{J\,\frac{d\Omega}{dt} = M - M_r}$$

unde $M$ este cuplul motorului, iar $M_r$ cuplul rezistent al mașinii de lucru (inclusiv frecările). Diferența $M_d = M - M_r$ se numește **cuplu dinamic**:

- $M = M_r$ – **regim staționar**, viteză constantă;
- $M > M_r$ – sistemul **accelerează**;
- $M < M_r$ – sistemul **decelerează**.

## 5.3. Raportarea la arborele motorului

Între motor și mașina de lucru există de regulă o transmisie cu raportul $i = \Omega_{motor}/\Omega_{mașină}$ și randamentul $\eta_t$. Pentru calcule, toate mărimile se **raportează la arborele motorului**, păstrând puterea și energia cinetică:

**Cuplul rezistent** (din conservarea puterii, cu pierderile din transmisie):

$$M_r' = \frac{M_{r}}{i\,\eta_t}\ \ \text{(puterea curge de la motor spre sarcină)}, \qquad M_r' = \frac{M_{r}\,\eta_t}{i}\ \ \text{(puterea curge de la sarcină spre motor)} .$$

**Momentul de inerție** (din conservarea energiei cinetice, $\tfrac12 J\Omega_{maș}^2 = \tfrac12 J'\Omega_{motor}^2$):

$$J' = \frac{J}{i^2} .$$

**Masele în translație** (viteza $v$): $\tfrac12 m v^2 = \tfrac12 J'\Omega^2$, deci

$$J' = m\left(\frac{v}{\Omega}\right)^2 .$$

Consecința practică: masele care se rotesc încet (după un reductor cu raport mare) contribuie foarte puțin la inerția totală; contează mai ales inerția rotorului și a pieselor de pe arborele rapid (problema 5.1).

## 5.4. Caracteristicile mecanice ale mașinilor de lucru

![Figura 5.1 – Caracteristici de sarcină](figuri/f05-1-caracteristici-sarcina.svg)

*Figura 5.1 – Tipuri de caracteristici mecanice ale mașinilor de lucru (valori relative).*

| Tip | Exemple | Consecință pentru acționare |
|---|---|---|
| $M_r$ = const | macarale, lifturi, benzi transportoare, compresoare cu piston | motorul trebuie să dezvolte cuplul nominal de la pornire |
| $M_r \propto \Omega$ | frecare vâscoasă, generator debitând pe rezistență | |
| $M_r \propto \Omega^2$ | **ventilatoare, pompe centrifuge** | cuplu mic la pornire; puterea $\propto \Omega^3$ – potențial mare de economie la reglarea vitezei (§ 5.10) |
| $P$ = const ($M_r \propto 1/\Omega$) | bobinatoare, strunguri la viteze mari | cuplu mare la viteze mici |

## 5.5. Punctul de funcționare și stabilitatea lui

În regim staționar, acționarea funcționează la intersecția caracteristicii motorului $M(\Omega)$ cu cea a mașinii de lucru $M_r(\Omega)$. Un punct de funcționare este **stabil** dacă, după o mică perturbație, sistemul revine în el. Scriind ecuația mișcării pentru o abatere mică $\Delta\Omega$:

$$J\frac{d\Delta\Omega}{dt} = \left(\frac{dM}{d\Omega} - \frac{dM_r}{d\Omega}\right)\Delta\Omega ,$$

abaterea se amortizează numai dacă paranteza este negativă:

$$\boxed{\frac{dM}{d\Omega} < \frac{dM_r}{d\Omega}}\qquad \text{(criteriul de stabilitate statică)} .$$

![Figura 5.2 – Stabilitatea punctului de funcționare](figuri/f05-3-stabilitate.svg)

*Figura 5.2 – Motorul M15 și un cuplu rezistent constant de 2·$M_n$: două puncte de intersecție, dintre care doar A este stabil (problema 5.5).*

Pentru motorul asincron, aceasta înseamnă că zona dintre $s = 0$ și $s_k$ este stabilă pentru orice sarcină cu $M_r$ constant sau crescător cu viteza, iar zona dintre $s_k$ și $s = 1$ este, de regulă, instabilă.

## 5.6. Cele patru cadrane de funcționare

Semnele cuplului și ale vitezei definesc patru cadrane (figura 5.3). În cadranele I și III mașina electrică funcționează ca **motor** ($P = M\Omega > 0$); în II și IV ca **frână** (generator, $P < 0$). O acționare care trebuie să lucreze în toate cele patru cadrane (lift, macara, vehicul) are nevoie de un convertor capabil să preia energia de frânare.

![Figura 5.3 – Cadranele de funcționare](figuri/f05-2-cadrane.svg)

*Figura 5.3 – Cadranele de funcționare, cu exemple pentru un troliu de macara.*

## 5.7. Regimurile tranzitorii. Pornirea

Din ecuația mișcării, timpul în care viteza crește de la $\Omega_a$ la $\Omega_b$ este

$$t = J\int_{\Omega_a}^{\Omega_b}\frac{d\Omega}{M(\Omega) - M_r(\Omega)} .$$

- Dacă **cuplul dinamic este constant** (de exemplu, convertor de frecvență cu limitare de curent și sarcină cu $M_r$ constant): $t = J\,\Delta\Omega/(M - M_r)$.
- Pentru un **ventilator** ($M_r = k\Omega^2$) accelerat cu cuplu constant $M$, integrala are soluție analitică (problema 5.2):

$$t = \frac{J}{\sqrt{Mk}}\,\operatorname{artanh}\left(\Omega\sqrt{\frac kM}\right).$$

- În general (motor alimentat direct de la rețea, cu caracteristica reală), integrala se calculează **numeric** (figura 5.4).

![Figura 5.4 – Pornirea directă](figuri/f05-5-pornire-directa.svg)

*Figura 5.4 – Pornirea directă a motorului M15 cu un ventilator (J total = 1 kg·m²), calculată numeric pe modelul cu colivie dublă. Model cvasistaționar: neglijează fenomenele electromagnetice tranzitorii, care produc în primele perioade vârfuri suplimentare de curent și cuplu.*

**Energia pierdută la pornire.** La pornirea **în gol** a unui motor asincron, energia transformată în căldură în rotor este egală cu energia cinetică finală, **oricare ar fi forma caracteristicii mecanice**:

$$W_{Cu2} = \int s\,P_\delta\,dt = \int s\,M\,\Omega_1\,dt = \int_0^{\Omega_1} s\,\Omega_1\,J\,d\Omega = J\Omega_1^2\int_0^1 s\,ds = \frac12 J\Omega_1^2$$

(s-au folosit $P_{Cu2} = sP_\delta$, $M = J\,d\Omega/dt$ și $d\Omega = -\Omega_1\,ds$). De aceea numărul de porniri pe oră al unui motor este limitat, mai ales când inerția antrenată este mare (problema 5.7).

## 5.8. Alegerea motorului

Etapele alegerii unui motor:

1. **Turația și cuplul** cerute de mașina de lucru, eventual prin transmisie (§ 5.3).
2. **Puterea**, ținând seama de **regimul de funcționare** (S1...S10, § 0.9) și de **încălzire**: motorul nu trebuie să depășească temperatura admisă de clasa de izolație.
3. **Verificarea la suprasarcină:** cel mai mare cuplu cerut trebuie să fie sub $M_{max}$, cu rezervă pentru scăderile de tensiune ($M_{max} \propto U^2$ la motorul asincron).
4. **Verificarea la pornire:** cuplul de pornire trebuie să depășească cuplul rezistent, cu o rezervă pentru un timp de pornire acceptabil.
5. **Condițiile de mediu și montaj:** grad de protecție IP, temperatura mediului, altitudinea, forma constructivă, clasa de randament (IE3/IE4, § 2.11).

### Metoda cuplului echivalent

Pentru o sarcină care variază periodic (ciclul $M_k$ pe durata $t_k$), pierderile variabile ale motorului sunt aproximativ proporționale cu $M^2$ (curentul este aproximativ proporțional cu cuplul). Dacă perioada ciclului este mult mai mică decât **constanta termică de timp** a motorului (zeci de minute), motorul se încălzește ca la un cuplu constant egal cu **valoarea pătratică medie**:

$$\boxed{M_{ech} = \sqrt{\frac{\sum_k M_k^2\, t_k}{\sum_k t_k}}}\qquad\text{și se cere}\qquad M_{ech} \le M_n .$$

Media aritmetică a cuplului **subestimează** încălzirea și nu se folosește pentru dimensionare (problema 5.3, figura 5.5).

![Figura 5.5 – Ciclul de sarcină și încălzirea](figuri/f05-6-ciclu-incalzire.svg)

*Figura 5.5 – Ciclul de sarcină din problema 5.3 și încălzirea calculată cu un model termic de ordinul 1: ciclul real încălzește motorul exact cât cuplul echivalent constant.*

## 5.9. Convertorul de frecvență

Convertorul de frecvență (în engleză *variable speed drive*, VSD, sau *inverter*) alimentează motorul cu tensiune și frecvență reglabile (figura 5.6):

1. **redresorul** (de regulă cu diode) transformă tensiunea alternativă a rețelei în tensiune continuă;
2. **circuitul intermediar de c.c.** (condensatoare) netezește tensiunea; la rețeaua de 400 V, valoarea medie a tensiunii redresate în punte trifazată este $\frac{3\sqrt2}{\pi}\cdot 400 \approx 540$ V;
3. **invertorul** cu tranzistoare IGBT comută tensiunea continuă astfel încât valoarea medie pe intervale scurte să urmărească o sinusoidă de frecvența dorită – **modulația în lățime a impulsurilor** (PWM, figura 5.7).

![Figura 5.6 – Structura convertorului de frecvență](figuri/f05-7-convertor-frecventa.svg)

*Figura 5.6 – Structura unui convertor de frecvență cu circuit intermediar de tensiune continuă.*

![Figura 5.7 – Modulația PWM](figuri/f05-8-pwm.svg)

*Figura 5.7 – Principiul PWM: tranzistoarele comută când referința sinusoidală intersectează purtătoarea triunghiulară. Fundamentala tensiunii de ieșire are amplitudinea $m_a U_d/2$ (verificat numeric: 216 V pentru $m_a$ = 0,8 și $U_d$ = 540 V). Inductivitatea motorului netezește curentul, care rezultă aproape sinusoidal.*

**Moduri de comandă:**

- **comanda scalară U/f** (§ 2.8): simplă, potrivită pentru pompe, ventilatoare, benzi transportoare;
- **comanda vectorială** (orientată după câmp) și **controlul direct al cuplului** (DTC): convertorul calculează în timp real fluxul și cuplul motorului și le reglează separat, obținând un comportament dinamic comparabil cu al motorului de curent continuu – pentru macarale, lifturi, mașini-unelte, servoacționări [6], [7].

**Frânarea.** Redresorul cu diode nu poate trimite energie înapoi în rețea. Energia de frânare încarcă circuitul intermediar și este disipată într-un **rezistor de frânare** (comandat de un chopper) sau – la acționările care frânează des (lifturi, macarale, centrifuge) – este trimisă în rețea de un **redresor activ** (frânare recuperativă).

**Aspecte practice:** convertorul produce armonici de curent în rețea (filtre, bobine de rețea), impulsuri de tensiune cu fronturi abrupte care solicită izolația motorului (mai ales la cabluri lungi) și pot produce curenți prin lagăre; producătorii indică lungimile maxime de cablu și filtrele necesare. În UE, convertoarele pentru motoare de 0,12–1000 kW trebuie să respecte clasa IE2 a variatoarelor [S6].

## 5.10. Eficiența energetică la pompe și ventilatoare

Pentru pompele centrifuge și ventilatoare, la turație variabilă (aceeași instalație, fără înălțime statică), se aplică **legile de similitudine**:

$$\frac{Q_2}{Q_1} = \frac{n_2}{n_1}, \qquad \frac{H_2}{H_1} = \left(\frac{n_2}{n_1}\right)^2, \qquad \frac{P_2}{P_1} = \left(\frac{n_2}{n_1}\right)^3 .$$

Reducerea debitului prin **clapetă** sau **vană de laminare** păstrează turația și disipă energia în clapetă; reducerea prin **turație** (convertor de frecvență) reduce puterea aproximativ cu cubul debitului. La 70 % din debit, puterea ideală este doar 34 % din cea nominală (problema 5.4, figura 5.8).

![Figura 5.8 – Ventilator: clapetă vs convertor](figuri/f05-9-ventilator.svg)

*Figura 5.8 – Puterea absorbită de un ventilator la debit redus.*

> **Atenție:** dacă instalația are o înălțime statică importantă (de exemplu, o pompă care ridică apa la un rezervor), legea cubului nu se mai aplică întregii puteri, iar economia este mai mică; calculul se face atunci cu caracteristicile pompei și ale instalației.

## 5.11. Scheme de comandă și protecție

Figura 5.9 prezintă **circuitul de forță** pentru pornirea directă a unui motor asincron:

![Figura 5.9 – Schema de forță a pornirii directe](figuri/f05-10-schema-pornire-directa.svg)

*Figura 5.9 – Pornirea directă: siguranțe (sau întrerupător automat), separator, contactor, releu termic, motor.*

| Aparat | Rol |
|---|---|
| **siguranțe fuzibile / întrerupător automat** | protecție la scurtcircuit |
| **separator** | separarea vizibilă de rețea pentru intervenții |
| **contactor** | conectarea și deconectarea motorului (comandă de la distanță, multe manevre) |
| **releu termic** | protecție la suprasarcină (încălzirea motorului) și, la cele moderne, la lipsa unei faze |

**Circuitul de comandă** (desenat separat) conține butoanele „Pornire” (normal deschis) și „Oprire” (normal închis), bobina contactorului și un **contact auxiliar de automenținere** al contactorului, în paralel cu butonul de pornire: după eliberarea butonului, contactorul rămâne atras prin propriul contact. Contactul normal închis al releului termic, în serie cu bobina, deconectează motorul la suprasarcină. Un avantaj important al schemei: la dispariția tensiunii, contactorul cade și motorul **nu repornește singur** la revenirea ei.

**Inversarea sensului** se face cu două contactoare: K1 conectează fazele L1, L2, L3 la bornele U, V, W, iar K2 la W, V, U (două faze inversate, § 0.8). Cele două contactoare **nu trebuie să se poată închide simultan** (ar scurtcircuita două faze): se folosesc **interblocări** electrice (contactul normal închis al fiecăruia în circuitul bobinei celuilalt) și, de regulă, mecanice.

**Pornirea stea-triunghi** folosește trei contactoare (de linie, de stea și de triunghi, cu interblocare între ultimele două) și un releu de timp care comandă trecerea din stea în triunghi.

---

## Probleme rezolvate

Toate rezultatele sunt calculate și verificate de scriptul [`scripts/probleme_cap05.py`](scripts/probleme_cap05.py). Problemele folosesc motorul M15 din capitolul 2.

### Problema 5.1 – Troliul: raportarea la arborele motorului

Un troliu ridică o masă $m$ = 2000 kg cu un tambur de diametru $D$ = 0,4 m ($J_{tambur}$ = 5 kg·m²), printr-un reductor cu $i$ = 60 și $\eta_t$ = 0,90. Motorul este M15 ($J_m$ = 0,1 kg·m²), considerat la turația nominală. Calculați: viteza de ridicare, cuplul și puterea raportate la motor (la ridicare și la coborâre), momentul de inerție total și timpul de accelerare cu un cuplu motor constant de 1,5·$M_n$.

**Rezolvare.**

- Vitezele: $\Omega_m = 2\pi\cdot 1466/60 = 153{,}52$ rad/s, $\Omega_t = \Omega_m/i = 2{,}559$ rad/s, $v = \Omega_tD/2 = 0{,}512$ m/s.
- Cuplul la tambur: $M_t = mgD/2 = 2000\cdot 9{,}81\cdot 0{,}2 = 3924$ N·m.
- Raportat la motor, la **ridicare**: $M_r' = M_t/(i\eta_t) = 72{,}67$ N·m (74 % din $M_n$ = 97,71 N·m – motorul este potrivit); la **coborâre**: $M_r' = M_t\eta_t/i = 58{,}86$ N·m (motorul frânează sarcina).
- Puterea la ridicare: $P = M_r'\Omega_m = 11{,}16$ kW.
- Momentul de inerție raportat: motorul 0,1; tamburul $5/60^2 = 0{,}00139$; masa $m(v/\Omega_m)^2 = 0{,}0222$ kg·m²; **total 0,124 kg·m²** – tamburul contează foarte puțin.
- Accelerarea cu $M$ = 1,5·$M_n$ = 146,6 N·m: $t = \dfrac{J\Omega_m}{M - M_r'} = \dfrac{0{,}1236\cdot 153{,}52}{146{,}6 - 72{,}67} = 0{,}257$ s.

**Verificări.** $P = mgv/\eta_t = 11{,}16$ kW ✓ (bilanț de putere); $\tfrac12 J_{masă}\Omega_m^2 = \tfrac12 mv^2 = 261{,}9$ J ✓ (bilanț de energie cinetică); timpul de accelerare obținut prin integrarea numerică a ecuației mișcării este 0,2568 s ✓.

*Observație:* la 74 % din cuplul nominal, turația reală a lui M15 ar fi puțin mai mare decât 1466 rot/min (circa 1475 rot/min, după formula lui Kloss), deci viteza de ridicare ar fi cu circa 0,6 % mai mare; simplificarea nu schimbă concluziile.

### Problema 5.2 – Pornirea unui ventilator cu cuplu constant

Un ventilator ($J$ total = 1,0 kg·m², cuplul $M_r = k\Omega^2$, cu $M_r = 0{,}8\,M_n$ la $\Omega_n$) este pornit de M15 alimentat de la un convertor care menține cuplul motor constant la 1,2·$M_n$ = 117,25 N·m până la turația nominală. Cât durează pornirea?

**Rezolvare.** $k = 0{,}8\cdot 97{,}71/153{,}52^2 = 3{,}32\cdot 10^{-3}$ N·m·s². Cu formula din § 5.7:

$$t = \frac{1}{\sqrt{117{,}25\cdot 0{,}00332}}\ \operatorname{artanh}\left(153{,}52\sqrt{\frac{0{,}00332}{117{,}25}}\right) = 1{,}838\ \text{s}.$$

**Verificări (două căi independente):** integrarea numerică a integralei $J\int d\Omega/(M - k\Omega^2)$ (cuadratură) și integrarea în timp a ecuației mișcării dau tot 1,838 s ✓ (figura 5.10).

Dacă s-ar presupune, greșit, că ventilatorul are tot timpul cuplul de la turația nominală, ar rezulta 3,93 s – o supraestimare de peste două ori.

![Figura 5.10 – Pornirea ventilatorului](figuri/f05-4-accelerare-ventilator.svg)

*Figura 5.10 – Turația ventilatorului în timpul pornirii: soluția analitică, integrarea numerică și ipoteza greșită a cuplului rezistent constant.*

### Problema 5.3 – Alegerea motorului pentru un ciclu de sarcină

O mașină cere periodic, la circa 1460 rot/min: 120 N·m timp de 10 s, 60 N·m timp de 30 s și 20 N·m timp de 20 s (fără pauze). Este potrivit un motor de 11 kW, 1460 rot/min, cu $\lambda = M_{max}/M_n$ = 2,8?

**Rezolvare.**

$$M_{ech} = \sqrt{\frac{120^2\cdot 10 + 60^2\cdot 30 + 20^2\cdot 20}{60}} = 65{,}83\ \text{N·m}.$$

Motorul: $M_n = 9550\cdot 11/1460 = 71{,}95$ N·m ≥ 65,83 N·m – **acceptat termic**. La suprasarcină: cuplul maxim cerut, 120 N·m, trebuie asigurat și la $U = 0{,}9U_n$: $M_{max}\cdot 0{,}81 \ge 120$, deci $M_{max} \ge 148{,}1$ N·m; motorul are $2{,}8\cdot 71{,}95 = 201$ N·m – **acceptat**.

**Verificare (model termic).** S-a simulat încălzirea motorului cu un model de ordinul 1 (constanta de timp 20 min, pierderi = 350 W constante + 700 W·$(M/M_n)^2$) timp de 150 de cicluri: supratemperatura medie în regim periodic este 74,84 K, iar cu cuplul $M_{ech}$ constant – 74,88 K ✓ (diferență 0,05 %). Cu media aritmetică a cuplului (56,67 N·m) s-ar obține doar 62,7 K – o subestimare periculoasă (figura 5.5).

### Problema 5.4 – Ventilator: clapetă sau convertor de frecvență?

Un ventilator absoarbe 30 kW la debitul nominal. El funcționează 6000 h/an la 70 % din debit. Cu reglaj prin clapetă, puterea absorbită la 70 % debit este 80 % din cea nominală (valoare citită de pe caracteristica ventilatorului – dată a problemei). Cât se economisește cu un convertor de frecvență cu randamentul 97 %?

**Rezolvare.** Cu clapetă: $0{,}8\cdot 30 = 24$ kW. Cu convertor (legea cubului): $30\cdot 0{,}7^3/0{,}97 = 10{,}61$ kW. Economia: 13,39 kW, adică **80 350 kWh/an**.

**Verificare (prin legile separate):** $Q \propto n$ → 0,7; $H \propto n^2$ → 0,49; $P \propto QH$ → $0{,}7\cdot 0{,}49 = 0{,}343$ ✓.

### Problema 5.5 – Stabilitatea punctelor de funcționare

M15 (formula lui Kloss cu datele de catalog) antrenează un cuplu rezistent constant $M_r = 2M_n$. Determinați punctele de funcționare și stabilitatea lor.

**Rezolvare.** Ecuația lui Kloss $2M_{max}/(s/s_k + s_k/s) = M_r$ are, cu $\lambda' = M_{max}/M_r = 1{,}55$, soluțiile

$$s = s_k\left(\lambda' \mp \sqrt{\lambda'^2 - 1}\right):\qquad s_A = 0{,}0500\ (n_A = 1425\ \text{rot/min}), \qquad s_B = 0{,}374\ (n_B = 939\ \text{rot/min}).$$

Pantele caracteristicii motorului: în A, $dM/d\Omega = -19{,}0$ N·m·s < 0 = $dM_r/d\Omega$ – **stabil**; în B, $dM/d\Omega = +2{,}54$ N·m·s > 0 – **instabil** (figura 5.2). **Verificare:** rezolvarea numerică a ecuației dă aceleași alunecări ✓.

### Problema 5.6 – Punctul de funcționare al unui ventilator

Un ventilator cere $0{,}9M_n$ la turația nominală ($M_r = k_v\Omega^2$). La ce turație funcționează M15 alimentat direct de la rețea?

**Rezolvare.** Rezolvând numeric $M_{Kloss}(s) = k_v[(1-s)\Omega_1]^2$: $s = 0{,}02039$, $n = 1469{,}4$ rot/min, $M = 88{,}35$ N·m, $P = 13{,}6$ kW. **Verificare** (aproximarea liniară $M \approx M_n s/s_n$, ecuație de gradul doi): $n = 1469{,}3$ rot/min ✓.

### Problema 5.7 – Energia pierdută în rotor la pornire

Câtă căldură se degajă în rotorul lui M15 la o pornire directă în gol ($J$ = 0,1 kg·m²)?

**Rezolvare.** $W_{Cu2} = \tfrac12J\Omega_1^2 = \tfrac12\cdot 0{,}1\cdot 157{,}08^2 = 1234$ J (§ 5.7). **Verificare:** integrarea numerică a pierderilor $sP_\delta$ în timpul pornirii simulate (modelul cu colivie dublă, durata ≈ 0,07 s) dă 1233,7 J ✓. La pornirea cu sarcină, energia pierdută este mai mare; la pornirea cu convertor de frecvență (alunecare mică în tot timpul pornirii), mult mai mică.

---

## Întrebări de autoevaluare

1. Care sunt componentele unei acționări electrice?
2. Scrieți ecuația fundamentală a mișcării și explicați regimurile pe care le descrie.
3. Cum se raportează un moment de inerție la arborele motorului printr-un reductor cu raportul $i$? De ce?
4. De ce cuplul raportat diferă la ridicarea și la coborârea unei sarcini?
5. Enunțați criteriul de stabilitate a punctului de funcționare.
6. Dați exemple de funcționare în cadranele II și IV.
7. De ce media aritmetică a cuplului nu este potrivită pentru alegerea motorului?
8. Care sunt etapele de conversie dintr-un convertor de frecvență?
9. De ce un convertor cu redresor cu diode are nevoie de rezistor de frânare?
10. Explicați de ce reglarea debitului unui ventilator prin turație este mult mai economică decât prin clapetă.
11. Ce rol are contactul de automenținere din schema de comandă a unui contactor?
12. De ce contactoarele de sens direct și invers trebuie interblocate?

<details>
<summary><b>Răspunsuri</b></summary>

1. Rețeaua, convertorul (opțional), motorul, transmisia, mașina de lucru și sistemul de comandă și reglare (§ 5.1).
2. $J\,d\Omega/dt = M - M_r$; regim staționar dacă $M = M_r$, accelerare dacă $M > M_r$, decelerare dacă $M < M_r$ (§ 5.2).
3. $J' = J/i^2$ – din conservarea energiei cinetice; masele de după un reductor cu raport mare contează puțin (§ 5.3).
4. Pentru că pierderile din transmisie sunt acoperite de motor la ridicare (cuplul raportat crește) și de sarcină la coborâre (cuplul raportat scade) (§ 5.3, problema 5.1).
5. $dM/d\Omega < dM_r/d\Omega$ în punctul de funcționare (§ 5.5).
6. Frânarea unui vehicul în mers înainte (II); coborârea unei sarcini grele cu o macara (IV) (§ 5.6).
7. Pentru că încălzirea depinde de pierderi, proporționale aproximativ cu $M^2$; media aritmetică subestimează pierderile (§ 5.8, problema 5.3).
8. Redresare (c.a. → c.c.), filtrare în circuitul intermediar, invertare PWM (c.c. → c.a. de frecvență și tensiune reglabile) (§ 5.9).
9. Pentru că energia de frânare nu poate trece prin diode înapoi în rețea; ar ridica tensiunea circuitului intermediar până la deconectarea convertorului (§ 5.9).
10. Puterea ventilatorului variază cu cubul turației; clapeta reduce debitul păstrând turația și disipă energia în pierderi de presiune (§ 5.10).
11. Menține bobina contactorului alimentată după eliberarea butonului de pornire; la căderea tensiunii, motorul nu repornește singur (§ 5.11).
12. Închiderea simultană ar scurtcircuita două faze ale rețelei (§ 5.11).

</details>

---

**Bibliografie pentru capitol:** [3], [5], [6], [7]; standarde [S1], [S6]. Lista completă este în [README](README.md#bibliografie).

[← Capitolul 4](04-motorul-sincron.md) · [Cuprins](README.md) · [Îndrumar de laborator →](06-indrumar-laborator.md)
