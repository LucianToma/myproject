# Modulul 1 — Introducere în electronica de putere

**Obiective.** La finalul modulului vei putea:

- spune ce face electronica de putere și de ce lucrează în **comutație**;
- explica, cu un calcul, de ce un regulator liniar are randament mic;
- clasifica convertoarele după tipul conversiei (AC-DC, DC-DC, DC-AC, AC-AC);
- descrie blocurile unui sistem de conversie.

---

## 1.1 Ce este electronica de putere

Electronica de putere se ocupă de **conversia și controlul energiei electrice**
cu ajutorul dispozitivelor semiconductoare folosite drept **comutatoare**.
Puterile acoperite merg de la câțiva wați (încărcătorul unui telefon) până la
gigawați (transportul de energie în curent continuu de înaltă tensiune, HVDC).

Exemple de conversii:

| Conversie | Denumire uzuală | Exemple de aplicații |
|---|---|---|
| AC → DC | redresor | alimentatoare, încărcătoare, intrarea oricărui echipament conectat la rețea |
| DC → DC | convertor DC-DC (chopper) | surse în comutație, alimentarea procesoarelor, sisteme auto 48 V/12 V |
| DC → AC | invertor | acționarea motoarelor, invertoare fotovoltaice, UPS |
| AC → AC | variator de tensiune alternativă, convertor de frecvență | pornire lină a motoarelor, convertoare AC-DC-AC |

## 1.2 De ce în comutație? Un calcul simplu

Puterea disipată într-un element este $p = v \cdot i$. Un **comutator ideal**
are doar două stări:

- **închis (ON):** $v = 0$, deci $p = 0 \cdot i = 0$;
- **deschis (OFF):** $i = 0$, deci $p = v \cdot 0 = 0$.

În ambele stări pierderile sunt zero. Un tranzistor real se apropie de acest
ideal: în conducție are o cădere mică de tensiune, iar în blocare un curent de
scurgere neglijabil. Pierderile apar mai ales **în timpul tranzițiilor** dintre
stări (Modulul 3 și Modulul 7).

### Comparație: regulator liniar vs. convertor în comutație

Un **regulator liniar** coboară tensiunea ținând tranzistorul în regiunea
activă: tranzistorul „preia” diferența de tensiune $V_{in} - V_o$ la tot
curentul de sarcină $I_o$.

Exemplu: $V_{in} = 12$ V, $V_o = 5$ V, $I_o = 1$ A.

$$P_{pierderi} = (V_{in} - V_o)\, I_o = (12 - 5) \cdot 1 = 7\ \text{W}$$

$$\eta = \frac{V_o I_o}{V_{in} I_o} = \frac{V_o}{V_{in}} = \frac{5}{12} \approx 41{,}7\ \%$$

(curentul de repaus al regulatorului a fost neglijat; el ar scădea și mai mult
randamentul).

Un convertor în comutație cu randament $\eta = 90\ \%$ livrează aceiași 5 W cu
pierderi

$$P_{pierderi} = P_o\left(\frac{1}{\eta} - 1\right) = 5\left(\frac{1}{0{,}9} - 1\right) \approx 0{,}56\ \text{W},$$

adică de aproximativ **12,6 ori mai puțin** decât regulatorul liniar. Diferența
contează pentru baterie, dar și pentru radiator: 7 W disipați într-o capsulă
mică cer un radiator considerabil (calculul termic este în Modulul 7).

> **Verificare.** `verificari/v07_pierderi.py` recalculează aceste valori și
> confirmă, prin simularea unui convertor buck cu comutatoare ideale, că
> randamentul acestuia este 100 % (puterea de intrare = puterea de ieșire,
> eroare relativă ~4·10⁻¹¹). Deci pierderile reale provin numai din
> imperfecțiunile componentelor, nu din principiul de funcționare.

## 1.3 Cum se obține o tensiune reglabilă cu un comutator

Dacă un comutator conectează periodic o sarcină la $V_{in}$ pentru o fracțiune
$D$ din perioada $T_s$, tensiunea rezultată este un tren de impulsuri cu
valoarea medie

$$\langle v \rangle = \frac{1}{T_s}\int_0^{T_s} v(t)\,dt = \frac{1}{T_s}\, V_{in}\, D T_s = D\, V_{in}.$$

- $D$ = **factorul de umplere** (*duty cycle*), $0 \le D \le 1$;
- $f_s = 1/T_s$ = **frecvența de comutație** (tipic zeci de kHz – MHz în
  convertoarele DC-DC moderne).

Un **filtru trece-jos LC** păstrează valoarea medie și atenuează componentele
de frecvență $f_s$ și multiplii ei. Așa funcționează convertorul **buck**
(Modulul 5). Modificând $D$ se reglează tensiunea, fără ca vreun element să
„ardă” diferența de tensiune. Tehnica se numește **modulație în lățime a
impulsurilor** (PWM — *pulse width modulation*).

## 1.4 Elementele de circuit ale electronicii de putere

În calea puterii se folosesc aproape exclusiv elemente care, ideal, **nu
disipă** energie:

| Element | Rol | Ideal disipă? |
|---|---|---|
| comutator semiconductor | dirijează fluxul de energie | nu (v = 0 sau i = 0) |
| bobină | stochează energie ($\tfrac12 L i^2$), netezește curentul | nu |
| condensator | stochează energie ($\tfrac12 C v^2$), netezește tensiunea | nu |
| transformator | adaptează tensiunea, asigură izolarea galvanică | nu |
| rezistor | — (evitat în calea puterii) | **da** |

Rezistoarele apar doar în circuitele de comandă, măsură sau protecție, unde
puterea este mică.

## 1.5 Structura unui sistem de conversie

```
            ┌──────────────────────────────────────────────┐
 sursă ───► │ filtru ─► ETAJ DE PUTERE ─► filtru de ieșire │ ───► sarcină
            └──────────────▲───────────────────────────────┘
                           │ semnale de comandă
                    ┌──────┴──────┐        ┌─────────────┐
                    │   driver    │ ◄───── │  control    │ ◄── referință
                    └─────────────┘        │ (PWM, buclă)│
                                           └──────▲──────┘
                                                  │ măsurători (V, I, T)
                                           ┌──────┴──────┐
                                           │  senzori +  │
                                           │  protecții  │
                                           └─────────────┘
```

- **Etajul de putere**: comutatoarele, diodele și elementele reactive.
- **Driverul**: adaptează semnalele logice la tensiunile/curenții ceruți de
  grilele tranzistoarelor (adesea cu izolare galvanică).
- **Controlul**: generează PWM-ul și închide bucla de reglare (de exemplu
  menține $V_o$ constantă când variază $V_{in}$ sau sarcina).
- **Senzorii și protecțiile**: supracurent, supratensiune, supratemperatură.

## 1.6 Ipotezele acestui curs

Ca să putem deriva relații simple:

1. Comutatoarele, diodele, bobinele și condensatoarele sunt **ideale**
   (excepție: Modulul 3 și Modulul 7, unde modelăm pierderile).
2. Circuitele lucrează în **regim permanent periodic**: toate mărimile se
   repetă identic de la o perioadă la alta.
3. Acolo unde o formulă este **aproximativă** (de exemplu „ondulație mică”),
   spunem explicit și arătăm cât de mare este eroarea.

## Întrebări de autoevaluare

1. De ce un comutator ideal nu disipă putere în niciuna dintre stări?
2. Un regulator liniar coboară 24 V la 3,3 V la 0,5 A. Cât disipă și ce
   randament are? *(Răspuns: 10,35 W; 13,75 %.)*
3. Ce mărime trebuie modificată pentru a regla tensiunea medie a unui tren de
   impulsuri de amplitudine constantă?
4. De ce se evită rezistoarele în calea puterii?

---

[Cuprins](../README.md) · [Modulul 2 →](02-fundamente.md)
