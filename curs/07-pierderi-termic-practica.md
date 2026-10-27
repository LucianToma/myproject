# Modulul 7 — Pierderi, calcul termic și aspecte practice

**Obiective.** La finalul modulului vei putea:

- face bilanțul de pierderi al unui convertor și estima randamentul;
- calcula temperatura joncțiunii și alege un radiator;
- recunoaște efectele elementelor parazite (supratensiuni, EMI) și regulile de
  bază pentru cablaj, comandă și protecție.

---

## 7.1 Bilanțul de pierderi: exemplu complet

Convertor buck: $V_{in}$ = 48 V, $V_o$ = 12 V, $I_o$ = 10 A ($P_o$ = 120 W),
$f_s$ = 100 kHz, deci $D$ = 0,25. Alegem $\Delta i_L$ = 3 A (30 %):
$L = V_o(1-D)/(f_s\Delta i_L)$ = 30 µH.

Date presupuse pentru componente (valori ilustrative, de ordinul celor din
cataloage):

| Parametru | Valoare |
|---|---|
| MOSFET: $R_{DS(on)}$ (la temperatura de lucru) | 10 mΩ |
| MOSFET: $t_{ri}$, $t_{fv}$ / $t_{rv}$, $t_{fi}$ | 20, 30 / 30, 20 ns |
| MOSFET: $Q_g$ la $V_{GS}$ = 10 V | 50 nC |
| diodă: $V_{F0}$, $r_D$ | 0,7 V, 10 mΩ |

**Curenți** (Modulul 2):
$I_{T,rms}^2 = D\,(I_o^2 + \Delta i_L^2/12)$ = 25,19 A²,
$I_{D,rms}^2 = (1-D)(I_o^2 + \Delta i_L^2/12)$ = 75,56 A²,
$I_{D,med} = (1-D)I_o$ = 7,5 A.
Simularea convertorului (`v07_pierderi.py`) confirmă aceste valori cu eroare
≤ 1,2·10⁻⁵.

**Pierderi:**

| Componentă | Formula | Valoare |
|---|---|---|
| conducție tranzistor | $R_{DS(on)} I_{T,rms}^2$ | 0,252 W |
| comutație tranzistor | $\tfrac12 V_{in} f_s[(I_o - \tfrac{\Delta i_L}{2})(t_{ri}+t_{fv}) + (I_o + \tfrac{\Delta i_L}{2})(t_{rv}+t_{fi})]$ | 2,400 W |
| diodă | $V_{F0} I_{D,med} + r_D I_{D,rms}^2$ | 6,006 W |
| comandă grilă | $Q_g V_{GS} f_s$ | 0,050 W |
| **total** | | **8,71 W → $\eta$ = 93,2 %** |

Observații:

- La pornire tranzistorul comută **curentul minim** (valea, 8,5 A), iar la
  blocare **curentul maxim** (vârful, 11,5 A).
- **Dioda domină**: conduce 75 % din timp, cu o cădere de 0,7 V. Cu
  **redresare sincronă** (al doilea MOSFET de 10 mΩ în locul diodei), pierderea
  ei devine $R_{DS(on)} I_{D,rms}^2$ = 0,756 W. Totalul scade la 3,51 W
  ($\eta$ = 97,2 %; am adăugat și comanda celui de-al doilea MOSFET și am
  neglijat conducția prin dioda intrinsecă pe durata timpului mort).
- **Comutația domină pierderile tranzistorului** (2,4 W față de 0,25 W).
  Pierderile de comutație cresc proporțional cu $f_s$, în timp ce $L$ și $C$
  scad cu $1/f_s$. Alegerea frecvenței este un compromis între randament și
  dimensiuni.
- Lipsesc din bilanț (pentru simplitate): pierderile în bobină (cupru + miez),
  ESR-ul condensatoarelor, recuperarea inversă a diodei, $E_{oss}$ și
  pierderile pe trasee. Un bilanț real le include.

## 7.2 Calculul termic

Căldura trece de la joncțiune la mediul ambiant printr-un lanț de **rezistențe
termice** (K/W), analog unui circuit electric: puterea joacă rolul curentului,
iar temperatura pe cel al tensiunii.

```
  P ──► (Tj) ──[R_th,jc]── (Tc) ──[R_th,cs]── (Ts) ──[R_th,sa]── (Ta)
        joncțiune      capsulă     pastă/pad     radiator      ambiant
```

$$T_j = T_a + P\,(R_{th,jc} + R_{th,cs} + R_{th,sa}).$$

**Exemplu.** MOSFET-ul de mai sus disipă $P$ = 0,252 + 2,400 = 2,652 W.
Cu $R_{th,jc}$ = 0,8 K/W, $R_{th,cs}$ = 0,5 K/W, $R_{th,sa}$ = 10 K/W și
$T_a$ = 40 °C:

$$T_j = 40 + 2{,}652 \cdot 11{,}3 \approx 70{,}0\ °\text{C}.$$

**Regim tranzitoriu.** Fiecare nod are și o **capacitate termică** (J/K).
După o treaptă de putere, temperatura crește exponențial (constantele de timp
merg de la milisecunde, pentru cip, la minute, pentru radiator) și abia apoi
atinge valoarea de mai sus. Pentru impulsuri scurte se folosește **impedanța
termică tranzitorie** $Z_{th}(t)$ din catalog.

> **Verificare.** `v07_pierderi.py` integrează în timp (Euler implicit) o rețea
> termică cu trei capacități și obține în regim staționar exact
> $T_a + P\sum R_{th}$ (69,966 °C, eroare 2·10⁻¹¹), precum și temperatura
> radiatorului $T_a + P R_{th,sa}$.

**Cuplajul electro-termic.** $R_{DS(on)}$ crește cu temperatura, deci
pierderile cresc și ele cu temperatura. Calculul corect este iterativ: estimezi
$T_j$, iei $R_{DS(on)}(T_j)$ din catalog, recalculezi $P$ și repeți până la
convergență. De aceea, în exemplu, $R_{DS(on)}$ a fost dat „la temperatura de
lucru”.

**Regula de proiectare:** $T_j$ calculată trebuie să rămână cu o marjă sub
$T_{j,max}$ din catalog (tipic 150–175 °C la Si). Marja se alege pentru
fiabilitate: durata de viață scade puternic cu temperatura.

## 7.3 Elemente parazite și cablaj (layout)

Orice conductor are inductanță. Pentru un fir drept de lungime $l$ și rază $r$
(la frecvență mare) $L \approx \frac{\mu_0 l}{2\pi}\left[\ln\frac{2l}{r} - 1\right]$,
adică aproximativ 7 nH pentru 10 mm de fir cu diametrul de 0,5 mm (de ordinul
1 nH/mm). Deasupra unui plan de masă apropiat, inductanța este mult mai mică.
La comutații rapide, $v = L\,di/dt$ produce supratensiuni:

$$L_p = 10\ \text{nH}, \quad \frac{di}{dt} = \frac{10\ \text{A}}{10\ \text{ns}} = 10^9\ \text{A/s}
\;\Rightarrow\; v = 10\ \text{V}$$

suprapuși peste tensiunea de blocare, plus oscilații cu capacitățile
parazite.

Reguli:

- **Bucla de comutație** (*hot loop*: condensatorul de intrare → tranzistorul
  de sus → tranzistorul/dioda de jos → înapoi) trebuie să aibă **arie
  minimă**. Condensatoarele ceramice de decuplare se pun cât mai aproape.
- Bucla de comandă a grilei trebuie să fie separată de bucla de putere. Se
  folosește conexiunea **Kelvin** a sursei, dacă există.
- Nodul de comutație (cu $dv/dt$ mare) trebuie să aibă arie mică, ca să
  cupleze capacitiv cât mai puțin zgomot.
- Planurile de masă trebuie să fie continue, cu rută de întoarcere scurtă
  pentru curenții mari.

**Snubber-e** (RC, RCD) limitează supratensiunile sau $dv/dt$, cu prețul unor
pierderi suplimentare. **Comutația moale** (ZVS/ZCS, în convertoare rezonante)
evită suprapunerea tensiune-curent și reduce pierderile de comutație.

## 7.4 Compatibilitate electromagnetică (EMI)

Fronturile rapide de tensiune și curent sunt surse de perturbații:

- **conduse** (pe cablurile de alimentare), atenuate cu filtre EMI de rețea
  (bobine de mod comun, condensatoare X/Y);
- **radiate** (prin bucle și cabluri care se comportă ca antene).

Echipamentele trebuie să respecte limitele din standardele de compatibilitate
electromagnetică aplicabile (de exemplu familia CISPR / EN 55xxx). Încetinirea
controlată a comutației (prin $R_g$) reduce EMI, dar crește pierderile: încă un
compromis.

## 7.5 Comandă și reglare (introducere)

- Convertoarele lucrează aproape întotdeauna **în buclă închisă**. Un
  regulator compară $V_o$ cu referința și ajustează $D$, ca să compenseze
  variațiile lui $V_{in}$ și ale sarcinii (Modulul 5 a arătat că în DCM
  $V_o$ depinde de sarcină).
- **Controlul în tensiune** (*voltage mode*): o singură buclă, cu PWM obținut
  prin compararea erorii amplificate cu o rampă.
- **Controlul în curent** (*current mode*): o buclă internă de curent prin
  bobină și una externă de tensiune. Are protecție inerentă la supracurent și
  o dinamică mai simplă.
- Proiectarea regulatorului se face pe un **model mediat de semnal mic**
  (vezi Erickson & Maksimović [B2]), un subiect pentru un curs următor.

## 7.6 Protecții

- **Supracurent**: limitare ciclu cu ciclu (în controlul în curent) sau
  oprire. La IGBT, detecția **desaturării** ($v_{CE}$ crește anormal în
  scurtcircuit) oprește dispozitivul în câteva µs.
- **Supratensiune** (de exemplu la intrare: varistoare, diode TVS).
- **Supratemperatură** (senzor NTC pe radiator sau în modul).
- **Subtensiune** la driver (UVLO): un MOSFET comandat cu tensiune de grilă
  prea mică intră în regiunea liniară și se supraîncălzește.

## 7.7 Siguranță

Electronica de putere lucrează cu tensiuni și energii **periculoase**:

- condensatoarele de c.c. pot rămâne încărcate mult după deconectare.
  Descarcă-le controlat și măsoară tensiunea înainte de a atinge circuitul;
- la circuitele conectate la rețea, sonda osciloscopului **nu** se conectează
  direct la noduri arbitrare (masa osciloscopului este legată la pământ). Se
  folosesc sonde diferențiale sau un transformator de separare, conform
  procedurilor laboratorului;
- testele de putere se fac cu limitare de curent și cu protecție la
  supracurent.

## Întrebări de autoevaluare

1. De ce, într-un buck cu $V_o$ mic, dioda domină pierderile?
2. Dacă dublezi $f_s$ în exemplul din 7.1, ce pierderi se dublează? Care rămân
   (aproximativ) neschimbate?
3. Un tranzistor disipă 5 W, $R_{th,jc}$ = 1 K/W, $R_{th,cs}$ = 0,5 K/W,
   $T_a$ = 45 °C. Ce $R_{th,sa}$ maxim permite $T_j \le$ 125 °C?
   *(14,5 K/W.)*
4. Ce supratensiune produce un $di/dt$ de 2 A/ns pe 5 nH? *(10 V.)*
5. De ce are importanță aria buclei de comutație?

---

[← Modulul 6](06-invertoare.md) · [Cuprins](../README.md) · [Modulul 8 →](08-exercitii.md)
