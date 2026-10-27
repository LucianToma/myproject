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
3. **Probleme rezolvate** – pas cu pas, fiecare cu o **verificare pe o cale independentă**.
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

- Fazorii (numere complexe) sunt subliniați: $\underline{U}$, $\underline{I}$; valorile efective nu: $U$, $I$.
- Indicii 0, 1, 2 notează componentele homopolară, directă și inversă; a, b, c fazele; $f$ – mărime de fază, $l$ – de linie.
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
13. C. Prévé – *Protection of Electrical Networks*, ISTE, Londra, 2006, ISBN 978-1-905209-06-4 (autor de la AREVA).

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
