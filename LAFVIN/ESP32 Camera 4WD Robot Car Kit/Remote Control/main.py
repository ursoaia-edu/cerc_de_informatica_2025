import network
import urequests
import time
from machine import Pin, ADC

# --- Hardware Setup ---

# Joystick ADC (ADC1 pins — safe with WiFi active)
vrx = ADC(Pin(34))
vry = ADC(Pin(35))
vrx.atten(ADC.ATTN_11DB)  # Full range 0-3.3V
vry.atten(ADC.ATTN_11DB)

# Button (active LOW with internal pull-up)
button = Pin(33, Pin.IN, Pin.PULL_UP)

# Status LED (built-in on DevKit V1)
led = Pin(2, Pin.OUT)

# --- Constants ---

ROBOT_IP = "http://192.168.4.1"
WIFI_SSID = "ESP32-CAM Robot"
WIFI_PASS = ""

# Dead zone thresholds (center ~2048, ±30%)
DEAD_LOW = 1400
DEAD_HIGH = 2700

# Timing (ms)
LOOP_INTERVAL = 50
REPEAT_INTERVAL = 500
DEBOUNCE_TIME = 200

# Direction constants
STOP = "stop"
FORWARD = "go"
BACKWARD = "back"
LEFT = "left"
RIGHT = "right"

# --- State ---

prev_direction = None
last_command_time = 0
last_button_time = 0
light_on = False
wlan = None


def connect_wifi():
    """Connect to robot's WiFi AP. Blinks LED while connecting."""
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASS)

    while not wlan.isconnected():
        led.value(not led.value())  # Blink
        time.sleep_ms(500)

    led.value(1)  # Solid ON = connected
    print("Connected:", wlan.ifconfig())


def send_command(cmd):
    """Send HTTP GET to robot. Ignore errors to keep loop running."""
    try:
        r = urequests.get(ROBOT_IP + "/" + cmd, timeout=1)
        r.close()
    except:
        pass


def read_direction():
    """Read joystick and return direction string."""
    x = vrx.read()
    y = vry.read()

    # Deflection from center
    dx = x - 2048
    dy = y - 2048

    x_outside = x < DEAD_LOW or x > DEAD_HIGH
    y_outside = y < DEAD_LOW or y > DEAD_HIGH

    if not x_outside and not y_outside:
        return STOP

    # Priority: axis with greater deflection
    if abs(dx) >= abs(dy):
        return LEFT if x < DEAD_LOW else RIGHT
    else:
        return FORWARD if y < DEAD_LOW else BACKWARD


def handle_button():
    """Check button press with debounce. Toggle flashlight."""
    global last_button_time, light_on

    now = time.ticks_ms()
    if button.value() == 0 and time.ticks_diff(now, last_button_time) > DEBOUNCE_TIME:
        last_button_time = now
        light_on = not light_on
        send_command("ledon" if light_on else "ledoff")


def main():
    global prev_direction, last_command_time

    connect_wifi()

    while True:
        # Reconnect if WiFi dropped
        if not wlan.isconnected():
            led.value(0)
            connect_wifi()

        now = time.ticks_ms()

        # --- Joystick ---
        direction = read_direction()

        if direction != prev_direction:
            send_command(direction)
            prev_direction = direction
            last_command_time = now
        elif direction != STOP and time.ticks_diff(now, last_command_time) > REPEAT_INTERVAL:
            send_command(direction)
            last_command_time = now

        # --- Button ---
        handle_button()

        time.sleep_ms(LOOP_INTERVAL)


main()
