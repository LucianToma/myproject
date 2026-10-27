# Îndrumar de laborator

Îndrumarul conține șapte lucrări, corelate cu capitolele cursului. Fiecare lucrare are: scopul, noțiunile necesare (cu trimitere la curs), aparatura, schema de montaj, măsurile de securitate specifice, modul de lucru, tabelele de măsurători, prelucrarea datelor și **verificările de coerență** – fiecare rezultat important se obține, unde este posibil, pe **două căi** (de exemplu, randamentul măsurat direct și calculat din pierderi), ca să se poată depista erorile de măsurare.

| Lucrare | Tema | Capitol |
|---|---|---|
| L1 | Transformatorul monofazat – încercările de mers în gol și de scurtcircuit | 1 |
| L2 | Transformatorul monofazat – funcționarea în sarcină | 1 |
| L3 | Motorul asincron trifazat – identificare, încercările de mers în gol și de scurtcircuit | 2 |
| L4 | Motorul asincron trifazat – caracteristicile de funcționare și pornirea stea-triunghi | 2, 5 |
| L5 | Generatorul sincron – caracteristicile de gol, de scurtcircuit și externă | 3 |
| L6 | Mașina sincronă la rețea – sincronizarea, reglajul puterilor, curbele în V | 3, 4 |
| L7 | Acționare cu convertor de frecvență – reglajul vitezei, economia de energie la o pompă/ventilator | 2, 5 |

Aparatura concretă (puteri, tensiuni, tipuri de aparate) diferă de la un laborator la altul; valorile se completează din plăcuțele indicatoare ale echipamentelor disponibile.

---

## Reguli de securitate în laborator

Activitatea în laborator se desfășoară numai după **instruirea de securitate și sănătate în muncă** (cadrul legal: Legea nr. 319/2006 [S9] și instrucțiunile proprii ale laboratorului) și numai sub supravegherea cadrului didactic.

1. **Montajul se realizează numai cu sursele deconectate**; înainte de punerea sub tensiune, el este verificat de cadrul didactic.
2. Se folosesc numai conductoare și borne de securitate (izolate), în stare bună. Nu se ating părțile conductoare ale montajului aflat sub tensiune.
3. Orice modificare a montajului se face **numai după deconectarea alimentării** și verificarea lipsei tensiunii.
4. **Piesele în mișcare** (arbori, cuplaje) trebuie să aibă apărătoare; nu se poartă haine largi, fulare, părul se strânge.
5. **Sursele reglabile** (autotransformatoare, excitații) se aduc la **zero** înainte de conectare și de deconectare.
6. **Secundarul unui transformator de curent nu se lasă niciodată deschis** (§ 1.10).
7. **Condensatoarele** din convertoarele de frecvență rămân încărcate după deconectare: se așteaptă timpul indicat de producător (de ordinul minutelor) și se verifică lipsa tensiunii înainte de orice intervenție.
8. La orice situație anormală (miros de ars, zgomot, fum, încălzire) se acționează **oprirea de urgență** și se anunță cadrul didactic.

**Referatul** fiecărei lucrări conține: schema de montaj, datele nominale ale echipamentelor, tabelele de măsurători, calculele (cu un exemplu de calcul complet), graficele, verificările de coerență și concluziile (comparație cu teoria și cu datele de catalog).

---

## L1. Transformatorul monofazat – încercările de mers în gol și de scurtcircuit

**Scop.** Determinarea raportului de transformare, a pierderilor în fier și în cupru, a tensiunii de scurtcircuit și a parametrilor schemei echivalente (§ 1.5, § 1.6, problema 1.2).

**Aparatură.** Transformator monofazat de încercat; autotransformator reglabil (AT); ampermetru, voltmetre, wattmetru (sau analizor de rețea); ohmmetru sau sursă de c.c. cu voltmetru și ampermetru.

**Măsuri specifice.** La încercarea de scurtcircuit, tensiunea se crește **lent, de la zero**, urmărind ampermetrul; nu se depășește curentul nominal. Domeniile aparatelor se aleg după curenții și tensiunile nominale.

### Mod de lucru

1. Se notează datele nominale: $S_n$, $U_{1n}$, $U_{2n}$, $I_{1n}$, $I_{2n}$, $f_n$.
2. Se măsoară rezistențele înfășurărilor în c.c. ($R_1$, $R_2$) și temperatura mediului.
3. **Mers în gol** (figura L.1): se alimentează înfășurarea JT de la AT; ÎT rămâne în gol, cu voltmetrul $V_2$. Se crește tensiunea de la circa 0,3·$U_n$ până la circa 1,1·$U_n$ și se notează, pentru 6–8 puncte: $U_0$, $I_0$, $P_0$, $U_{20}$.
4. **Scurtcircuit** (figura L.2): se alimentează ÎT de la AT, cu JT scurtcircuitată prin ampermetru. Se crește tensiunea de la zero până la $I = I_n$ (eventual 1,1·$I_n$), notând 5–6 puncte: $U_{sc}$, $I_{sc}$, $P_{sc}$, $I_{2sc}$.

![Figura L.1 – Încercarea de mers în gol](figuri/fL-1-incercare-gol.svg)

*Figura L.1 – Montajul pentru încercarea de mers în gol.*

![Figura L.2 – Încercarea de scurtcircuit](figuri/fL-2-incercare-scurtcircuit.svg)

*Figura L.2 – Montajul pentru încercarea de scurtcircuit.*

### Tabele de măsurători

**Mers în gol**

| Nr. | $U_0$ [V] | $I_0$ [A] | $P_0$ [W] | $U_{20}$ [V] | $k = U_{20}/U_0$ | $\cos\varphi_0$ | $i_0$ [%] |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| ... | | | | | | | |

**Scurtcircuit**

| Nr. | $U_{sc}$ [V] | $I_{sc}$ [A] | $P_{sc}$ [W] | $I_{2sc}$ [A] | $Z_{sc}$ [Ω] | $R_{sc}$ [Ω] | $\cos\varphi_{sc}$ |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| ... | | | | | | | |

### Prelucrarea datelor

- Graficele $I_0(U_0)$, $P_0(U_0)$, $\cos\varphi_0(U_0)$ – se observă creșterea rapidă a curentului peste tensiunea nominală (saturația, § 0.2); $P_0$ crește aproximativ cu $U_0^2$.
- Graficele $U_{sc}(I_{sc})$ (liniar), $P_{sc}(I_{sc})$ (parabolă).
- La $U_0 = U_n$: $R_{Fe}$, $X_m$; la $I_{sc} = I_n$: $Z_{sc}$, $R_{sc}$, $X_{sc}$, $u_{sc}$, $u_R$, $u_X$ – cu formulele din § 1.5–1.6.

### Verificări de coerență

1. **Raportul de transformare** din încercarea de gol ($U_{20}/U_0$) și din încercarea de scurtcircuit ($I_{2sc}/I_{sc}$) trebuie să fie apropiate (în scurtcircuit, curentul de magnetizare este neglijabil).
2. **$R_{sc}$ din încercarea de scurtcircuit** față de **$R_1 + k^2R_2$ din măsurarea în c.c.**: prima este puțin mai mare (rezistența în c.a., efectul pelicular, pierderile suplimentare și eventual încălzirea); o diferență mare indică o eroare.
3. **$P_0$ la $U_n$** comparat cu pierderile din catalog (dacă există). Pentru comparații corecte, **$P_{sc}$** se raportează la temperatura de referință a standardului (pentru transformatoarele în ulei, 75 °C – IEC 60076-1 [S3]), ținând seama de variația rezistenței cuprului cu temperatura.

### Întrebări

1. De ce la mers în gol se alimentează, de regulă, înfășurarea de JT?
2. De ce $\cos\varphi_0$ este mic?
3. Ce s-ar întâmpla dacă încercarea de scurtcircuit s-ar începe la tensiunea nominală?

---

## L2. Transformatorul monofazat – funcționarea în sarcină

**Scop.** Ridicarea caracteristicii externe $U_2(I_2)$ și a randamentului $\eta(\beta)$; compararea cu valorile calculate din parametrii determinați în L1 (§ 1.7).

**Aparatură.** Transformatorul din L1; sarcină rezistivă reglabilă (reostat sau rezistențe în trepte) și, dacă există, sarcină inductivă (bobine) sau capacitivă (condensatoare); aparate de măsură pe primar și pe secundar (ampermetre, voltmetre, wattmetre sau analizoare).

### Mod de lucru

1. Se alimentează primarul la $U_{1n}$ (menținută constantă pe tot parcursul).
2. Se crește sarcina rezistivă de la zero la circa 1,1·$I_{2n}$, în 6–8 trepte. Pentru fiecare treaptă: $U_1$, $I_1$, $P_1$, $U_2$, $I_2$, $P_2$.
3. Dacă există sarcină inductivă/capacitivă: se repetă pentru $\cos\varphi_2 \approx 0{,}8$.

| Nr. | $U_1$ [V] | $I_1$ [A] | $P_1$ [W] | $U_2$ [V] | $I_2$ [A] | $P_2$ [W] | $\beta$ | $\eta_{direct}$ [%] | $\eta_{indirect}$ [%] | $\Delta U$ [%] |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | | |
| ... | | | | | | | | | | |

### Prelucrarea datelor și verificări

- **Randamentul pe două căi:** (a) **direct**, $\eta = P_2/P_1$; (b) **indirect**, din pierderile măsurate în L1: $\eta = \dfrac{P_2}{P_2 + P_0 + \beta^2P_{sc}}$. Metoda indirectă este, de regulă, **mai precisă** la transformatoarele cu randament mare: o eroare de 1 % la măsurarea lui $P_1$ și $P_2$ poate schimba mult diferența lor, deci pierderile (de aceea și standardele preferă determinarea din pierderi).
- **Căderea de tensiune pe două căi:** măsurată, $\Delta U = (U_{20} - U_2)/U_{20}$, și calculată cu formula din § 1.7, cu $u_R$, $u_X$ din L1.
- Graficele $U_2(\beta)$ și $\eta(\beta)$; se marchează $\beta_{opt} = \sqrt{P_0/P_{sc}}$ și se compară cu maximul curbei măsurate.

### Întrebări

1. De ce randamentul este mic la sarcini foarte mici?
2. Cum arată caracteristica externă la sarcină capacitivă și de ce?

---

## L3. Motorul asincron trifazat – identificare, încercările de mers în gol și de scurtcircuit

**Scop.** Interpretarea plăcuței indicatoare, conexiunile stea/triunghi și inversarea sensului de rotație; determinarea pierderilor și a parametrilor schemei echivalente (§ 2.3, problema 2.2).

**Aparatură.** Motor asincron cu rotor în colivie; sursă trifazată reglabilă (autotransformator trifazat); aparate de măsură trifazate (sau ampermetru, voltmetru și două wattmetre, montajul Aron – figura L.3); tahometru; dispozitiv de blocare a rotorului; sursă de c.c. pentru măsurarea rezistențelor.

![Figura L.3 – Metoda celor două wattmetre](figuri/fL-3-metoda-aron.svg)

*Figura L.3 – Măsurarea puterii trifazate prin metoda celor două wattmetre (Aron). Indicația unui wattmetru poate deveni negativă la $\cos\varphi < 0{,}5$ (de exemplu, la mers în gol) – atunci se inversează bobina lui de tensiune și citirea se scade.*

### Mod de lucru

1. **Plăcuța:** se notează $P_n$, $U_n$ și conexiunea, $I_n$, $n_n$, $\cos\varphi_n$, $\eta_n$, clasa IE, clasa de izolație, IP, regimul. Se verifică $P_n \approx \sqrt3U_nI_n\cos\varphi_n\eta_n$ (§ 0.10).
2. **Conexiunea:** se stabilește, din plăcuță și tensiunea rețelei, dacă motorul se leagă în stea sau în triunghi (§ 0.7) și se realizează legăturile în cutia de borne.
3. **Rezistența statorică:** se măsoară în c.c. rezistența între două borne, $R_b$; pentru steaua echivalentă, $R_1 = R_b/2$ (valabil pentru ambele conexiuni).
4. **Sensul de rotație:** se pornește motorul în gol, se notează sensul; se inversează două faze și se verifică inversarea sensului (§ 0.8).
5. **Mers în gol:** motorul fără sarcină se alimentează la tensiuni de la circa 1,1·$U_n$ coborând spre circa 0,3·$U_n$ (sau până când turația începe să scadă vizibil). Pentru 7–9 puncte: $U_0$, $I_0$, $P_0$, $n_0$.
6. **Scurtcircuit (rotor blocat):** cu rotorul blocat mecanic, se crește tensiunea de la zero până la $I = I_n$; se notează $U_{sc}$, $I_{sc}$, $P_{sc}$ în 4–5 puncte. **Măsurătoarea se face rapid**, motorul blocat nu se răcește.

### Tabele de măsurători

**Mers în gol**

| Nr. | $U_0$ [V] | $I_0$ [A] | $P_0$ [W] | $n_0$ [rot/min] | $P_{Cu1,0} = 3R_1I_0^2$ [W] | $P_0' = P_0 - P_{Cu1,0}$ [W] | $U_0^2$ [V²] |
|---|---|---|---|---|---|---|---|
| 1 | | | | | | | |
| ... | | | | | | | |

**Scurtcircuit**

| Nr. | $U_{sc}$ [V] | $I_{sc}$ [A] | $P_{sc}$ [W] | $Z_{sc}$ [Ω] | $R_{sc}$ [Ω] | $X_{sc}$ [Ω] |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| ... | | | | | | |

### Prelucrarea datelor

- **Separarea pierderilor:** $P_0' = P_{Fe} + P_m$, cu $P_{Fe} \propto U^2$ și $P_m$ practic constant (turația aproape constantă). Se reprezintă $P_0'$ în funcție de $U_0^2$: punctele sunt aproximativ pe o dreaptă, care, **extrapolată la $U = 0$**, dă $P_m$; la $U_n$, diferența este $P_{Fe}$ (metoda este descrisă și în IEC 60034-2-1 [S10]).
- **Scurtcircuit, pe steaua echivalentă:** $Z_{sc} = \dfrac{U_{sc}/\sqrt3}{I_{sc}}$, $R_{sc} = \dfrac{P_{sc}}{3I_{sc}^2}$, $X_{sc} = \sqrt{Z_{sc}^2 - R_{sc}^2}$; $R_2' \approx R_{sc} - R_1$; $X_{1\sigma} \approx X_{2\sigma}' \approx X_{sc}/2$.
- **Valori de pornire estimate:** $I_p \approx I_{sc}\dfrac{U_n}{U_{sc}}$, $M_p \approx \dfrac{P_{sc} - 3R_1I_{sc}^2}{\Omega_1}\left(\dfrac{U_n}{U_{sc}}\right)^2$ (puterea transmisă rotorului blocat se transformă integral în pierderi, $P_\delta = P_{Cu2}$, iar $M = P_\delta/\Omega_1$). Ambele sunt aproximative: la tensiune nominală, saturarea căilor fluxului de dispersie mărește curentul de pornire real.

### Verificări de coerență

1. $I_p/I_n$ și $M_p/M_n$ estimate se compară cu datele de catalog.
2. Cu parametrii determinați, se calculează (ca în problema 2.2) curentul și $\cos\varphi$ la alunecarea nominală și se compară cu plăcuța.

### Întrebări

1. De ce curentul de mers în gol al motorului (în % din $I_n$) este mult mai mare decât la transformator?
2. De ce la tensiuni mici turația de mers în gol începe să scadă?

---

## L4. Motorul asincron trifazat – caracteristicile de funcționare și pornirea stea-triunghi

**Scop.** Ridicarea caracteristicilor de funcționare și a unei porțiuni a caracteristicii mecanice; observarea curentului la pornirea directă și stea-triunghi (§ 2.5–2.7, § 5.2).

**Aparatură.** Motorul din L3, cuplat cu o **frână** cu măsurarea cuplului (frână electromagnetică/cu pulberi cu dinamometru, generator de c.c. etalonat sau traductor de cuplu); tahometru; aparate de măsură trifazate; comutator stea-triunghi; clește ampermetric cu memorarea valorii de vârf sau osciloscop cu sondă de curent.

### Mod de lucru

1. Se alimentează motorul la $U_n$ (menținută constantă). Se încarcă treptat cu frâna, de la gol până la circa 1,2·$P_n$ (fără a depăși durata admisă la suprasarcină).
2. Pentru fiecare treaptă: $U$, $I$, $P_1$, $n$, $M$.
3. **Pornirea:** se înregistrează vârful curentului și durata pornirii la pornirea directă și la pornirea stea-triunghi, în gol (motorul trebuie să admită conexiunea triunghi la tensiunea rețelei).

| Nr. | $U$ [V] | $I$ [A] | $P_1$ [W] | $n$ [rot/min] | $M$ [N·m] | $s$ | $P_2 = M\Omega$ [W] | $\eta$ [%] | $\cos\varphi$ |
|---|---|---|---|---|---|---|---|---|---|
| 1 | | | | | | | | | |
| ... | | | | | | | | | |

### Prelucrarea datelor și verificări

- Graficele $\eta$, $\cos\varphi$, $I$, $n$ în funcție de $P_2$ (ca în figura 2.6) și $M(n)$ în zona stabilă.
- **Cuplul pe două căi:** măsurat la frână și calculat din puteri: $M \approx \dfrac{P_1 - P_{Cu1} - P_{Fe}}{\Omega_1}$ (cuplul electromagnetic, din puterea electromagnetică, cu $P_{Fe}$ din L3); diferența față de cuplul măsurat la arbore corespunde pierderilor mecanice.
- **Caracteristica mecanică pe două căi:** punctele măsurate se compară cu formula lui Kloss construită din datele de catalog și cu schema echivalentă din L3.
- **Pornirea:** raportul vârfurilor curentului de linie la pornirea directă și stea-triunghi se compară cu valoarea teoretică 3 (§ 2.7). În practică, raportul măsurat poate fi afectat de vârful tranzitoriu de la comutarea din stea în triunghi.

### Întrebări

1. De ce randamentul și factorul de putere scad mult la sarcini mici?
2. Ce se întâmplă dacă sarcina depășește cuplul maxim?

---

## L5. Generatorul sincron – caracteristicile de gol, de scurtcircuit și externă

**Scop.** Ridicarea caracteristicilor de mers în gol și de scurtcircuit, determinarea reactanței sincrone și a SCR, ridicarea caracteristicii externe (§ 3.3–3.7, problema 3.2).

**Aparatură.** Generator sincron antrenat la turație constantă (de un motor de c.c. sau de un motor asincron alimentat de la convertor); sursă de c.c. reglabilă pentru excitație, cu ampermetru; tahometru; voltmetre și ampermetre pe stator; sarcină rezistivă trifazată.

**Măsuri specifice.** Curentul de excitație se variază **într-un singur sens** pe parcursul unei caracteristici (crescător), pentru a nu introduce erori de histerezis. La scurtcircuit, bornele statorului se scurtcircuitează (prin ampermetre) **înainte** de aplicarea excitației, care se crește de la zero.

### Mod de lucru

1. Se aduce generatorul la turația nominală și se menține constantă.
2. **Mers în gol:** se crește $I_e$ de la zero până la $U_0 \approx 1{,}2U_n$; se notează $I_e$, $U_0$ (și tensiunea remanentă la $I_e = 0$).
3. **Scurtcircuit:** cu statorul scurtcircuitat, se crește $I_e$ până la $I_{sc} \approx I_n$; se notează $I_e$, $I_{sc}$.
4. **Caracteristica externă:** se reglează $I_e$ pentru $U = U_n$ la $I = I_n$ (sarcină rezistivă), apoi, cu $I_e$ și $n$ constante, se reduce sarcina până la gol, notând $U$ și $I$.

| $I_e$ [A] | $U_0$ [V] | | $I_e$ [A] | $I_{sc}$ [A] | | $I$ [A] | $U$ [V] |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

### Prelucrarea datelor și verificări

- Graficele $U_0(I_e)$ și $I_{sc}(I_e)$ pe aceeași diagramă (ca în figura 3.2); se trasează dreapta întrefierului.
- $X_s = U_{0f}(I_{e0})/I_{sc}(I_{e0})$ la $I_{e0}$ care dă $U_n$ în gol; $x_s$ în unități relative; **SCR pe două căi:** $I_{e0}/I_{e,sc}$ și $1/x_s$ (problema 3.2).
- **Caracteristica externă pe două căi:** măsurată și calculată din $E_0 = \sqrt{U^2 + (X_sI)^2}$ (sarcină rezistivă, § 3.5). Diferențele se datorează saturației și rezistenței statorice.

### Întrebări

1. De ce caracteristica de scurtcircuit este liniară?
2. De ce tensiunea scade la creșterea sarcinii rezistive la excitație constantă?

---

## L6. Mașina sincronă la rețea – sincronizarea, reglajul puterilor, curbele în V

**Scop.** Sincronizarea unui generator cu rețeaua; observarea reglajului independent al puterii active (din mașina de antrenare) și al puterii reactive (din excitație); ridicarea curbelor în V (§ 3.9, § 4.3).

**Aparatură.** Grupul din L5; trei becuri de sincronizare (sau sincronoscop/releu de sincronizare); voltmetru dublu și frecvențmetru dublu (rețea – generator); întrerupător trifazat; aparate de măsură trifazate pe stator (P, Q, I, cos φ).

**Măsuri specifice.** Becurile de sincronizare sunt supuse până la dublul tensiunii de fază – se folosesc becuri (sau grupuri de becuri) dimensionate corespunzător. Conectarea se face **numai** cu acordul cadrului didactic.

### Mod de lucru

1. **Condițiile de sincronizare** (§ 3.9): se reglează turația (frecvența) și excitația (tensiunea) generatorului până la valori egale cu ale rețelei.
2. **Becurile „stinse”:** becurile sunt legate între fazele omoloage ale generatorului și rețelei. Când frecvențele sunt apropiate, becurile se aprind și se sting **simultan**, din ce în ce mai rar; dacă ele se aprind **pe rând** (lumina „se rotește”), succesiunea fazelor diferă și se inversează două faze ale generatorului. Întrerupătorul se închide în mijlocul intervalului în care becurile sunt stinse.
3. **Puterea activă:** se mărește cuplul mașinii de antrenare; se observă creșterea lui $P$, turația rămânând constantă. Apoi se reduce cuplul de antrenare până la zero și chiar negativ: mașina sincronă trece în regim de **motor** (P schimbă semnul).
4. **Curbele în V:** la puterea activă menținută constantă (de exemplu $P \approx 0$ și $P \approx 0{,}5P_n$), se variază $I_e$ și se notează $I_e$, $I$, $P$, $Q$, $\cos\varphi$; nu se coboară excitația până la ieșirea din sincronism.

| $P$ ≈ ... | $I_e$ [A] | $I$ [A] | $P$ [W] | $Q$ [var] | $\cos\varphi$ | caracter |
|---|---|---|---|---|---|---|
| | | | | | | |

### Prelucrarea datelor și verificări

- Curbele $I(I_e)$ la cele două puteri (ca în figura 4.3) și curba punctelor cu $\cos\varphi = 1$.
- **Verificare pe două căi:** pentru fiecare punct, $\cos\varphi$ indicat de aparat se compară cu $P/\sqrt{P^2 + Q^2}$ și cu $P/(\sqrt3UI)$.
- Se verifică faptul că minimul curentului coincide cu $Q \approx 0$.

### Întrebări

1. Ce s-ar întâmpla la închiderea întrerupătorului cu tensiunile în opoziție de fază?
2. Ce mărime trebuie modificată pentru ca generatorul să livreze mai multă putere reactivă?

---

## L7. Acționare cu convertor de frecvență – reglajul vitezei și economia de energie

**Scop.** Parametrizarea unui convertor de frecvență, observarea comenzii U/f și a rampelor de accelerare/frânare; verificarea legilor de similitudine pe o pompă sau un ventilator (§ 2.8, § 5.9, § 5.10, problema 5.4).

**Aparatură.** Convertor de frecvență cu motor asincron cuplat cu o pompă (circuit hidraulic cu vană) sau un ventilator (tubulatură cu clapetă); analizor de rețea la intrarea convertorului; debitmetru (sau anemometru) și manometru; tahometru.

**Măsuri specifice.** Nu se intervine în convertor sau la bornele motorului decât după deconectare, așteptarea timpului de descărcare a condensatoarelor și verificarea lipsei tensiunii. Bornele de ieșire ale convertorului **nu** se leagă la rețea.

### Mod de lucru

1. **Parametrizare:** se introduc datele de pe plăcuța motorului ($P_n$, $U_n$, $I_n$, $f_n$, $n_n$, $\cos\varphi_n$); se rulează, dacă există, funcția de identificare automată a motorului; se aleg comanda U/f și rampele (de exemplu 5 s).
2. Se observă tensiunea circuitului intermediar (afișată de convertor) – se compară cu valoarea teoretică ≈ 540 V la rețeaua de 400 V (§ 5.9).
3. **Rampe:** se reduce progresiv timpul rampei de frânare și se observă (fără rezistor de frânare) apariția avertizării sau a deconectării la supratensiune în circuitul intermediar; se explică fenomenul (§ 5.9).
4. **Legile de similitudine:** cu vana/clapeta complet deschisă, pentru $f$ = 50, 45, 40, 35, 30, 25 Hz se notează: $f$, $n$, $Q$, $H$ (sau $\Delta p$), $P_1$ (la intrarea convertorului).
5. **Comparație cu laminarea:** la $f$ = 50 Hz, se reduce debitul cu vana/clapeta la aceleași valori ca la pasul 4 și se notează $P_1$.

| $f$ [Hz] | $n$ [rot/min] | $Q$ | $H$ sau $\Delta p$ | $P_1$ convertor [W] | $P_1$ cu vană [W] la același $Q$ |
|---|---|---|---|---|---|
| 50 | | | | | |
| ... | | | | | |

### Prelucrarea datelor și verificări

- **Legea cubului pe două căi:** (a) rapoartele $P/P_{50}$ comparate cu $(n/n_{50})^3$; (b) panta dreptei de regresie a lui $\ln P$ în funcție de $\ln n$ (teoretic 3). Abaterile se explică prin pierderile convertorului și ale motorului, prin înălțimea statică a instalației (la pompe) și prin variația randamentului mașinii de lucru.
- **Similar pentru $Q \propto n$ și $H \propto n^2$.**
- Graficul $P_1(Q)$ pentru cele două metode de reglaj (ca în figura 5.8) și economia anuală de energie pentru un profil de funcționare dat de cadrul didactic.

### Întrebări

1. De ce convertorul semnalează supratensiune la o frânare prea rapidă?
2. De ce economia de energie este mai mică la o pompă care ridică apa la o înălțime statică mare?

---

**Bibliografie pentru laborator:** [1], [2], [3]; standarde [S3], [S9], [S10]. Lista completă este în [README](README.md#bibliografie).

[← Capitolul 5](05-actionari-electrice.md) · [Cuprins](README.md)
