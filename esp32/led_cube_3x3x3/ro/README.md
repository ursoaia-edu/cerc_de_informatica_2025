# Cub LED 3x3x3 pe ESP32 (MicroPython)

Versiune simplificată a proiectului [8x8x8 LED Cube](https://www.instructables.com/8x8x8-Arduino-LED-Cube/),
adaptată pentru ESP32 cu MicroPython.

---

## Principiul de funcționare

Cubul folosește **multiplexare pe straturi** (layer multiplexing):

- **9 coloane** (anoduri LED) sunt conectate la pinii GPIO ai ESP32 prin rezistoare de 220 Ω.
- **3 straturi** (catoduri LED) sunt controlate prin tranzistoare NPN (2N2222 / BC547).
- ESP32 comută rapid straturile (POV — persistence of vision), creând iluzia
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
| ESP32 DevKit              | 1          |                                |
| LED 5mm (orice culoare)   | 27         | Se pot folosi 3 culori × 9 buc |
| Rezistor 220 Ω            | 9          | Limitare curent (coloane)      |
| Rezistor 1 kΩ             | 3          | Pentru baza tranzistoarelor (straturi) |
| Tranzistor NPN 2N2222     | 3          | Sau BC547/BC337                |
| Placă de test (breadboard)| 1          | 830 puncte                     |
| Fire (jumper wires)       | ~20        | M-M                           |

---

## Schema de conectare

```
                        ESP32 DevKit
                     ┌──────────────────┐
                     │                  │
    Coloane          │  GPIO2  ──[220Ω]── C0 (anod LED)
    (anoduri)        │  GPIO4  ──[220Ω]── C1
                     │  GPIO5  ──[220Ω]── C2
                     │  GPIO18 ──[220Ω]── C3
                     │  GPIO19 ──[220Ω]── C4
                     │  GPIO21 ──[220Ω]── C5
                     │  GPIO22 ──[220Ω]── C6
                     │  GPIO23 ──[220Ω]── C7
                     │  GPIO25 ──[220Ω]── C8
                     │                  │
    Straturi         │  GPIO26 ──[1kΩ]──┐│
    (catoduri         │  GPIO27 ──[1kΩ]──┤│
     prin             │  GPIO32 ──[1kΩ]──┤│
     tranzistoare)   │                │ │
                     │  GND ──────────┘ │
                     └──────────────────┘

    Tranzistor 2N2222 (pentru fiecare strat):

        ESP32 GPIO ──[1kΩ]──► Base
                              Collector ◄── Catodurile stratului (toate 9 LED)
                              Emitter ──► GND
```

### Conectarea pinilor

| ESP32 Pin  | Destinație            |
|------------|-----------------------|
| GPIO 2     | Coloana 0 (anod)      |
| GPIO 4     | Coloana 1             |
| GPIO 5     | Coloana 2             |
| GPIO 18    | Coloana 3             |
| GPIO 19    | Coloana 4             |
| GPIO 21    | Coloana 5             |
| GPIO 22    | Coloana 6             |
| GPIO 23    | Coloana 7             |
| GPIO 25    | Coloana 8             |
| GPIO 26    | Stratul 0 (inferior)  |
| GPIO 27    | Stratul 1 (mijlociu)  |
| GPIO 32    | Stratul 2 (superior)  |
| GND        | Emitoarele tranzistoarelor |

> **Notă:** Pinii GPIO au fost aleși pentru a evita pinii de boot-strapping
> (GPIO 0, 12, 15) și pinii doar-intrare (GPIO 34, 35, 36, 39).

---

## Asamblarea cubului

### 1. Pregătirea LED-urilor
- Verifică fiecare LED înainte de lipire (cu rezistor de 220 Ω de la 3.3V).
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

### 5. Conectarea la ESP32
- 9 anoduri (coloane) → prin rezistoare de 220 Ω → GPIO 2,4,5,18,19,21,22,23,25.
- 3 straturi catodice → prin tranzistoare 2N2222 → GPIO 26,27,32.

---

## Încărcarea codului

1. Flashuiește firmware-ul MicroPython pe ESP32 (dacă nu a fost deja făcut).
2. Copiază `main.py` pe ESP32 folosind Thonny, ampy sau mpremote.
3. Codul pornește automat la alimentare.

---

## Animațiile din cod

| Animație           | Descriere                                          |
|--------------------|----------------------------------------------------|
| `all_on_off`       | Pornire/oprire întregul cub                        |
| `layer_wipe`       | Aprinderea secvențială a straturilor de jos în sus  |
| `column_wipe`      | Aprinderea secvențială a coloanelor                 |
| `rain`             | Efect de ploaie — picături aleatoare cad în jos     |
| `spiral`           | Spirală pe perimetrul cubului                       |
| `random_blink`     | Clipire aleatoare a LED-urilor individuale           |
| `plane_bounce`     | Stratul „sare" în sus și în jos                     |
| `diagonal_wipe`    | Undă diagonală                                      |
| `edges_only`       | Doar muchiile cubului                               |
| `fireworks`        | Simulare simplă de artificii (inspirat din original)|

---

## Comparație: Arduino vs ESP32

| Parametru            | Arduino Uno          | ESP32                |
|----------------------|----------------------|----------------------|
| Limbaj               | C++ (.ino)           | MicroPython (.py)    |
| Tensiune logică      | 5V                   | 3.3V                 |
| Pini GPIO            | 14 digitali          | 34 GPIO              |
| Instrument încărcare | Arduino IDE          | Thonny / ampy        |
| Frecvența ceasului   | 16 MHz               | 240 MHz              |

---

## Linkuri

- [Proiectul original 8x8x8](https://www.instructables.com/8x8x8-Arduino-LED-Cube/)
- [Arduino Forum: Simple 3x3x3 cube](https://forum.arduino.cc/t/very-simple-3x3x3-cube-sketch/922655)
- [Documentație MicroPython ESP32](https://docs.micropython.org/en/latest/esp32/quickref.html)
