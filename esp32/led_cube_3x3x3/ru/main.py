"""
LED Куб 3x3x3 — ESP32 (MicroPython)
====================================
Упрощённая версия проекта 8x8x8 LED Cube
https://www.instructables.com/8x8x8-Arduino-LED-Cube/

Подключение:
  Столбцы (аноды) → GPIO 2,4,5,18,19,21,22,23,25 через резисторы 220 Ом
  Слои   (катоды) → GPIO 26,27,32 через NPN транзисторы 2N2222

  Вид сверху (столбцы):
      C0(2)   C1(4)   C2(5)
      C3(18)  C4(19)  C5(21)
      C6(22)  C7(23)  C8(25)

  Слои:
      Layer 0 (нижний)  → GPIO 26
      Layer 1 (средний) → GPIO 27
      Layer 2 (верхний) → GPIO 32
"""

import machine
import time
import urandom

# === Настройки пинов ===
COL_PINS = [machine.Pin(p, machine.Pin.OUT) for p in (2, 4, 5, 18, 19, 21, 22, 23, 25)]
LAYER_PINS = [machine.Pin(p, machine.Pin.OUT) for p in (26, 27, 32)]

NUM_LAYERS = 3
NUM_COLS = 9

# Буфер куба: cube[layer] — битовая маска 9 столбцов
cube = [0, 0, 0]

# Задержка мультиплексирования (мс) — persistence of vision
POV_DELAY = 3


# === Вспомогательные функции ===

def display_cube():
    """Отобразить текущее состояние куба (один цикл POV)."""
    for layer in range(NUM_LAYERS):
        # Выключить все слои
        for l in range(NUM_LAYERS):
            LAYER_PINS[l].value(0)
        # Установить столбцы для текущего слоя
        for col in range(NUM_COLS):
            COL_PINS[col].value((cube[layer] >> col) & 1)
        # Включить текущий слой
        LAYER_PINS[layer].value(1)
        time.sleep_ms(POV_DELAY)
    # Выключить последний слой
    for l in range(NUM_LAYERS):
        LAYER_PINS[l].value(0)


def show_for(duration_ms):
    """Отображать куб в течение duration_ms миллисекунд."""
    start = time.ticks_ms()
    while time.ticks_diff(time.ticks_ms(), start) < duration_ms:
        display_cube()


def clear_cube():
    """Очистить буфер куба."""
    for i in range(NUM_LAYERS):
        cube[i] = 0


def fill_cube():
    """Заполнить весь куб."""
    for i in range(NUM_LAYERS):
        cube[i] = 0b111111111


def set_led(x, y, z, state):
    """Установить отдельный LED: (x, y, z), state = True/False.
    x = 0..2 (колонка), y = 0..2 (ряд), z = 0..2 (слой)
    """
    col = y * 3 + x
    if state:
        cube[z] |= (1 << col)
    else:
        cube[z] &= ~(1 << col)


# === Анимации ===

def anim_all_on_off():
    """Включить/выключить весь куб."""
    fill_cube()
    show_for(1000)
    clear_cube()
    show_for(500)


def anim_layer_wipe():
    """Последовательное зажигание слоёв."""
    for i in range(3):
        clear_cube()
        cube[i] = 0b111111111
        show_for(400)
    for i in range(1, -1, -1):
        clear_cube()
        cube[i] = 0b111111111
        show_for(400)


def anim_column_wipe():
    """Последовательное зажигание столбцов."""
    for col in range(NUM_COLS):
        clear_cube()
        for layer in range(NUM_LAYERS):
            cube[layer] = (1 << col)
        show_for(200)


def anim_rain():
    """Эффект дождя — случайные капли падают вниз."""
    for _ in range(15):
        col = urandom.getrandbits(4) % NUM_COLS
        for z in range(NUM_LAYERS - 1, -1, -1):
            clear_cube()
            cube[z] = (1 << col)
            show_for(150)
    clear_cube()


def anim_spiral():
    """Спираль по периметру куба."""
    perimeter = [0, 1, 2, 5, 8, 7, 6, 3]
    for _ in range(3):
        for col in perimeter:
            clear_cube()
            for layer in range(NUM_LAYERS):
                cube[layer] = (1 << col)
            show_for(150)


def anim_random_blink():
    """Случайное мигание отдельных LED."""
    for _ in range(30):
        clear_cube()
        x = urandom.getrandbits(2) % 3
        y = urandom.getrandbits(2) % 3
        z = urandom.getrandbits(2) % 3
        set_led(x, y, z, True)
        show_for(100)


def anim_plane_bounce():
    """Слой прыгает вверх-вниз."""
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
    """Диагональная волна."""
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
    """Только рёбра куба."""
    clear_cube()
    cube[0] = 0b111111111
    cube[1] = 0b101010101
    cube[2] = 0b111111111
    show_for(2000)
    clear_cube()
    show_for(500)


def anim_fireworks():
    """Имитация фейерверка (вдохновлено оригинальным 8x8x8)."""
    for _ in range(5):
        # Ракета летит вверх по центральному столбцу (C4)
        for z in range(NUM_LAYERS):
            clear_cube()
            cube[z] = (1 << 4)
            show_for(200)
        # Взрыв — все LED верхнего слоя
        clear_cube()
        cube[2] = 0b111111111
        show_for(300)
        # Разлёт — все слои, потом гаснут
        fill_cube()
        show_for(200)
        # Гаснут сверху вниз
        cube[2] = 0
        show_for(150)
        cube[1] = 0
        show_for(150)
        cube[0] = 0
        show_for(300)


# === Основная программа ===

def main():
    # Инициализация — все пины LOW
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
