#include <Wire.h>
#include "DFRobot_HuskylensV2.h"

HuskylensV2 huskylens;

// Trained gesture IDs
#define ID_FIST     1   // Fist = aim/draw
#define ID_PALM     2   // Open hand = release/fire


bool grabbed = false;
int baseX = -1, baseY = -1;
unsigned long grabStartMs = 0;
float lastPower = 0, lastAngle = 0;

template<typename T>
T clamp(T v, T lo, T hi) { return v < lo ? lo : (v > hi ? hi : v); }

bool readBoxByID(int id, int &x, int &y, int &w, int &h) {
  // Use the cache API to get the first target with this ID
  Result* r = huskylens.getCachedResultByID(ALGORITHM_HAND_RECOGNITION, id);
  if (r == NULL) return false;

  x = r->xCenter;
  y = r->yCenter;
  w = r->width;
  h = r->height;

  // Validation (HUSKYLENS standard resolution 320x240)
  if (w <= 0 || h <= 0) return false;
  if (x < 0 || x > 320 || y < 0 || y > 240) return false;
  return true;
}

void sendGrabJSON(float power, float angle, int id, int x, int y, int w, int h) {
  Serial.print("{\"gesture\":\"grab\",\"id\":");
  Serial.print(id);
  Serial.print(",\"power\":");
  Serial.print(power, 1);
  Serial.print(",\"angle\":");
  Serial.print(angle, 4);
  Serial.print(",\"x\":");
  Serial.print(x);
  Serial.print(",\"y\":");
  Serial.print(y);
  Serial.print(",\"w\":");
  Serial.print(w);
  Serial.print(",\"h\":");
  Serial.print(h);
  Serial.print(",\"held_ms\":");
  Serial.print((unsigned long)(millis() - grabStartMs));
  Serial.println("}");
}

void sendSimpleJSON(const char* g, int id) {
  Serial.print("{\"gesture\":\""); Serial.print(g);
  Serial.print("\",\"id\":"); Serial.print(id);
  Serial.println("}");
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  while (!huskylens.begin(Wire)) delay(100);
  huskylens.switchAlgorithm(ALGORITHM_HAND_RECOGNITION);
  Serial.println("{\"status\":\"ready\",\"mode\":\"learned_ID\"}");
}

void loop() {
  huskylens.getResult(ALGORITHM_HAND_RECOGNITION);
  if (!huskylens.available(ALGORITHM_HAND_RECOGNITION)) { delay(30); return; }

  int x, y, w, h;

  // 1) Fist priority: enter/maintain aiming
  if (readBoxByID(ID_FIST, x, y, w, h)) {
    if (!grabbed) {
      grabbed = true;
      baseX = x; baseY = y;
      grabStartMs = millis();
      lastPower = 0; lastAngle = 0;
    }
    int dx = x - baseX;
    int dy = y - baseY;

    float dist  = sqrtf((float)dx*dx + (float)dy*dy);
    float power = clamp(dist / 2.0f, 0.0f, 100.0f); // 0~100
    float angle = atan2f(-dy, (float)dx);           // Consistent with the game

    lastPower = power; lastAngle = angle;
    sendGrabJSON(power, angle, ID_FIST, x, y, w, h);
    delay(30);
    return;
  }

  // 2) Open hand: if drawing, then release
  if (readBoxByID(ID_PALM, x, y, w, h)) {
    if (grabbed) {
      Serial.print("{\"gesture\":\"release\",\"id\":");
      Serial.print(ID_PALM);
      Serial.print(",\"power\":"); Serial.print(lastPower, 1);
      Serial.print(",\"angle\":"); Serial.print(lastAngle, 4);
      Serial.println("}");
      grabbed = false;
      baseX = baseY = -1;
      lastPower = lastAngle = 0;
    } else {
      sendSimpleJSON("hand_open", ID_PALM);
    }
    delay(50);
    return;
  }

  delay(100);
}
