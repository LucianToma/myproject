# Automatizări în energetică

**Protecții prin relee și automatizări în sistemele electroenergetice** – curs pentru studenții de la specializările de inginerie energetică (și, în general, de la specializările care au parcurs un curs de bază de electrotehnică și mașini electrice): regimurile de defect, transformatoarele de măsură, protecțiile maximale, diferențiale și de distanță, protecția generatoarelor și a motoarelor, automatizările de rețea (RAR, AAR, sincronizare, protecția la refuzul întrerupătorului), reglajul automat al frecvenței și al tensiunii, descărcarea automată a sarcinii și automatizarea stațiilor (SCADA, IEC 61850). Cursul are probleme rezolvate și verificate numeric, întrebări de autoevaluare și un îndrumar de laborator.

Cursul urmărește în primul rând cărțile de referință publicate de firmele **Alstom** (Network Protection & Automation Guide), **Siemens** (cărțile lui G. Ziegler despre protecția de distanță și diferențială, Power Engineering Guide) și **ABB** (Protective Relaying – W. A. Elmore, Distribution Automation Handbook, Switchgear Manual, Substation Automation Handbook). Lista completă, cu datele bibliografice verificate, este la sfârșitul acestei pagini.

## Cuprins

| Capitol | Conținut |
|---|---|
| [0. Introducere](00-introducere.md) | rolul protecțiilor și automatizărilor, defecte și regimuri anormale, cerințele (selectivitate, rapiditate, sensibilitate, siguranță), lanțul de protecție, codurile ANSI/IEEE, rețeaua de referință |
| [1. Regimuri de defect](01-regimuri-de-defect.md) | unități relative, curenții de scurtcircuit (IEC 60909), componente simetrice, defecte nesimetrice, curentul de șoc, tratarea neutrului rețelelor de medie tensiune |
| [2. Transformatoare de măsură](02-transformatoare-de-masura.md) | transformatoarele de curent și de tensiune pentru protecție, clase de precizie, saturația, triunghiul deschis, conversia impedanțelor în secundar |
| [3. Protecția maximală de curent](03-protectia-maximala.md) | treapta instantanee și temporizată, caracteristici dependente IEC/IEEE, coordonarea pe un fider radial, protecția barelor prin blocare, protecția homopolară și direcțională |
| [4. Protecția diferențială](04-protectia-diferentiala.md) | principiul, caracteristica cu frânare, protecția transformatorului (grupa de conexiuni, curentul de magnetizare la conectare), protecția barelor și a liniilor |
| [5. Protecția de distanță](05-protectia-de-distanta.md) | măsurarea impedanței, zone și temporizări, caracteristici mho și poligonale, compensarea homopolară, rezistența de defect, alimentarea de la capătul opus, pendulații, teleprotecție |
| [6. Protecția generatoarelor și a motoarelor](06-protectia-generatoarelor-si-motoarelor.md) | protecția termică, pornirea și rotorul blocat, puterea inversă, pierderea excitației, sarcina nesimetrică, punerea la pământ a statorului |
| [7. Automatizări de rețea](07-automatizari-de-retea.md) | stabilitatea tranzitorie și timpul critic, reanclanșarea automată (RAR), anclanșarea automată a rezervei (AAR), sincronizarea, protecția la refuzul întrerupătorului |
| [8. Reglajul automat al frecvenței și al tensiunii](08-reglajul-frecventei-si-tensiunii.md) | reglajul primar, secundar și terțiar, descărcarea automată a sarcinii la scăderea frecvenței, regulatorul automat de tensiune, reglajul sub sarcină al transformatoarelor |
| [9. Automatizarea stațiilor](09-automatizarea-statiilor.md) | arhitectura (proces, celulă, stație, dispecer), SCADA și IEC 60870-5-104, IEC 61850 (modelul de date, GOOSE, valori eșantionate, SCL), sincronizarea timpului, măsurarea sincrofazorilor, securitatea cibernetică |
| [Îndrumar de laborator](10-indrumar-laborator.md) | securitatea muncii și lucrările L1–L7 |

## Structura fiecărui capitol

1. **Obiective** – ce trebuie să știe studentul la final.
2. **Teorie** – cu figuri și formule; formulele esențiale sunt încadrate.
3. **Probleme rezolvate** – pas cu pas, fiecare cu un paragraf **„Verificare”**, care spune ce se verifică și dacă verificarea este o cale de calcul independentă sau doar o verificare de consistență.
4. **Întrebări de autoevaluare** – cu răspunsuri ascunse (se deschid cu un clic).
5. **Bibliografie** pentru capitol, cu numerotarea din lista de mai jos.

Problemele folosesc aceeași **rețea de referință** (§ 0.7, figura 0.1): rețeaua de 110 kV A–B–C cu sursele echivalente QA și QC, transformatorul T1 de 25 MVA, 110/20 kV, rețeaua de 20 kV cu fiderul F1 și releele R0–R3, generatorul hidro G1 de 50 MVA și motorul asincron M1 de 800 kW. Datele sunt construite pentru curs, cu valori în domeniile uzuale; nu reproduc o instalație reală.

## Cărțile firmelor Alstom, Siemens și ABB: ce conțin și unde se găsesc

| Carte | Firma | Ce acoperă din curs | Disponibilitate |
|---|---|---|---|
| *Network Protection & Automation Guide* (NPAG), 2011 [1] | Alstom Grid (azi GE Vernova) | ghidul general al domeniului: releele de protecție și aplicațiile lor, automatizările, protecția sistemului (*system integrity protection*), măsurarea sincrofazorilor, încercarea releelor, calitatea energiei, stația digitală (IEC 61850) | ediția GE (*Protection & Automation Application Guide*) se descarcă de pe site-ul GE Vernova, după autentificare; copiile de pe site-uri terțe nu sunt oficiale |
| G. Ziegler – *Numerical Distance Protection*, 2011 [2] | Siemens | capitolul 5 (protecția de distanță, teleprotecția) | carte tipărită și electronică (Publicis / Wiley-VCH) |
| G. Ziegler – *Numerical Differential Protection*, 2012 [3] | Siemens | capitolele 2 (TC în regim tranzitoriu) și 4 (protecția diferențială) | carte tipărită și electronică (Publicis / Wiley-VCH) |
| *Power Engineering Guide*, Edition 8.0 [4] | Siemens | privire de ansamblu asupra echipamentelor de transport și distribuție; ediția 7.1 are capitole despre aparataj și stații, transformatoare, „Protection, Substation Automation, Power Quality and Measurements”, comunicații și analiza rețelelor | descărcare gratuită de pe siemens.com |
| H. Kiank, W. Fruth – *Planning Guide for Power Distribution Plants*, 2011 [5] | Siemens | proiectarea, realizarea și exploatarea rețelelor industriale de distribuție | carte (Publicis / Wiley-VCH) |
| R. Roeper – *Short-circuit Currents in Three-phase Systems*, 1985 [6] | Siemens | capitolul 1 (calculul curenților de scurtcircuit) | epuizată; în biblioteci |
| W. A. Elmore (ed.) – *Protective Relaying: Theory and Applications*, 2003 [7] | ABB | capitolele 0–8: componente simetrice, TC/TT, protecția generatoarelor, motoarelor, transformatoarelor și liniilor, stabilitatea, descărcarea sarcinii și releele de frecvență | carte (CRC Press / Routledge) |
| W. A. Elmore – *Pilot Protective Relaying*, 2000 [8] | ABB | teleprotecția și protecția diferențială a liniilor (capitolele 4 și 5) | carte (CRC Press / Routledge) |
| *Distribution Automation Handbook*, secțiunea 8 [9] | ABB | capitolele 3, 4, 5 și 7 la medie tensiune: coordonarea releelor, puneri la pământ, protecția transformatoarelor, distanța în rețele buclate, reanclanșarea automată | descărcare gratuită (PDF pe capitole) de pe abb.com |
| *Switchgear Manual* [10] | ABB (azi Hitachi Energy) | aparatajul de toate tensiunile, planificarea rețelelor, protecția și comanda, transformatoarele, solicitările la scurtcircuit | ediția a 13-a se comandă de la Hitachi Energy |
| K.-P. Brand, V. Lohmann, W. Wimmer – *Substation Automation Handbook*, 2003 [11] | autori din ABB | capitolul 9 (automatizarea stațiilor, IEC 61850) | carte |
| *ABB Review – Special Report IEC 61850*, 2010 [12] | ABB | capitolul 9 | descărcare gratuită de pe abb.com |

Datele bibliografice exacte (ediții, ISBN, contradicțiile dintre surse) sunt în lista de mai jos.

## Cum au fost verificate calculele

Toate rezultatele numerice din probleme și toate figurile (cu excepția schițelor) sunt calculate de scripturile Python din [`scripts/`](scripts/):

- `modele.py` – modelele comune: rețeaua de referință, rezolvată pe **două căi independente** (rețelele de secvență cu matricea impedanțelor nodale și rezolvarea directă în coordonate de fază, cu transformatorul modelat ca trei unități monofazate conectate fizic în stea și în triunghi), caracteristicile releelor maximale, modelul termic, transformatorul de curent saturabil, criteriul ariilor egale;
- `probleme_cap00.py` … `probleme_cap10.py` – rezolvă problemele fiecărui capitol (și valorile așteptate din îndrumarul de laborator) și verifică rezultatele. Orice verificare eșuată oprește scriptul cu eroare;
- `calcul_cap04.py` … `calcul_cap09.py` – funcțiile folosite atât de probleme, cât și de figurile capitolelor respective;
- `figuri_cap00.py` … `figuri_cap09.py` – generează figurile SVG din [`figuri/`](figuri/); reglajele și rezultatele sunt citite din aceleași scripturi de probleme, astfel încât figurile și textul să nu se poată despărți;
- `ruleaza_tot.py` – rulează tot și numără verificările.

```bash
cd curs-automatizari-energetica/scripts
pip install -r requirements.txt
python ruleaza_tot.py
```

La ultima rulare: 21 de scripturi, 905 verificări, toate trecute (durata: aproximativ 3 minute). Figurile SVG sunt reproductibile: o nouă rulare produce fișiere identice.

Verificările sunt de două feluri, iar textul fiecărei probleme spune care este care:

- **căi independente** – același rezultat obținut cu un alt model sau o altă metodă: rețele de secvență față de coordonate de fază, formulă analitică față de simulare numerică, model liniar față de model neliniar, calcul analitic față de Monte Carlo;
- **verificări de consistență** – aceeași relație scrisă altfel, bilanțuri (de exemplu legea lui Kirchhoff la o bară) sau condiții pe care reglajele trebuie să le îndeplinească. Ele prind greșeli de calcul, dar nu greșeli de model.

Afirmațiile care nu rezultă din calcul (date normative, terminologie, conținutul cărților) au fost verificate în surse publicate, de regulă în cel puțin două surse independente. Ce nu a putut fi verificat este enumerat mai jos.

## Ce nu a putut fi verificat

În această versiune, căutarea surselor a fost limitată (accesul direct la unele site-uri, de exemplu cel al Transelectrica, nu a fost posibil). Următoarele lucruri **nu au fost confirmate** din surse primare și trebuie tratate cu prudență:

- **Normative românești.** Normativul PE 501 (proiectarea protecțiilor și automatizărilor) și normativele privind tratarea neutrului nu au putut fi găsite; treptele actuale ale DASF din România (Transelectrica a prezentat în 2016 o actualizare a normativului DAS-fmin, dar valorile provin dintr-o singură sursă) nu sunt reproduse în curs.
- **Abrevieri românești.** RAR (reanclanșare automată rapidă) – o singură sursă găsită; DRRI – găsită numai în documente din Republica Moldova; AAR, DASF, BPN, „rezistor pentru tratarea neutrului” și „bobină de stingere” sunt confirmate.
- **IEEE C37.2.** Denumirile funcțiilor au fost verificate în liste secundare ale codurilor, nu în textul standardului; pentru codurile 25, 40 și 49 s-a găsit o singură sursă.
- **IEC 60909-0.** Ediția a 3-a a apărut în iulie 2026; nu s-a putut verifica dacă tabelul factorului $c$ s-a schimbat. Regulile de aplicare a factorului de siguranță al metodei B și detaliile metodei C (frecvența echivalentă de 20 Hz) sunt cele din literatura de specialitate, necitite direct din standard.
- **Clasele TC** PR, PX, PXR, TPX, TPY, TPZ din IEC 61869-2: existența claselor PR și PX a fost confirmată dintr-o singură sursă; restul descrierii provine din literatura de specialitate.
- **IEC 61850-5:** valorile claselor de timp de transfer TT0–TT4 provin dintr-o singură sursă publicată (TT5 = 10 ms și TT6 = 3 ms sunt confirmate). Atribuirea protocoalelor de redundanță PRP/HSR unui standard anume, parametrii de temporizare IEC 60870-5-104 și programul de retransmisie GOOSE (care diferă de la un producător la altul) nu au fost verificate; în curs apar numai ca exemple.
- **Ecuația timpului de declanșare din IEC 60255-149** nu a putut fi citită din standard; în curs ea este **dedusă** din modelul termic de ordinul întâi.
- **Valorile „tipice”** ale treptei de timp la protecțiile maximale și ale acoperirilor zonelor de distanță nu au fost confirmate din surse; în curs ele sunt **deduse** din componentele lor (erori, timpi de întrerupere), date ca date de problemă.
- **Regulamentul (UE) 2016/631 (RfG):** domeniile de frecvență pentru Europa continentală au fost confirmate indirect, prin tabelul identic din Regulamentul (UE) 2016/1388 (DCC).
- **Criteriul ANSI C50.41** (1,33 u.r. V/Hz la transferul motoarelor) este menționat în capitolul 7, dar nu a fost verificat.
- **Regulamentul (UE) 2017/2196 (NC ER):** valorile tabelului DASF sunt confirmate, dar formularea exactă din anexă pentru banda de implementare de ±7 % nu a fost citită; capitolul 8 folosește interpretarea „bandă în jurul dreptei 49,0 Hz/5 % → 48,0 Hz/45 %” și o spune explicit. Traducerile oficiale în limba română ale denumirilor FCR, aFRR, mFRR și RR nu au fost verificate.
- **Practici de exploatare** prezentate calitativ, fără o sursă anume: ordinea de acționare a regulatoarelor de ploturi în cascadă, blocarea lor la tensiuni foarte mici, reglarea parțială a compensării căderii de tensiune (LDC), reconectarea bateriilor de condensatoare numai după descărcare, folosirea releelor 81R la deficite mari, faptul că sursele racordate prin convertoare nu aduc inerție proprie și faptul că amortizarea oscilațiilor dintre zone vine în principal de la regulatoarele de tensiune și stabilizatoarele de sistem (PSS). La fel, în capitolele 4–7: denumirile clasice (schema Merz–Price), comportarea releului Buchholz, blocarea încrucișată la armonica a doua, protecția 100 % a statorului prin armonica a treia sau prin injecție, logica POTT/PUTT/blocare și cea de închidere pe defect (SOTF).
- **Conținutul detaliat al cărților:** faptul că NPAG [1] tratează protecția de distanță și descărcarea sarcinii în anumite capitole, iar [17] modurile de oscilație dintre zone, a fost confirmat numai din titlurile capitolelor; în curs cărțile sunt citate fără numere de capitol.
- **Cărți:** anul și ISBN-ul ediției a 13-a a *Switchgear Manual*; anul și numărul de pagini ale *Power Engineering Guide* 8.0; dacă textul actual al ghidului GE este identic cu ediția Alstom din 2011; lista completă a capitolelor NPAG (confirmată doar parțial).
- **Datele rețelei de referință** (puteri de scurtcircuit, parametrii liniilor și cablurilor, curentul de 300 A al rezistorului de neutru, datele generatorului G1 și ale motorului M1) sunt **construite pentru curs**; ele nu sunt date normative.

## Plan orientativ (un semestru de 14 săptămâni)

| Săpt. | Curs (2 h) | Laborator (2 h) |
|---|---|---|
| 1 | Cap. 0 – introducere, rețeaua de referință | instructaj de securitate |
| 2 | Cap. 1 – unități relative, IEC 60909, curentul de șoc (§ 1.1–1.3) | |
| 3 | Cap. 1 – componente simetrice, defecte nesimetrice, tratarea neutrului (§ 1.4–1.6) | |
| 4 | Cap. 2 – transformatoare de măsură | L2 – verificarea TC |
| 5 | Cap. 3 – caracteristici, reglaje, coordonare (§ 3.1–3.5) | |
| 6 | Cap. 3 – blocare, protecția homopolară și direcțională (§ 3.6–3.8) | L1 – releul maximal |
| 7 | Cap. 4 – protecția diferențială | |
| 8 | Cap. 5 – protecția de distanță | L3 – protecția diferențială |
| 9 | Cap. 5 (continuare) și cap. 6 – protecția motoarelor | |
| 10 | Cap. 6 – protecția generatoarelor | L4 – protecția de distanță |
| 11 | Cap. 7 – stabilitate, RAR, sincronizare, AAR, refuzul întrerupătorului | |
| 12 | Cap. 8 – reglajul frecvenței și al tensiunii, DASF | L5 – RAR, sincronizare, AAR |
| 13 | Cap. 9 – automatizarea stațiilor, IEC 61850 | L6 – reglajul frecvenței (simulare) |
| 14 | Cap. 9 (continuare), recapitulare | L7 – mesaje GOOSE; recuperări |

## Notații și convenții

- Fazorii (numere complexe) sunt subliniați când trebuie deosebiți de valorile efective: $\underline{U}$, $\underline{I}$; valorile efective nu: $U$, $I$.
- Tensiunile se notează cu $U$; în § 1.4–1.5, la componentele simetrice, se folosește și $V$, ca în literatura de specialitate.
- Indicii 0, 1, 2 notează componentele homopolară, directă și inversă; a, b, c fazele; $U_f$ – tensiune de fază, $U_l$ – de linie. Atenție: $Z_f$ și $R_f$ notează impedanța și rezistența **defectului**.
- $I''_k$ – curentul de scurtcircuit inițial simetric (IEC 60909-0); $I''_{k3}$, $I''_{k2}$, $I''_{k1}$ – trifazat, bifazat, monofazat; $c$ – factorul de tensiune; $i_p$ – curentul de șoc.
- $I_s$ – curentul de pornire al unei protecții; TMS – multiplicatorul de timp; $3I_0$, $3U_0$ – curentul și tensiunea reziduale.
- Funcțiile de protecție sunt notate cu codurile IEEE C37.2 (§ 0.6): 21, 50/51, 87 etc.
- u.r. – unități relative. Virgula este separatorul zecimal (convenția românească).

## Bibliografie

Datele bibliografice de mai jos au fost verificate în cataloage de bibliotecă (WorldCat, British Library, Google Books, cataloage universitare), pe paginile editorilor și pe paginile firmelor. Unde sursele se contrazic, se spune explicit.

**Cărți și ghiduri publicate de Alstom, Siemens și ABB (sau scrise de inginerii lor)**

1. Alstom Grid – *Network Protection & Automation Guide: Protective Relays, Measurement & Control* (NPAG), ediția din mai 2011, ISBN 978-0-9568678-0-3. Cartea continuă ghidurile *Protective Relays Application Guide* ale GEC Measurements (1966, 1975, 1987) și prima ediție NPAG a ALSTOM (2002, ISBN 2-9518589-0-6). Alstom o numește „ediția a 5-a” (numărând toată seria), iar cataloagele „ediția a 2-a” (sub titlul NPAG). Astăzi este distribuită de GE Vernova sub titlul *Protection & Automation Application Guide* (descărcare după autentificare): <https://www.gevernova.com/grid-solutions/multilin/publications/application_guide.htm>.
2. G. Ziegler – *Numerical Distance Protection: Principles and Applications*, ed. 4, Publicis Publishing, Erlangen, 2011, ISBN 978-3-89578-381-4. Autorul a lucrat la Siemens AG; cartea folosește releele SIPROTEC ca exemple.
3. G. Ziegler – *Numerical Differential Protection: Principles and Applications*, ed. 2, Publicis Publishing, Erlangen, 2012, ISBN 978-3-89578-351-7 (inclusiv dimensionarea transformatoarelor de curent în regim tranzitoriu).
4. Siemens – *Power Engineering Guide*, Edition 8.0 (descărcare gratuită de pe siemens.com; capitolul „Protection, Substation Automation, Power Quality and Measurements”).
5. H. Kiank, W. Fruth – *Planning Guide for Power Distribution Plants*, Publicis Publishing, Erlangen, 2011, ISBN 978-3-89578-371-5 (autori de la Siemens).
6. R. Roeper – *Short-circuit Currents in Three-phase Systems*, ed. 2, Siemens AG, Berlin/München, 1985, ISBN 3-8009-1427-1.
7. W. A. Elmore (ed.) – *Protective Relaying: Theory and Applications*, ed. 2, Marcel Dekker, New York, 2003, ISBN 978-0-8247-0972-3 (ABB Power T&D Company). British Library și WorldCat indică anul 2004.
8. W. A. Elmore – *Pilot Protective Relaying*, Marcel Dekker, New York, 2000, ISBN 978-0-8247-8195-8.
9. ABB – *Distribution Automation Handbook*, secțiunea 8 „Power System Protection” (documentele 1MRS757284 … 1MRS757294: coordonarea releelor, protecția la puneri la pământ în rețele de medie tensiune, protecția transformatoarelor, protecția de distanță, reanclanșarea automată etc.), descărcare gratuită de pe abb.com.
10. ABB – *Switchgear Manual*, ed. 11, H. Gremmel (ed.), Cornelsen Scriptor, Berlin, 2006, ISBN 978-3-589-24112-5. Ediția a 13-a se comandă de la Hitachi Energy (anul și ISBN-ul ei nu au putut fi confirmate).
11. K.-P. Brand, V. Lohmann, W. Wimmer – *Substation Automation Handbook*, Utility Automation Consulting Lohmann, Bremgarten, 2003, ISBN 978-3-85758-951-5 (autori din ABB; anterior ediției a 2-a a IEC 61850).
12. ABB Review – *Special Report IEC 61850*, august 2010.
13. C. Prévé – *Protection of Electrical Networks*, ISTE, Londra, 2006, ISBN 978-1-905209-06-4 (nota editorului îl prezintă pe autor ca inginer la AREVA, firmă din aceeași linie cu Alstom Grid).

**Manuale în limba română**

14. R. Tîrnovan, I. Vădan, H. Bălan, A. Botezan – *Protecții prin relee în sistemele electroenergetice*, U.T. Press, Cluj-Napoca, 2008.
15. S. Ștefănescu, R.-A. Tîrnovan – *Automatizări în sistemele electroenergetice – Curs*, U.T. Press, Cluj-Napoca, 2019, ISBN 978-606-737-367-7.
16. R.-A. Tîrnovan – *Protecții digitale în sistemele electroenergetice*, U.T. Press, Cluj-Napoca, 2019, ISBN 978-606-737-370-7.

**Alte manuale**

17. P. Kundur – *Power System Stability and Control*, McGraw-Hill, New York, 1994.

**Standarde și reglementări**

- [S1] IEC 60909-0:2016 – *Short-circuit currents in three-phase a.c. systems – Part 0: Calculation of currents* (ed. 2). Ediția a 3-a a apărut în iulie 2026; valorile citate în curs (factorul c, factorul $K_T$, factorul κ) sunt cele din ediția 2016.
- [S2] IEC 60255-151:2009 – *Measuring relays and protection equipment – Part 151: Functional requirements for over/under current protection*.
- [S3] IEEE C37.112-2018 – *IEEE Standard for Inverse-Time Characteristics Equations for Overcurrent Relays*.
- [S4] IEC 60255-121:2014 – *Functional requirements for distance protection*.
- [S5] IEC 60255-149:2013 – *Functional requirements for thermal electrical relays*.
- [S6] IEC 60255-187-1:2021 – *Functional requirements for differential protection – Restrained and unrestrained differential protection of motors, generators and transformers*.
- [S7] IEC 61869-2:2012 – *Instrument transformers – Additional requirements for current transformers*.
- [S8] IEC 61869-3:2011 – *Instrument transformers – Additional requirements for inductive voltage transformers*.
- [S9] IEC 61869-9:2016 – *Instrument transformers – Digital interface for instrument transformers*.
- [S10] IEC 61850 – *Communication networks and systems for power utility automation* (părțile -5, -6, -7-4, -8-1, -9-2) și IEC/IEEE 61850-9-3:2016 (profilul PTP pentru energetică).
- [S11] IEC 60870-5-104 (ed. 2.0, 2006, cu amendamentul 1:2016) – *Network access for IEC 60870-5-101 using standard transport profiles*.
- [S12] IEEE C37.2-2022 – *Standard for Electrical Power System Device Function Numbers, Acronyms, and Contact Designations*.
- [S13] IEC/IEEE 60255-118-1:2018 – *Synchrophasor for power systems – Measurements* (înlocuiește IEEE C37.118.1-2011).
- [S14] IEC 62351 – *Power systems management and associated information exchange – Data and communications security*.
- [S15] IEC 62443 – *Security for industrial automation and control systems*.
- [S16] Regulamentul (UE) 2017/1485 de stabilire a unei linii directoare privind operarea sistemului de transport al energiei electrice (SOGL).
- [S17] Regulamentul (UE) 2017/2196 de stabilire a unui cod de rețea privind starea de urgență și restaurarea sistemelor electroenergetice (NC ER).
- [S18] Regulamentul (UE) 2016/631 de instituire a unui cod de rețea privind cerințele pentru racordarea la rețea a instalațiilor de generare (RfG).
- [S19] Codul tehnic al rețelei electrice de transport, Revizia I, aprobat prin Ordinul ANRE nr. 20/2004, cu modificările și completările ulterioare.
- [S20] Seria IEC 60364 (tabelele factorului k pentru verificarea conductoarelor la scurtcircuit) și IEC 60949 (calculul curenților de scurtcircuit admisibili, inclusiv încălzirea neadiabatică).
- [S21] ST 96-MT – *Rezistor pentru tratarea neutrului rețelelor de MT*, Distribuție Energie, ed. U1, rev. 0, 2020.
- [S22] Legea nr. 319/2006 a securității și sănătății în muncă.
