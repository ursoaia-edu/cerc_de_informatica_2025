"""
Cub LED 3x3x3 — ESP32 (MicroPython)
====================================
Versiune simplificată a proiectului 8x8x8 LED Cube
https://www.instructables.com/8x8x8-Arduino-LED-Cube/

Conectare:
  Coloane (anoduri) → GPIO 2,4,5,18,19,21,22,23,25 prin rezistoare de 220 Ω
  Straturi (catoduri) → GPIO 26,27,32 prin tranzistoare NPN 2N2222

  Vedere de sus (coloane):
      C0(2)   C1(4)   C2(5)
      C3(18)  C4(19)  C5(21)
      C6(22)  C7(23)  C8(25)

  Straturi:
      Layer 0 (inferior) → GPIO 26
      Layer 1 (mijlociu) → GPIO 27
      Layer 2 (superior) → GPIO 32
"""

import machine
import time
import urandom

# === Configurarea pinilor ===
COL_PINS = [machine.Pin(p, machine.Pin.OUT) for p in (2, 4, 5, 18, 19, 21, 22, 23, 25)]
LAYER_PINS = [machine.Pin(p, machine.Pin.OUT) for p in (26, 27, 32)]

NUM_LAYERS = 3
NUM_COLS = 9

# Bufferul cubului: cube[layer] — mască de biți pe 9 coloane
cube = [0, 0, 0]

# Întârziere multiplexare (ms) — persistența vizuală
POV_DELAY = 3


# === Funcții auxiliare ===

def display_cube():
    """Afișează starea curentă a cubului (un ciclu POV)."""
    for layer in range(NUM_LAYERS):
        # Oprește toate straturile
        for l in range(NUM_LAYERS):
            LAYER_PINS[l].value(0)
        # Setează coloanele pentru stratul curent
        for col in range(NUM_COLS):
            COL_PINS[col].value((cube[layer] >> col) & 1)
        # Pornește stratul curent
        LAYER_PINS[layer].value(1)
        time.sleep_ms(POV_DELAY)
    # Oprește ultimul strat
    for l in range(NUM_LAYERS):
        LAYER_PINS[l].value(0)


def show_for(duration_ms):
    """Afișează cubul timp de duration_ms milisecunde."""
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        display_cube()


def clear_cube():
    """Golește bufferul cubului."""
    for i in range(NUM_LAYERS):
        cube[i] = 0


def fill_cube():
    """Umple întregul cub."""
    for i in range(NUM_LAYERS):
        cube[i] = 0b111111111


def set_led(x, y, z, state):
    """Setează un singur LED: (x, y, z), state = True/False.
    x = 0..2 (coloană), y = 0..2 (rând), z = 0..2 (strat)
    """
    col = y * 3 + x
    if state:
        cube[z] |= (1 << col)
    else:
        cube[z] &= ~(1 << col)


# === Animații ===

def anim_all_on_off():
    """Pornire/oprire întregul cub."""
    fill_cube()
    show_for(1000)
    clear_cube()
    show_for(500)


def anim_layer_wipe():
    """Aprinderea secvențială a straturilor."""
    for i in range(3):
        clear_cube()
        cube[i] = 0b111111111
        show_for(400)
    for i in range(1, -1, -1):
        clear_cube()
        cube[i] = 0b111111111
        show_for(400)


def anim_column_wipe():
    """Aprinderea secvențială a coloanelor."""
    for col in range(NUM_COLS):
        clear_cube()
        for layer in range(NUM_LAYERS):
            cube[layer] = (1 << col)
        show_for(200)


def anim_rain():
    """Efect de ploaie — picături aleatoare cad în jos."""
    for _ in range(15):
        col = urandom.getrandbits(4) % NUM_COLS
        for z in range(NUM_LAYERS - 1, -1, -1):
            clear_cube()
            cube[z] = (1 << col)
            show_for(150)
    clear_cube()


def anim_spiral():
    """Spirală pe perimetrul cubului."""
    perimeter = [0, 1, 2, 5, 8, 7, 6, 3]
    for _ in range(3):
        for col in perimeter:
            clear_cube()
            for layer in range(NUM_LAYERS):
                cube[layer] = (1 << col)
            show_for(150)


def anim_random_blink():
    """Clipire aleatoare a LED-urilor individuale."""
    for _ in range(30):
        clear_cube()
        x = urandom.getrandbits(2) % 3
        y = urandom.getrandbits(2) % 3
        z = urandom.getrandbits(2) % 3
        set_led(x, y, z, True)
        show_for(100)


def anim_plane_bounce():
    """Stratul sare în sus și în jos."""
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
    """Undă diagonală."""
    diags = [
        0b000000001,  # x+y=0 → C0
        0b000001010,  # x+y=1 → C1, C3
        0b001010100,  # x+y=2 → C2, C4, C6
        0b010100000,  # x+y=3 → C5, C7
        0b100000000,  # x+y=4 → C8
    ]
    for _ in range(3):
        for d in diags:
            clear_cube()
            for layer in range(NUM_LAYERS):
                cube[layer] = d
            show_for(250)


def anim_edges_only():
    """Doar muchiile cubului."""
    clear_cube()
    cube[0] = 0b111111111
    cube[1] = 0b101010101
    cube[2] = 0b111111111
    show_for(2000)
    clear_cube()
    show_for(500)


def anim_fireworks():
    """Simulare simplă de artificii (inspirat din originalul 8x8x8)."""
    for _ in range(5):
        # Racheta urcă pe coloana centrală (C4)
        for z in range(NUM_LAYERS):
            clear_cube()
            cube[z] = (1 << 4)
            show_for(200)
        # Explozie — toate LED-urile din stratul superior
        clear_cube()
        cube[2] = 0b111111111
        show_for(300)
        # Împrăștiere — toate straturile, apoi se sting
        fill_cube()
        show_for(200)
        # Se sting de sus în jos
        cube[2] = 0
        show_for(150)
        cube[1] = 0
        show_for(150)
        cube[0] = 0
        show_for(300)


# === Programul principal ===

def main():
    # Inițializare — toți pinii LOW
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
