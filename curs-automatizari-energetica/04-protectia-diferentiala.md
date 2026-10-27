# Capitolul 4. Protecția diferențială

> **Obiective.** După acest capitol ar trebui să puteți: (1) explica principiul protecției diferențiale și de ce ea este selectivă fără temporizare; (2) defini curentul diferențial și curentul de frânare și citi o caracteristică cu frânare; (3) adapta amplitudinile și compensa grupa de conexiuni a unui transformator, inclusiv eliminarea componentei homopolare; (4) verifica stabilitatea protecției la defecte exterioare, cu comutatorul de ploturi în poziție extremă și cu erorile transformatoarelor de curent; (5) explica curentul de magnetizare la conectare și blocarea la armonica a doua; (6) descrie protecția diferențială a barelor (de impedanță mare și mică) și a liniilor.

Protecția diferențială compară curenții de la **toate** capetele elementului protejat. Ea are o zonă **închisă**, delimitată exact de transformatoarele de curent (§ 0.5), deci nu trebuie coordonată în timp cu protecțiile vecine: poate acționa instantaneu. De aceea este protecția de bază a transformatoarelor, generatoarelor, motoarelor mari și barelor, iar cu un canal de comunicație și a liniilor.

În capitol folosim transformatorul **T1** al rețelei de referință (25 MVA, 110/20 kV, YNd11, § 0.7) și bara B de 110 kV.

---

## 4.1. Principiul

Pe fiecare capăt al obiectului protejat se montează câte un TC, cu același raport (raportat la curentul nominal al obiectului), iar secundarele se leagă astfel încât curenții să **circule** între ele; releul este legat în ramura care unește punctele de egal potențial ale circuitului secundar (figura 4.1). Schema este cunoscută și după numele inventatorilor ei (Merz–Price).

![Figura 4.1 – Principiul protecției diferențiale](figuri/f04-1-principiu.svg)

*Figura 4.1 – La un defect exterior curentul secundar circulă prin cele două TC și nu trece prin releu; la un defect interior curenții secundari se adună în releu.*

- La un **defect exterior** (sau la sarcină), curentul care intră în zonă iese din ea; curenții secundari se compensează, iar releul este parcurs (ideal) de zero.
- La un **defect interior**, curenții de pe ambele capete intră în zonă; prin releu trece suma lor, adică (raportat la secundar) curentul de defect.

Releul nu are nevoie de temporizare: el „știe” unde este defectul din semnul relativ al curenților, nu din valoarea lor. Toată dificultatea protecției diferențiale constă în a menține curentul prin releu suficient de mic la defectele exterioare mari, când TC au erori și se pot satura (§ 2.3), iar la transformatoare și când curenții de pe cele două părți nu sunt egali nici măcar în regim ideal (§ 4.3).

## 4.2. Curentul diferențial și curentul de frânare

Releele numerice calculează, pe fiecare fază, din curenții care **intră** în zonă (raportați la secundar și adaptați, § 4.3):

$$\boxed{I_d = \left|\underline{I}_1 + \underline{I}_2\right|, \qquad I_b = \frac{|\underline{I}_1| + |\underline{I}_2|}{2}}$$

$I_d$ este **curentul diferențial** (de acționare), iar $I_b$ – **curentul de frânare** (de stabilizare), o măsură a curentului care traversează zona. Producătorii folosesc definiții diferite pentru curentul de frânare (media, suma sau maximul modulelor, eventual numai pentru unele capete); reglajele trebuie citite întotdeauna împreună cu definiția folosită de releul respectiv. În curs folosim media modulelor.

La un defect exterior, $I_d$ nu este exact zero: erorile TC (care cresc cu curentul) și raportul real al transformatorului diferit de cel pentru care s-a făcut adaptarea (comutatorul de ploturi) produc un curent diferențial **aproximativ proporțional cu curentul traversant**; curentul de magnetizare, practic constant în regim normal, este acoperit de pragul minim. De aceea pragul de acționare nu este constant, ci crește cu curentul de frânare – **caracteristica cu frânare** (figura 4.2). În curs folosim o caracteristică cu două pante (date de reglaj ale cursului):

$$I_{d,\text{acț}} = \begin{cases} \max\left(0{,}30\thinspace I_n;\ 0{,}30\thinspace I_b\right), & I_b \le 3\thinspace I_n \\ 0{,}30 \cdot 3\thinspace I_n + 0{,}70\thinspace(I_b - 3\thinspace I_n), & I_b > 3\thinspace I_n \end{cases}$$

- **pragul minim** (0,30·In) acoperă curentul de magnetizare și erorile la curenți mici;
- **prima pantă** (30 %) acoperă erorile proporționale cu curentul: comutatorul de ploturi și erorile TC; în problema 4.2 se arată că, pentru T1, acestea dau cel mult 20,47 % din curentul de frânare;
- **a doua pantă** (70 %), mai abruptă, acoperă saturația **parțială** a TC la curenți traversanți mari, când un TC dă un curent mai mic decât celălalt. Saturația puternică nu poate fi acoperită numai prin pantă; ea se evită prin dimensionarea TC (§ 2.3), iar multe relee numerice o recunosc și își măresc temporar stabilizarea.

![Figura 4.2 – Caracteristica cu frânare](figuri/f04-2-caracteristica.svg)

*Figura 4.2 – Caracteristica cu frânare folosită în curs și punctele de funcționare calculate în problemele 4.1–4.3. Punctele defectelor exterioare rămân sub caracteristică; defectul exterior de pe bara de 110 kV ar intra în zona de acționare dacă releul nu ar elimina componenta homopolară.*

Pe lângă treapta frânată, releele au o **treaptă nefrânată** (instantanee), care acționează numai după $I_d$, fără frânare și fără blocarea la armonici (§ 4.4). Ea se reglează peste curentul diferențial maxim care poate apărea la un defect exterior sau la conectare. Dacă la un defect exterior un TC se saturează complet, curentul diferențial poate ajunge cel mult la curentul de pe cealaltă parte; pentru T1, cel mai mare curent traversant este cel al unui defect pe bara B2: 8,36·In cu plotul nominal și 9,20·In (pe partea de 20 kV) cu plotul în poziția +10 % (problema 4.2). De aceea treapta nefrânată se reglează în curs la **11·In**: cu o rezervă de 1,20 față de acest curent și peste fundamentala curentului de magnetizare la conectare (2,61·In, problema 4.4).

Cerințele funcționale pentru protecțiile diferențiale frânate și nefrânate ale motoarelor, generatoarelor și transformatoarelor sunt stabilite în IEC 60255-187-1 [S6].

## 4.3. Protecția diferențială a transformatorului

Un transformator nu este un „conductor”: curenții de pe cele două părți diferă ca valoare și ca fază chiar în regim normal. Releul trebuie să corecteze trei efecte înainte de a calcula $I_d$ și $I_b$.

**1. Adaptarea de amplitudine.** Curenții nominali ai lui T1 sunt 131,2 A pe 110 kV și 721,7 A pe 20 kV. TC standardizate alese (150/1 A și 800/1 A) nu au exact raportul curenților nominali, așa că releul înmulțește curentul secundar de pe fiecare parte cu un factor de adaptare și lucrează în **multipli ai curentului nominal al transformatorului**:

$$k_{IT} = \frac{150}{131{,}2} = 1{,}1432, \qquad k_{JT} = \frac{800}{721{,}7} = 1{,}1085 .$$

Vechile relee electromecanice foloseau pentru aceasta TC intermediare; releele numerice o fac prin calcul.

**2. Compensarea grupei de conexiuni.** La T1 (YNd11), sistemul direct de pe 20 kV este **defazat înainte cu 30°** față de cel de pe 110 kV, iar sistemul invers – înapoi cu 30° (§ 1.4). Releul rotește curenții de pe partea în stea cu o matrice care face exact acest lucru:

$$\boxed{\begin{bmatrix} I'_A \\ I'_B \\ I'_C \end{bmatrix} = \frac{1}{\sqrt3}\begin{bmatrix} 1 & -1 & 0 \\ 0 & 1 & -1 \\ -1 & 0 & 1 \end{bmatrix} \begin{bmatrix} I_A \\ I_B \\ I_C \end{bmatrix}}$$

Pentru sistemul direct, $I'_A = I_A\thinspace(1 - a^2)/\sqrt3 = I_A \angle +30°$; pentru cel invers, $I'_A = I_A\thinspace(1 - a)/\sqrt3 = I_A\angle -30°$, exact defazajele transformatorului (figura 4.3).

**3. Eliminarea componentei homopolare.** Neutrul înfășurării de 110 kV a lui T1 este legat la pământ, așa că la un defect cu pământul în rețeaua de **110 kV** T1 debitează curent homopolar pe partea de 110 kV (prin neutrul lui), fără niciun curent corespunzător în liniile de 20 kV (curentul homopolar circulă în interiorul triunghiului). Fără corecție, acest curent ar apărea ca diferențial și protecția ar declanșa transformatorul la un defect exterior. Matricea de mai sus are suma coeficienților pe fiecare linie zero, deci **elimină automat componenta homopolară**. În schemele clasice, același efect se obținea legând în triunghi TC de pe partea în stea. La transformatoarele YNyn (fără defazaj), releul elimină explicit $I_0$ din curenții de pe fiecare parte cu neutrul legat la pământ.

![Figura 4.3 – Compensarea grupei de conexiuni](figuri/f04-3-compensare.svg)

*Figura 4.3 – Fazorii curenților la un defect trifazat și la unul monofazat în P1 (exteriori zonei), în multipli ai curenților nominali: după compensare, fiecare fazor de pe 110 kV este egal și opus celui de pe 20 kV.*

Pe lângă acestea, protecția diferențială a transformatorului trebuie să țină seama de:

- **comutatorul de ploturi**: adaptarea se face pentru raportul nominal; în pozițiile extreme apare un curent diferențial proporțional cu sarcina (problema 4.2);
- **curentul de magnetizare**: în regim normal este mic (în modelul din problema 4.4, 0,4 % din In) și este acoperit de pragul minim; la conectare și la supraexcitare devine însă mare (§ 4.4);
- **defectele cu pământul pe partea de 20 kV**: în rețeaua cu neutrul tratat prin rezistor, curentul de defect este limitat la circa 300 A, adică 0,4–0,46·In al lui T1; dacă releul elimină și componenta homopolară de pe partea de 20 kV, el vede numai 2/3 din curent: la limita pragului minim (0,304·In la $c$ = 1,1) sau sub el (0,276·In la $c$ = 1,0; problema 4.3). Aceste defecte sunt lăsate unei protecții dedicate (§ 4.5).

## 4.4. Curentul de magnetizare la conectare

La conectarea unui transformator în gol, fluxul din miez nu pornește de la valoarea lui de regim permanent, ci de la **fluxul remanent** lăsat de ultima deconectare. Dacă tensiunea $v = V_m \sin\omega t$ se aplică la trecerea ei prin zero, fluxul înlănțuit total al circuitului crește, într-o semiperioadă, cu

$$\Delta\psi = \int_0^{\pi/\omega} V_m \sin\omega t\thinspace dt = \frac{2 V_m}{\omega} = 2\thinspace\psi_n .$$

Fără rezistențe, fluxul înlănțuit total (al miezului și al inductivității rețelei) ajunge la $\psi_{rem} + 2\psi_n$ – de 2,8 ori fluxul nominal pentru $\psi_{rem}$ = 0,8·ψn, **dacă fluxul remanent are același semn cu variația fluxului**. O parte din tensiune cade pe inductivitatea rețelei, așa că fluxul din miez rămâne puțin mai mic: 2,694·ψn fără rezistențe și 2,649·ψn cu rezistențele circuitului (problema 4.4). Miezul se saturează adânc, iar curentul de magnetizare, limitat numai de inductivitatea înfășurării cu miezul saturat și de cea a rețelei, ajunge la câțiva curenți nominali (problema 4.4). Curentul are forma unor **impulsuri unipolare** care se amortizează lent (figura 4.4), cu constanta de timp dată de rezistențele circuitului.

Curentul de magnetizare circulă numai pe partea alimentată, deci pentru protecția diferențială este un **curent diferențial**. Treapta frânată ar acționa dacă nu ar fi blocată. Forma de undă are însă un conținut mare de **armonica a doua** (o undă unipolară nu are simetrie de semiundă), pe care curenții de defect nu îl au în regim stabilizat. Releele calculează raportul $I_{2f}/I_{1f}$ pe o fereastră de o perioadă și blochează treapta frânată cât timp raportul depășește un prag; în curs pragul este **12 %**. Alegerea lui este justificată în problema 4.4:

- în simulare, curentul de conectare al lui T1 are, în cazul de bază, 14,7 % în prima perioadă, apoi raportul crește (61,8 % după 0,4 s);
- un defect interior la bornele de 20 kV, cu componentă aperiodică maximă, are numai 6,0 % în prima perioadă și nu este blocat;
- un defect interior la bornele de 110 kV are 12,6 % în prima perioadă și ar putea fi blocat câteva milisecunde, dar curentul lui (50·In) acționează treapta nefrânată, care nu se blochează.

![Figura 4.4 – Curentul de conectare și armonica a doua](figuri/f04-4-inrush.svg)

*Figura 4.4 – Simularea conectării lui T1 pe partea de 110 kV (model monofazat, flux remanent 0,8·ψn, conectare la trecerea tensiunii prin zero): curentul (sus) și raportul armonicii a doua pe o fereastră alunecătoare de o perioadă (jos).*

Marja dintre cele două situații este mică și depinde puternic de miezul transformatorului: în simulare, un cot de saturație mai jos (1,1·ψn în loc de 1,2·ψn) coboară raportul minim la 10,6 % (problema 4.4). În plus, modelul din curs este monofazat, iar releul nu analizează curentul unei faze, ci curentul diferențial compensat – pentru YNd11, de exemplu $(i_A - i_B)/\sqrt3$ –, în care impulsurile a două faze se combină și raportul armonicii a doua poate fi mai mic decât într-un curent de fază. Din aceste motive, releele moderne completează criteriul armonicii a doua cu alte criterii: blocarea tuturor fazelor când una singură detectează conectarea (blocare încrucișată), analiza formei de undă (intervalele în care curentul este aproape zero), iar reglajul se verifică pentru transformatorul concret.

La **supraexcitare** (tensiune prea mare sau frecvență prea mică, adică $U/f$ mare – de exemplu la descărcarea bruscă a unui generator), curentul de magnetizare crește și el, dar rămâne simetric, deci conține numai armonici impare. Cea mai mare este armonica a treia, dar ea este eliminată de înfășurarea în triunghi și de filtrarea componentei homopolare din releu (armonicile multiplu de trei formează, în trifazat, un sistem homopolar); de aceea releele folosesc armonica a cincea. Unele relee blochează treapta frânată după armonica a cincea, iar supraexcitarea se tratează cu o protecție separată, după raportul $U/f$ (capitolul 6).

## 4.5. Alte protecții ale transformatorului

Protecția diferențială nu acoperă toate defectele transformatorului; ea se completează cu:

- **releul de gaze (Buchholz)**, la transformatoarele în ulei cu conservator: un defect în cuvă (chiar o scurtcircuitare între câteva spire, cu curent prea mic pentru protecția diferențială) descompune uleiul în gaze. Acumularea lentă a gazelor dă un semnal de avertizare; un val de ulei spre conservator (defect puternic) comandă declanșarea;
- **protecția restrânsă la pământ**. La o înfășurare în stea cu neutrul legat la pământ, ea compară curentul din neutru cu suma curenților de fază ai aceleiași înfășurări. Înfășurarea de 20 kV a lui T1 este însă în triunghi, fără neutru, iar curentul de punere la pământ vine de la bobina de punct neutru (BPN), aflată pe bare, în afara zonei. Defectele cu pământul dintre T1 și TC lui de 20 kV, ca cel din problema 4.3 (c), se detectează atunci după **curentul rezidual al TC de 20 kV ai lui T1**: la un defect exterior el este zero (triunghiul nu transmite componentă homopolară), iar la un defect în zonă este egal cu curentul de defect (problema 4.3). Protecția este deci „restrânsă” la zona dintre TC și transformator, cu un prag raportat la curentul de defect de circa 300 A, nu la curentul nominal;
- **protecția homopolară a BPN** (curentul prin rezistorul de neutru, § 1.6), care vede toate punerile la pământ din rețeaua de 20 kV; ea nu este selectivă și servește ca rezervă, cu temporizare mai mare decât protecțiile homopolare ale fiderilor (capitolul 3);
- **protecția termică** (49), după un model termic de felul celui din § 6.2, și supravegherea temperaturii uleiului și a înfășurărilor;
- **protecțiile maximale** de rezervă pe ambele părți (capitolul 3), care acoperă și defectele exterioare neeliminate.

Declanșările date de protecțiile care indică un defect interior (diferențială, gaze) trec de obicei printr-un **releu de blocare** (86, § 0.6): după o asemenea declanșare, transformatorul nu poate fi reconectat până când personalul nu verifică defectul și nu deblochează manual releul.

## 4.6. Protecția diferențială a barelor

O bară are multe circuite; un defect pe bară este rar, dar foarte grav (se pierd toate circuitele), iar un defect exterior foarte apropiat produce cei mai mari curenți traversanți posibili printr-un singur TC. Există două familii de scheme:

- **de impedanță mare**: secundarele tuturor TC (cu același raport) sunt legate în paralel pe un releu de tensiune cu un rezistor de stabilizare de valoare mare. La un defect exterior, cel mai defavorabil caz este saturația completă a TC de pe circuitul cu defectul: el devine, în secundar, o simplă rezistență $R_{ct}$, iar curentul celorlalte TC se închide prin ea și prin conductoarele de legătură. Tensiunea pe releu este atunci cel mult $I_{k,sec}\thinspace(R_{ct} + 2R_L)$, unde $R_L$ este rezistența unui conductor de legătură (bucla are două conductoare) și $I_{k,sec}$ cel mai mare curent secundar care poate traversa un singur TC; releul se reglează la
  $$\boxed{V_s \ge I_{k,sec}\thinspace(R_{ct} + 2R_L)}$$
  (figura 4.5, problema 4.5). Curentul $I_{k,sec}$ se caută pe toate celulele: cel mai sever caz este adesea celula unui transformator fără sursă în spate, prin al cărei TC trece, la un defect imediat după el, întregul curent de defect al barei. La un defect interior, toate TC debitează în releul de impedanță mare; tensiunea ar ajunge la mii de volți (problema 4.5), de aceea în paralel cu releul se montează un **limitator neliniar de tensiune**. Ca să poată acționa sigur, TC trebuie să aibă **tensiunea de cot** a curbei de magnetizare mult peste $V_s$ (în curs: cel puțin $2V_s$, regulă de proiectare a cursului). Schema este simplă și foarte stabilă, dar cere TC dedicate, cu același raport;
- **de impedanță mică (numerice, cu frânare)**: releul primește curenții tuturor circuitelor (adesea prin unități de achiziție în celule), îi adaptează prin calcul (rapoartele TC pot fi diferite), calculează $I_d$ și $I_b$ ca în § 4.2 și urmărește configurația separatoarelor de bare, ca să știe ce circuite aparțin fiecărei secții de bare. Multe relee recunosc saturația TC (de exemplu, din faptul că, la un defect exterior, curentul diferențial apare abia după câteva milisecunde de la defect) și o tratează ca atare.

![Figura 4.5 – Protecția de bare de impedanță mare](figuri/f04-5-bare-impedanta-mare.svg)

*Figura 4.5 – Cazul de stabilitate al schemei de impedanță mare pentru bara B: la un defect exterior imediat după TC al celulei T1, acesta este complet saturat și se reduce la rezistența lui $R_{ct}$ (în serie cu conductoarele de legătură); în paralel cu releul se află limitatorul neliniar de tensiune.*

## 4.7. Protecția diferențială a liniilor

La o linie, cele două capete sunt la kilometri distanță, deci curenții trebuie transmiși pe un **canal de comunicație** [8], [3]. Releele numerice de la cele două capete schimbă eșantioane sau fazori ai curenților, de obicei prin fibră optică (directă sau prin rețeaua de telecomunicații), și calculează fiecare $I_d$ și $I_b$. Probleme specifice:

- **sincronizarea**: curenții comparați trebuie să fie măsurați în același moment; releele măsoară timpul de propagare pe canal (presupunând, de obicei, întârzieri egale pe cele două sensuri) sau folosesc un semnal de timp extern, de exemplu de la GPS (capitolul 9);
- **curentul capacitiv** al liniei (mare la cablurile și liniile lungi) apare ca diferențial; releele îl compensează din tensiune sau îl acoperă prin pragul minim;
- **canalul** poate cădea; releul trece atunci pe o protecție de rezervă (de exemplu de distanță sau maximală, capitolele 3 și 5).

Protecția diferențială de linie are zona închisă, deci este selectivă fără temporizare și este mult mai puțin influențată de pendulații, de rezistența de defect sau de alimentarea de la capătul opus – dificultățile principale ale protecției de distanță (capitolul 5).

---

## Probleme rezolvate

### Problema 4.1 – Adaptarea și compensarea grupei de conexiuni

Protecția diferențială a lui T1 este alimentată de TC 150/1 A pe 110 kV și 800/1 A pe 20 kV. Să se calculeze factorii de adaptare și mărimile releului la trei defecte **exterioare**: (a) trifazat în P1; (b) monofazat pe bara B de 110 kV; (c) monofazat în P1 (rețeaua de 20 kV tratată prin rezistor). Toate cu $c_{max}$.

**Rezolvare.**

- $I_n$ = 25 MVA/(√3 · 110 kV) = **131,2 A** pe 110 kV și 25 MVA/(√3 · 20 kV) = **721,7 A** pe 20 kV; factorii de adaptare sunt **1,1432** și **1,1085** (§ 4.3).

| Defect | curenții primari pe 110 kV | curenții primari pe 20 kV | $I_d$ (cu eliminarea $I_0$) | $I_b$ |
|---|---|---|---|---|
| (a) trifazat în P1 | 378,0 A pe fiecare fază | 2079,0 A pe fiecare fază | 0 | 2,881·In |
| (b) monofazat pe bara B | 583,8 A pe fiecare fază, toți în fază ($I_0$ = 583,8 A) | 0 | 0 | 0 |
| (c) monofazat în P1 | 30,7 / 30,7 / 0 A | 194,9 / 97,5 / 97,5 A | 0 | 0,270 / 0,135 / 0,135·In |

- (a) În secundar circulă 2,520 A pe 110 kV și 2,599 A pe 20 kV; după adaptare, ambele devin 2,881·In, iar după compensarea defazajului de 30° fazorii sunt egali și opuși (figura 4.3): $I_d$ = 0.
- (b) Curentul prin T1 este pur homopolar: el intră pe fazele de 110 kV și iese prin neutru, iar pe 20 kV nu apare nimic. Matricea de compensare îl elimină: $I_d$ = 0. **Fără eliminarea componentei homopolare**, releul ar vedea pe fiecare fază $I_d$ = 583,8/131,2 = **4,449·In**, cu $I_b$ = 2,22·In, mult peste prag: protecția ar declanșa T1 la fiecare defect cu pământul din rețeaua de 110 kV din apropiere.
- (c) Pe 20 kV curentul de defect are componentă homopolară, dar ea vine de la bobina de punct neutru, nu din T1: liniile lui T1 transportă numai componentele directă și inversă. După compensare, $I_d$ = 0 pe toate fazele.

**Verificare.** Curenții de 20 kV au fost calculați pe două căi: (1) din componentele simetrice ale curentului de 110 kV (rețelele de secvență), cu teoria transformatorului YNd11 – raportul $n$ = 5,5, defazajul +30° pentru sistemul direct și −30° pentru cel invers, fără homopolară în liniile triunghiului; (2) din rezolvarea rețelei în coordonate de fază, în care T1 este format din trei transformatoare monofazate legate fizic în stea și în triunghi. Curenții coincid pentru toate cele trei defecte, iar $I_b$ calculat din ei la fel. Pentru cazul (b), curentul diferențial fără eliminarea homopolarei este exact $|I_0|/I_n$ pe fiecare fază.

### Problema 4.2 – Comutatorul de ploturi în poziție extremă

Comutatorul de ploturi al lui T1 permite modificarea raportului cu ±10 % pe partea de 110 kV. Releul este adaptat pentru raportul nominal. Să se verifice stabilitatea la defecte trifazate exterioare în P1 și pe bara B2, în ambele poziții extreme; apoi să se adauge erorile TC.

**Rezolvare.** Cu raportul real $t \cdot n$ (t = 1,10 sau 0,90), curentul de 110 kV este, raportat la 20 kV, de $1/t$ ori curentul de 20 kV. După adaptarea pentru $n$:

$$\frac{I_d}{I_b} = \frac{|1 - 1/t|}{(1 + 1/t)/2} = \begin{cases} 0{,}0952 & t = 1{,}10 \\ 0{,}1053 & t = 0{,}90 \end{cases}$$

| Plot | defect | $I_b$ | $I_d$ | pragul caracteristicii |
|---|---|---|---|---|
| +10 % | P1 | 2,633·In | 0,251·In | 0,790·In |
| +10 % | B2 | 8,778·In | 0,836·In | 4,945·In |
| −10 % | P1 | 3,158·In | 0,332·In | 1,010·In |
| −10 % | B2 | 7,942·In | 0,836·In | 4,360·In |

Toate punctele sunt sub caracteristică (figura 4.2). Cel mai defavorabil caz adaugă erori **opuse** de câte 5 % ale celor două TC (eroarea compusă a clasei 5P, § 2.2, luată acoperitor pentru toți curenții): raportul $I_d/I_b$ ajunge la **0,2047**, sub panta de 0,30, cu o rezervă de 1,47.

Pentru treapta nefrânată contează cel mai mare curent traversant, pe oricare parte: la un defect în B2 el este 8,36·In cu plotul nominal sau −10 % și **9,20·In** (pe partea de 20 kV) cu plotul +10 %. Treapta de 11·In are deci o rezervă de **1,20** chiar dacă un TC s-ar satura complet.

**Verificare.** (1) Rezolvând rețeaua în coordonate de fază cu raportul real al lui T1 modificat (121 kV, respectiv 99 kV pe partea de 110 kV), raportul $I_d/I_b$ calculat de releu este exact 0,0952 și 0,1053, pentru ambele defecte – nu depinde de curent. (2) Căutarea numerică pe o grilă de 41 de poziții ale ploturilor și 21 × 21 de combinații de erori între −5 % și +5 % confirmă că maximul raportului (0,2047) se află într-un colț al domeniului: plotul −10 %, curentul de 110 kV cu +5 %, cel de 20 kV cu −5 %. (3) Pentru fiecare poziție a plotului, curentul traversant maxim calculat în rețea este egal cu $I_b + I_d/2$, ca pentru definiția cu media modulelor.

### Problema 4.3 – Defecte interioare

Să se verifice acționarea protecției la: (a) un scurtcircuit trifazat la bornele de 20 kV ale lui T1, între transformator și TC de 20 kV; (b) un scurtcircuit trifazat la bornele de 110 kV; (c) o punere la pământ la bornele de 20 kV (rețeaua tratată prin rezistor), pentru $c$ = 1,1 și $c$ = 1,0.

**Rezolvare.**

- (a) Rețeaua de 20 kV nu are surse, deci TC de 20 kV nu văd curent; tot curentul vine de pe 110 kV: $I_d$ = **8,360·In**, $I_b$ = 4,180·In. Pragul caracteristicii este 0,30 · 3 + 0,70 · (4,180 − 3) = **1,726·In**, deci protecția acționează cu o rezervă de 4,84. Treapta nefrânată (11·In) nu este atinsă; acționează treapta frânată, care nu este blocată (armonica a doua 6,0 %, problema 4.4).
- (b) Defectul este alimentat din rețeaua de 110 kV: $I_d$ = **50,24·In**, de peste patru ori treapta nefrânată, care acționează instantaneu.
- (c) Componentele directă și inversă ale curentului de defect vin prin T1 (TC de 110 kV), iar componenta homopolară vine de la bobina de punct neutru prin TC de 20 kV.

| $c$ | curentul de defect | $I_d$, homopolara de pe 20 kV păstrată | $I_d$, homopolara de pe 20 kV eliminată |
|---|---|---|---|
| 1,1 | 328,9 A = 0,456·In | 0,456·In | 0,304·In |
| 1,0 | 299,0 A = 0,414·In | 0,414·In | 0,276·In |

Cu pragul minim de 0,30·In, protecția sesizează sigur defectul numai dacă homopolara de pe 20 kV este păstrată în calcul (rezerva este doar 0,41/0,30 = 1,38); dacă este eliminată, curentul diferențial este la limita pragului (0,304·In la $c$ = 1,1) sau sub el (0,276·In la $c$ = 1,0). Concluzia: defectele cu pământul din rețelele cu neutrul tratat prin rezistor nu se lasă protecției diferențiale a transformatorului, ci protecției restrânse la pământ (§ 4.5). Curentul rezidual al TC de 20 kV ai lui T1 este 299,0 A (egal cu curentul de defect) pentru defectul de la borne și practic zero (sub 1 mA) pentru un defect monofazat exterior în P1, ambele la $c$ = 1,0.

**Verificare.** (a) $I_d$ coincide cu $I''_{k3}(B2)/I_n$ = 6034/721,7 = 8,36, valoarea calculată independent în capitolul 1. (b) La fel, $I''_{k3}(B)/I_n$ = 6592/131,2 = 50,24. (c) Pe calea componentelor simetrice: curentul de defect este $3I_0$, iar componentele directă și inversă transmise prin T1 sunt egale cu $I_0$ și, pe faza defectă, în fază; fără homopolară releul vede $2I_0 = (2/3)\thinspace I_{defect}$, adică exact valorile din coloana a patra. Curentul rezidual de 299,0 A coincide cu $3I_0$ din rețelele de secvență.

### Problema 4.4 – Curentul de magnetizare la conectare

T1 se conectează în gol pe partea de 110 kV. Model (monofazat, pentru o fază): tensiunea de fază $V_m = \sqrt2 \cdot 110/\sqrt3$ kV, rețeaua de la bara B ($R$ = 2,434 Ω, $X$ = 10,314 Ω, capitolul 1), rezistența înfășurării de 110 kV 1,16 Ω (jumătate din $R_k = P_k U^2/S_n^2$ = 2,323 Ω); curba de magnetizare liniară până la 1,2·ψn (la tensiunea nominală, curentul de magnetizare are valoarea efectivă de 0,4 % din In), iar peste cot inductivitatea înfășurării cu miezul saturat corespunde unei reactanțe de 0,30 u.r. (date de model). Flux remanent 0,8·ψn, conectare la trecerea tensiunii prin zero. Să se determine vârful curentului, armonica a doua și să se justifice pragul de blocare.

**Rezolvare.**

- $\psi_n = V_m/\omega$ = **285,9 V·s**; $L_m$ = 385 H; inductivitatea cu miezul saturat $L_s$ = 0,4622 H; inductivitatea rețelei $L_r$ = 0,0328 H.
- Fără rezistențe, la $\omega t = \pi$: $L_r\thinspace i + \psi = \psi_{rem} + 2\psi_n$, iar în saturație $\psi = \psi_s + (i - i_s)\thinspace L_s$. Rezultă vârful
  $$i_{max} = \frac{\psi_{rem} + 2\psi_n - \psi_s + i_s L_s}{L_r + L_s} = \textbf{924,9 A},$$
  iar fluxul din miez este atunci $\psi_s + (i_{max} - i_s)\thinspace L_s$ = 2,694·ψn (restul de până la 2,8·ψn este fluxul inductivității rețelei).
- Cu rezistențe (simulare numerică, figura 4.4): vârful este **897,3 A = 4,84·(√2·In)**, iar fluxul maxim din miez 2,649·ψn. În prima perioadă, fundamentala are 2,592·In (valoare efectivă), componenta continuă 2,844·In, iar armonica a doua **14,7 %** din fundamentală. Pe fereastra alunecătoare, raportul minim este 14,7 % (în prima perioadă) și crește la 61,8 % după 0,4 s; fundamentala maximă este 2,606·In.
- Fără blocare, protecția ar acționa (2,59·In > 0,30·In). Treapta nefrânată (11·In) nu este atinsă.
- Curenții de defect interiori, cu componentă aperiodică maximă (constanta de timp a rețelei, capitolul 1), au în prima perioadă: la bornele de 20 kV (R/X = 0,0749) **6,0 %**, la bornele de 110 kV (R/X = 0,2360) **12,6 %**.
- Pragul de **12 %** se află între 6,0 % (defect interior, nu trebuie blocat) și 14,7 % (conectare, trebuie blocată). Defectul de la bornele de 110 kV, cu 12,6 %, ar fi blocat în prima perioadă, dar curentul lui (50,24·In, problema 4.3) acționează treapta nefrânată.

Sensibilitatea la datele modelului (simulări de 0,1 s):

| Variantă | vârful curentului | armonica a doua minimă |
|---|---|---|
| flux remanent 0 | 2,44·(√2·In) | 54,1 % |
| flux remanent 0,4·ψn | 3,65·(√2·In) | 33,3 % |
| flux remanent 0,8·ψn (cazul de bază) | 4,84·(√2·In) | 14,7 % |
| cot de saturație 1,1·ψn | 5,13·(√2·In) | 10,6 % |
| cot de saturație 1,3·ψn | 4,54·(√2·In) | 19,1 % |

Cu cât miezul este mai saturat, cu atât impulsurile sunt mai late și armonica a doua mai mică. Pentru un cot de 1,1·ψn, pragul de 12 % nu ar mai bloca în prima perioadă – motivul pentru care releele combină mai multe criterii (§ 4.4) și pentru care reglajul se verifică cu datele transformatorului real. Modelul este monofazat; releul analizează curentul diferențial compensat, în care raportul armonicii a doua poate fi mai mic (§ 4.4).

**Verificare.** (1) Simularea (Runge–Kutta de ordinul 4, pas de 2 µs), rulată fără rezistențe, dă vârful de 924,9 A, ca formula analitică. (2) Metoda de calcul al armonicilor (transformata Fourier discretă pe o perioadă) a fost verificată pe impulsuri sinusoidale trunchiate $i(\theta) = \cos\theta - \cos\alpha$ pentru $|\theta| \le \alpha$, a căror serie Fourier se calculează analitic: raportul armonicii a doua este 70,50 %, 42,44 % și 17,13 % pentru unghiurile de conducție de 120°, 180° și 240°, identic pe ambele căi (toți coeficienții până la armonica a cincea coincid cu o abatere sub 2·10⁻⁴). (3) Pentru simularea însăși: primul impuls simulat (intervalul în care miezul este saturat) conduce **247,3°**; impulsul sinusoidal trunchiat analitic cu același unghi are armonica a doua 14,69 %, iar curentul simulat 14,69 % – acord în limita a 0,1 puncte procentuale.

### Problema 4.5 – Protecția de bare de impedanță mare

Bara B de 110 kV are trei celule (L1, L2 și T1) și o protecție de impedanță mare, cu TC 1200/1 A, $R_{ct}$ = 4,0 Ω, conductoare de legătură de 1,5 Ω (un sens) și releu cu curentul de acționare de 0,1 A. Curentul de magnetizare al unui TC la 50 V este 0,03 A (din curba de magnetizare; date de problemă). Să se regleze tensiunea releului și să se calculeze sensibilitatea.

**Rezolvare.**

- Curentul printr-un TC, la un defect exterior imediat după el, este suma aporturilor celorlalte celule ($c_{max}$):

| Defect imediat după TC | TC L1 | TC L2 | TC T1 |
|---|---|---|---|
| trifazat | 3279 A | 3315 A | **6592 A** |
| monofazat | 3078 A | 2996 A | 4915 A |

  Cel mai sever caz este TC al celulei **T1**: în spatele lui T1 nu există sursă, deci la un defect imediat după acest TC tot curentul de defect al barei (6592 A, capitolul 1) trece prin el. În secundar: 6592/1200 = **5,493 A**.
- $V_s \ge$ 5,493 · (4,0 + 2 · 1,5) = **38,45 V**. Cu o rezervă de 1,2 și rotunjire în sus la 5 V (alegeri ale cursului): 1,2 · 38,45 = 46,1 V → $V_s$ = **50 V**; rezistența releului (cu rezistorul de stabilizare) este $V_s/I_R$ = **500 Ω**. Un reglaj calculat numai pentru celulele de linie (de exemplu 25 V) ar fi **instabil** la un defect exterior după TC al lui T1.
- Tensiunea de cot a TC: cel puțin $2V_s$ = **100 V** (regula de proiectare a cursului).
- Curentul primar minim de acționare: TC trebuie să alimenteze releul (0,1 A) și magnetizarea celor trei TC la 50 V: $I_{op}$ = 1200 · (0,1 + 3 · 0,03) = **228 A**. Cel mai mic defect pe bară (monofazat, $c_{min}$) are 4994 A: sensibilitatea este **21,9**.
- La un defect interior de 6592 A, curentul secundar de 5,49 A ar produce pe 500 Ω, fără saturație, **2747 V**: limitatorul neliniar de tensiune este indispensabil.

**Verificare.** (1) Curenții prin fiecare TC au fost calculați pe două căi independente – rețelele de secvență și rezolvarea în coordonate de fază – pentru defecte trifazate, bifazate, bifazate cu pământul și monofazate imediat după fiecare TC; valorile coincid pe toate fazele. (2) Valoarea pentru TC T1 la defect trifazat este exact $I''_{k3}(B)$ din capitolul 1. (3) Cu releul de 500 Ω în paralel pe ramura TC saturat, tensiunea reală este 37,92 V, sub valoarea formulei: formula este acoperitoare, iar releul reglat la 50 V rămâne stabil.

---

## Întrebări de autoevaluare

1. De ce protecția diferențială nu are nevoie de temporizare pentru a fi selectivă?
   <details><summary>Răspuns</summary>

   Zona ei este închisă, delimitată exact de TC. Releul decide din semnul relativ al curenților de la capete (care intră sau ies din zonă), nu din valoarea lor, deci nu poate confunda un defect exterior cu unul interior și nu trebuie coordonat cu protecțiile vecine.

   </details>

2. De ce caracteristica releului diferențial are pantă (frânare) și nu un prag constant?
   <details><summary>Răspuns</summary>

   La defectele exterioare apare un curent diferențial fals proporțional cu curentul traversant: erorile TC, raportul real diferit de cel de adaptare (ploturile), iar la curenți mari saturația TC. Un prag constant ar trebui ales peste curentul fals maxim și ar face protecția insensibilă la defectele interioare mici. Pragul proporțional cu curentul de frânare rămâne mic la sarcină și crește numai când curentul traversant crește.

   </details>

3. Ce se întâmplă cu protecția diferențială a unui transformator YNd11 la un defect cu pământul în rețeaua de 110 kV, dacă releul nu elimină componenta homopolară?
   <details><summary>Răspuns</summary>

   Neutrul legat la pământ al înfășurării în stea permite curentului homopolar să circule pe fazele de 110 kV ale transformatorului; pe partea în triunghi curentul homopolar rămâne în interiorul înfășurării și nu ajunge la TC de 20 kV. Releul vede un curent diferențial egal cu $I_0$ pe fiecare fază (4,449·In în problema 4.1) și declanșează greșit transformatorul.

   </details>

4. De ce conține curentul de magnetizare la conectare armonica a doua, iar curentul de scurtcircuit aproape deloc?
   <details><summary>Răspuns</summary>

   Curentul de conectare este format din impulsuri unipolare (miezul se saturează numai într-un sens), deci nu are simetrie de semiundă; o asemenea formă conține armonici pare. Curentul de scurtcircuit este sinusoidal, cu o componentă aperiodică; în prima perioadă aceasta produce și ea puțină armonică a doua (6–13 % în problema 4.4), de aceea pragul de blocare trebuie ales cu grijă și completat de treapta nefrânată.

   </details>

5. De ce defectele cu pământul de pe partea de 20 kV a lui T1, într-o rețea tratată prin rezistor, nu sunt lăsate protecției diferențiale a transformatorului?
   <details><summary>Răspuns</summary>

   Rezistorul limitează curentul de defect la circa 300 A, sub jumătate din curentul nominal al transformatorului, aproape de pragul minim al protecției, iar componenta homopolară vine de la bobina de punct neutru. Pentru aceste defecte se folosește protecția restrânsă la pământ (curentul rezidual al TC de 20 kV ai transformatorului), cu pragul raportat la curentul de defect, nu la curentul nominal; protecția homopolară a bobinei de punct neutru rămâne rezervă neselectivă.

   </details>

6. Ce caz verifică formula $V_s \ge I_{k,sec}(R_{ct} + 2R_L)$ la protecția de bare de impedanță mare?
   <details><summary>Răspuns</summary>

   Un defect exterior imediat după TC al unui circuit, cu acest TC complet saturat: el nu mai produce curent și se reduce la rezistența lui. Curentul celorlalte TC se închide prin această rezistență și prin conductoarele de legătură, iar tensiunea pe releu este cel mult produsul lor. Cazul se verifică pentru toate celulele; cel mai sever este de obicei celula fără sursă în spate (la bara B, celula lui T1). Releul reglat peste această tensiune rămâne stabil; la un defect interior, toate TC debitează în releul de impedanță mare, iar tensiunea este limitată de limitatorul neliniar.

   </details>

7. Ce problemă specifică are protecția diferențială a liniilor, față de cea a transformatorului?
   <details><summary>Răspuns</summary>

   Capetele sunt la distanță, deci curenții se transmit pe un canal de comunicație; măsurările trebuie sincronizate (întârzierea canalului se măsoară sau se folosește un semnal de timp extern), curentul capacitiv al liniei apare ca diferențial și trebuie compensat, iar la căderea canalului releul trebuie să treacă pe o protecție de rezervă.

   </details>

## Bibliografie

- [1] Alstom Grid – *Network Protection & Automation Guide*, 2011.
- [3] G. Ziegler – *Numerical Differential Protection: Principles and Applications*, ed. 2, Publicis, 2012.
- [7] W. A. Elmore (ed.) – *Protective Relaying: Theory and Applications*, ed. 2, Marcel Dekker, 2003.
- [8] W. A. Elmore – *Pilot Protective Relaying*, Marcel Dekker, 2000.
- [9] ABB – *Distribution Automation Handbook*, secțiunea 8 (protecția transformatoarelor de înaltă tensiune).
- [14] R. Tîrnovan, I. Vădan, H. Bălan, A. Botezan – *Protecții prin relee în sistemele electroenergetice*, U.T. Press, 2008.
- [16] R.-A. Tîrnovan – *Protecții digitale în sistemele electroenergetice*, U.T. Press, 2019.
- [S6] IEC 60255-187-1:2021; [S7] IEC 61869-2:2012; [S12] IEEE C37.2-2022.
