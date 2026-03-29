# Cub LED 3x3x3 pe Arduino Uno

Versiune simplificată a proiectului [8x8x8 LED Cube](https://www.instructables.com/8x8x8-Arduino-LED-Cube/),
adaptată pentru începători.

---

## Principiul de funcționare

Cubul folosește **multiplexare pe straturi** (layer multiplexing):

- **9 coloane** (anoduri LED) sunt conectate la pinii digitali ai Arduino prin rezistoare de 220 Ω.
- **3 straturi** (catoduri LED) sunt controlate prin tranzistoare NPN (2N2222 / BC547).
- Arduino comută rapid straturile (POV — persistence of vision), creând iluzia
  luminării simultane a tuturor celor 27 de LED-uri.

```
     Vedere de sus (numerotarea coloanelor):

         C0   C1   C2
         C3   C4   C5
         C6   C7   C8

     Straturi (vedere laterală):
         Layer 2 (superior)
         Layer 1 (mijlociu)
         Layer 0 (inferior)
```

---

## Lista componentelor

| Componentă               | Cantitate  | Observații                     |
|---------------------------|------------|--------------------------------|
| Arduino Uno (CH340)       | 1          | Sau Nano                       |
| LED 5mm (orice culoare)   | 27         | Se pot folosi 3 culori × 9 buc |
| Rezistor 220 Ω            | 9          | Limitare curent (coloane)      |
| Rezistor 1 kΩ             | 3          | Pentru baza tranzistoarelor (straturi) |
| Tranzistor NPN 2N2222     | 3          | Sau BC547/BC337                |
| Placă de test (breadboard)| 1          | 830 puncte                     |
| Fire (jumper wires)       | ~20        | M-M                           |

> Toate componentele se găsesc în setul **LA036 Super Starter Kit for Arduino UNO**.

---

## Schema de conectare

```
                        Arduino Uno
                     ┌──────────────────┐
                     │                  │
    Coloane          │  D2  ──[220Ω]──── C0 (anod LED)
    (anoduri)        │  D3  ──[220Ω]──── C1
                     │  D4  ──[220Ω]──── C2
                     │  D5  ──[220Ω]──── C3
                     │  D6  ──[220Ω]──── C4
                     │  D7  ──[220Ω]──── C5
                     │  D8  ──[220Ω]──── C6
                     │  D9  ──[220Ω]──── C7
                     │  D10 ──[220Ω]──── C8
                     │                  │
    Straturi         │  D11 ──[1kΩ]──┐  │
    (catoduri         │  D12 ──[1kΩ]──┤  │
     prin             │  D13 ──[1kΩ]──┤  │
     tranzistoare)   │                │  │
                     │  GND ──────────┘  │
                     └──────────────────┘

    Tranzistor 2N2222 (pentru fiecare strat):

        Arduino Pin ──[1kΩ]──► Base
                               Collector ◄── Catodurile stratului (toate 9 LED)
                               Emitter ──► GND
```

### Conectarea pinilor

| Arduino Pin | Destinație            |
|-------------|-----------------------|
| D2          | Coloana 0 (anod)      |
| D3          | Coloana 1             |
| D4          | Coloana 2             |
| D5          | Coloana 3             |
| D6          | Coloana 4             |
| D7          | Coloana 5             |
| D8          | Coloana 6             |
| D9          | Coloana 7             |
| D10         | Coloana 8             |
| D11         | Stratul 0 (inferior)  |
| D12         | Stratul 1 (mijlociu)  |
| D13         | Stratul 2 (superior)  |
| GND         | Emitoarele tranzistoarelor |

---

## Asamblarea cubului

### 1. Pregătirea LED-urilor
- Verifică fiecare LED înainte de lipire (cu rezistor de 220 Ω de la 5V).
- Determină polaritatea: piciorușul lung = anod (+), scurt = catod (−).
- Îndoaie catodul (−) al fiecărui LED la 90° — acestea se vor conecta orizontal într-un strat.

### 2. Realizarea șablonului (jig)
- Desenează o grilă 3×3 pe carton/placaj cu distanța de ~20 mm între centre.
- Găurește 9 orificii cu diametrul de 5 mm.

### 3. Lipirea straturilor
- Introdu 9 LED-uri în șablon.
- Lipește toate catodurile (−) într-o rețea orizontală cu ajutorul sârmei de cupru.
- Repetă pentru toate 3 straturile. Verifică fiecare strat!

### 4. Conectarea coloanelor
- Așază stratul inferior pe placa de test.
- Lipește stratul mijlociu deasupra, conectând anodurile (+) vertical.
- Lipește stratul superior.
- Folosește distanțiere de aceeași înălțime între straturi (~20 mm).

### 5. Conectarea la Arduino
- 9 anoduri (coloane) → prin rezistoare de 220 Ω → pinii D2–D10.
- 3 straturi catodice → prin tranzistoare 2N2222 → pinii D11–D13.

---

## Încărcarea codului

1. Deschide `led_cube_3x3x3.ino` în Arduino IDE.
2. Selectează placa: **Arduino Uno**.
3. Selectează portul.
4. Apasă **Upload**.

---

## Animațiile din cod

| Animație           | Descriere                                          |
|--------------------|----------------------------------------------------|
| `allOn/allOff`     | Pornire/oprire întregul cub                        |
| `layerWipe`        | Aprinderea secvențială a straturilor de jos în sus  |
| `columnWipe`       | Aprinderea secvențială a coloanelor                 |
| `rain`             | Efect de ploaie — picături aleatoare cad în jos     |
| `spiral`           | Spirală pe perimetrul cubului                       |
| `randomBlink`      | Clipire aleatoare a LED-urilor individuale           |
| `planeBounce`      | Stratul „sare" în sus și în jos                     |
| `diagonalWipe`     | Undă diagonală                                      |
| `edgesOnly`        | Doar muchiile cubului                               |
| `fireworks`        | Simulare simplă de artificii (inspirat din original)|

---

## Comparație cu originalul 8x8x8

| Parametru            | 8x8x8 (original)      | 3x3x3 (al nostru)     |
|----------------------|------------------------|------------------------|
| Nr. LED-uri          | 512                    | 27                     |
| Pini Arduino         | 64 anoduri + 8 catoduri| 9 anoduri + 3 catoduri |
| Circuite suplimentare| Shift registers        | Nu sunt necesare!      |
| Tranzistoare         | 8                      | 3                      |
| Dificultatea lipirii | Foarte ridicată        | Simplă                 |
| Timp de asamblare    | 20+ ore                | 2–3 ore                |

---

## Linkuri

- [Proiectul original 8x8x8](https://www.instructables.com/8x8x8-Arduino-LED-Cube/)
- [Arduino Forum: Simple 3x3x3 cube](https://forum.arduino.cc/t/very-simple-3x3x3-cube-sketch/922655)
- [Instructables: 3x3x3 LED Cube Arduino-UNO](https://www.instructables.com/3x3x3-LED-Cube-Arduino-UNO/)
