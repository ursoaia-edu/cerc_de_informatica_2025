"""
LED Cube 3x3x3 — ESP32 (MicroPython)
=====================================
Simplified version of the 8x8x8 LED Cube project
https://www.instructables.com/8x8x8-Arduino-LED-Cube/

Wiring:
  Columns (anodes) → GPIO 2,4,5,18,19,21,22,23,25 through 220 Ω resistors
  Layers  (cathodes) → GPIO 26,27,32 through NPN transistors 2N2222

  Top view (columns):
      C0(2)   C1(4)   C2(5)
      C3(18)  C4(19)  C5(21)
      C6(22)  C7(23)  C8(25)

  Layers:
      Layer 0 (bottom) → GPIO 26
      Layer 1 (middle) → GPIO 27
      Layer 2 (top)    → GPIO 32
"""

import machine
import time
import urandom

# === Pin configuration ===
COL_PINS = [machine.Pin(p, machine.Pin.OUT) for p in (2, 4, 5, 18, 19, 21, 22, 23, 25)]
LAYER_PINS = [machine.Pin(p, machine.Pin.OUT) for p in (26, 27, 32)]

NUM_LAYERS = 3
NUM_COLS = 9

# Cube buffer: cube[layer] — 9-bit bitmask of columns
cube = [0, 0, 0]

# Multiplexing delay (ms) — persistence of vision
POV_DELAY = 3


# === Helper functions ===

def display_cube():
    """Render current cube state (one POV cycle)."""
    for layer in range(NUM_LAYERS):
        # Turn off all layers
        for l in range(NUM_LAYERS):
            LAYER_PINS[l].value(0)
        # Set columns for current layer
        for col in range(NUM_COLS):
            COL_PINS[col].value((cube[layer] >> col) & 1)
        # Turn on current layer
        LAYER_PINS[layer].value(1)
        time.sleep_ms(POV_DELAY)
    # Turn off last layer
    for l in range(NUM_LAYERS):
        LAYER_PINS[l].value(0)


def show_for(duration_ms):
    """Display cube for duration_ms milliseconds."""
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        display_cube()


def clear_cube():
    """Clear the cube buffer."""
    for i in range(NUM_LAYERS):
        cube[i] = 0


def fill_cube():
    """Fill the entire cube."""
    for i in range(NUM_LAYERS):
        cube[i] = 0b111111111


def set_led(x, y, z, state):
    """Set a single LED: (x, y, z), state = True/False.
    x = 0..2 (column), y = 0..2 (row), z = 0..2 (layer)
    """
    col = y * 3 + x
    if state:
        cube[z] |= (1 << col)
    else:
        cube[z] &= ~(1 << col)


# === Animations ===

def anim_all_on_off():
    """Turn the entire cube on/off."""
    fill_cube()
    show_for(1000)
    clear_cube()
    show_for(500)


def anim_layer_wipe():
    """Sequential layer lighting from bottom to top."""
    for i in range(3):
        clear_cube()
        cube[i] = 0b111111111
        show_for(400)
    for i in range(1, -1, -1):
        clear_cube()
        cube[i] = 0b111111111
        show_for(400)


def anim_column_wipe():
    """Sequential column lighting."""
    for col in range(NUM_COLS):
        clear_cube()
        for layer in range(NUM_LAYERS):
            cube[layer] = (1 << col)
        show_for(200)


def anim_rain():
    """Rain effect — random drops fall downward."""
    for _ in range(15):
        col = urandom.getrandbits(4) % NUM_COLS
        for z in range(NUM_LAYERS - 1, -1, -1):
            clear_cube()
            cube[z] = (1 << col)
            show_for(150)
    clear_cube()


def anim_spiral():
    """Spiral along the cube perimeter."""
    perimeter = [0, 1, 2, 5, 8, 7, 6, 3]
    for _ in range(3):
        for col in perimeter:
            clear_cube()
            for layer in range(NUM_LAYERS):
                cube[layer] = (1 << col)
            show_for(150)


def anim_random_blink():
    """Random blinking of individual LEDs."""
    for _ in range(30):
        clear_cube()
        x = urandom.getrandbits(2) % 3
        y = urandom.getrandbits(2) % 3
        z = urandom.getrandbits(2) % 3
        set_led(x, y, z, True)
        show_for(100)


def anim_plane_bounce():
    """Layer bounces up and down."""
    for _ in range(4):
        for i in range(NUM_LAYERS):
            clear_cube()
            cube[i] = 0b111111111
            show_for(250)
        for i in range(NUM_LAYERS - 2, 0, -1):
            clear_cube()
            cube[i] = 0b111111111
            show_for(250)


def anim_diagonal_wipe():
    """Diagonal wave."""
    diags = [
        0b000000001,  # x+y=0 -> C0
        0b000001010,  # x+y=1 -> C1, C3
        0b001010100,  # x+y=2 -> C2, C4, C6
        0b010100000,  # x+y=3 -> C5, C7
        0b100000000,  # x+y=4 -> C8
    ]
    for _ in range(3):
        for d in diags:
            clear_cube()
            for layer in range(NUM_LAYERS):
                cube[layer] = d
            show_for(250)


def anim_edges_only():
    """Cube edges only."""
    clear_cube()
    cube[0] = 0b111111111
    cube[1] = 0b101010101
    cube[2] = 0b111111111
    show_for(2000)
    clear_cube()
    show_for(500)


def anim_fireworks():
    """Simple fireworks simulation (inspired by the original 8x8x8)."""
    for _ in range(5):
        # Rocket rises through center column (C4)
        for z in range(NUM_LAYERS):
            clear_cube()
            cube[z] = (1 << 4)
            show_for(200)
        # Burst — all LEDs on top layer
        clear_cube()
        cube[2] = 0b111111111
        show_for(300)
        # Spread — all layers, then fade
        fill_cube()
        show_for(200)
        # Fade from top to bottom
        cube[2] = 0
        show_for(150)
        cube[1] = 0
        show_for(150)
        cube[0] = 0
        show_for(300)


# === Main program ===

def main():
    # Initialize all pins to LOW
    for pin in COL_PINS:
        pin.value(0)
    for pin in LAYER_PINS:
        pin.value(0)

    clear_cube()

    while True:
        anim_all_on_off()
        anim_layer_wipe()
        anim_column_wipe()
        anim_plane_bounce()
        anim_spiral()
        anim_diagonal_wipe()
        anim_rain()
        anim_random_blink()
        anim_edges_only()
        anim_fireworks()


main()
