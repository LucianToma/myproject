# Bibliografie

Referințele sunt citate în text cu indicativul [Bn].

## Manuale de bază

- **[B1]** N. Mohan, T. M. Undeland, W. P. Robbins, *Power Electronics:
  Converters, Applications, and Design*, ed. 3, Wiley, 2003. Manual clasic,
  acoperă toate modulele acestui curs (redresoare, DC-DC, invertoare,
  dispozitive, aspecte practice).
- **[B2]** R. W. Erickson, D. Maksimović, *Fundamentals of Power Electronics*,
  ed. 3, Springer, 2020. Referința standard pentru convertoare DC-DC: bilanțul
  volt-secundă, aproximarea ondulației mici, DCM, modelare și control.
- **[B3]** M. H. Rashid, *Power Electronics: Devices, Circuits, and
  Applications*, ed. 4, Pearson, 2014.
- **[B4]** D. G. Holmes, T. A. Lipo, *Pulse Width Modulation for Power
  Converters: Principles and Practice*, IEEE Press / Wiley, 2003. Analiza
  Fourier dublă a PWM (expresiile cu funcții Bessel din Modulul 6).
- **[B5]** B. J. Baliga, *Fundamentals of Power Semiconductor Devices*, ed. 2,
  Springer, 2019. Rezistența specifică ideală a zonei de drift și dependența de
  $V_B$ și $E_c$ (Modulul 3).
- **[B6]** J. G. Kassakian, D. J. Perreault, G. C. Verghese, M. F. Schlecht,
  *Principles of Power Electronics*, ed. 2, Cambridge University Press, 2023.

## Standarde și note de aplicație

- **[B7]** IEC 61000-3-2, *Electromagnetic compatibility (EMC) — Part 3-2:
  Limits — Limits for harmonic current emissions (equipment input current
  ≤ 16 A per phase)*.
- **[B8]** L. Balogh, *Design and Application Guide for High Speed MOSFET Gate
  Drive Circuits*, Texas Instruments, SLUP169. Comanda pe grilă, mecanismul
  comutației și limitele modelelor simple de pierderi.

## Surse pentru datele despre dispozitive (Modulul 3)

Cifrele de mai jos au fost consultate la redactarea cursului (octombrie 2026).
Produsele evoluează, așa că, pentru un proiect, verifică întotdeauna catalogul
actual al producătorului.

- **[B9]** ABB, *New Low Loss Phase Control Thyristors for Medium Current UHVDC
  Transmission*, PCIM Europe 2018 — tiristoare de clasa 8,5 kV pentru HVDC.
  <https://www.vde-verlag.de/proceedings-en/564646089.html>
- **[B10]** Infineon, module IGBT IHV 6500 V.
  <https://www.infineon.com/cms/en/product/promopages/6500v/>
- **[B11]** Dynex Semiconductor, gama de IGBT de 6,5 kV.
  <https://dynexsemi.com/Resources/News/High-voltage-65kV-IGBT-range>
- **[B12]** Tabel comparativ al proprietăților Si, SiC, GaN (lățimea benzii
  interzise, câmp critic, conductivitate termică).
  <https://www.halbleiter.org/en/compound-semiconductors/fundamentals-material-system/>
- **[B13]** *Nanoscale Research Letters*, Tabelul 1: comparația proprietăților
  fizice ale Si, GaN, SiC și β-Ga₂O₃ (valori diferite pentru 4H-SiC: 2,5 MV/cm,
  2,7 W/(cm·K), ceea ce ilustrează variația dintre surse).
  <https://nanoscalereslett.springeropen.com/articles/10.1186/s11671-018-2712-1/tables/1>
- **[B14]** Măsurători ale conductivității termice a SiC și GaN între 150 și
  850 K, *Physical Review Materials* 3, 014601 (2019).
  <https://link.aps.org/accepted/10.1103/PhysRevMaterials.3.014601>
- **[B15]** Mitsubishi Electric, *3.3 kV All-SiC Power Module for Traction
  System Use*, PCIM Europe 2017.
  <https://www.vde-verlag.de/proceedings-en/564424004.html>
- **[B16]** *Commercial GaN-Based Power Electronic Systems: A Review*
  (Texas Tech University). Pentru segmentul de înaltă tensiune, tranzistoarele
  GaN laterale comerciale erau tipic de ~650 V, sub 1 kV, la data publicării
  recenziei. Între timp au apărut și dispozitive integrate de tensiune mai mare
  [B20].
  <https://scholars.ttu.edu/en/publications/commercial-gan-based-power-electronic-systems-a-review>
- **[B17]** Toshiba, FAQ despre diode SiC Schottky (câmp critic 4H-SiC
  ≈ 2,8 MV/cm).
  <https://toshiba.semicon-storage.com/eu/semiconductor/knowledge/faq/diode_sic-sbd/sic-sbd001.html>
- **[B18]** GeneSiC / Navitas, diode SiC Schottky MPS de 3300 V (de exemplu
  GC50MPS33H, 3,3 kV / 50 A, TO-247-2).
  <https://www.mouser.fr/genesic-3300v-5a-sic-schottky-diode>
- **[B19]** EPC (Efficient Power Conversion): tranzistoare și circuite integrate
  eGaN de 15–350 V; pagina de aplicații LiDAR (dispozitive recomandate de
  15–200 V).
  <https://epc-co.com/epc/Applications/LiDAR.aspx>
- **[B20]** Power Integrations, *Power Integrations Launches 1700 V GaN Switcher
  IC*, comunicat din 4 noiembrie 2024 (familia InnoMux-2). Anterior, pe 30
  octombrie 2023, fusese lansată familia InnoSwitch3-EP cu comutator GaN de
  1250 V.
  <https://www.powersystemsdesign.com/articles/power-integrations-launches-1700-v-gan-switcher-ic-setting-new-benchmark-for-gallium-nitride-technology/6/22227>
  <https://semiconductor-today.com/news_items/2023/oct/powerintegrations-311023.shtml>

---

[← Modulul 8](08-exercitii.md) · [Cuprins](../README.md)
