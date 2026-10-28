# Mașini electrice și acționări electrice

**Curs pentru studenții de la specializările de inginerie non-electrică** (mecanică, energetică, mecatronică etc.): transformatorul, mașina asincronă, generatorul sincron, motorul sincron și acționările electrice, cu probleme rezolvate, întrebări de autoevaluare și îndrumar de laborator.

## Cuprins

| Capitol | Conținut |
|---|---|
| [0. Noțiuni fundamentale](00-notiuni-fundamentale.md) | circuitul magnetic, inducția, forța electromagnetică, fazori și puteri, sisteme trifazate, câmpul învârtitor, pierderi și încălzire, plăcuța indicatoare |
| [1. Transformatorul](01-transformatorul.md) | construcție (tole și mărcile lor, miezuri în trepte și îmbinări step-lap, înfășurări, izolație, răcire, accesorii), transformatorul ideal, schema echivalentă, încercările de gol și scurtcircuit, căderea de tensiune, randamentul, transformatorul trifazat, grupa de conexiuni, funcționarea în paralel, transformatoare speciale |
| [2. Mașina asincronă](02-masina-asincrona.md) | construcție (carcasă și gabarite, tole, înfășurări, colivie, lagăre, ventilație, fișa unui motor real), alunecare, schema echivalentă, bilanțul puterilor, caracteristica mecanică, formula lui Kloss, pornirea, reglarea vitezei, frânarea, clasele de randament IE |
| [3. Generatorul sincron](03-generatorul-sincron.md) | construcție (bare Roebel, rotor forjat și inele de bandaj, poli aparenți, excitație, răcire), reacția indusului, reactanța sincronă, caracteristici, puterea și stabilitatea, sincronizarea, reglajul P și Q, statismul |
| [4. Motorul sincron](04-motorul-sincron.md) | principiu, diagrama fazorială, cuplul de desprindere, curbele în V, compensarea factorului de putere, pornirea, motoare cu magneți permanenți, rotoare moderne și materiale magnetice |
| [5. Acționări electrice](05-actionari-electrice.md) | ecuația mișcării, raportarea la arbore, caracteristicile mașinilor de lucru, stabilitatea, cele patru cadrane, pornirea, alegerea motorului, convertorul de frecvență, eficiența energetică, scheme de comandă, componentele constructive (frână, cuplaj, reductor, traductor, modulul IGBT, condensatoare) |
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

Toate rezultatele numerice din probleme și din secțiunile de construcție, precum și toate figurile, sunt **generate de scripturile Python** din [`scripts/`](scripts/), din aceleași modele (desenele constructive sunt schematice, fără scară):

- `modele.py` – modelele comune (transformator, mașina asincronă cu schema în T, inclusiv varianta cu colivie dublă, formula lui Kloss, mașina sincronă);
- `probleme_cap00.py` … `probleme_cap05.py` – rezolvă problemele fiecărui capitol și **verifică fiecare rezultat pe cel puțin două căi independente** (de exemplu: bilanțul puterilor față de calculul direct, formula aproximativă față de soluția exactă, soluția analitică față de integrarea numerică). Orice nepotrivire oprește scriptul cu eroare;
- `constructie.py` – exemplele numerice din secțiunile de construcție (secțiunea în trepte a coloanei, miezul transformatorului de 400 kVA, cupru sau aluminiu, solicitarea rotoarelor rapide, magneții permanenți, frâna troliului, autoblocarea melcului, substratul modulelor IGBT, condensatoarele), verificate tot pe două căi;
- `figuri_cap00.py` … `figuri_cap05.py`, `figuri_laborator.py` – generează figurile SVG din [`figuri/`](figuri/);
- `figuri_constructie_cap01.py` … `figuri_constructie_cap04_05.py` – desenele constructive;
- `ruleaza_tot.py` – rulează tot.

```bash
cd curs-masini-electrice/scripts
pip install -r requirements.txt
python ruleaza_tot.py
```

La ultima rulare: 18 scripturi, 124 de verificări, toate trecute.

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
- $M$ – cuplu [N·m], $\Omega$ – viteză unghiulară [rad/s], $n$ – turație [rot/min]; $\Omega = 2\pi n/60$, iar $M\thinspace [\text{N·m}] = 9550\thinspace P\thinspace [\text{kW}]/n\thinspace [\text{rot/min}]$.
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
9. J. Pyrhönen, T. Jokinen, V. Hrabovcová – *Design of Rotating Electrical Machines*, ed. 2, Wiley, 2014.
10. S. V. Kulkarni, S. A. Khaparde – *Transformer Engineering: Design, Technology, and Diagnostics*, ed. 2, CRC Press, 2013 (ISBN 978-1-4398-5377-1).
11. I. Boldea – *Synchronous Generators* (*The Electric Generators Handbook*), ed. 2, CRC Press, 2016 (ISBN 978-1-4987-2356-5).
12. J. R. Hendershot, T. J. E. Miller – *Design of Brushless Permanent-Magnet Machines*, Motor Design Books, 2010.

Cărțile [9]–[12] sunt recomandate pentru aprofundarea aspectelor constructive și de proiectare.

**Standarde și reglementări**

- [S1] IEC 60034-1 – *Rotating electrical machines – Part 1: Rating and performance* (regimurile S1–S10, datele nominale).
- [S2] IEC 60034-30-1:2014 – *Efficiency classes of line operated AC motors (IE code)*. Ediția a 2-a (decembrie 2025) o înlocuiește și adaugă clasa IE5; valorile citate în curs sunt din ediția 2014.
- [S3] IEC 60076-1 – *Power transformers – Part 1: General*.
- [S4] IEC 60085 – *Electrical insulation – Thermal evaluation and designation* (clasele termice 130 (B), 155 (F), 180 (H) etc.).
- [S5] IEC 60529 – *Degrees of protection provided by enclosures (IP Code)*.
- [S6] Regulamentul (UE) 2019/1781 privind cerințele de proiectare ecologică pentru motoarele electrice și variatoarele de viteză (modificat prin Regulamentul (UE) 2021/341).
- [S7] Regulamentul (UE) nr. 548/2014 privind cerințele de proiectare ecologică pentru transformatoarele de putere mică, medie și mare (modificat prin Regulamentul (UE) 2019/1783).
- [S8] IEC 60034-12 – *Starting performance of single-speed three-phase cage induction motors*.
- [S9] Legea nr. 319/2006 a securității și sănătății în muncă.
- [S10] IEC 60034-2-1 – *Standard methods for determining losses and efficiency from tests*.
- [S11] EN 10106 (corespondent IEC 60404-8-4) – tablă și bandă de oțel electrotehnic cu grăunți neorientați, laminată la rece, livrată în stare finală.
- [S12] EN 10107:2022 (corespondent IEC 60404-8-7) – tablă și bandă de oțel electrotehnic cu grăunți orientați, livrată în stare finală.
- [S13] IEC 60034-8 – *Terminal markings and direction of rotation*.
- [S14] IEC 60072-1 – *Dimensions and output series for rotating electrical machines – Part 1: Frame numbers 56 to 400 and flange numbers 55 to 1080*.
- [S15] IEC 60076-2 – *Power transformers – Part 2: Temperature rise for liquid-immersed transformers* (inclusiv codurile de răcire ONAN, ONAF etc.).
- [S16] IEC 62770 – *Fluids for electrotechnical applications – Unused natural esters for transformers and similar electrical equipment*.
- [S17] IEC TS 60034-25:2022 – *AC electrical machines used in power drive systems – Application guide*.
- [S18] EN 14492-1 și EN 14492-2:2019 – *Cranes – Power driven winches and hoists* (Partea 1: trolii; Partea 2: palane).
- [S19] IEC 60034-7 – *Classification of types of construction, mounting arrangements and terminal box position (IM Code)*.
- [S20] IEC 60034-6 – *Methods of cooling (IC Code)*.

**Surse online** (pentru date constructive și valori tipice; consultate în 2026)

- [W1] Altair Flux – *Designation of magnetic steel sheets*: https://2023.help.altair.com/2023/flux/Flux/Help/english/UserGuide/English/topics/DesignationToleMagnetique.htm
- [W2] Waelzholz – fișa tehnică a tablelor conform EN 10106: https://www.waelzholz.com/fileadmin/Website-EN/Documents/Data-sheet/waelzholz-electrical-steel-strip-en10106-metric-en.pdf
- [W3] EN 10107:2022 – fișa de catalog: https://iteh.es/catalog/standards/cen/fce01aba-ad8d-4217-89af-19fa711a1c44/en-10107-2022 ; tabelul mărcilor cu grăunți orientați: https://www.e-magnetica.pl/doku.php/summary_of_grades_grain_oriented_electrical_steel
- [W4] Transformatoare cu miez amorf – teză Chalmers: https://publications.lib.chalmers.se/records/fulltext/167013.pdf ; lucrare ITB: https://gcs.itb.ac.id/proceeding-igsc/index.php/igsc/article/download/431/287/2118
- [W5] Specificație tehnică pentru transformatoare de distribuție de 315 kVA (TS Transco): https://tgtransco.com/images/data/pdfs/spec_downloads/Technical_Spec._of_315_KVA_DTRs.pdf ; note de proiectare UPES: https://dr.ddn.upes.ac.in/bitstream/123456789/2719/32/4-E-ElectricalMachineDesign_20181031055109.229_X.pdf
- [W6] Conductivitatea electrică și indicele IACS: https://audiophonics.fr/en/blog-diy-audio/68-electrical-conductivity-of-materials-and-iacs-index.html ; https://viox.com/de/conductivity-vs-resistivity-iacs/
- [W7] Esteri naturali pentru transformatoare – broșura Cargill FR3: https://www.cargill.com/doc/1432227943103/fr3r-brochure-2023.pdf ; Transformer Technology: https://transformer-technology.com/article-hub/a-tale-of-two-esters-why-the-natural-one-is-the-better-dielectric-fluid/
- [W8] Codurile de răcire ale transformatoarelor: https://www.gigaenergy.com/blog/transformer-cooling-methods
- [W9] Gabaritele IEC: https://inverterdrive.com/help-and-guidance/motor-frame-vs-shaft ; afișul ABB al dimensiunilor IEC: https://library.e.abb.com/public/03f0a0cfc65f46dfa71209e0120ffbf9/IEC%20Poster_24x36.pdf ; tabel de cote (neoficial): https://www.scribd.com/document/751342661/Frame-Size-to-Terminal-Size
- [W10] Marathon Electric – fișa motorului 6RN160L04E34U461081 (15 kW, 4 poli, IE3, 160L): https://media.marathonelectric.com/images/d120001/medias/docus/573/Article_6RN160L04E34U461081_DataPack_9.pdf
- [W11] Copper Development Association – colivia rotorică: https://www.copper.org/environment/sustainable-energy/electric-motors/education/motor-rotor/pdf/Squirrel_Cage.pdf ; *Analysis and Reduction of Parasitic Effects in Induction Motors With Die-Cast Rotors* (KTH): https://katalog.lib.cas.cz/KNAV/EdsRecord/edsndl,edsndl.UPSALLA1.oai.DiVA.org.kth.119603
- [W12] Întrefierul motoarelor asincrone (valori orientative): https://www.xindamotor.com/knowledge/air-gap-size-of-asynchronous-motor-stator-and-rotor
- [W13] Power Engineering – *Retaining ring replacement can prevent catastrophic generator failure*: https://www.power-eng.com/operations-maintenance/retaining-ring-replacement-can-prevent-catastrophic-generator-failure/ ; brevetul US 5 174 011: https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5174011
- [W14] Oțeluri pentru rotoare de turbogeneratoare (26NiCrMoV14-5, 18Mn18Cr): https://gruppofrattura.it/ocs/index.php/gigf/YSESM2010/paper/download/893/831
- [W15] IEEE – *Turbogenerators*: https://technav.ieee.org/topic/turbogenerators/ ; ABB – turbogeneratoare răcite cu aer: https://library.e.abb.com/public/0440b8d51c43f92ac1256ddd00347011/20-28m499.pdf
- [W16] Comparația materialelor magnetice: https://radialmagnet.com/magnet-material-comparison/ ; Arnold Magnetics – coeficienți de temperatură: https://www.arnoldmagnetics.com/wp-content/uploads/2017/10/TN_0303_rev_150715.pdf ; Goudsmit – mărci de ferită: https://www.goudsmitmagnetics.com/uploads/pdf/ferrite_grades_available_at_goudsmit_20250822_4120.pdf
- [W17] OSHA 29 CFR 1910.179(f)(2) – frânele de menținere ale mecanismelor de ridicare: https://osha.gov/laws-regs/interlinking/standards/1910.179/all ; textul echivalent din California (Title 8, § 4898): https://dir.ca.gov/title8/4898.html
- [W18] Frâne electromagnetice cu arcuri – Mayr: https://www.mayr.com/en/products/safety-brakes~48215 ; KEB: https://www.keb-automation.com/technology/brakes-clutches/operating-principle/safety-brakes
- [W19] SEW-EURODRIVE – catalog de reductoare (randamente, autoblocare): https://download.sew-eurodrive.com/download/pdf/16840011_G05.pdf ; Martin Sprocket – angrenaje melcate: https://martinsprocket.com/docs//catalogs/power%20transmission/4_gear%20catalog/worm-worm-gears.pdf
- [W20] Semikron Danfoss – construcția modulelor de putere: https://www.semikron-danfoss.com/innovation-technology/packaging-technology.html ; Ferrotec – substraturi DBC: https://www.ferrotec.com/products-technologies/power-electronic-substrates/ ; Vincotech – materiale pentru substraturi: https://www.vincotech.com/tech-insights/dcb-substrate-materials/ ; gelul siliconic: https://jps.usm.my/wp-content/uploads/2020/11/JPS-313_Art1-1-15.pdf
- [W21] Mecanisme de defectare a modulelor IGBT – Fraunhofer: https://publica.fraunhofer.de/handle/publica/384285 ; oboseala lipiturii: https://koreascience.kr/article/JAKO201628740956649.page
- [W22] Würth Elektronik SN008 – durata de viață a condensatoarelor electrolitice: https://www.we-online.com/components/media/o173043v410%20SN008a%20EN.pdf ; Rohm – regula celor 10 °C: https://micro.rohm.com/en/techweb/knowledge/acdc/acdc_sr/acdc_sr01/3177
- [W23] Manualele convertoarelor Yaskawa F7 și J1000 (durata de viață a ventilatoarelor și condensatoarelor): https://www.manualslib.com/manual/1343226/Yaskawa-F7.html?page=161 ; https://www.manualslib.com/manual/1188409/Yaskawa-J1000.html?page=159
- [W24] ABB – *Technical guide No. 5: Bearing currents in modern AC drive systems* și broșura *Bearing currents options* (9AKK107336): https://library.e.abb.com/public/619767be6f9340009060c208fe3c2d45/Bearing%20currents%20options-9AKK107336-EN-06-2018.pdf ; SKF INSOCOAT: https://www.engineeringnews.co.za/article/skf-delivers-higher-performance-across-its-insocoat-bearings-range-2017-05-12
- [W25] Rulmentul SKF 6309-2Z/C3 (fișă de distribuitor): https://uk.rs-online.com/web/p/ball-bearings/6671125

Sursele online au fost folosite pentru valori tipice și pentru confirmarea datelor; unde au dat valori diferite, cursul indică intervale sau trimite la fișa producătorului.
