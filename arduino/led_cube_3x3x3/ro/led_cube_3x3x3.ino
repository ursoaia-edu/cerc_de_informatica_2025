/*
 * Cub LED 3x3x3 — Arduino Uno
 * ============================
 * Versiune simplificată a proiectului 8x8x8 LED Cube
 * https://www.instructables.com/8x8x8-Arduino-LED-Cube/
 *
 * Conectare:
 *   Coloane (anoduri) → D2..D10 prin rezistoare de 220 Ω
 *   Straturi (catoduri) → D11..D13 prin tranzistoare NPN 2N2222
 *
 *   Vedere de sus (coloane):
 *       C0(D2)  C1(D3)  C2(D4)
 *       C3(D5)  C4(D6)  C5(D7)
 *       C6(D8)  C7(D9)  C8(D10)
 *
 *   Straturi:
 *       Layer 0 (inferior)  → D11
 *       Layer 1 (mijlociu)  → D12
 *       Layer 2 (superior)  → D13
 */

// === Configurarea pinilor ===
const byte COL_PINS[9] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
const byte LAYER_PINS[3] = {11, 12, 13};

// Numărul de straturi și coloane
#define NUM_LAYERS  3
#define NUM_COLS    9

// Buffer-ul cubului: cube[layer] — mască de biți pentru 9 coloane
// bit 0 = C0, bit 1 = C1, ... bit 8 = C8
uint16_t cube[NUM_LAYERS];

// Întârziere multiplexare (ms) — persistence of vision
#define POV_DELAY 3

// === Funcții auxiliare ===

// Afișează starea curentă a cubului (un ciclu POV)
void displayCube() {
  for (byte layer = 0; layer < NUM_LAYERS; layer++) {
    // Oprește toate straturile
    for (byte l = 0; l < NUM_LAYERS; l++) {
      digitalWrite(LAYER_PINS[l], LOW);
    }
    // Setează coloanele pentru stratul curent
    for (byte col = 0; col < NUM_COLS; col++) {
      digitalWrite(COL_PINS[col], (cube[layer] >> col) & 1);
    }
    // Pornește stratul curent
    digitalWrite(LAYER_PINS[layer], HIGH);
    delay(POV_DELAY);
  }
  // Oprește ultimul strat
  for (byte l = 0; l < NUM_LAYERS; l++) {
    digitalWrite(LAYER_PINS[l], LOW);
  }
}

// Afișează cubul pe durata a duration ms
void showFor(unsigned long duration) {
  unsigned long start = millis();
  while (millis() - start < duration) {
    displayCube();
  }
}

// Golește buffer-ul cubului
void clearCube() {
  for (byte i = 0; i < NUM_LAYERS; i++) {
    cube[i] = 0;
  }
}

// Umple întregul cub
void fillCube() {
  for (byte i = 0; i < NUM_LAYERS; i++) {
    cube[i] = 0b111111111;
  }
}

// Setează un LED individual: (x, y, z), state = HIGH/LOW
// x = 0..2 (coloană), y = 0..2 (rând), z = 0..2 (strat)
void setLed(byte x, byte y, byte z, bool state) {
  byte col = y * 3 + x;  // indexul coloanei 0..8
  if (state) {
    cube[z] |= (1 << col);
  } else {
    cube[z] &= ~(1 << col);
  }
}

// === Animații ===

// 1. Pornire/oprire întregul cub
void animAllOnOff() {
  fillCube();
  showFor(1000);
  clearCube();
  showFor(500);
}

// 2. Aprinderea secvențială a straturilor
void animLayerWipe() {
  for (int i = 0; i < 3; i++) {
    clearCube();
    cube[i] = 0b111111111;
    showFor(400);
  }
  // Înapoi
  for (int i = 1; i >= 0; i--) {
    clearCube();
    cube[i] = 0b111111111;
    showFor(400);
  }
}

// 3. Aprinderea secvențială a coloanelor
void animColumnWipe() {
  for (byte col = 0; col < NUM_COLS; col++) {
    clearCube();
    for (byte layer = 0; layer < NUM_LAYERS; layer++) {
      cube[layer] = (1 << col);
    }
    showFor(200);
  }
}

// 4. Efect de ploaie
void animRain() {
  for (int drop = 0; drop < 15; drop++) {
    byte col = random(NUM_COLS);
    // Picătura cade de sus în jos
    for (int z = NUM_LAYERS - 1; z >= 0; z--) {
      clearCube();
      cube[z] = (1 << col);
      showFor(150);
    }
  }
  clearCube();
}

// 5. Spirală pe perimetru
void animSpiral() {
  // Ordinea parcurgerii perimetrului: 0,1,2,5,8,7,6,3
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

// 6. Clipire aleatoare
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

// 7. Stratul sare în sus și în jos
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

// 8. Undă diagonală
void animDiagonalWipe() {
  // Grupuri diagonale de coloane (după suma x+y)
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

// 9. Doar muchiile cubului
void animEdgesOnly() {
  clearCube();
  // Stratul inferior — toate 9
  cube[0] = 0b111111111;
  // Stratul mijlociu — doar colțuri și laturi (perimetru)
  cube[1] = 0b101010101;
  // Stratul superior — toate 9
  cube[2] = 0b111111111;
  showFor(2000);
  clearCube();
  showFor(500);
}

// 10. Simulare de artificii (inspirat din originalul 8x8x8)
void animFireworks() {
  for (byte burst = 0; burst < 5; burst++) {
    // Racheta urcă pe coloana centrală (C4)
    for (byte z = 0; z < NUM_LAYERS; z++) {
      clearCube();
      cube[z] = (1 << 4);  // coloana centrală
      showFor(200);
    }

    // Explozie — toate LED-urile stratului superior
    clearCube();
    cube[2] = 0b111111111;
    showFor(300);

    // Împrăștiere — toate straturile, apoi se sting
    fillCube();
    showFor(200);

    // Se sting de sus în jos
    cube[2] = 0;
    showFor(150);
    cube[1] = 0;
    showFor(150);
    cube[0] = 0;
    showFor(300);
  }
}

// === Programul principal ===

void setup() {
  // Configurează pinii coloanelor ca ieșiri
  for (byte i = 0; i < NUM_COLS; i++) {
    pinMode(COL_PINS[i], OUTPUT);
    digitalWrite(COL_PINS[i], LOW);
  }

  // Configurează pinii straturilor ca ieșiri
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
