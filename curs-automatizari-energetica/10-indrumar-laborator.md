# Îndrumar de laborator

Lucrările de laborator urmăresc capitolele cursului: L1 și L2 – protecția maximală și transformatoarele de curent (capitolele 2 și 3), L3 – protecția diferențială (capitolul 4), L4 – protecția de distanță (capitolul 5), L5 – reanclanșarea, sincronizarea și AAR (capitolul 7), L6 – reglajul frecvenței și descărcarea sarcinii (capitolul 8, lucrare de simulare), L7 – mesajele GOOSE IEC 61850 (capitolul 9).

Valorile așteptate din tabele sunt calculate de scripturile cursului (`scripts/probleme_cap10.py` pentru L1–L2 și scripturile capitolelor pentru celelalte lucrări), din reglajele stabilite în problemele rezolvate.

---

## Securitatea muncii

Regulile generale sunt cele din Legea nr. 319/2006 a securității și sănătății în muncă [S22] și din instrucțiunile proprii ale laboratorului, pe care fiecare student le semnează la instructajul de la începutul semestrului. Pentru lucrările cu relee și transformatoare de măsură se adaugă:

1. Se lucrează **numai pe circuitele secundare** și numai cu sursele de încercare ale laboratorului (trusa de injecție de curent și tensiune). Echipamentele primare nu se ating.
2. **Secundarul unui transformator de curent aflat sub curent nu se deschide niciodată** (§ 2.2). Înainte de a scoate un releu sau un aparat de măsură din circuit, secundarul TC se scurtcircuitează cu clemele de încercare.
3. **Secundarul unui transformator de tensiune nu se scurtcircuitează.** Circuitele de tensiune se conectează și se deconectează numai cu sursa oprită.
4. Ieșirile de declanșare ale releului se conectează numai la intrarea de oprire a cronometrului trusei de încercare sau la sarcina de simulare a laboratorului, niciodată la un întrerupător real.
5. Montajul se verifică de cadrul didactic înainte de punerea sub tensiune. Orice modificare a montajului se face cu sursa oprită.
6. Curenții de injecție mari (peste curentul nominal secundar) se aplică numai pe durata necesară măsurării, ca să nu se încălzească bornele și conductoarele.

---

## L1. Încercarea releului de protecție maximală de curent

**Scopul lucrării.** Verificarea reglajelor releului R1 al fiderului F1 (problema 3.2) prin injecție secundară: curentul de pornire, raportul de revenire, caracteristica de timp dependentă SI și treapta instantanee.

**Reglajele de încercat** (TC 400/1 A): $I_s$ = 300 A primar = **0,750 A** secundar; TMS = **0,19**, caracteristica IEC normal inversă; $I_{>>}$ = 2800 A primar = **7,00 A** secundar, instantaneu.

**Montajul.** Trusa de injecție alimentează intrarea de curent a fazei a a releului. Contactul de declanșare al releului oprește cronometrul trusei. Pornirea cronometrului se face odată cu aplicarea curentului.

**Mod de lucru.**

1. *Curentul de pornire.* Creșteți lent curentul de la 0,5 A până la pornirea releului (semnalizarea „start”). Notați $I_{pornire}$. Scădeți apoi lent curentul până la revenire și notați $I_{revenire}$. Calculați raportul de revenire $k_r = I_{revenire}/I_{pornire}$. Repetați de trei ori.
2. *Caracteristica de timp.* Blocați temporar treapta instantanee (sau verificați că injecțiile sunt sub 7,00 A). Aplicați brusc curenții din tabelul 1 și măsurați timpul de acționare. Repetați fiecare măsurare de trei ori.
3. *Treapta instantanee.* Aplicați 6,30 A (0,9·I>>): trebuie să acționeze treapta temporizată după aproximativ 0,612 s. Aplicați 8,40 A (1,2·I>>): trebuie să acționeze treapta instantanee. Măsurați timpul propriu al treptei instantanee.
4. Verificați și celelalte două faze la un singur punct (4·Is).

**Tabelul 1 – Caracteristica de timp (valori așteptate din formula IEC 60255-151)**

| Curentul injectat | $I/I_s$ | Timpul așteptat | $t_1$ | $t_2$ | $t_3$ | Media | Abaterea [%] |
|---|---|---|---|---|---|---|---|
| 1,50 A | 2 | 1,906 s | | | | | |
| 3,00 A | 4 | 0,946 s | | | | | |
| 4,50 A | 6 | 0,729 s | | | | | |
| 6,00 A | 8 | 0,626 s | | | | | |
| 6,30 A | 8,4 | 0,612 s | | | | | |

**Prelucrarea.** Reprezentați punctele măsurate pe un grafic log-log peste caracteristica teoretică (figura 3.1). Comparați abaterile cu toleranța de timp declarată în documentația releului. Explicați de ce abaterea relativă este mai mare la curenți apropiați de $I_s$.

**Întrebări.**

1. De ce raportul de revenire trebuie să fie apropiat de 1? Ce s-ar întâmpla la un raport de 0,8 după eliminarea unui defect exterior (§ 3.3)?
2. Cât ar fi timpul de acționare la 4·Is dacă TMS ar fi 0,13 (ca la R2)? Verificați cu formula.
3. De ce injecția de 6,30 A dă un timp mai scurt decât cea de 6,00 A, deși ambele sunt sub pragul treptei instantanee?
4. Ce verificare suplimentară ar fi necesară pentru a confirma selectivitatea R1–R2 în instalație, nu numai reglajul lui R1?

---

## L2. Verificarea transformatorului de curent

**Scopul lucrării.** Verificarea polarității și a raportului unui TC 400/1 A, 5P20, 5 VA, măsurarea rezistenței înfășurării secundare și a sarcinii, calculul factorului limită de precizie efectiv (problema 2.1).

**Mod de lucru.**

1. *Polaritatea.* Cu o sursă de curent continuu de câțiva volți și un întrerupător în primar (borna P1) și un miliampermetru cu zero la mijloc în secundar (borna S1 la „+”), închideți scurt circuitul primar. Deviația la dreapta la închidere confirmă polaritatea P1–S1.
2. *Raportul.* Injectați în primar curenții din tabelul 2 (trusa de curent mare a laboratorului) și măsurați curentul secundar cu un ampermetru de clasă bună. Calculați eroarea de raport.
3. *Rezistența secundară.* Măsurați $R_{ct}$ în curent continuu (punte sau metoda voltmetru–ampermetru), cu primarul deschis. Măsurați rezistența buclei conductoarelor de legătură și consumul releului.
4. *Curba de magnetizare.* Cu primarul deschis, alimentați secundarul de la o sursă de tensiune alternativă reglabilă și măsurați perechi (tensiune, curent) până când curentul crește brusc la creșteri mici ale tensiunii. Atenție: tensiunile pot ajunge la sute de volți; se lucrează numai cu montajul verificat și cu sursa laboratorului.

**Tabelul 2 – Raportul de transformare**

| Curentul primar | Curentul secundar așteptat | Curentul secundar măsurat | Eroarea de raport [%] |
|---|---|---|---|
| 100 A | 0,250 A | | |
| 200 A | 0,500 A | | |
| 400 A | 1,000 A | | |

**Prelucrarea.** Calculați $ALF_{ef} = 20\thinspace(R_{ct} + 5\thinspace Ω)/(R_{ct} + R_b)$ cu valorile măsurate. Pentru $R_{ct}$ = 1,5 Ω și $R_b$ = 0,242 Ω (problema 2.1) rezultă 74,6. Comparați cu raportul $I''_{k3max}/I_n$ = 15,08 la bara B2. Trasați curba de magnetizare și marcați tensiunea electromotoare la limita de precizie, $E_{ALF} = 20 \cdot 1\thinspace\text{A} \cdot (R_{ct} + 5\thinspace Ω)$ (130 V pentru $R_{ct}$ = 1,5 Ω): punctul trebuie să se afle înainte de creșterea bruscă a curentului de magnetizare.

**Întrebări.**

1. De ce polaritatea TC contează pentru protecțiile direcționale și diferențiale, dar nu și pentru o protecție maximală nedirecțională?
2. Cum se modifică $ALF_{ef}$ dacă releul este mutat la 100 m de TC (problema 2.2)? Ce consecință are asupra timpului până la saturație?
3. De ce încercarea curbei de magnetizare se face din secundar, cu primarul deschis, și nu prin injecție în primar?

---

## L3. Verificarea protecției diferențiale a transformatorului

**Scop.** Verificarea prin injecție secundară a unui releu diferențial numeric reglat pentru transformatorul T1 (25 MVA, 110/20 kV, YNd11; TC 150/1 A și 800/1 A): pragul minim, compensarea grupei de conexiuni, caracteristica cu frânare și blocarea la armonica a doua (capitolul 4).

**Aparatura.** Releu diferențial numeric de transformator; trusă de injecție cu șase surse de curent (trei pentru partea de 110 kV, trei pentru partea de 20 kV), cu reglaj de fază și posibilitatea de a adăuga armonica a doua; calculator cu programul releului.

**Reglajele releului** (problemele 4.1–4.4): $I_n$ = 131,2 A (110 kV) și 721,7 A (20 kV); grupa YNd11, cu eliminarea componentei homopolare pe partea de 110 kV; pragul minim 0,30·In; panta 1: 30 % până la $I_b$ = 3·In; panta 2: 70 %; treapta nefrânată 11·In; blocare la armonica a doua: 12 %; curentul de frânare = media modulelor (dacă releul folosit are altă definiție, valorile așteptate se recalculează cu scriptul `probleme_cap04.py`).

**Securitatea muncii.** Releul se separă de circuitele secundare reale ale TC prin blocurile de încercare; circuitele de curent ale TC se scurtcircuitează **înainte** de a le deconecta de la releu (§ 2.2). Ieșirile de declanșare ale releului se leagă numai la intrarea de oprire a trusei de injecție. Curenții mari (peste 4–5 A) se injectează numai pe durate scurte, conform datelor releului.

**Mod de lucru**

1. *Pragul minim.* Se injectează un curent monofazat numai pe faza a a părții de 20 kV, crescând lent până la acționare; apoi numai pe faza a a părții de 110 kV. Pe partea de 110 kV, matricea de compensare împarte curentul la √3 și îl arată pe fazele a și c ale releului; pe partea de 20 kV curentul ajunge nemodificat.
2. *Stabilitatea la curent traversant.* Se injectează simultan curenți trifazați simetrici pe ambele părți: 110 kV cu 0,8748 A ∠0°, 20 kV cu 0,9021 A ∠210° (1·In pe ambele părți, cu defazajul de 30° al grupei și sensul opus). Releul nu trebuie să acționeze; se citesc $I_d$ și $I_b$ afișate. Se repetă cu defazajul greșit (∠180° pe 20 kV) și se notează curentul diferențial afișat (valoarea așteptată: 2·sin 15° = 0,5176·In).
3. *Caracteristica cu frânare.* Se menține curentul de 20 kV la valoarea din tabel (∠210°) și se crește curentul de 110 kV (∠0°) până la acționare.
4. *Blocarea la armonica a doua.* Se injectează pe partea de 110 kV, trifazat, 1·In fundamentală cu 20 % armonica a doua (releul nu trebuie să acționeze); se scade conținutul de armonică în trepte de 1 % până la acționare.
5. *Treapta nefrânată.* Cu blocarea la armonica a doua activă, se injectează scurt pe partea de 20 kV un curent trifazat de 12·In (10,825 A) cu 20 % armonica a doua: treapta frânată este blocată, treapta nefrânată trebuie să acționeze.

**Valori așteptate** (calculate de `probleme_cap04.py`)

| Încercarea | Valoarea așteptată |
|---|---|
| pragul minim, injecție pe faza a, 110 kV | 0,4545 A |
| pragul minim, injecție pe faza a, 20 kV | 0,2706 A |
| stabilitate, 1·In pe ambele părți | $I_d$ = 0, $I_b$ = 1,000·In |

| 20 kV (fix) | 110 kV la acționare | $I_b$ | $I_d$ |
|---|---|---|---|
| 0,902 A (1,0·In) | 1,184 A (1,353·In) | 1,176·In | 0,353·In |
| 1,804 A (2,0·In) | 2,367 A (2,706·In) | 2,353·In | 0,706·In |
| 3,608 A (4,0·In) | 5,652 A (6,462·In) | 5,231·In | 2,462·In |
| 5,413 A (6,0·In) | 9,286 A (10,615·In) | 8,308·In | 4,615·In |

**Tabel de măsurători**

| Încercarea | Valoarea așteptată | Valoarea măsurată | Abaterea [%] |
|---|---|---|---|
| prag 110 kV (faza a) | 0,4545 A | | |
| prag 20 kV (faza a) | 0,2706 A | | |
| punctul 1 al caracteristicii | 1,184 A | | |
| punctul 2 | 2,367 A | | |
| punctul 3 | 5,652 A | | |
| punctul 4 | 9,286 A | | |
| armonica a doua la deblocare | 12 % | | |

**Întrebări**

1. De ce pragul măsurat la injecția pe partea de 110 kV este de √3 ori mai mare (raportat la $I_n$) decât la injecția pe partea de 20 kV?
2. Ce curent diferențial ați citit la încercarea de stabilitate cu defazajul greșit (∠180°)? Explicați valoarea cu ajutorul figurii 4.3.
3. Reprezentați punctele măsurate pe caracteristica din figura 4.2. Ce pantă rezultă între punctele 3 și 4?
4. De ce treapta nefrânată nu este blocată de armonica a doua? Ce defect din problema 4.3 justifică acest lucru?

---

## L4. Verificarea protecției de distanță

**Scopul lucrării.** Verificarea prin injecție secundară a acoperirilor și temporizărilor zonelor unei protecții de distanță numerice, reglată ca releul 21 din stația A (capitolul 5, problema 5.1). Se urmărește și efectul compensării homopolare $k_0$.

**Echipament.** Releu de distanță numeric (sau simulator de releu), sursă de injecție trifazată de tensiune și curent cu comandă de impedanță (trusă de încercare a protecțiilor), calculator cu programul trusei, cronometrarea intrării binare de declanșare.

**Măsuri de securitate.** Lucrarea se face numai pe circuite secundare, cu releul separat de TC și TT ai instalației. Blocurile de încercare se deschid în ordinea din instrucțiunea standului: întâi se scurtcircuitează secundarul TC, apoi se separă TT, apoi se separă declanșarea spre întrerupător. Circuitele secundare ale TC nu se deschid sub curent. Se respectă instructajul general al laboratorului (Legea 319/2006 [S22]).

**Reglajele releului (secundar, TC 600/1 A, TT 110/0,1 kV).**

| Zona | modulul Z (mho, la 73,3°) | X (poligon) | R (poligon) | t |
|---|---|---|---|---|
| 1 | 7,471 Ω | 7,156 Ω | 8,18 Ω | 0 |
| 2 | 10,934 Ω | 10,473 Ω | 10,91 Ω | 0,3 s |
| 3 | 22,636 Ω | 21,682 Ω | 16,36 Ω | 0,6 s |

Factorul de compensare homopolară: $\underline{k}_0$ = 0,655 ∠ 4,02° (sau, după convenția releului, $\underline{Z}_0/\underline{Z}_1$ = 2,962 ∠ 2,66°; se verifică în manualul releului ce mărime cere).

**Desfășurarea lucrării.**

1. Se introduc reglajele în releu și se verifică pe afișaj valorile secundare.
2. **Acoperirea pe direcția liniei** (bucla a–b, apoi bucla a–p): se injectează defecte în punctele din tabelul de mai jos și se notează dacă releul acționează și după cât timp.
3. **Acoperirea rezistivă** (numai caracteristica poligonală, bucla a–p): puncte la jumătatea acoperirii reactive, la 0,9 și 1,1 din limita din dreapta.
4. **Compensarea homopolară**: se repetă punctul „zona 1, 0,9·Z” pe bucla a–p cu $k_0$ = 0 în releu; se notează în ce zonă apare defectul și se compară cu problema 5.2.
5. **Direcția**: se injectează un defect cu Z = −0,9·$Z_1$ (în cadranul III); releul nu trebuie să acționeze.

În tabelul următor, $Z_1$, $Z_2$ și $Z_3$ notează acoperirile zonelor 1, 2 și 3 pe direcția liniei (nu impedanțele de secvență).

| Punctul (secundar) | Ce trebuie să se întâmple |
|---|---|
| 0,9·$Z_1$ = 1,932 + j6,441 Ω | declanșare în zona 1, fără temporizare |
| 1,1·$Z_1$ = 2,362 + j7,872 Ω | declanșare în zona 2, după 0,3 s |
| 0,9·$Z_2$ = 2,828 + j9,425 Ω | declanșare în zona 2, după 0,3 s |
| 1,1·$Z_2$ = 3,456 + j11,520 Ω | declanșare în zona 3, după 0,6 s |
| 0,9·$Z_3$ = 5,854 + j19,514 Ω | declanșare în zona 3, după 0,6 s |
| 1,1·$Z_3$ = 7,155 + j23,850 Ω | nicio declanșare |
| zona 1, R: 8,330 + j3,578 Ω | declanșare în zona 1 (poligon); cu caracteristici mho: zona 3 |
| zona 1, R: 10,181 + j3,578 Ω | declanșare în zona 2 (poligon); cu caracteristici mho: zona 3 |

**Rezultate.** Tabel cu: punctul injectat, bucla, zona așteptată, zona indicată de releu, timpul măsurat, abaterea față de temporizarea reglată. Pentru fiecare zonă se determină și limita reală pe direcția liniei, prin apropieri succesive (pas de 1 %), și se compară cu reglajul.

**Întrebări.**

1. De ce punctul 8,330 + j3,578 Ω este în zona 1 poligonală, dar în afara cercurilor mho ale zonelor 1 și 2?
2. Ce eroare relativă a acoperirii zonei 1 ați măsurat? Este compatibilă cu bugetul de erori al releului din problema 5.1 (±5 %)?
3. Cum s-ar schimba punctele din tabel dacă TC ar fi 1200/1 A în loc de 600/1 A?
4. De ce, la încercarea cu $k_0$ = 0, defectul monofazat „se mută” mai departe pe linie?

---

## L5. Reanclanșarea automată, sincronizarea și AAR

**Scop.** Verificarea ciclului unui automat de reanclanșare (pauze, timp de revenire, blocare, accelerare), a funcției de control al sincronismului și a logicii unui AAR, prin injecție secundară și simularea pozițiilor întrerupătoarelor. Legătura cu teoria: capitolul 7 (§ 7.2–7.4, problemele 7.2, 7.4 și 7.5).

**Echipament.** Terminal numeric de protecție a fiderului, cu funcțiile 50/51, 79 și 25 (sau un terminal separat de control al sincronismului). Trusă de injecție secundară trifazată, cu cel puțin două sisteme de tensiune reglabile independent ca valoare, frecvență și fază, și cu intrări/ieșiri binare pentru simularea întrerupătorului. Calculator cu programul de configurare al terminalului.

**Securitatea muncii.** Se lucrează numai în circuitele secundare, cu terminalul scos din instalație sau cu circuitele de declanșare spre întrerupătoarele reale separate (cleme de încercare deschise). Circuitele secundare ale transformatoarelor de curent nu se deschid sub sarcină, iar cele ale transformatoarelor de tensiune nu se scurtcircuitează. Montajul se verifică de cadrul didactic înainte de alimentare (Legea 319/2006 [S22] și instructajul din laborator).

**Schema.** Ieșirea de declanșare a terminalului comandă intrarea „deschide” a simulatorului de întrerupător din trusă. Ieșirea de reanclanșare comandă intrarea „închide”. Simulatorul răspunde cu poziția întrerupătorului (contact auxiliar) după timpii proprii reglați: 0,06 s la deschidere și 0,08 s la închidere. Curentul de defect se injectează numai cât întrerupătorul simulat este închis.

**Mod de lucru**

1. Se introduc reglajele din problema 7.2: $I_s$ = 300 A primar (TC 400/1 A, deci 0,75 A secundar), TMS = 0,19, caracteristică normal inversă, treapta instantanee la 2800 A (7,0 A secundar), două reanclanșări (pauze reglate de 0,5 s și 15 s), timpul de revenire 30 s, accelerare după reanclanșare 0,04 s.
2. **Defect trecător:** se injectează 2079 A primar (5,20 A secundar), iar trusa oprește injecția la prima deschidere. Se măsoară timpul de declanșare, pauza de tensiune (de la deschidere la închiderea întrerupătorului simulat; calculat 0,58 s) și momentul reanclanșării. Se verifică revenirea după timpul de revenire.
3. **Defect permanent:** trusa reia injecția la fiecare închidere. Se înregistrează toate momentele de deschidere și închidere și momentul blocării. Se repetă fără accelerare.
4. **Blocări:** se verifică faptul că RAR nu acționează la o declanșare manuală și la o declanșare dată printr-o intrare binară „protecția barelor”.
5. **Controlul sincronismului:** se aplică pe cele două intrări de tensiune 100 V și 100 V, cu frecvențele 50,0 Hz și 50,1 Hz. Se reglează pragurile Δφ ≤ 20°, Δf ≤ 0,2 Hz, ΔU ≤ 10 % (date ale lucrării) și se înregistrează intervalele în care închiderea este permisă. Se repetă cu ΔU = 15 % și cu Δf = 0,3 Hz.
6. **AAR (opțional, pe macheta de laborator):** se simulează pierderea tensiunii pe bara de lucru (tensiunea scade la 0) și se măsoară timpul până la comanda de închidere a sursei de rezervă. Se verifică blocarea când lipsește tensiunea sursei de rezervă și când bara a fost deconectată de protecția barelor.

**Tabele de completat**

| Încercarea | Deschidere 1 [s] | Închidere 1 [s] | Deschidere 2 [s] | Închidere 2 [s] | Deschidere 3 / blocare [s] |
|---|---|---|---|---|---|
| calculat (problema 7.2), permanent, cu accelerare | 0,734 | 1,314 | 1,414 | 16,494 | 16,594 |
| calculat, permanent, fără accelerare | 0,734 | 1,314 | 2,048 | 17,128 | 17,861 |
| măsurat, cu accelerare | | | | | |
| măsurat, fără accelerare | | | | | |

| Δf [Hz] | ΔU [%] | Închidere permisă? | Durata intervalului permis [s] | Calculat: 2·20°/(360°·Δf) [s] |
|---|---|---|---|---|
| 0,1 | 0 | | | 1,11 |
| 0,1 | 15 | | | – (blocat de ΔU) |
| 0,3 | 0 | | | – (blocat de Δf) |

**Întrebări**

1. De ce timpul măsurat de la începutul injecției până la prima reanclanșare este mai mare decât suma dintre temporizarea protecției și pauza reglată?
2. Ce s-ar întâmpla dacă timpul de revenire ar fi reglat mai scurt decât temporizarea protecției la curentul de defect?
3. Cum se modifică durata intervalului în care închiderea este permisă dacă alunecarea crește de două ori? Ce legătură are aceasta cu unghiul de avans al sincronizatorului?
4. De ce AAR nu trebuie să acționeze când bara a fost deconectată de protecția barelor?

---

## L6. Reglajul frecvenței și descărcarea automată a sarcinii – lucrare de simulare

**Scopul lucrării.** Observarea, pe un model numeric, a efectului inerției, al statismului regulatoarelor de viteză și al descărcării automate a sarcinii la scăderea frecvenței (DASF) asupra frecvenței unui sistem izolat; verificarea unei scheme DASF față de cerințele Regulamentului (UE) 2017/2196 (capitolul 8, § 8.1–8.5).

**Modelul.** Sistemul este reprezentat printr-o singură bară (§ 8.1): $M\thinspace d\Delta f/dt = \Delta P_m - \Delta P - D\thinspace\Delta f$, cu $M = 2HS/f_0$. Regulatoarele de viteză sunt modelate prin statismul $s$ și două întârzieri de ordinul întâi ($T_g$, $T_t$), iar puterea lor suplimentară este limitată la rezerva disponibilă. Treptele DASF deconectează sarcina după o întârziere fixă (releu + întrerupător). Funcțiile sunt în [`scripts/calcul_cap08.py`](scripts/calcul_cap08.py): `izolat_ode` (sistem izolat) și `dasf_simulare` (insulă cu DASF).

**Mod de lucru.**

1. Rulați `python probleme_cap08.py` din directorul `scripts/` și regăsiți în rezultate valorile din problemele 8.1 și 8.3.
2. **Inerția.** Cu datele problemei 8.1, simulați pierderea a 100 MW pentru $H$ = 2, 3, 5 și 8 s (de exemplu, într-un fișier nou care importă `izolat_ode` și `M_inertie`). Notați în tabelul 1 RoCoF inițial (din primul pas al simulării), nadirul și momentul lui, abaterea staționară. Comparați RoCoF cu $-\Delta P/M$.
3. **Statismul.** Cu $H$ = 5 s, repetați pentru statismul de 3 %, 5 % și 8 %. Comparați abaterea staționară cu $-\Delta P/(K_\text{reg} + D)$.
4. **DASF.** Cu datele problemei 8.3 (insulă de 600 MW, deficit de 180 MW, rezervă 80 MW), simulați: (a) fără DASF; (b) cu schema de 9 trepte × 5 %; (c) cu schema de 6 trepte la 0,2 Hz de 10/8/8/8/8/3 %; (d) cu schema (b) și întârzierea mărită de la 0,15 s la 0,5 s. Completați tabelul 2.
5. Pentru fiecare schemă (inclusiv varianta c', cu 6 trepte egale de 7,5 %), verificați programatic condițiile NC ER: prima treaptă la 49,0 Hz (cu 5 % ± 7 %), 45 % cumulat la 48,0 Hz, cel puțin 6 trepte, cel mult 10 % pe treaptă și banda de ±7 % (interpretarea din § 8.5).

**Tabelul 1 – Sistem izolat, pierderea a 100 MW**

| $H$ [s] | statism | RoCoF simulat [Hz/s] | $-\Delta P/M$ [Hz/s] | nadir [mHz] | $t_{nadir}$ [s] | $\Delta f_{st}$ simulat [mHz] | $-\Delta P/(K_\text{reg}+D)$ [mHz] |
|---|---|---|---|---|---|---|---|
| 2 | 5 % | | | | | | |
| 5 | 5 % | | | | | | |
| 8 | 5 % | | | | | | |
| 5 | 3 % | | | | | | |
| 5 | 8 % | | | | | | |

**Tabelul 2 – Insula cu deficit de 30 %**

| Varianta | trepte acționate | sarcină deconectată [MW] | $f_{min}$ [Hz] | $f$ finală [Hz] | conformă NC ER? |
|---|---|---|---|---|---|
| (a) fără DASF | – | – | | | – |
| (b) 9 × 5 %, 0,15 s | | | | | |
| (c) 6 trepte, 10/8/8/8/8/3 % | | | | | |
| (c') 6 trepte egale de 7,5 % | | | | | |
| (d) 9 × 5 %, 0,5 s | | | | | |

**Întrebări.**

1. Care dintre mărimile din tabelul 1 depinde de inerție și care nu? Explicați cu ecuația mișcării.
2. De ce nadirul este mai jos decât abaterea staționară? Ce caracteristică a turbinelor îl influențează?
3. Ce se întâmplă cu frecvența minimă și cu frecvența finală când întârzierea treptelor crește (varianta d)? De ce?
4. Câte trepte au acționat în fiecare variantă? Ar fi fost mai bine dacă ar fi acționat mai multe? (Indicație: urmăriți frecvența finală și riscul de supracompensare.)
5. Calculați frecvența finală din numărul de trepte acționate, ca în problema 8.3, și comparați-o cu simularea.

---

## L7. IEC 61850 – observarea mesajelor GOOSE

**Scopul lucrării.** Observarea unui flux GOOSE real: structura cadrului, programul de retransmisie după o schimbare de stare, contoarele stNum și sqNum, timpul de valabilitate și efectul pierderii legăturii (§ 9.5, problema 9.3).

**Echipamente și programe.**

- două IED-uri cu IEC 61850 (sau, în lipsa lor, două calculatoare care rulează programele de exemplu pentru publicare și abonare GOOSE din biblioteca open-source **libIEC61850**);
- un comutator Ethernet și un calculator cu **Wireshark** (analizorul de protocoale are un decodor pentru GOOSE);
- fișierele de configurare ale IED-urilor (ICD/CID) puse la dispoziție de cadrul didactic.

**Reguli de lucru.** Rețeaua laboratorului este izolată, fără legătură cu rețeaua instituției. Nu se conectează echipamente din laborator la rețeaua unei stații reale. Modificările de configurare a IED-urilor se fac numai cu acordul cadrului didactic.

**Mod de lucru.**

1. Identificați în fișierul SCD (sau CID) blocul de control GOOSE al publicatorului: setul de date, identificatorul aplicației (APPID), adresa multicast de destinație, intervalele de retransmisie configurate. Notați-le în tabelul 1.
2. Porniți captura în Wireshark cu filtrul `goose`. În repaus, măsurați intervalul dintre mesaje ($T_0$) și notați valorile stNum, sqNum și timeAllowedToLive.
3. Provocați o schimbare de stare la publicator (o intrare binară, o comandă de test sau, pentru programul de exemplu, modificarea valorii publicate). Exportați momentele de sosire ale mesajelor (coloana *Time*) pentru primele 2 s după schimbare și completați tabelul 2.
4. Comparați intervalele măsurate cu cele configurate și cu programul din figura 9.3. Verificați că stNum a crescut cu 1, iar sqNum a fost repus la zero și crește la fiecare repetare.
5. Deconectați cablul publicatorului. Măsurați, la abonat (semnalizarea „GOOSE invalid” sau jurnalul programului), timpul până la detectarea pierderii. Repetați de 5 ori, la momente diferite față de ultimul mesaj, și comparați cu intervalul $TAL - T_0 \ldots TAL$ (problema 9.3).
6. (Opțional) Introduceți între publicator și abonat un al doilea comutator și estimați, din momentele de captură, contribuția rețelei la timpul de transfer.

**Tabelul 1 – Configurația blocului de control GOOSE**

| Parametru | Valoare |
|---|---|
| referința blocului de control (gocbRef) | |
| setul de date (datSet) | |
| APPID / adresa MAC multicast | |
| intervalul minim / maxim de retransmisie | |

**Tabelul 2 – Mesajele după o schimbare de stare**

| Nr. | Momentul [ms] | Intervalul față de mesajul anterior [ms] | stNum | sqNum | timeAllowedToLive [ms] |
|---|---|---|---|---|---|
| 1 | 0 | – | | | |
| 2 | | | | | |
| … | | | | | |

**Tabelul 3 – Detectarea pierderii legăturii**

| Încercarea | Timp de la ultimul mesaj până la deconectare [s] | Timp până la detectare [s] |
|---|---|---|
| 1 … 5 | | |

**Întrebări.**

1. De ce intervalul de retransmisie este scurt imediat după o schimbare de stare și lung în repaus?
2. Cum recunoaște abonatul un mesaj pierdut? Dar un mesaj vechi, sosit după unul mai nou?
3. Între ce limite poate varia timpul de detectare a pierderii legăturii? Comparați cu măsurările din tabelul 3.
4. Ce ar trebui să facă protecția barelor prin blocare (§ 3.6) când semnalul GOOSE de blocare devine invalid? Argumentați ambele variante discutate în problema 9.3.
5. De ce mesajele GOOSE nu trebuie să părăsească rețeaua stației fără măsuri de securitate (§ 9.12)?

---

## Bibliografie

- [1] Alstom Grid – *Network Protection & Automation Guide*, 2011 (capitolul despre încercarea și punerea în funcțiune a releelor).
- [7] W. A. Elmore (ed.) – *Protective Relaying: Theory and Applications*, ed. 2, Marcel Dekker, 2003.
- [14] R. Tîrnovan, I. Vădan, H. Bălan, A. Botezan – *Protecții prin relee în sistemele electroenergetice*, U.T. Press, 2008.
- [S2] IEC 60255-151:2009; [S7] IEC 61869-2:2012; [S10] IEC 61850; [S17] Regulamentul (UE) 2017/2196; [S22] Legea nr. 319/2006.
