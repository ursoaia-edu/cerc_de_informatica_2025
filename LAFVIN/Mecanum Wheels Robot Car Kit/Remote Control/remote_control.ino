// ============================================================
//  Universal Remote Control — LAFVIN Mecanum Wheels Robot Car
//  ESP32 + 2x PS2 Joystick + Bluetooth Classic (built-in)
// ============================================================

#include "BluetoothSerial.h"
#include <math.h>

BluetoothSerial bt;

// ── CONFIG ──────────────────────────────────────────────────

// MAC address of HC-06 on the car (find via BT scan or AT+ADDR on HC-06)
// Format: {0xXX, 0xXX, 0xXX, 0xXX, 0xXX, 0xXX}
// Set to all zeros to connect by name instead
uint8_t BT_MAC[] = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
const char* BT_NAME = "HC-06";  // used if MAC is all zeros

// Left joystick (translation)
const int JOY_L_VRX = 34;  // ADC1_CH6
const int JOY_L_VRY = 35;  // ADC1_CH7

// Right joystick (rotation)
const int JOY_R_VRX = 36;  // ADC1_CH0 (VP)

// Buttons (active LOW, internal pull-up)
const int BTN1_PIN = 33;
const int BTN2_PIN = 32;
const int BTN3_PIN = 25;

// Status LED
const int LED_PIN = 2;

// Dead zone: center (2048) ± DEAD
const int CENTER   = 2048;
const int DEAD     = 650;

// Repeat interval (ms) — car needs continuous commands
const unsigned long REPEAT_MS = 150;

// Debounce (ms)
const unsigned long DEBOUNCE_MS = 200;

// ── DIRECTION ENUM ──────────────────────────────────────────

enum Direction {
  DIR_STOP,
  DIR_FORWARD,
  DIR_BACKWARD,
  DIR_LEFT,
  DIR_RIGHT,
  DIR_UP_LEFT,
  DIR_UP_RIGHT,
  DIR_DOWN_LEFT,
  DIR_DOWN_RIGHT,
  DIR_ROTATE_LEFT,
  DIR_ROTATE_RIGHT,
  DIR_COUNT
};

// Direction → command string
const char* COMMANDS[] = {
  "%S#",   // DIR_STOP
  "%A#",   // DIR_FORWARD
  "%B#",   // DIR_BACKWARD
  "%C#",   // DIR_LEFT
  "%D#",   // DIR_RIGHT
  "%G#",   // DIR_UP_LEFT
  "%H#",   // DIR_UP_RIGHT
  "%I#",   // DIR_DOWN_LEFT
  "%J#",   // DIR_DOWN_RIGHT
  "%E#",   // DIR_ROTATE_LEFT
  "%F#",   // DIR_ROTATE_RIGHT
};

// Button commands
const char* BTN_COMMANDS[][2] = {
  {"%T#", "%S#"},   // BTN1: Ultrasonic Avoidance / Stop
  {"%W#", "%S#"},   // BTN2: Ultrasonic Follow / Stop
  {"%K#", "%L#"},   // BTN3: Drift Left / Drift Right
};

// ── STATE ───────────────────────────────────────────────────

Direction prevDirection = DIR_COUNT;  // invalid → forces first send
unsigned long repeatTimer = 0;

bool btnStates[] = {false, false, false};
unsigned long btnLast[] = {0, 0, 0};
const int btnPins[] = {BTN1_PIN, BTN2_PIN, BTN3_PIN};
const int BTN_COUNT = 3;

// ── INPUT LAYER ─────────────────────────────────────────────

Direction readTranslation() {
  int x = analogRead(JOY_L_VRX);
  int y = analogRead(JOY_L_VRY);

  int dx = x - CENTER;
  int dy = CENTER - y;  // invert: low ADC = stick pushed forward

  if (abs(dx) < DEAD && abs(dy) < DEAD) {
    return DIR_STOP;
  }

  // atan2(dx, dy) → angle from north (forward), clockwise positive
  float angle = atan2((float)dx, (float)dy) * 180.0f / M_PI;
  if (angle < 0) angle += 360.0f;

  // 8 sectors of 45°
  if (angle < 22.5f  || angle >= 337.5f) return DIR_FORWARD;
  if (angle < 67.5f)  return DIR_UP_RIGHT;
  if (angle < 112.5f) return DIR_RIGHT;
  if (angle < 157.5f) return DIR_DOWN_RIGHT;
  if (angle < 202.5f) return DIR_BACKWARD;
  if (angle < 247.5f) return DIR_DOWN_LEFT;
  if (angle < 292.5f) return DIR_LEFT;
  return DIR_UP_LEFT;
}

Direction readRotation() {
  int x = analogRead(JOY_R_VRX);

  if (x < CENTER - DEAD) return DIR_ROTATE_LEFT;
  if (x > CENTER + DEAD) return DIR_ROTATE_RIGHT;
  return DIR_COUNT;  // DIR_COUNT = no rotation
}

// Returns command string if button toggled, nullptr otherwise
const char* readButtons() {
  unsigned long now = millis();
  for (int i = 0; i < BTN_COUNT; i++) {
    if (digitalRead(btnPins[i]) == LOW) {
      if (now - btnLast[i] > DEBOUNCE_MS) {
        btnLast[i] = now;
        btnStates[i] = !btnStates[i];
        return BTN_COMMANDS[i][btnStates[i] ? 0 : 1];
      }
    }
  }
  return nullptr;
}

// ── TRANSPORT LAYER ─────────────────────────────────────────

void transportConnect() {
  Serial.println("Connecting to car...");

  bool useMac = false;
  for (int i = 0; i < 6; i++) {
    if (BT_MAC[i] != 0) { useMac = true; break; }
  }

  bool connected = false;
  while (!connected) {
    // Blink while connecting
    digitalWrite(LED_PIN, !digitalRead(LED_PIN));
    delay(500);

    if (useMac) {
      connected = bt.connect(BT_MAC);
    } else {
      connected = bt.connect(BT_NAME);
    }

    if (!connected) {
      Serial.println("Connection failed, retrying...");
    }
  }

  digitalWrite(LED_PIN, HIGH);
  Serial.println("Connected!");
}

void transportSend(const char* cmd) {
  if (bt.connected()) {
    bt.print(cmd);
  }
}

// ── SETUP & LOOP ────────────────────────────────────────────

void setup() {
  Serial.begin(115200);

  // LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  // Buttons with internal pull-up
  for (int i = 0; i < BTN_COUNT; i++) {
    pinMode(btnPins[i], INPUT_PULLUP);
  }

  // ADC — ESP32 Arduino defaults to 12-bit (0–4095), no extra config needed

  // Bluetooth Classic
  bt.begin("ESP32 Remote", true);  // true = master mode
  transportConnect();

  repeatTimer = millis();
}

void loop() {
  // Reconnect if lost
  if (!bt.connected()) {
    digitalWrite(LED_PIN, LOW);
    transportConnect();
  }

  // 1. Buttons (highest priority)
  const char* btn = readButtons();
  if (btn != nullptr) {
    transportSend(btn);
    delay(50);
    return;
  }

  // 2. Right joystick (rotation) > Left joystick (translation)
  Direction rotation = readRotation();
  Direction direction = (rotation != DIR_COUNT) ? rotation : readTranslation();

  unsigned long now = millis();

  if (direction != prevDirection) {
    // Direction changed — send immediately
    transportSend(COMMANDS[direction]);
    prevDirection = direction;
    repeatTimer = now;
  } else if (direction != DIR_STOP && (now - repeatTimer) > REPEAT_MS) {
    // Still moving — repeat command (car needs continuous stream)
    transportSend(COMMANDS[direction]);
    repeatTimer = now;
  }

  delay(50);
}
