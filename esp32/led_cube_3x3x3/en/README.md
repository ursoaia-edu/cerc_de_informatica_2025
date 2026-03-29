# 3x3x3 LED Cube on ESP32 (MicroPython)

A simplified version of the [8x8x8 LED Cube](https://www.instructables.com/8x8x8-Arduino-LED-Cube/) project,
adapted for ESP32 with MicroPython.

---

## How It Works

The cube uses **layer multiplexing**:

- **9 columns** (LED anodes) are connected to ESP32 GPIO pins through 220 Ω resistors.
- **3 layers** (LED cathodes) are controlled via NPN transistors (2N2222 / BC547).
- ESP32 rapidly switches layers (POV — persistence of vision), creating the illusion
  that all 27 LEDs are lit simultaneously.

```
     Top view (column numbering):

         C0   C1   C2
         C3   C4   C5
         C6   C7   C8

     Layers (side view):
         Layer 2 (top)
         Layer 1 (middle)
         Layer 0 (bottom)
```

---

## Bill of Materials

| Component                | Quantity   | Notes                          |
|--------------------------|------------|--------------------------------|
| ESP32 DevKit             | 1          |                                |
| LED 5mm (any color)      | 27         | Can use 3 colors, 9 each      |
| 220 Ω resistor           | 9          | Current-limiting (columns)     |
| 1 kΩ resistor            | 3          | For transistor bases (layers)  |
| NPN transistor 2N2222    | 3          | Or BC547/BC337                 |
| Breadboard               | 1          | 830 tie-points                 |
| Jumper wires             | ~20        | M-M                           |

---

## Wiring Diagram

```
                        ESP32 DevKit
                     ┌──────────────────┐
                     │                  │
    Columns          │  GPIO2  ──[220Ω]── C0 (LED anode)
    (anodes)         │  GPIO4  ──[220Ω]── C1
                     │  GPIO5  ──[220Ω]── C2
                     │  GPIO18 ──[220Ω]── C3
                     │  GPIO19 ──[220Ω]── C4
                     │  GPIO21 ──[220Ω]── C5
                     │  GPIO22 ──[220Ω]── C6
                     │  GPIO23 ──[220Ω]── C7
                     │  GPIO25 ──[220Ω]── C8
                     │                  │
    Layers           │  GPIO26 ──[1kΩ]──┐│
    (cathodes         │  GPIO27 ──[1kΩ]──┤│
     via              │  GPIO32 ──[1kΩ]──┤│
     transistors)    │                │ │
                     │  GND ──────────┘ │
                     └──────────────────┘

    2N2222 transistor (for each layer):

        ESP32 GPIO ──[1kΩ]──► Base
                              Collector ◄── Layer cathodes (all 9 LEDs)
                              Emitter ──► GND
```

### Pin Assignment

| ESP32 Pin | Function             |
|-----------|----------------------|
| GPIO 2    | Column 0 (anode)     |
| GPIO 4    | Column 1             |
| GPIO 5    | Column 2             |
| GPIO 18   | Column 3             |
| GPIO 19   | Column 4             |
| GPIO 21   | Column 5             |
| GPIO 22   | Column 6             |
| GPIO 23   | Column 7             |
| GPIO 25   | Column 8             |
| GPIO 26   | Layer 0 (bottom)     |
| GPIO 27   | Layer 1 (middle)     |
| GPIO 32   | Layer 2 (top)        |
| GND       | Transistor emitters  |

> **Note:** GPIO pins were chosen to avoid boot-strapping pins (GPIO 0, 12, 15)
> and input-only pins (GPIO 34, 35, 36, 39).

---

## Building the Cube

### 1. Preparing the LEDs
- Test each LED before soldering (with a 220 Ω resistor from 3.3V).
- Identify polarity: long leg = anode (+), short leg = cathode (−).
- Bend the cathode (−) of each LED at 90° — they will be connected horizontally to form a layer.

### 2. Making a Jig
- Draw a 3×3 grid on cardboard or plywood with ~20 mm spacing between centers.
- Drill 9 holes with a 5 mm diameter.

### 3. Soldering the Layers
- Insert 9 LEDs into the jig.
- Solder all cathodes (−) into a horizontal grid using copper wire.
- Repeat for all 3 layers. Test each layer!

### 4. Connecting the Columns
- Place the bottom layer on the breadboard.
- Solder the middle layer on top, connecting anodes (+) vertically.
- Solder the top layer.
- Use spacers of equal height between layers (~20 mm).

### 5. Connecting to ESP32
- 9 anodes (columns) → through 220 Ω resistors → GPIO 2,4,5,18,19,21,22,23,25.
- 3 cathode layers → through 2N2222 transistors → GPIO 26,27,32.

---

## Uploading the Code

1. Flash MicroPython firmware to ESP32 (if not done already).
2. Copy `main.py` to the ESP32 using Thonny, ampy, or mpremote.
3. The code runs automatically on boot.

---

## Animations in the Code

| Animation         | Description                                        |
|-------------------|----------------------------------------------------|
| `all_on_off`      | Turn the entire cube on/off                        |
| `layer_wipe`      | Sequential layer lighting from bottom to top       |
| `column_wipe`     | Sequential column lighting                         |
| `rain`            | Rain effect — random drops fall downward            |
| `spiral`          | Spiral along the cube perimeter                    |
| `random_blink`    | Random blinking of individual LEDs                 |
| `plane_bounce`    | Layer "bounces" up and down                        |
| `diagonal_wipe`   | Diagonal wave                                      |
| `edges_only`      | Cube edges only                                    |
| `fireworks`       | Simple fireworks simulation (inspired by original) |

---

## Comparison: Arduino vs ESP32

| Parameter          | Arduino Uno          | ESP32                |
|--------------------|----------------------|----------------------|
| Language           | C++ (.ino)           | MicroPython (.py)    |
| Logic voltage      | 5V                   | 3.3V                 |
| GPIO pins          | 14 digital           | 34 GPIO              |
| Upload tool        | Arduino IDE          | Thonny / ampy        |
| Clock speed        | 16 MHz               | 240 MHz              |

---

## References

- [Original 8x8x8 project](https://www.instructables.com/8x8x8-Arduino-LED-Cube/)
- [Arduino Forum: Simple 3x3x3 cube](https://forum.arduino.cc/t/very-simple-3x3x3-cube-sketch/922655)
- [MicroPython ESP32 documentation](https://docs.micropython.org/en/latest/esp32/quickref.html)
