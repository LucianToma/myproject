# Capitolul 1. Transformatorul

> **Obiective.** După acest capitol ar trebui să puteți: (1) explica de ce energia se transportă la tensiune înaltă; (2) descrie construcția și principiul de funcționare al transformatorului; (3) desena și folosi schema echivalentă; (4) determina parametrii schemei din încercările de gol și scurtcircuit; (5) calcula căderea de tensiune și randamentul în sarcină; (6) interpreta notația grupei de conexiuni (ex. Dyn11) și condițiile de funcționare în paralel.

Transformatorul este studiat **primul** pentru că este cea mai simplă mașină electrică (nu are piese în mișcare), iar ideile introduse aici – raportarea mărimilor, schema echivalentă, încercările de gol și scurtcircuit – se refolosesc direct la motorul asincron (cap. 2).

---

## 1.1. Rolul transformatorului

Transformatorul modifică **tensiunea și curentul** unui sistem de curent alternativ, păstrând frecvența și (aproape) puterea. Este indispensabil în transportul energiei: la aceeași putere $S = \sqrt3 U I$, creșterea tensiunii de $k$ ori reduce curentul de $k$ ori, iar pierderile în linie, $3RI^2$, scad de $k^2$ ori. De exemplu, transportând aceeași putere la 110 kV în loc de 20 kV ($k = 5{,}5$), pierderile în aceeași linie scad de circa 30 de ori.

Un lanț tipic: generator (la generatoarele mari, de ordinul 10–27 kV) → transformator ridicător → linii de 220–400 kV → transformatoare coborâtoare → rețele de 110 kV și 20 kV → **transformatoare de distribuție** 20/0,4 kV → consumatori la 230/400 V.

## 1.2. Construcția

- **Miezul magnetic** – din tole de oțel electrotehnic (de regulă cu grăunți orientați, 0,23–0,35 mm), izolate între ele, pentru limitarea curenților turbionari. Are **coloane** (pe care stau înfășurările) și **juguri** (care închid circuitul magnetic).
- **Înfășurările** – din cupru sau aluminiu. Înfășurarea conectată la sursă este **primarul**, cea conectată la sarcină – **secundarul**. După tensiune: înfășurarea de **înaltă tensiune (ÎT)** și cea de **joasă tensiune (JT)**. De obicei sunt concentrice, cu JT lângă miez (izolația față de miez este mai ușor de realizat pentru tensiunea mică).
- **Sistemul de răcire** – transformatoarele mari sunt cufundate în **ulei** (care izolează și răcește) într-o cuvă cu radiatoare; există și transformatoare **uscate** (izolate cu rășini), folosite în clădiri.
- **Accesorii** (transformatoare în ulei): conservator de ulei, releu de gaze (Buchholz), comutator de prize pentru reglarea raportului de transformare, termometre, izolatoare de trecere.

![Figura 1.1 – Principiul transformatorului monofazat](figuri/f01-1-principiu.svg)

*Figura 1.1 – Transformatorul monofazat: două înfășurări pe același miez magnetic, cuplate prin fluxul util Φ.*

## 1.3. Principiul de funcționare. Transformatorul ideal

Primarul, alimentat cu tensiunea alternativă $u_1$, produce în miez un flux alternativ $\Phi$. Acesta străbate ambele înfășurări și induce în ele, conform legii inducției (§ 0.4), tensiunile

$$E_1 = 4{,}44\, f N_1 \Phi_{max}, \qquad E_2 = 4{,}44\, f N_2 \Phi_{max}.$$

**Transformatorul ideal** are înfășurări fără rezistență, tot fluxul trece prin miez (fără dispersie), iar miezul are permeabilitate infinită și nu are pierderi. Pentru el:

$$\boxed{\frac{U_1}{U_2} = \frac{N_1}{N_2} = k}, \qquad \boxed{\frac{I_1}{I_2} = \frac{N_2}{N_1} = \frac1k}, \qquad U_1 I_1 = U_2 I_2 .$$

$k$ este **raportul de transformare**. A doua relație rezultă din legea circuitului magnetic: un miez ideal nu are nevoie de solenație pentru a fi magnetizat, deci $N_1 I_1 - N_2 I_2 = 0$ – **solenația secundarului este compensată de primar**. Așa „află” primarul cât curent cere sarcina.

**Transferul impedanței.** O impedanță $\underline{Z}$ legată la secundar este „văzută” din primar ca

$$\underline{Z}' = \frac{U_1}{I_1} = \frac{k U_2}{I_2/k} = k^2\,\underline{Z} .$$

> **Observație importantă.** Fluxul nu depinde de sarcină: la tensiune și frecvență constante, $\Phi_{max} = U_1/(4{,}44 f N_1)$ (§ 0.4). Când crește curentul secundar crește și cel primar, dar fluxul rămâne practic același.

## 1.4. Transformatorul real și schema echivalentă

Transformatorul real diferă de cel ideal prin:

| Fenomen | Element în schema echivalentă |
|---|---|
| rezistența înfășurărilor (pierderi Joule) | $R_1$, $R_2$ |
| fluxurile de dispersie (linii de câmp care înconjoară doar o înfășurare) | reactanțele de dispersie $X_{1\sigma}$, $X_{2\sigma}$ |
| curentul necesar magnetizării miezului | reactanța de magnetizare $X_m$ |
| pierderile în fier | rezistența $R_{Fe}$ |

Pentru a putea lega electric cele două părți, mărimile secundare se **raportează la primar** (se notează cu apostrof): $U_2' = kU_2$, $I_2' = I_2/k$, $R_2' = k^2R_2$, $X_{2\sigma}' = k^2X_{2\sigma}$. Raportarea păstrează puterile și pierderile. Ecuațiile transformatorului devin:

$$\underline{U}_1 = (R_1 + jX_{1\sigma})\,\underline{I}_1 + \underline{E}_1, \qquad \underline{E}_1 = \underline{U}_2' + (R_2' + jX_{2\sigma}')\,\underline{I}_2', \qquad \underline{I}_1 = \underline{I}_0 + \underline{I}_2',$$

cu $\underline{I}_0 = \underline{E}_1/R_{Fe} + \underline{E}_1/(jX_m)$ – **curentul de mers în gol**. Acestor ecuații le corespunde **schema echivalentă în T** (figura 1.2).

![Figura 1.2 – Schema echivalentă în T](figuri/f01-2-schema-T.svg)

*Figura 1.2 – Schema echivalentă în T a transformatorului, cu mărimile secundare raportate la primar.*

Curentul de mers în gol este mic (de ordinul unităților de procent din curentul nominal la transformatoarele de putere), iar căderile de tensiune pe $R_1$, $X_{1\sigma}$ sunt și ele mici. De aceea, pentru calculul funcționării în sarcină, se folosește **schema simplificată** (figura 1.3), în care ramura de magnetizare se neglijează și impedanțele longitudinale se adună:

$$R_{sc} = R_1 + R_2', \qquad X_{sc} = X_{1\sigma} + X_{2\sigma}', \qquad \underline{U}_1 = \underline{U}_2' + (R_{sc} + jX_{sc})\,\underline{I}_2' .$$

![Figura 1.3 – Schema simplificată](figuri/f01-3-schema-simplificata.svg)

*Figura 1.3 – Schema echivalentă simplificată, folosită pentru calculul căderii de tensiune.*

Problema 1.2 arată că diferența dintre schema în T și cea simplificată este sub 0,1 % pentru tensiunea secundară.

### Diagrama fazorială

Ecuația schemei simplificate se reprezintă grafic prin **diagrama fazorială** (figura 1.4), construită pornind de la $\underline{U}_2'$ și $\underline{I}_2'$ (defazat cu $\varphi_2$), la care se adaugă căderea pe rezistență (paralelă cu curentul) și căderea pe reactanță (perpendiculară pe curent, înainte cu 90°).

![Figura 1.4 – Diagrama fazorială](figuri/f01-4-diagrama-fazoriala.svg)

*Figura 1.4 – Diagrama fazorială pentru sarcină inductivă, calculată pentru transformatorul din problema 1.2. Căderile de tensiune sunt mărite de 5 ori, altfel nu s-ar distinge.*

## 1.5. Încercarea de mers în gol

**Montaj** (lucrarea L1 din [îndrumarul de laborator](06-indrumar-laborator.md)): o înfășurare (de regulă JT) se alimentează la tensiunea nominală, cealaltă rămâne deschisă. Se măsoară $U_0$, $I_0$, $P_0$ (și $U_{20}$, pentru raportul de transformare).

**Interpretare.** Curentul $I_0$ este mic, deci pierderile Joule $R_1 I_0^2$ sunt neglijabile, iar tensiunea și fluxul sunt cele nominale. Prin urmare

$$P_0 \approx P_{Fe}, \qquad \cos\varphi_0 = \frac{P_0}{U_0 I_0}, \qquad R_{Fe} = \frac{U_0}{I_0\cos\varphi_0}, \qquad X_m = \frac{U_0}{I_0\sin\varphi_0}, \qquad k \approx \frac{U_{1}}{U_{20}} .$$

Curentul de gol procentual este $i_0 = 100\, I_0/I_n$ [%].

## 1.6. Încercarea de scurtcircuit

**Montaj:** o înfășurare (de regulă ÎT) se alimentează de la o sursă reglabilă, cealaltă se scurtcircuitează (printr-un ampermetru). **Tensiunea se crește treptat de la zero** până când curentul ajunge la valoarea nominală. Se măsoară $U_{sc}$, $I_{sc} = I_n$, $P_{sc}$.

**Interpretare.** Tensiunea necesară este mică (câteva procente din $U_n$), deci fluxul și pierderile în fier sunt neglijabile, iar curenții sunt nominali:

$$P_{sc} \approx P_{Cu,n}, \qquad Z_{sc} = \frac{U_{sc}}{I_{n}}, \qquad R_{sc} = \frac{P_{sc}}{I_n^2}, \qquad X_{sc} = \sqrt{Z_{sc}^2 - R_{sc}^2}.$$

**Tensiunea de scurtcircuit procentuală** și componentele ei:

$$u_{sc} = 100\frac{U_{sc}}{U_n}\ [\%], \qquad u_R = 100\frac{P_{sc}}{S_n}, \qquad u_X = \sqrt{u_{sc}^2 - u_R^2} .$$

$u_{sc}$ este o mărime de catalog foarte importantă: la transformatoarele de distribuție are valori de ordinul 4–6 %. Ea determină

- **căderea de tensiune în sarcină** (§ 1.7);
- **curentul de scurtcircuit** la bornele secundare (alimentare de la o rețea foarte puternică): $I_{sc,borne} \approx 100\,I_n/u_{sc}$ – de exemplu, 25·$I_n$ pentru $u_{sc} = 4$ %;
- **împărțirea sarcinii** între transformatoare în paralel (§ 1.9).

## 1.7. Funcționarea în sarcină

### Căderea de tensiune

Definim **factorul de încărcare** $\beta = I_2/I_{2n} \approx S/S_n$. Proiectând ecuația fazorială a schemei simplificate pe direcția lui $\underline{U}_2'$, se obține formula practică

$$\boxed{\Delta U\% \approx \beta\,(u_R\cos\varphi_2 + u_X\sin\varphi_2)}$$

($\sin\varphi_2 > 0$ pentru sarcină inductivă, $< 0$ pentru capacitivă). O aproximare mai bună adaugă termenul de ordinul doi $\beta^2(u_X\cos\varphi_2 - u_R\sin\varphi_2)^2/200$; problemele 1.2 și 1.3 arată că, astfel corectată, formula coincide cu soluția exactă a ecuației fazoriale.

**Caracteristica externă** $U_2(\beta)$ la $U_1 = U_{1n}$ (figura 1.5): tensiunea scade cu sarcina inductivă și poate **crește** la sarcină capacitivă (când $u_X\lvert\sin\varphi_2\rvert > u_R\cos\varphi_2$).

![Figura 1.5 – Caracteristica externă](figuri/f01-6-caracteristica-externa.svg)

*Figura 1.5 – Caracteristica externă a transformatorului de 400 kVA, 20/0,4 kV, $u_{sc}$ = 4 % din problema 1.3 (calcul exact cu schema simplificată).*

Pentru menținerea tensiunii consumatorilor, transformatoarele au **prize** (de obicei ±2×2,5 %) care modifică puțin numărul de spire al înfășurării ÎT.

### Randamentul

Pierderile sunt de două feluri: **constante** (în fier, $P_0$, independente de sarcină) și **variabile** (în cupru, $\beta^2 P_{sc}$). Randamentul este

$$\boxed{\eta = \frac{\beta S_n\cos\varphi_2}{\beta S_n\cos\varphi_2 + P_0 + \beta^2 P_{sc}}} .$$

Derivând în raport cu $\beta$ și egalând cu zero, se obține că **randamentul este maxim când pierderile variabile sunt egale cu cele constante**:

$$\beta^2 P_{sc} = P_0 \quad\Rightarrow\quad \beta_{opt} = \sqrt{\frac{P_0}{P_{sc}}} .$$

![Figura 1.6 – Randamentul în funcție de încărcare](figuri/f01-5-randament.svg)

*Figura 1.6 – Randamentul transformatorului de 400 kVA ($P_0$ = 0,43 kW, $P_{sc}$ = 4,6 kW). Maximul este la $\beta \approx 0{,}31$, indiferent de $\cos\varphi_2$.*

Transformatoarele de distribuție funcționează mult timp la sarcini parțiale și sunt conectate permanent (pierderile în fier există 8760 h/an), de aceea sunt proiectate cu $P_0$ mic, deci cu $\beta_{opt}$ sub 0,5. Randamentul transformatoarelor de putere depășește, de regulă, 98 %.

Pierderile maxime admise pentru transformatoarele noi puse pe piața UE sunt reglementate de **Regulamentul (UE) nr. 548/2014** (proiectare ecologică), în două etape: Tier 1 din 1 iulie 2015 și Tier 2 din 1 iulie 2021 [S7].

## 1.8. Transformatorul trifazat

Un transformator trifazat poate fi realizat din trei transformatoare monofazate sau, mai economic, pe un **miez cu trei coloane**, câte o fază pe coloană.

**Conexiunile înfășurărilor** se notează cu **litere mari pentru ÎT** și **litere mici pentru JT**: Y/y – stea, D/d – triunghi, Z/z – zigzag; N/n – neutrul este scos la bornă.

**Atenție la raportul de transformare:** raportul tensiunilor *de linie* nu mai este neapărat egal cu raportul numărului de spire. La un transformator Dyn 20/0,4 kV, înfășurarea ÎT (în triunghi) are 20 kV pe fază, iar cea de JT (în stea) are $400/\sqrt3 = 230{,}9$ V pe fază: raportul spirelor este 86,6, nu 50 (problema 1.3).

### Grupa de conexiuni

Conexiunile diferite introduc un **defazaj** între tensiunile de linie ale ÎT și JT, întotdeauna multiplu de 30°. Defazajul se exprimă printr-un număr de la 0 la 11, după **analogia cu ceasul**: fazorul tensiunii ÎT este „minutarul” fixat la ora 12, iar fazorul corespunzător al JT este „orarul”. **Dyn11** înseamnă: ÎT în triunghi, JT în stea cu neutru accesibil, tensiunea JT defazată cu 11·30° = 330° în urma celei de ÎT (adică 30° înainte) – figura 1.7.

![Figura 1.7 – Grupa de conexiuni Dyn11](figuri/f01-7-grupa-dyn11.svg)

*Figura 1.7 – Grupa de conexiuni Dyn11 reprezentată pe cadranul ceasului.*

Dyn11 este conexiunea obișnuită a transformatoarelor de distribuție: neutrul JT permite alimentarea consumatorilor monofazați la 230 V, iar triunghiul de pe ÎT permite circulația curenților de secvență zero și a armonicilor de rang 3, care altfel ar deforma fluxul și ar dezechilibra tensiunile la sarcini nesimetrice.

## 1.9. Funcționarea în paralel

Două sau mai multe transformatoare funcționează în paralel când au legate împreună atât bornele primare, cât și cele secundare. Condiții:

1. **aceleași tensiuni nominale** (același raport de transformare) – altfel apare un curent de circulație chiar în gol;
2. **aceeași grupă de conexiuni** – altfel tensiunile secundare sunt defazate și curentul de circulație este de ordinul curentului de scurtcircuit;
3. **tensiuni de scurtcircuit cât mai apropiate** (în practică, abatere de cel mult ±10 %) – altfel sarcina nu se împarte proporțional cu puterile nominale;
4. ca recomandare practică, raportul puterilor nominale nu depășește 3:1.

Puterea preluată de transformatorul $i$ este invers proporțională cu impedanța lui (problema 1.4):

$$S_i = S_{total}\, \frac{S_{ni}/u_{sc,i}}{\sum_j S_{nj}/u_{sc,j}} .$$

Transformatorul cu $u_{sc}$ mai mic se încarcă mai mult și limitează puterea totală care poate fi transmisă fără suprasarcină.

## 1.10. Transformatoare speciale

- **Autotransformatorul** are o singură înfășurare, cu o priză; o parte din putere trece direct, electric, și numai fracțiunea $1 - U_2/U_1$ este transferată electromagnetic (problema 1.5). Este mai mic și mai ieftin când raportul de transformare este apropiat de 1, dar **nu asigură separarea galvanică** între circuite. Autotransformatorul reglabil (cu cursor) este sursa reglabilă folosită în laborator.
- **Transformatorul de curent** (de măsură) are primarul în serie cu circuitul și secundarul închis pe un ampermetru (impedanță foarte mică). **Secundarul nu trebuie lăsat niciodată deschis** sub sarcină: dispare solenația care compensa primarul, fluxul crește foarte mult, iar în secundar apar tensiuni periculoase.
- **Transformatorul de tensiune** (de măsură) funcționează practic în gol; **secundarul lui nu se scurtcircuitează**.
- **Transformatorul de sudură** are reactanța de dispersie mare (caracteristică externă puternic căzătoare), care limitează curentul la scurtcircuitul produs de electrod.
- **Transformatorul de separație** (raport 1:1) izolează galvanic un consumator de rețea, pentru protecția împotriva electrocutării.

---

## Probleme rezolvate

Toate rezultatele sunt calculate și verificate pe cel puțin două căi de scriptul [`scripts/probleme_cap01.py`](scripts/probleme_cap01.py).

### Problema 1.1 – Transformatorul ideal

Un transformator ideal 230/12 V, 50 Hz, are $N_1 = 1150$ spire și alimentează un bec de 12 V, 60 W. Determinați $N_2$, curenții, rezistența becului raportată la primar și fluxul maxim. Ce secțiune trebuie să aibă miezul pentru $B_{max} = 1{,}2$ T?

**Rezolvare.** $k = 230/12 = 19{,}167$; $N_2 = N_1/k = 60$ spire. $I_2 = P/U_2 = 5$ A, $R = U_2/I_2 = 2{,}4$ Ω. $I_1 = I_2/k = 0{,}2609$ A. Rezistența raportată: $R' = k^2R = 881{,}7$ Ω.

$$\Phi_{max} = \frac{U_1}{4{,}44 f N_1} = \frac{230}{4{,}44\cdot 50\cdot 1150} = 0{,}901\ \text{mWb}, \qquad A_{Fe} = \frac{\Phi_{max}}{B_{max}} = 7{,}51\ \text{cm}^2 .$$

**Verificare.** $I_1 = U_1/R' = 230/881{,}7 = 0{,}2609$ A ✓; $U_1I_1 = U_2I_2 = 60$ VA ✓.

### Problema 1.2 – Parametrii schemei echivalente din încercări

Un transformator monofazat 20 kVA, 2400/240 V, 50 Hz a dat la încercări:

| Încercare | Partea alimentată | U | I | P |
|---|---|---|---|---|
| mers în gol | JT | 240 V | 2,0 A | 120 W |
| scurtcircuit | ÎT | 96 V | 8,33 A | 300 W |

Determinați: (a) parametrii schemei echivalente; (b) tensiunea secundară la sarcină nominală cu $\cos\varphi_2 = 0{,}8$ inductiv; (c) randamentul în aceste condiții și randamentul maxim.

**(a) Parametrii.** Curenții nominali: $I_{1n} = 20\,000/2400 = 8{,}333$ A, $I_{2n} = 83{,}33$ A.

*Mers în gol (mărimi raportate la JT):* $\cos\varphi_0 = \dfrac{120}{240\cdot 2} = 0{,}25$; $I_a = 0{,}5$ A, $I_\mu = 2\sqrt{1 - 0{,}25^2} = 1{,}936$ A;

$$R_{Fe} = \frac{240}{0{,}5} = 480\ \Omega, \qquad X_m = \frac{240}{1{,}936} = 123{,}9\ \Omega .$$

Raportate la ÎT (înmulțite cu $k^2 = 100$): $R_{Fe} = 48{,}0$ kΩ, $X_m = 12{,}39$ kΩ. Curentul de gol este $i_0 = 2/83{,}33 = 2{,}4$ %.

*Scurtcircuit (mărimi raportate la ÎT):*

$$Z_{sc} = \frac{96}{8{,}333} = 11{,}52\ \Omega,\qquad R_{sc} = \frac{300}{8{,}333^2} = 4{,}32\ \Omega,\qquad X_{sc} = \sqrt{11{,}52^2 - 4{,}32^2} = 10{,}68\ \Omega .$$

$u_{sc} = 96/2400 = 4$ %, $u_R = 300/20\,000 = 1{,}5$ %, $u_X = \sqrt{4^2 - 1{,}5^2} = 3{,}708$ %. Dacă nu există alte informații, se ia $R_1 \approx R_2' = R_{sc}/2$ și $X_{1\sigma} \approx X_{2\sigma}' = X_{sc}/2$.

**(b) Tensiunea secundară.** Cu formula aproximativă:

$$\Delta U\% \approx 1\cdot(1{,}5\cdot 0{,}8 + 3{,}708\cdot 0{,}6) = 3{,}425\ \%,$$

iar cu termenul de ordinul doi: $3{,}425 + \dfrac{(3{,}708\cdot 0{,}8 - 1{,}5\cdot 0{,}6)^2}{200} = 3{,}446$ %. Deci $U_2 = 240\,(1 - 0{,}03446) = 231{,}7$ V.

*Verificare (calea a doua, exactă):* rezolvând ecuația fazorială $\underline{U}_1 = \underline{U}_2' + (R_{sc}+jX_{sc})\underline{I}_2'$ cu $U_1 = 2400$ V: $U_2' = 2317{,}3$ V, adică $U_2 = 231{,}73$ V și $\Delta U = 3{,}446$ % ✓. Recalculând $\underline{U}_1$ din $\underline{U}_2'$ și $\underline{I}_2'$ se obține $2400{,}0\angle 1{,}18°$ V ✓.

*Verificare (calea a treia, schema completă în T):* $U_2' = 2316{,}2$ V – diferență de 0,05 % față de schema simplificată.

**(c) Randamentul.**

$$\eta = \frac{20\,000\cdot 0{,}8}{16\,000 + 120 + 300} = 97{,}44\ \%, \qquad \beta_{opt} = \sqrt{\frac{120}{300}} = 0{,}632, \qquad \eta_{max} = 97{,}68\ \% .$$

*Verificare:* (1) $\beta_{opt}$ și $\eta_{max}$ s-au regăsit prin scanarea numerică a funcției $\eta(\beta)$; (2) schema în T dă pierderi totale de 421,4 W față de $P_0 + P_{sc} = 420$ W (diferență 0,3 %). Randamentul din schema în T, 97,34 %, este ușor mai mic pentru că acolo $P_2$ se calculează la tensiunea reală (231,7 V), nu la cea nominală; folosind aceeași $P_2$ reală în formula cu pierderi, rezultă 97,35 % ✓. Formula cu $P_2 = \beta S_n\cos\varphi_2$ dă **randamentul convențional**, calculat la tensiunea nominală.

### Problema 1.3 – Transformatorul de distribuție

Un transformator trifazat 400 kVA, 20/0,4 kV, Dyn11 are $u_{sc} = 4$ %, $P_0 = 0{,}43$ kW, $P_{sc} = 4{,}6$ kW. Alimentează o sarcină de 300 kW la $\cos\varphi = 0{,}9$ inductiv. Calculați: curenții nominali, raportul spirelor, căderea de tensiune, randamentul, încărcarea optimă și curentul de scurtcircuit la bornele JT.

**Rezolvare.**

- Curenții de linie: $I_{1n} = \dfrac{400\,000}{\sqrt3\cdot 20\,000} = 11{,}55$ A, $I_{2n} = \dfrac{400\,000}{\sqrt3\cdot 400} = 577{,}4$ A. Prin înfășurarea ÎT (triunghi) circulă $11{,}55/\sqrt3 = 6{,}67$ A.
- Raportul tensiunilor de linie: 50; raportul spirelor (tensiuni de fază): $20\,000/230{,}9 = 86{,}6$.
- $u_R = 4{,}6/400 = 1{,}15$ %, $u_X = \sqrt{4^2 - 1{,}15^2} = 3{,}831$ %.
- Încărcarea: $S = 300/0{,}9 = 333{,}3$ kVA, $\beta = 0{,}8333$.
- Căderea de tensiune: $\Delta U \approx 0{,}8333\,(1{,}15\cdot 0{,}9 + 3{,}831\cdot 0{,}436) = 2{,}254$ %; cu termenul de ordinul doi, 2,284 %; deci $U_2 = 390{,}9$ V.
- Pierderile: $P_0 + \beta^2P_{sc} = 430 + 0{,}8333^2\cdot 4600 = 3624$ W; randamentul $\eta = \dfrac{300\,000}{303\,624} = 98{,}81$ %.
- Încărcarea optimă: $\beta_{opt} = \sqrt{0{,}43/4{,}6} = 0{,}306$, adică 122 kVA; $\eta_{max}(\cos\varphi = 0{,}9) = 99{,}23$ %.
- Curentul de scurtcircuit la bornele JT (rețea de alimentare considerată de putere infinită): $I_{sc} \approx 577{,}4\cdot 100/4 = 14{,}4$ kA.

**Verificare.** Pe schema pe fază (stea echivalentă la 0,4 kV: $R_{sc} = 4{,}600$ mΩ, $X_{sc} = 15{,}32$ mΩ): ecuația fazorială exactă dă $\Delta U = 2{,}284$ % ✓, pierderile $3RI^2$ dau același randament ✓, iar $I_{sc} = 230{,}9/\lvert R_{sc}+jX_{sc}\rvert = 14{,}43$ kA ✓.

### Problema 1.4 – Funcționarea în paralel

Un transformator T1 de 630 kVA cu $u_{sc} = 6$ % și unul T2 de 400 kVA cu $u_{sc} = 4$ % (aceleași tensiuni și grupă) alimentează în paralel 1000 kVA. Cum se împarte sarcina? Ce putere maximă se poate transmite fără suprasarcină?

**Rezolvare.** $S_{n1}/u_{sc1} = 105$, $S_{n2}/u_{sc2} = 100$ (kVA/%):

$$S_1 = 1000\cdot\frac{105}{205} = 512{,}2\ \text{kVA}\ (81{,}3\ \%), \qquad S_2 = 1000\cdot\frac{100}{205} = 487{,}8\ \text{kVA}\ (\mathbf{122\ \%}) .$$

T2 este suprasolicitat, deși puterea totală instalată (1030 kVA) depășește sarcina. Limita este atinsă când T2 ajunge la 400 kVA: $S_{max} = 400\cdot 205/100 = 820$ kVA, adică doar 79,6 % din puterea instalată.

**Verificare (prin impedanțe în ohmi, raportate la 0,4 kV).** $Z_1 = 0{,}06\cdot 0{,}4^2/0{,}63 = 15{,}24$ mΩ, $Z_2 = 0{,}04\cdot 0{,}4^2/0{,}4 = 16{,}00$ mΩ. Curenții (și puterile) se împart invers proporțional cu impedanțele: $S_1 = 1000\cdot Z_2/(Z_1+Z_2) = 512{,}2$ kVA ✓. (Calculul presupune același raport $X/R$ la ambele transformatoare.)

### Problema 1.5 – Autotransformatorul

Un autotransformator 230/200 V alimentează o sarcină de 2 kVA. Ce curent trece prin porțiunea comună a înfășurării? Ce putere se transferă electromagnetic?

**Rezolvare.** $I_1 = 2000/230 = 8{,}696$ A, $I_2 = 2000/200 = 10$ A. Prin porțiunea comună circulă diferența $I_2 - I_1 = 1{,}304$ A. Puterea transferată electromagnetic este

$$S_{em} = S\left(1 - \frac{U_2}{U_1}\right) = 2000\cdot\frac{30}{230} = 260{,}9\ \text{VA}\ (13\ \%\ \text{din}\ S).$$

**Verificare (două căi):** $U_2(I_2 - I_1) = 200\cdot 1{,}304 = 260{,}9$ VA ✓; $(U_1 - U_2)I_1 = 30\cdot 8{,}696 = 260{,}9$ VA ✓. Un transformator cu două înfășurări ar trebui dimensionat pentru 2000 VA; autotransformatorul, practic doar pentru 261 VA.

---

## Întrebări de autoevaluare

1. De ce se transportă energia electrică la tensiuni înalte?
2. De ce transformatorul nu funcționează în curent continuu?
3. Ce se întâmplă cu fluxul din miez când crește sarcina transformatorului? Justificați.
4. Ce reprezintă fiecare element din schema echivalentă în T?
5. De ce, la încercarea de mers în gol, puterea măsurată reprezintă pierderile în fier?
6. De ce, la încercarea de scurtcircuit, tensiunea se crește treptat de la zero? Ce s-ar întâmpla la tensiune nominală?
7. Ce informații practice furnizează tensiunea de scurtcircuit $u_{sc}$?
8. Poate crește tensiunea secundară la creșterea sarcinii? În ce condiții?
9. La ce încărcare are transformatorul randamentul maxim și de ce transformatoarele de distribuție sunt proiectate cu $\beta_{opt}$ mic?
10. Ce înseamnă notația Dyn11?
11. Care sunt condițiile de funcționare în paralel și ce se întâmplă dacă $u_{sc}$ diferă mult?
12. De ce secundarul unui transformator de curent nu trebuie lăsat deschis?

<details>
<summary><b>Răspunsuri</b></summary>

1. La aceeași putere, curentul scade proporțional cu tensiunea, iar pierderile în linie scad cu pătratul ei (§ 1.1).
2. Tensiunea indusă este proporțională cu variația fluxului; în c.c. fluxul este constant, nu se induce nimic în secundar, iar curentul primar ar fi limitat doar de rezistența mică a înfășurării – transformatorul s-ar arde.
3. Rămâne practic constant: la tensiune și frecvență date, $\Phi_{max} \approx U_1/(4{,}44 f N_1)$; creșterea solenației secundare este compensată de creșterea curentului primar (§ 1.3).
4. $R_1$, $R_2'$ – rezistențele înfășurărilor (pierderi Joule); $X_{1\sigma}$, $X_{2\sigma}'$ – fluxurile de dispersie; $X_m$ – magnetizarea miezului; $R_{Fe}$ – pierderile în fier (§ 1.4).
5. Pentru că tensiunea (deci fluxul) este nominală, iar curentul este foarte mic, deci pierderile Joule sunt neglijabile (§ 1.5).
6. Pentru că, cu secundarul în scurtcircuit, curentul nominal se obține la doar câteva procente din tensiunea nominală; la tensiune nominală curentul ar fi de $100/u_{sc}$ ori (de ordinul 15–25 ori) mai mare decât cel nominal (§ 1.6).
7. Căderea de tensiune în sarcină, curentul de scurtcircuit la borne și modul de împărțire a sarcinii în paralel (§ 1.6).
8. Da, la sarcină capacitivă suficient de puternică: când $u_X\lvert\sin\varphi_2\rvert > u_R\cos\varphi_2$, $\Delta U$ devine negativ (figura 1.5).
9. La $\beta_{opt} = \sqrt{P_0/P_{sc}}$ (pierderi variabile = pierderi constante). Pentru că ele sunt conectate permanent și lucrează mult timp la sarcini parțiale; contează energia pierdută pe an, nu doar randamentul la sarcină nominală (§ 1.7).
10. ÎT în triunghi, JT în stea cu neutru scos, tensiunea JT defazată cu 330° în urma celei de ÎT (30° înainte) (§ 1.8).
11. Aceleași tensiuni, aceeași grupă de conexiuni, $u_{sc}$ apropiate (±10 %), raport de puteri de cel mult 3:1. La $u_{sc}$ diferite, transformatorul cu $u_{sc}$ mic se supraîncarcă înaintea celuilalt (§ 1.9, problema 1.4).
12. Dispare solenația secundară care compensa solenația primară; fluxul crește mult, miezul se saturează și se încălzește, iar în secundar apar tensiuni periculoase pentru om și pentru izolație (§ 1.10).

</details>

---

**Bibliografie pentru capitol:** [1] cap. 2, [2] cap. 2, [3]; standarde [S3], [S7]. Lista completă este în [README](README.md#bibliografie).

[← Capitolul 0](00-notiuni-fundamentale.md) · [Cuprins](README.md) · [Capitolul 2. Mașina asincronă →](02-masina-asincrona.md)
