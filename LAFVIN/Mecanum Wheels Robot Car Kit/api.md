# LAFVIN Mecanum Wheels Robot Car — Bluetooth API

## Transport

- **Interface:** Bluetooth Classic (Serial), HC-06 module
- **Baud rate:** 9600
- **Connection:** SoftwareSerial on Arduino pins A0 (RX), A1 (TX)

## Protocol

Формат команды: `%<CMD>#`

Один символ между `%` и `#`. Сообщение длиной 3 байта.
Если длина сообщения > 4 — машинка делает stop (защита от мусора).
Если нет данных от BT — stop.

## Commands

### Movement (translation)

| CMD | Action          | Dir byte | Delay |
|-----|-----------------|----------|-------|
| `A` | Forward         | 39       | 200ms |
| `B` | Backward        | 216      | 200ms |
| `C` | Strafe Left     | 116      | 200ms |
| `D` | Strafe Right    | 139      | 200ms |
| `G` | Diagonal Up-Left    | 36   | 300ms |
| `H` | Diagonal Up-Right   | 3    | 300ms |
| `I` | Diagonal Down-Left  | 80   | 300ms |
| `J` | Diagonal Down-Right | 136  | 300ms |

### Rotation

| CMD | Action       | Dir byte | Delay |
|-----|--------------|----------|-------|
| `E` | Rotate Left  | 106      | 100ms |
| `F` | Rotate Right | 149      | 100ms |

### Drift

| CMD | Action     | Dir byte | Delay |
|-----|------------|----------|-------|
| `K` | Drift Left | 20       | 300ms |
| `L` | Drift Right| 10       | 300ms |

### Control

| CMD | Action               |
|-----|----------------------|
| `S` | Stop                 |
| `T` | Ultrasonic Avoidance (autonomous loop) |
| `W` | Ultrasonic Follow (autonomous loop)    |

## Motor System

- 4 motors via L293D shield + shift register (shiftOut)
- Dir byte = 8-bit bitmask controlling direction pins of 4 motors
- Speed: PWM 0–255, default all 255 (full speed)
- No speed control from BT — fixed speed

## Important Behavior

1. **No keep-alive** — if BT buffer is empty, car stops immediately
2. **Command = impulse** — each command runs the motors for its delay, then the loop re-reads BT. Car needs continuous stream of commands to keep moving
3. **Autonomous modes** (`T`, `W`) — once entered, run in a blocking loop using ultrasonic sensor. BT is still read each iteration, so sending another command switches mode

## Remote Control Mapping

Машинка на меканум-колёсах — может ехать в любом направлении без поворота корпуса.
Нужны **два джойстика**:

### Left Joystick — Translation (8 directions)

```
        G (↖)    A (↑)    H (↗)
                  |
  C (←) ────── STOP ────── D (→)
                  |
        I (↙)    B (↓)    J (↘)
```

Маппинг по двум осям с dead zone:

```
X = ADC left/right,  Y = ADC forward/back
center ≈ 2048,  dead zone: 1400–2700

if X and Y both in dead zone → Stop

dx = X - 2048   (positive = right)
dy = 2048 - Y   (positive = forward, ADC inverted)

angle = atan2(dx, dy)   → 8 sectors by 45°

Sector:        Command:
 -22.5°..22.5°    A  (Forward)
  22.5°..67.5°    H  (Up-Right)
  67.5°..112.5°   D  (Right)
 112.5°..157.5°   J  (Down-Right)
 157.5°..202.5°   B  (Backward)
 202.5°..247.5°   I  (Down-Left)
 247.5°..292.5°   C  (Left)
 292.5°..337.5°   G  (Up-Left)
```

### Right Joystick — Rotation (X axis only)

```
VRX < 1400  →  E (Rotate Left)
VRX > 2700  →  F (Rotate Right)
otherwise   →  (no rotation command)
```

### Buttons

| Button | On         | Off  | Description |
|--------|------------|------|-------------|
| BTN1 (GPIO 33) | `T` | `S` | Ultrasonic Avoidance toggle |
| BTN2 (GPIO 32) | `W` | `S` | Ultrasonic Follow toggle |
| BTN3 (GPIO 25) | `K` | `L` | Drift Left / Drift Right |

### Wiring — Remote Control (ESP32)

```
ESP32 DevKit V1 (Remote)
┌──────────────────────────────────────┐
│                                      │
│  Left Joystick (translation):        │
│  GPIO 34 ◄─── VRX   (ADC1_CH6)      │
│  GPIO 35 ◄─── VRY   (ADC1_CH7)      │
│  3.3V ────── VCC                     │
│  GND ─────── GND                     │
│                                      │
│  Right Joystick (rotation):          │
│  GPIO 36 ◄─── VRX   (ADC1_CH0, VP)  │
│  GPIO 39 ◄─── VRY   (ADC1_CH3, VN)  │  ← не используется
│  3.3V ────── VCC                     │
│  GND ─────── GND                     │
│                                      │
│  Buttons:                            │
│  GPIO 33 ◄─── BTN1  (Avoidance)     │
│  GPIO 32 ◄─── BTN2  (Follow)        │
│  GPIO 25 ◄─── BTN3  (Drift)         │
│                                      │
│  GPIO 2  ───► LED   (status)         │
│                                      │
└──────────────────────────────────────┘
```

**Notes:**
- Bluetooth Classic — встроенный в ESP32, дополнительных модулей не нужно
- GPIO 34, 35, 36, 39 — input-only, ADC1 (безопасно при работе с BT)
- Код пульта: `Remote Control/remote_control/remote_control.ino` (Arduino, рекомендуемый)
- Альтернатива: `Remote Control/main.py` (MicroPython, требует HC-05 на UART)
