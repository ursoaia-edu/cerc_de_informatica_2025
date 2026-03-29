/*
 * LED Куб 3x3x3 — Arduino Uno
 * ============================
 * Упрощённая версия проекта 8x8x8 LED Cube
 * https://www.instructables.com/8x8x8-Arduino-LED-Cube/
 *
 * Подключение:
 *   Столбцы (аноды) → D2..D10 через резисторы 220 Ом
 *   Слои   (катоды) → D11..D13 через NPN транзисторы 2N2222
 *
 *   Вид сверху (столбцы):
 *       C0(D2)  C1(D3)  C2(D4)
 *       C3(D5)  C4(D6)  C5(D7)
 *       C6(D8)  C7(D9)  C8(D10)
 *
 *   Слои:
 *       Layer 0 (нижний)  → D11
 *       Layer 1 (средний) → D12
 *       Layer 2 (верхний) → D13
 */

// === Настройки пинов ===
const byte COL_PINS[9] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
const byte LAYER_PINS[3] = {11, 12, 13};

// Количество слоёв и столбцов
#define NUM_LAYERS  3
#define NUM_COLS    9

// Буфер куба: cube[layer] — битовая маска 9 столбцов
// bit 0 = C0, bit 1 = C1, ... bit 8 = C8
uint16_t cube[NUM_LAYERS];

// Задержка мультиплексирования (мс) — persistence of vision
#define POV_DELAY 3

// === Вспомогательные функции ===

// Отобразить текущее состояние куба (один цикл POV)
void displayCube() {
  for (byte layer = 0; layer < NUM_LAYERS; layer++) {
    // Выключить все слои
    for (byte l = 0; l < NUM_LAYERS; l++) {
      digitalWrite(LAYER_PINS[l], LOW);
    }
    // Установить столбцы для текущего слоя
    for (byte col = 0; col < NUM_COLS; col++) {
      digitalWrite(COL_PINS[col], (cube[layer] >> col) & 1);
    }
    // Включить текущий слой
    digitalWrite(LAYER_PINS[layer], HIGH);
    delay(POV_DELAY);
  }
  // Выключить последний слой
  for (byte l = 0; l < NUM_LAYERS; l++) {
    digitalWrite(LAYER_PINS[l], LOW);
  }
}

// Отображать куб в течение duration мс
void showFor(unsigned long duration) {
  unsigned long start = millis();
  while (millis() - start < duration) {
    displayCube();
  }
}

// Очистить буфер куба
void clearCube() {
  for (byte i = 0; i < NUM_LAYERS; i++) {
    cube[i] = 0;
  }
}

// Заполнить весь куб
void fillCube() {
  for (byte i = 0; i < NUM_LAYERS; i++) {
    cube[i] = 0b111111111;
  }
}

// Установить отдельный LED: (x, y, z), state = HIGH/LOW
// x = 0..2 (колонка), y = 0..2 (ряд), z = 0..2 (слой)
void setLed(byte x, byte y, byte z, bool state) {
  byte col = y * 3 + x;  // индекс столбца 0..8
  if (state) {
    cube[z] |= (1 << col);
  } else {
    cube[z] &= ~(1 << col);
  }
}

// === Анимации ===

// 1. Включить/выключить весь куб
void animAllOnOff() {
  fillCube();
  showFor(1000);
  clearCube();
  showFor(500);
}

// 2. Последовательное зажигание слоёв
void animLayerWipe() {
  for (int i = 0; i < 3; i++) {
    clearCube();
    cube[i] = 0b111111111;
    showFor(400);
  }
  // Обратно
  for (int i = 1; i >= 0; i--) {
    clearCube();
    cube[i] = 0b111111111;
    showFor(400);
  }
}

// 3. Последовательное зажигание столбцов
void animColumnWipe() {
  for (byte col = 0; col < NUM_COLS; col++) {
    clearCube();
    for (byte layer = 0; layer < NUM_LAYERS; layer++) {
      cube[layer] = (1 << col);
    }
    showFor(200);
  }
}

// 4. Эффект дождя
void animRain() {
  for (int drop = 0; drop < 15; drop++) {
    byte col = random(NUM_COLS);
    // Капля падает сверху вниз
    for (int z = NUM_LAYERS - 1; z >= 0; z--) {
      clearCube();
      cube[z] = (1 << col);
      showFor(150);
    }
  }
  clearCube();
}

// 5. Спираль по периметру
void animSpiral() {
  // Порядок обхода периметра: 0,1,2,5,8,7,6,3
  const byte perimeterOrder[] = {0, 1, 2, 5, 8, 7, 6, 3};
  for (byte repeat = 0; repeat < 3; repeat++) {
    for (byte i = 0; i < 8; i++) {
      clearCube();
      byte col = perimeterOrder[i];
      for (byte layer = 0; layer < NUM_LAYERS; layer++) {
        cube[layer] = (1 << col);
      }
      showFor(150);
    }
  }
}

// 6. Случайное мигание
void animRandomBlink() {
  for (int i = 0; i < 30; i++) {
    clearCube();
    byte x = random(3);
    byte y = random(3);
    byte z = random(3);
    setLed(x, y, z, true);
    showFor(100);
  }
}

// 7. Слой прыгает вверх-вниз
void animPlaneBounce() {
  for (byte repeat = 0; repeat < 4; repeat++) {
    for (byte i = 0; i < NUM_LAYERS; i++) {
      clearCube();
      cube[i] = 0b111111111;
      showFor(250);
    }
    for (int i = NUM_LAYERS - 2; i >= 1; i--) {
      clearCube();
      cube[i] = 0b111111111;
      showFor(250);
    }
  }
}

// 8. Диагональная волна
void animDiagonalWipe() {
  // Диагональные группы столбцов (по сумме x+y)
  const uint16_t diags[] = {
    0b000000001,  // x+y=0 → C0
    0b000001010,  // x+y=1 → C1, C3
    0b001010100,  // x+y=2 → C2, C4, C6
    0b010100000,  // x+y=3 → C5, C7
    0b100000000   // x+y=4 → C8
  };

  for (byte repeat = 0; repeat < 3; repeat++) {
    for (byte d = 0; d < 5; d++) {
      clearCube();
      for (byte layer = 0; layer < NUM_LAYERS; layer++) {
        cube[layer] = diags[d];
      }
      showFor(250);
    }
  }
}

// 9. Только рёбра куба
void animEdgesOnly() {
  clearCube();
  // Нижний слой — все 9
  cube[0] = 0b111111111;
  // Средний слой — только углы и стороны (периметр)
  cube[1] = 0b101010101;
  // Верхний слой — все 9
  cube[2] = 0b111111111;
  showFor(2000);
  clearCube();
  showFor(500);
}

// 10. Имитация фейерверка (вдохновлено оригинальным 8x8x8)
void animFireworks() {
  for (byte burst = 0; burst < 5; burst++) {
    // Ракета летит вверх по центральному столбцу (C4)
    for (byte z = 0; z < NUM_LAYERS; z++) {
      clearCube();
      cube[z] = (1 << 4);  // центральный столбец
      showFor(200);
    }

    // Взрыв — все LED верхнего слоя
    clearCube();
    cube[2] = 0b111111111;
    showFor(300);

    // Разлёт — все слои, потом гаснут
    fillCube();
    showFor(200);

    // Гаснут сверху вниз
    cube[2] = 0;
    showFor(150);
    cube[1] = 0;
    showFor(150);
    cube[0] = 0;
    showFor(300);
  }
}

// === Основная программа ===

void setup() {
  // Настроить пины столбцов как выходы
  for (byte i = 0; i < NUM_COLS; i++) {
    pinMode(COL_PINS[i], OUTPUT);
    digitalWrite(COL_PINS[i], LOW);
  }

  // Настроить пины слоёв как выходы
  for (byte i = 0; i < NUM_LAYERS; i++) {
    pinMode(LAYER_PINS[i], OUTPUT);
    digitalWrite(LAYER_PINS[i], LOW);
  }

  randomSeed(analogRead(A0));
  clearCube();
}

void loop() {
  animAllOnOff();
  animLayerWipe();
  animColumnWipe();
  animPlaneBounce();
  animSpiral();
  animDiagonalWipe();
  animRain();
  animRandomBlink();
  animEdgesOnly();
  animFireworks();
}
