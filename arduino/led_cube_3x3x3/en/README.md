# 3x3x3 LED Cube on Arduino Uno

A simplified version of the [8x8x8 LED Cube](https://www.instructables.com/8x8x8-Arduino-LED-Cube/) project,
adapted for beginners.

---

## How It Works

The cube uses **layer multiplexing**:

- **9 columns** (LED anodes) are connected to Arduino digital pins through 220 Ω resistors.
- **3 layers** (LED cathodes) are controlled via NPN transistors (2N2222 / BC547).
- Arduino rapidly switches layers (POV — persistence of vision), creating the illusion
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
| Arduino Uno (CH340)      | 1          | Or Nano                        |
| LED 5mm (any color)      | 27         | Can use 3 colors, 9 each      |
| 220 Ω resistor           | 9          | Current-limiting (columns)     |
| 1 kΩ resistor            | 3          | For transistor bases (layers)  |
| NPN transistor 2N2222    | 3          | Or BC547/BC337                 |
| Breadboard               | 1          | 830 tie-points                 |
| Jumper wires             | ~20        | M-M                           |

> All components are included in the **LA036 Super Starter Kit for Arduino UNO**.

---

## Wiring Diagram

```
                        Arduino Uno
                     ┌──────────────────┐
                     │                  │
    Columns          │  D2  ──[220Ω]──── C0 (LED anode)
    (anodes)         │  D3  ──[220Ω]──── C1
                     │  D4  ──[220Ω]──── C2
                     │  D5  ──[220Ω]──── C3
                     │  D6  ──[220Ω]──── C4
                     │  D7  ──[220Ω]──── C5
                     │  D8  ──[220Ω]──── C6
                     │  D9  ──[220Ω]──── C7
                     │  D10 ──[220Ω]──── C8
                     │                  │
    Layers           │  D11 ──[1kΩ]──┐  │
    (cathodes         │  D12 ──[1kΩ]──┤  │
     via               │  D13 ──[1kΩ]──┤  │
     transistors)    │                │  │
                     │  GND ──────────┘  │
                     └──────────────────┘

    2N2222 transistor (for each layer):

        Arduino Pin ──[1kΩ]──► Base
                               Collector ◄── Layer cathodes (all 9 LEDs)
                               Emitter ──► GND
```

### Pin Assignment

| Arduino Pin | Function             |
|-------------|----------------------|
| D2          | Column 0 (anode)     |
| D3          | Column 1             |
| D4          | Column 2             |
| D5          | Column 3             |
| D6          | Column 4             |
| D7          | Column 5             |
| D8          | Column 6             |
| D9          | Column 7             |
| D10         | Column 8             |
| D11         | Layer 0 (bottom)     |
| D12         | Layer 1 (middle)     |
| D13         | Layer 2 (top)        |
| GND         | Transistor emitters  |

---

## Building the Cube

### 1. Preparing the LEDs
- Test each LED before soldering (with a 220 Ω resistor from 5V).
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

### 5. Connecting to Arduino
- 9 anodes (columns) → through 220 Ω resistors → pins D2–D10.
- 3 cathode layers → through 2N2222 transistors → pins D11–D13.

---

## Uploading the Code

1. Open `led_cube_3x3x3.ino` in Arduino IDE.
2. Select board: **Arduino Uno**.
3. Select port.
4. Click **Upload**.

---

## Animations in the Code

| Animation         | Description                                        |
|-------------------|----------------------------------------------------|
| `allOn/allOff`    | Turn the entire cube on/off                        |
| `layerWipe`       | Sequential layer lighting from bottom to top       |
| `columnWipe`      | Sequential column lighting                         |
| `rain`            | Rain effect — random drops fall downward            |
| `spiral`          | Spiral along the cube perimeter                    |
| `randomBlink`     | Random blinking of individual LEDs                 |
| `planeBounce`     | Layer "bounces" up and down                        |
| `diagonalWipe`    | Diagonal wave                                      |
| `edgesOnly`       | Cube edges only                                    |
| `fireworks`       | Simple fireworks simulation (inspired by original) |

---

## Comparison with the Original 8x8x8

| Parameter          | 8x8x8 (original)    | 3x3x3 (ours)        |
|--------------------|----------------------|----------------------|
| Number of LEDs     | 512                  | 27                   |
| Arduino pins       | 64 anodes + 8 cathodes | 9 anodes + 3 cathodes |
| Additional ICs     | Shift registers      | Not needed!          |
| Transistors        | 8                    | 3                    |
| Soldering difficulty | Very high           | Simple               |
| Assembly time      | 20+ hours            | 2–3 hours            |

---

## References

- [Original 8x8x8 project](https://www.instructables.com/8x8x8-Arduino-LED-Cube/)
- [Arduino Forum: Simple 3x3x3 cube](https://forum.arduino.cc/t/very-simple-3x3x3-cube-sketch/922655)
- [Instructables: 3x3x3 LED Cube Arduino-UNO](https://www.instructables.com/3x3x3-LED-Cube-Arduino-UNO/)
