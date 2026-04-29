# Remote Control Spec — ESP32 + PS2 Joystick

## Overview

Беспроводной пульт управления для ESP32 Camera 4WD Robot Car.
Пульт подключается к WiFi AP робота и отправляет HTTP-команды.

## Hardware

### Components

| Component | Qty |
|-----------|-----|
| ESP32 DevKit V1 | 1 |
| PS2 Joystick Module | 1 |
| Push Button | 1 |

### Wiring

```
ESP32 DevKit V1
┌──────────────────────┐
│                      │
│  GPIO 34 ◄─── VRX   │  Joystick X axis (left/right)
│  GPIO 35 ◄─── VRY   │  Joystick Y axis (forward/back)
│  3.3V ────── +5V    │  Joystick power (3.3V is fine)
│  GND ─────── GND    │  Joystick ground
│                      │
│  GPIO 33 ◄─── BTN   │  Push button (other leg to GND)
│                      │
│  GPIO 2 ───► LED     │  Built-in LED (connection status)
│                      │
└──────────────────────┘
```

**Pin choices:**
- GPIO 34, 35 — input-only, ADC1 (ADC2 нельзя использовать при активном WiFi)
- GPIO 33 — internal pull-up, хорошо для кнопки
- GPIO 2 — встроенный LED на DevKit V1

### Joystick SW (нажатие стика)

Не подключается, не используется.

## Software

### Platform

MicroPython на ESP32 DevKit V1.

### Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point: WiFi + main loop |

### WiFi Connection

- Connect to AP: `ESP32-CAM Robot` (open network, no password)
- Robot IP: `192.168.4.1`
- Retry connection indefinitely with 1s delay
- LED indication:
  - **Blinking** (500ms) — connecting to WiFi
  - **Solid ON** — connected
  - **Off** — not connected / error

### Joystick → Direction Mapping

ADC range: 0–4095. Center ≈ 2048.

```
Dead zone: 1400–2700 (center ± ~30%)

         VRY < 1400
           ↑ FORWARD
           |
VRX < 1400 ←── STOP ──→ VRX > 2700
   LEFT     (dead zone)    RIGHT
           |
           ↓ BACKWARD
         VRY > 2700
```

**Priority:** if both axes are outside dead zone, use the axis with greater deflection from center.

### Control Logic

```
LOOP (every 50ms):
│
├── Read ADC: vrx, vry
├── Determine direction (forward/back/left/right/stop)
│
├── If direction != previous_direction:
│   ├── Send HTTP GET to robot (new command)
│   └── Save direction, reset repeat timer
│
├── Else if direction != stop AND repeat_timer > 500ms:
│   ├── Re-send same command (keep-alive, handles packet loss)
│   └── Reset repeat timer
│
├── Read button (with debounce 200ms):
│   └── On press: toggle LED state → send /ledon or /ledoff
│
└── Update status LED
```

### HTTP Requests

Non-blocking (with short timeout ~1s). If request fails — skip, try next cycle.

| State | HTTP Request |
|-------|-------------|
| Forward | `GET http://192.168.4.1/go` |
| Backward | `GET http://192.168.4.1/back` |
| Left | `GET http://192.168.4.1/left` |
| Right | `GET http://192.168.4.1/right` |
| Stop | `GET http://192.168.4.1/stop` |
| Light ON | `GET http://192.168.4.1/ledon` |
| Light OFF | `GET http://192.168.4.1/ledoff` |

### Debounce

- **Button:** 200ms debounce. Toggle mode (press once = ON, press again = OFF).
- **Joystick:** no debounce needed, direction change detection is sufficient.

### Error Handling

- WiFi disconnect → re-enter connection loop, LED blinking
- HTTP timeout → ignore, continue loop
- ADC read error → treat as center (stop)

## Limitations

- No speed control (robot firmware has hardcoded `speed = 150`)
- No diagonal movement (robot API supports only 4 directions)
- No camera control from remote (could be added later via `/control` endpoint)

## Future Improvements (out of scope)

- Add speed control endpoint to robot firmware (`/speed?val=N`)
- Add OLED display for battery/status/stream
- Add second joystick or buttons for camera pan/tilt
- Proportional speed control (requires firmware modification)
