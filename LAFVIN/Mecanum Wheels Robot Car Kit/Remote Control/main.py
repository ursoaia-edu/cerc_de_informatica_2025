# ============================================================
#  Universal Remote Control — LAFVIN Mecanum Wheels Robot Car
#  ESP32 + 2x PS2 Joystick + HC-05 Bluetooth
# ============================================================

import time
import math
from machine import Pin, ADC, UART

# ── CONFIG ──────────────────────────────────────────────────

CONFIG = {
    # Transport
    "transport": "bluetooth_uart",

    # HC-05 on UART2 (master mode, auto-connects to HC-06 on car)
    "bt_uart_id": 2,
    "bt_uart_tx": 17,
    "bt_uart_rx": 16,
    "bt_baudrate": 9600,

    # Left joystick pins (translation)
    "joy_left_vrx": 34,   # ADC1_CH6
    "joy_left_vry": 35,   # ADC1_CH7

    # Right joystick pin (rotation, X axis only)
    "joy_right_vrx": 36,  # ADC1_CH0 (VP)

    # Dead zone: center (2048) ± this value
    "dead_zone": 650,

    # Repeat interval — car stops if BT buffer empty, so keep it short
    "repeat_ms": 150,

    # Direction -> command mapping
    "commands": {
        "forward":      "%A#",
        "backward":     "%B#",
        "left":         "%C#",
        "right":        "%D#",
        "up_left":      "%G#",
        "up_right":     "%H#",
        "down_left":    "%I#",
        "down_right":   "%J#",
        "rotate_left":  "%E#",
        "rotate_right": "%F#",
        "stop":         "%S#",
    },

    # Buttons: (gpio, on_command, off_command)
    "buttons": [
        (33, "%T#", "%S#"),   # BTN1: Ultrasonic Avoidance / Stop
        (32, "%W#", "%S#"),   # BTN2: Ultrasonic Follow / Stop
        (25, "%K#", "%L#"),   # BTN3: Drift Left / Drift Right
    ],
}

# ── INPUT LAYER ─────────────────────────────────────────────

CENTER = 2048
DEAD = CONFIG["dead_zone"]

# Left joystick ADC (translation)
_jlx = ADC(Pin(CONFIG["joy_left_vrx"]))
_jlx.atten(ADC.ATTN_11DB)
_jly = ADC(Pin(CONFIG["joy_left_vry"]))
_jly.atten(ADC.ATTN_11DB)

# Right joystick ADC (rotation)
_jrx = ADC(Pin(CONFIG["joy_right_vrx"]))
_jrx.atten(ADC.ATTN_11DB)

# Sector boundaries for 8-direction mapping (degrees from north, clockwise)
_SECTORS = [
    (337.5, 360.0, "forward"),
    (0.0,    22.5, "forward"),
    (22.5,   67.5, "up_right"),
    (67.5,  112.5, "right"),
    (112.5, 157.5, "down_right"),
    (157.5, 202.5, "backward"),
    (202.5, 247.5, "down_left"),
    (247.5, 292.5, "left"),
    (292.5, 337.5, "up_left"),
]


def read_translation():
    """Read left joystick -> one of 8 directions or 'stop'."""
    try:
        x = _jlx.read()
        y = _jly.read()
    except Exception:
        return "stop"

    dx = x - CENTER
    dy = CENTER - y  # invert: low ADC = stick pushed forward

    if abs(dx) < DEAD and abs(dy) < DEAD:
        return "stop"

    angle = math.atan2(dx, dy) * 180.0 / math.pi
    if angle < 0:
        angle += 360.0

    for lo, hi, direction in _SECTORS:
        if lo <= angle < hi:
            cmd = CONFIG["commands"].get(direction)
            if cmd is not None:
                return direction
    return "stop"


def read_rotation():
    """Read right joystick X axis -> 'rotate_left', 'rotate_right', or None."""
    try:
        x = _jrx.read()
    except Exception:
        return None

    if x < CENTER - DEAD:
        if CONFIG["commands"].get("rotate_left") is not None:
            return "rotate_left"
    elif x > CENTER + DEAD:
        if CONFIG["commands"].get("rotate_right") is not None:
            return "rotate_right"
    return None


# Buttons: state tracking
_buttons = []
_btn_states = []
_btn_last = []
_DEBOUNCE_MS = 200

for _gpio, _on, _off in CONFIG["buttons"]:
    _buttons.append((Pin(_gpio, Pin.IN, Pin.PULL_UP), _on, _off))
    _btn_states.append(False)
    _btn_last.append(0)


def read_buttons():
    """Check buttons. On toggle, return command string. Otherwise None."""
    now = time.ticks_ms()
    for i, (pin, on_cmd, off_cmd) in enumerate(_buttons):
        if pin.value() == 0:  # active LOW
            if time.ticks_diff(now, _btn_last[i]) > _DEBOUNCE_MS:
                _btn_last[i] = now
                _btn_states[i] = not _btn_states[i]
                return on_cmd if _btn_states[i] else off_cmd
    return None


# ── TRANSPORT LAYER ─────────────────────────────────────────

led = Pin(2, Pin.OUT)


def _blink(count, interval_ms=250):
    for _ in range(count):
        led.value(not led.value())
        time.sleep_ms(interval_ms)
    led.off()


# -- Bluetooth UART (HC-05) ----------------------------------

if CONFIG["transport"] == "bluetooth_uart":
    _uart = UART(
        CONFIG["bt_uart_id"],
        baudrate=CONFIG["bt_baudrate"],
        tx=CONFIG["bt_uart_tx"],
        rx=CONFIG["bt_uart_rx"],
    )

    def transport_connect():
        # HC-05 master mode auto-connects on power-up.
        # Blink LED while settling, then solid ON.
        _blink(10, 250)
        led.on()

    def transport_send(cmd):
        try:
            _uart.write(cmd)
        except Exception:
            pass

    def transport_connected():
        return True  # HC-05 manages connection internally


# -- WiFi HTTP ------------------------------------------------

elif CONFIG["transport"] == "wifi_http":
    import network
    import urequests

    _sta = network.WLAN(network.STA_IF)

    def transport_connect():
        _sta.active(True)
        _sta.connect(CONFIG["wifi_ssid"], CONFIG["wifi_pass"])
        deadline = time.ticks_add(time.ticks_ms(), 15000)
        while not _sta.isconnected():
            led.value(not led.value())
            time.sleep_ms(500)
            if time.ticks_diff(deadline, time.ticks_ms()) <= 0:
                break
        if _sta.isconnected():
            led.on()
        else:
            led.off()

    def transport_send(cmd):
        if not _sta.isconnected():
            return
        try:
            r = urequests.get(CONFIG["base_url"] + "/" + cmd, timeout=1)
            r.close()
        except Exception:
            pass

    def transport_connected():
        return _sta.isconnected()


# ── CONTROLLER LAYER ────────────────────────────────────────

def main():
    transport_connect()

    prev = None
    repeat_at = time.ticks_ms()
    repeat_ms = CONFIG["repeat_ms"]
    commands = CONFIG["commands"]

    while True:
        # 1. Buttons (highest priority)
        btn = read_buttons()
        if btn is not None:
            transport_send(btn)
            time.sleep_ms(50)
            continue

        # 2. Right joystick (rotation) > Left joystick (translation)
        rot = read_rotation()
        direction = rot if rot else read_translation()

        now = time.ticks_ms()

        if direction != prev:
            # Direction changed — send immediately
            transport_send(commands[direction])
            prev = direction
            repeat_at = now
        elif direction != "stop" and time.ticks_diff(now, repeat_at) > repeat_ms:
            # Still moving — repeat command (car needs continuous stream)
            transport_send(commands[direction])
            repeat_at = now

        # Reconnect if transport lost
        if not transport_connected():
            led.off()
            transport_connect()

        time.sleep_ms(50)


main()
