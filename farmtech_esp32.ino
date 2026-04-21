// ============================================================
// FarmTech Solutions - Sistema de Irrigação Inteligente
// Cultura: Milho
// Plataforma: ESP32 (Wokwi)
// Sensores: DHT22, LDR, 3x Botões (N, P, K), Relé
// ============================================================

#include <DHT.h>

// ---- Pinos ----
#define PIN_DHT       4    // DHT22 - umidade (simula umidade do solo)
#define PIN_LDR       34   // LDR   - luz analógica (simula pH)
#define PIN_BTN_N     12   // Botão Nitrogênio
#define PIN_BTN_P     13   // Botão Fósforo
#define PIN_BTN_K     14   // Botão Potássio
#define PIN_RELE      26   // Relé - bomba d'água

// ---- Configurações do DHT ----
#define DHT_TYPE DHT22
DHT dht(PIN_DHT, DHT_TYPE);

// ---- Parâmetros ideais para MILHO ----
// Umidade do solo: irrigar se < 50%
#define UMIDADE_MIN       50.0

// pH ideal: 5.5 a 7.0
// LDR retorna 0-4095 (12 bits ADC no ESP32)
// Mapeamos para pH 0-14
#define PH_MIN            5.5
#define PH_MAX            7.0

// Variável de controle: chuva prevista via Python (Serial)
// 0 = sem chuva prevista, 1 = chuva prevista
int chuva_prevista = 0;

// ---- Funções auxiliares ----

float lerPH() {
  int ldr_raw = analogRead(PIN_LDR);
  // Mapeia 0-4095 para pH 0.0-14.0
  float ph = map(ldr_raw, 0, 4095, 0, 140) / 10.0;
  return ph;
}

bool lerNutriente(int pino) {
  // Botão pressionado = nutriente presente (true)
  // Pull-up interno: LOW = pressionado
  return (digitalRead(pino) == LOW);
}

void ligarBomba() {
  digitalWrite(PIN_RELE, HIGH);
  Serial.println("[BOMBA] LIGADA - Irrigando lavoura de milho...");
}

void desligarBomba() {
  digitalWrite(PIN_RELE, LOW);
  Serial.println("[BOMBA] DESLIGADA");
}

// ---- Leitura de dados do Python via Serial ----
// Envie "CHUVA:1" ou "CHUVA:0" pelo Monitor Serial
void lerSerial() {
  if (Serial.available() > 0) {
    String entrada = Serial.readStringUntil('\n');
    entrada.trim();
    if (entrada.startsWith("CHUVA:")) {
      chuva_prevista = entrada.substring(6).toInt();
      if (chuva_prevista == 1) {
        Serial.println("[CLIMA] Previsão de chuva recebida - irrigação suspensa.");
      } else {
        Serial.println("[CLIMA] Sem previsão de chuva.");
      }
    }
  }
}

// ---- Setup ----
void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(PIN_BTN_N, INPUT_PULLUP);
  pinMode(PIN_BTN_P, INPUT_PULLUP);
  pinMode(PIN_BTN_K, INPUT_PULLUP);
  pinMode(PIN_RELE, OUTPUT);

  digitalWrite(PIN_RELE, LOW); // Bomba começa desligada

  Serial.println("============================================");
  Serial.println("  FarmTech Solutions - Irrigacao Inteligente");
  Serial.println("  Cultura: Milho");
  Serial.println("============================================");
  Serial.println("Dica: envie CHUVA:1 ou CHUVA:0 pelo Serial");
  Serial.println();
}

// ---- Loop principal ----
void loop() {
  lerSerial(); // Verifica dados do Python

  // Leitura dos sensores
  float umidade  = dht.readHumidity();
  float temp     = dht.readTemperature();
  float ph       = lerPH();
  bool  n_ok     = lerNutriente(PIN_BTN_N);
  bool  p_ok     = lerNutriente(PIN_BTN_P);
  bool  k_ok     = lerNutriente(PIN_BTN_K);

  // Verificação de leitura válida do DHT22
  if (isnan(umidade) || isnan(temp)) {
    Serial.println("[ERRO] Falha na leitura do DHT22!");
    delay(2000);
    return;
  }

  // ---- Exibição no Monitor Serial ----
  Serial.println("---- Leitura dos Sensores ----");
  Serial.print("Umidade do solo : "); Serial.print(umidade);  Serial.println(" %");
  Serial.print("Temperatura     : "); Serial.print(temp);     Serial.println(" C");
  Serial.print("pH do solo      : "); Serial.println(ph);
  Serial.print("Nitrogenio (N)  : "); Serial.println(n_ok ? "PRESENTE" : "AUSENTE");
  Serial.print("Fosforo (P)     : "); Serial.println(p_ok ? "PRESENTE" : "AUSENTE");
  Serial.print("Potassio (K)    : "); Serial.println(k_ok ? "PRESENTE" : "AUSENTE");
  Serial.print("Chuva prevista  : "); Serial.println(chuva_prevista ? "SIM" : "NAO");

  // ---- Alertas de nutrientes ----
  if (!n_ok) Serial.println("[ALERTA] Nitrogenio baixo! Considere adubar.");
  if (!p_ok) Serial.println("[ALERTA] Fosforo baixo! Considere adubar.");
  if (!k_ok) Serial.println("[ALERTA] Potassio baixo! Considere adubar.");

  // ---- Alerta de pH ----
  if (ph < PH_MIN) {
    Serial.println("[ALERTA] pH abaixo do ideal para milho (< 5.5). Adicione calcario.");
  } else if (ph > PH_MAX) {
    Serial.println("[ALERTA] pH acima do ideal para milho (> 7.0). Verifique o solo.");
  }

  // ---- Lógica de decisão de irrigação ----
  // Regra: Liga bomba se:
  //   1. Umidade do solo < 50%
  //   2. pH dentro da faixa ideal (5.5 a 7.0)
  //   3. Não há previsão de chuva (dado do Python)

  bool ph_ok       = (ph >= PH_MIN && ph <= PH_MAX);
  bool umidade_baixa = (umidade < UMIDADE_MIN);
  bool sem_chuva   = (chuva_prevista == 0);

  Serial.println("---- Decisao de Irrigacao ----");
  Serial.print("Umidade baixa? "); Serial.println(umidade_baixa ? "SIM" : "NAO");
  Serial.print("pH ideal?      "); Serial.println(ph_ok         ? "SIM" : "NAO");
  Serial.print("Sem chuva?     "); Serial.println(sem_chuva     ? "SIM" : "NAO");

  if (umidade_baixa && ph_ok && sem_chuva) {
    ligarBomba();
  } else {
    desligarBomba();
    if (!umidade_baixa)  Serial.println("[INFO] Solo com umidade suficiente.");
    if (!ph_ok)          Serial.println("[INFO] pH fora da faixa - corrigir antes de irrigar.");
    if (!sem_chuva)      Serial.println("[INFO] Chuva prevista - irrigacao suspensa.");
  }

  Serial.println("==============================");
  delay(5000); // Atualiza a cada 5 segundos
}
