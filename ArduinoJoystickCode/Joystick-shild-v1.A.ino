#define X_PIN A0
#define Y_PIN A1
#define K_PIN 8  // Кнопка джойстика

#define INVERT_X // Инвертиция оси X
//#define INVERT_Y // Инвертация оси Y

// Кнопки A, B, C, D, E, F
const byte BUTTON_PINS[] = {2, 3, 4, 5, 6, 7};
const int NUM_BUTTONS = sizeof(BUTTON_PINS) / sizeof(BUTTON_PINS[0]);

void setup() {
  Serial.begin(115200);
  pinMode(K_PIN, INPUT_PULLUP);
  for (int i = 0; i < NUM_BUTTONS; i++) {
    pinMode(BUTTON_PINS[i], INPUT_PULLUP);
  }
}

void loop() {
  // 1. Читаем и нормализуем оси джойстика (-1.0 .. 1.0)
  float x_val = (analogRead(X_PIN) - 344.0) / 344.0;
  float y_val = (analogRead(Y_PIN) - 340.0) / 340.0;

  #ifdef INVERT_X
  x_val *= -1;
  #endif
  
  #ifdef INVERT_Y
  y_val *= -1;
  #endif

  // 2. Читаем состояния кнопок (0 - нажата, 1 - не нажата)
  int button_states[NUM_BUTTONS + 1];
  button_states[0] = !digitalRead(K_PIN); // Инвертируем, чтобы нажатие было "1"
  for (int i = 0; i < NUM_BUTTONS; i++) {
    button_states[i + 1] = !digitalRead(BUTTON_PINS[i]);
  }

  // 3. Формируем строку для отправки
  Serial.print(x_val, 4); Serial.print(",");
  Serial.print(y_val, 4); Serial.print(",");
  Serial.print(button_states[0]);
  for (int i = 1; i <= NUM_BUTTONS; i++) {
    Serial.print(",");
    Serial.print(button_states[i]);
  }
  Serial.println();

  delay(20); // Частота отправки ~50 Гц
}