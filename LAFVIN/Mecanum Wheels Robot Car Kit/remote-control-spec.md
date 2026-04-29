# Universal Remote Control Spec — ESP32 + PS2 Joysticks

Универсальный пульт управления для любых радиоуправляемых машинок.
Одна и та же аппаратная часть и логика ввода, разный транспорт и набор команд.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    main.py                          │
│                                                     │
│  ┌──────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │  Input    │   │  Controller  │   │  Transport  │ │
│  │          │──►│              │──►│             │ │
│  │ Joystick │   │  Direction   │   │ WiFi HTTP   │ │
│  │ L + R    │   │  mapping +   │   │ BT Classic  │ │
│  │ Buttons  │   │  dedup       │   │ BLE         │ │
│  └──────────┘   └──────────────┘   │ IR          │ │
│                                     └─────────────┘ │
│  ┌──────────┐                                       │
│  │  Status  │  LED on GPIO 2                        │
│  └──────────┘                                       │
└─────────────────────────────────────────────────────┘
```

Три слоя:
1. **Input** — чтение двух джойстиков и кнопок (всегда одинаковый)
2. **Controller** — маппинг направления → команда, дедупликация, repeat (всегда одинаковый)
3. **Transport** — отправка команды машинке (меняется под каждую машинку)

## Hardware (constant)

### Components

| Component | Qty |
|-----------|-----|
| ESP32 DevKit V1 | 1 |
| PS2 Joystick Module | 2 |
| Push Button(s) | 1–3 |

### Wiring

```
ESP32 DevKit V1
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
│  GPIO 39 ◄─── VRY   (ADC1_CH3, VN)  │  ← optional
│  3.3V ────── VCC                     │
│  GND ─────── GND                     │
│                                      │
│  Buttons (active LOW, internal pull-up): │
│  GPIO 33 ◄─── BTN1  (other leg → GND)   │
│  GPIO 32 ◄─── BTN2  (optional)          │
│  GPIO 25 ◄─── BTN3  (optional)          │
│                                      │
│  GPIO 2  ───► LED   (status)         │
│                                      │
└──────────────────────────────────────┘
```

**Notes:**
- GPIO 34, 35, 36, 39 — input-only, ADC1 (ADC2 конфликтует с WiFi/BT)
- Кнопки — internal pull-up, active LOW
- Джойстики питать от 3.3V (не 5V, иначе нужен voltage divider)
- Joystick SW (нажатие стика) — не используется
- Bluetooth Classic — встроенный в ESP32, дополнительных модулей не нужно

## Input Layer

### Left Joystick — Translation (8 directions)

ADC range: 0–4095. Center ≈ 2048.

```
Dead zone: center ± 650 (1398–2698)

dx = X - 2048          (positive = right)
dy = 2048 - Y          (positive = forward, ADC inverted)

Both in dead zone → "stop"

angle = atan2(dx, dy)   → 8 sectors by 45°

         up_left (G)    forward (A)    up_right (H)
                  ╲        ↑        ╱
                   ╲       |       ╱
      left (C)  ←── ── STOP ── ──→  right (D)
                   ╱       |       ╲
                  ╱        ↓        ╲
       down_left (I)   backward (B)  down_right (J)
```

Sector mapping (angle from north, clockwise):

| Angle range | Direction |
|-------------|-----------|
| 337.5°–22.5° | `forward` |
| 22.5°–67.5° | `up_right` |
| 67.5°–112.5° | `right` |
| 112.5°–157.5° | `down_right` |
| 157.5°–202.5° | `backward` |
| 202.5°–247.5° | `down_left` |
| 247.5°–292.5° | `left` |
| 292.5°–337.5° | `up_left` |

### Right Joystick — Rotation (X axis only)

```
VRX < 1398  →  "rotate_left"
VRX > 2698  →  "rotate_right"
otherwise   →  None (no rotation)
```

Right joystick Y axis не используется.

### Priority

```
1. Button press (highest) → send button command
2. Right joystick rotation → send rotate command
3. Left joystick translation → send direction command
4. Nothing → "stop"
```

### Buttons

Debounce 200ms. Toggle mode: нажал — ON, нажал ещё раз — OFF.
Каждая кнопка — пара команд (on_command / off_command).

## Controller Layer

```
LOOP (every 50ms):
│
├── btn_cmd = read_buttons()
├── If btn_cmd:
│   └── transport.send(btn_cmd)
│
├── rotation = read_rotation()       # right joystick
├── direction = rotation OR read_translation()  # left joystick
│
├── If direction != prev_direction:
│   ├── transport.send(COMMANDS[direction])
│   └── Reset repeat timer
│
├── Else if direction != "stop" AND repeat_timer expired:
│   ├── transport.send(COMMANDS[direction])   # keep-alive
│   └── Reset repeat timer
│
└── Update status LED
```

**Repeat interval** задаётся в CONFIG (`repeat_ms`). Для машинок, которые останавливаются
при пустом буфере (как LAFVIN Mecanum) — 150ms. Для машинок с keep-alive — 500ms.

Контроллер не знает о WiFi, Bluetooth, конкретных URL — он работает с абстрактным `transport.send(command)`.

## Transport Layer

Транспорт реализует два метода:

```python
class Transport:
    def connect(self):
        """Establish connection. Called on startup and reconnect."""
        ...

    def send(self, command):
        """Send a command string to the vehicle. Non-blocking, timeout ~1s."""
        ...

    def is_connected(self):
        """Return True if connection is alive."""
        ...
```

### Transport: WiFi HTTP

```python
TRANSPORT = "wifi_http"
WIFI_SSID = "ESP32-CAM Robot"
WIFI_PASS = ""
BASE_URL = "http://192.168.4.1"
```

`send(cmd)` → `GET {BASE_URL}/{cmd}`

### Transport: Bluetooth Classic (ESP32 built-in)

```cpp
// Arduino: BluetoothSerial library (built into ESP32 Arduino core)
BT_NAME = "HC-06"           // target device name
BT_MAC  = "XX:XX:XX:XX:XX:XX"  // or connect by name
```

ESP32 в режиме master подключается к HC-06/HC-05 slave на машинке
через встроенный Bluetooth Classic. Дополнительных модулей не нужно.

`send(cmd)` → `bt.print(cmd)`

> **Note:** MicroPython на ESP32 не поддерживает BT Classic SPP.
> Для MicroPython — используй HC-05 модуль на UART (см. `main.py`).
> Для Arduino — используй `BluetoothSerial` из коробки (см. `remote_control.ino`).

### Transport: BLE

```python
TRANSPORT = "ble"
BLE_NAME = "RobotCar"
BLE_SERVICE_UUID = "..."
BLE_CHAR_UUID = "..."
```

`send(cmd)` → write to BLE characteristic

## Config (per vehicle)

Весь конфиг конкретной машинки задаётся в одном словаре в начале `main.py`:

```python
CONFIG = {
    # Transport
    "transport": "bluetooth",   # "wifi_http" | "bluetooth" | "ble"

    # WiFi HTTP settings
    "wifi_ssid": None,
    "wifi_pass": None,
    "base_url": None,

    # Bluetooth Classic settings
    "bt_name": "HC-06",           # target device name
    "bt_mac": None,               # or "XX:XX:XX:XX:XX:XX"

    # BLE settings
    "ble_name": None,
    "ble_service_uuid": None,
    "ble_char_uuid": None,

    # Joystick pins
    "joy_left_vrx": 34,
    "joy_left_vry": 35,
    "joy_right_vrx": 36,

    # Dead zone (center ± this value)
    "dead_zone": 650,

    # Repeat interval for keep-alive (ms)
    "repeat_ms": 150,

    # Direction → command mapping (up to 11 directions)
    "commands": {
        "forward":      "go",
        "backward":     "back",
        "left":         "left",
        "right":        "right",
        "up_left":      None,       # None = not supported
        "up_right":     None,
        "down_left":    None,
        "down_right":   None,
        "rotate_left":  None,
        "rotate_right": None,
        "stop":         "stop",
    },

    # Buttons: list of (gpio, on_command, off_command)
    "buttons": [
        (33, "ledon", "ledoff"),
    ],
}
```

Для новой машинки — меняем только `CONFIG`. Код `main.py` остаётся тем же.
Если команда = `None`, направление игнорируется (полезно для машинок без диагоналей).

## Status LED (GPIO 2)

| State | LED |
|-------|-----|
| Connecting | Blink 500ms |
| Connected | Solid ON |
| Disconnected / error | OFF |

## Error Handling

- Connection lost → re-enter `transport.connect()`, LED blinking
- `send()` timeout/error → ignore, continue loop
- ADC read error → treat as center (stop)

## File Structure

```
Remote Control/
├── remote_control/
│   └── remote_control.ino   # Arduino C++ (recommended — built-in BT Classic)
└── main.py                  # MicroPython (needs HC-05 for BT Classic)
```

Один файл на каждую платформу. Транспорты — функции внутри файла, не отдельные модули.
Arduino версия — рекомендуемая (ESP32 BluetoothSerial из коробки, без доп. модулей).
