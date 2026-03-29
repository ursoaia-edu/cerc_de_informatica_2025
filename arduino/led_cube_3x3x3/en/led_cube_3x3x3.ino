/*
 * 3x3x3 LED Cube — Arduino Uno
 * ============================
 * Simplified version of the 8x8x8 LED Cube project
 * https://www.instructables.com/8x8x8-Arduino-LED-Cube/
 *
 * Wiring:
 *   Columns (anodes) → D2..D10 through 220 Ω resistors
 *   Layers  (cathodes) → D11..D13 through NPN transistors 2N2222
 *
 *   Top view (columns):
 *       C0(D2)  C1(D3)  C2(D4)
 *       C3(D5)  C4(D6)  C5(D7)
 *       C6(D8)  C7(D9)  C8(D10)
 *
 *   Layers:
 *       Layer 0 (bottom) → D11
 *       Layer 1 (middle) → D12
 *       Layer 2 (top)    → D13
 */

// === Pin configuration ===
const byte COL_PINS[9] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
const byte LAYER_PINS[3] = {11, 12, 13};

// Number of layers and columns
#define NUM_LAYERS  3
#define NUM_COLS    9

// Cube buffer: cube[layer] — bitmask for 9 columns
// bit 0 = C0, bit 1 = C1, ... bit 8 = C8
uint16_t cube[NUM_LAYERS];

// Multiplexing delay (ms) — persistence of vision
#define POV_DELAY 3

// === Helper functions ===

// Display the current cube state (one POV cycle)
void displayCube() {
  for (byte layer = 0; layer < NUM_LAYERS; layer++) {
    // Turn off all layers
    for (byte l = 0; l < NUM_LAYERS; l++) {
      digitalWrite(LAYER_PINS[l], LOW);
    }
    // Set columns for the current layer
    for (byte col = 0; col < NUM_COLS; col++) {
      digitalWrite(COL_PINS[col], (cube[layer] >> col) & 1);
    }
    // Turn on the current layer
    digitalWrite(LAYER_PINS[layer], HIGH);
    delay(POV_DELAY);
  }
  // Turn off the last layer
  for (byte l = 0; l < NUM_LAYERS; l++) {
    digitalWrite(LAYER_PINS[l], LOW);
  }
}

// Display the cube for duration ms
void showFor(unsigned long duration) {
  unsigned long start = millis();
  while (millis() - start < duration) {
    displayCube();
  }
}

// Clear the cube buffer
void clearCube() {
  for (byte i = 0; i < NUM_LAYERS; i++) {
    cube[i] = 0;
  }
}

// Fill the entire cube
void fillCube() {
  for (byte i = 0; i < NUM_LAYERS; i++) {
    cube[i] = 0b111111111;
  }
}

// Set an individual LED: (x, y, z), state = HIGH/LOW
// x = 0..2 (column), y = 0..2 (row), z = 0..2 (layer)
void setLed(byte x, byte y, byte z, bool state) {
  byte col = y * 3 + x;  // column index 0..8
  if (state) {
    cube[z] |= (1 << col);
  } else {
    cube[z] &= ~(1 << col);
  }
}

// === Animations ===

// 1. Turn the entire cube on/off
void animAllOnOff() {
  fillCube();
  showFor(1000);
  clearCube();
  showFor(500);
}

// 2. Sequential layer lighting
void animLayerWipe() {
  for (int i = 0; i < 3; i++) {
    clearCube();
    cube[i] = 0b111111111;
    showFor(400);
  }
  // Reverse
  for (int i = 1; i >= 0; i--) {
    clearCube();
    cube[i] = 0b111111111;
    showFor(400);
  }
}

// 3. Sequential column lighting
void animColumnWipe() {
  for (byte col = 0; col < NUM_COLS; col++) {
    clearCube();
    for (byte layer = 0; layer < NUM_LAYERS; layer++) {
      cube[layer] = (1 << col);
    }
    showFor(200);
  }
}

// 4. Rain effect
void animRain() {
  for (int drop = 0; drop < 15; drop++) {
    byte col = random(NUM_COLS);
    // Drop falls from top to bottom
    for (int z = NUM_LAYERS - 1; z >= 0; z--) {
      clearCube();
      cube[z] = (1 << col);
      showFor(150);
    }
  }
  clearCube();
}

// 5. Spiral along the perimeter
void animSpiral() {
  // Perimeter traversal order: 0,1,2,5,8,7,6,3
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

// 6. Random blinking
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

// 7. Layer bounces up and down
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

// 8. Diagonal wave
void animDiagonalWipe() {
  // Diagonal column groups (by x+y sum)
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

// 9. Cube edges only
void animEdgesOnly() {
  clearCube();
  // Bottom layer — all 9
  cube[0] = 0b111111111;
  // Middle layer — corners and sides only (perimeter)
  cube[1] = 0b101010101;
  // Top layer — all 9
  cube[2] = 0b111111111;
  showFor(2000);
  clearCube();
  showFor(500);
}

// 10. Fireworks simulation (inspired by the original 8x8x8)
void animFireworks() {
  for (byte burst = 0; burst < 5; burst++) {
    // Rocket flies up the center column (C4)
    for (byte z = 0; z < NUM_LAYERS; z++) {
      clearCube();
      cube[z] = (1 << 4);  // center column
      showFor(200);
    }

    // Explosion — all LEDs on the top layer
    clearCube();
    cube[2] = 0b111111111;
    showFor(300);

    // Scatter — all layers, then fade out
    fillCube();
    showFor(200);

    // Fade out from top to bottom
    cube[2] = 0;
    showFor(150);
    cube[1] = 0;
    showFor(150);
    cube[0] = 0;
    showFor(300);
  }
}

// === Main program ===

void setup() {
  // Configure column pins as outputs
  for (byte i = 0; i < NUM_COLS; i++) {
    pinMode(COL_PINS[i], OUTPUT);
    digitalWrite(COL_PINS[i], LOW);
  }

  // Configure layer pins as outputs
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
