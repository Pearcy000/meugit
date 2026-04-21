# 🌽 FarmTech Solutions — Sistema de Irrigação Inteligente
### Fase 2 — IoT com ESP32 | Cultura: Milho

---

## 📋 Índice

- [Descrição do Projeto](#descrição-do-projeto)
- [Cultura Escolhida: Milho](#cultura-escolhida-milho)
- [Componentes e Sensores](#componentes-e-sensores)
- [Lógica de Irrigação](#lógica-de-irrigação)
- [Circuito no Wokwi](#circuito-no-wokwi)
- [Código ESP32 (C/C++)](#código-esp32-cc)
- [Ir Além — Integração Python + OpenWeather](#ir-além--integração-python--openweather)
- [Como Executar](#como-executar)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Vídeo de Demonstração](#vídeo-de-demonstração)
- [Integrantes](#integrantes)

---

## 📌 Descrição do Projeto

Este projeto faz parte da **Fase 2** do desafio da startup **FarmTech Solutions**, desenvolvido na FIAP. O objetivo é construir um sistema de irrigação automatizado e inteligente utilizando um ESP32 simulado na plataforma [Wokwi.com](https://wokwi.com), integrando sensores de umidade, pH e nutrientes do solo para decidir quando ligar ou desligar uma bomba d'água.

Como opcional do programa **Ir Além**, o sistema também integra dados meteorológicos em tempo real via **API OpenWeather** usando Python, permitindo suspender a irrigação automaticamente quando há previsão de chuva.

---

## 🌽 Cultura Escolhida: Milho

O milho foi escolhido por ser uma das culturas mais importantes do agronegócio brasileiro. Suas necessidades são bem documentadas e servem como base sólida para a lógica de irrigação.

| Parâmetro       | Valor ideal para Milho     |
|-----------------|---------------------------|
| Umidade do solo | Acima de 50%               |
| pH do solo      | 5,5 a 7,0                  |
| Nitrogênio (N)  | Essencial (alto consumo)   |
| Fósforo (P)     | Essencial (enraizamento)   |
| Potássio (K)    | Essencial (resistência)    |

> **Fonte:** Embrapa Milho e Sorgo — Recomendações técnicas para a cultura do milho.

---

## 🔧 Componentes e Sensores

| Componente       | Representa (simulação)     | Pino ESP32 |
|------------------|---------------------------|------------|
| **DHT22**        | Umidade do solo            | GPIO 4     |
| **LDR**          | pH do solo (0,0 a 14,0)    | GPIO 34    |
| **Botão Verde N**| Nível de Nitrogênio        | GPIO 12    |
| **Botão Verde P**| Nível de Fósforo           | GPIO 13    |
| **Botão Verde K**| Nível de Potássio          | GPIO 14    |
| **Relé Azul**    | Bomba d'água               | GPIO 26    |

### Substituições didáticas adotadas

- **DHT22** → mede umidade do ar, mas é usado aqui como simulação da umidade do solo.
- **LDR** → mede intensidade de luz. O valor analógico (0–4095) é mapeado para a escala de pH (0,0–14,0). Quanto mais luz, maior o pH simulado.
- **Botões** → representam sensores de nutrientes N, P e K. Botão pressionado = nutriente **presente**; solto = **ausente**.
- **Relé** → representa a bomba d'água real da lavoura.

---

## 🧠 Lógica de Irrigação

A bomba d'água (relé) é **ligada** quando **todas** as condições abaixo são satisfeitas:

```
LIGAR BOMBA se:
  ✅ Umidade do solo < 50%        (solo seco, precisa de água)
  ✅ pH entre 5,5 e 7,0           (solo em condição adequada para milho)
  ✅ Sem previsão de chuva        (dado recebido via Python/Serial)
```

A bomba é **desligada** se qualquer uma dessas condições falhar:

```
DESLIGAR BOMBA se:
  ❌ Umidade >= 50%               (solo já úmido o suficiente)
  ❌ pH fora da faixa ideal       (corrigir solo antes de irrigar)
  ❌ Chuva prevista               (economiza água, aguarda chuva natural)
```

### Alertas gerados (sem bloquear irrigação):

| Situação                  | Alerta exibido no Serial                          |
|---------------------------|---------------------------------------------------|
| Botão N não pressionado   | `[ALERTA] Nitrogênio baixo! Considere adubar.`   |
| Botão P não pressionado   | `[ALERTA] Fósforo baixo! Considere adubar.`      |
| Botão K não pressionado   | `[ALERTA] Potássio baixo! Considere adubar.`     |
| pH < 5,5                  | `[ALERTA] pH abaixo do ideal. Adicione calcário.` |
| pH > 7,0                  | `[ALERTA] pH acima do ideal. Verifique o solo.`  |

> Os alertas de nutrientes informam o agricultor mas **não bloqueiam** a irrigação, pois a bomba pode ser necessária independentemente do estado dos nutrientes.

### Fluxograma de decisão

```
Início
  │
  ├─ Lê DHT22 → Umidade < 50%?
  │     ├─ NÃO → Desliga bomba ("Solo úmido")
  │     └─ SIM ↓
  │
  ├─ Lê LDR → pH entre 5.5 e 7.0?
  │     ├─ NÃO → Desliga bomba ("Corrigir pH")
  │     └─ SIM ↓
  │
  ├─ Lê Serial → Chuva prevista?
  │     ├─ SIM → Desliga bomba ("Aguardando chuva")
  │     └─ NÃO ↓
  │
  └─ LIGA BOMBA ✅
```

---

## 🔌 Circuito no Wokwi

> 📸 **Adicione aqui os prints do circuito montado no Wokwi.**

<!-- Substitua os caminhos abaixo pelos prints reais do seu circuito -->
![Circuito Completo](./imagens/circuito_completo.png)
![Detalhe Sensores](./imagens/detalhe_sensores.png)

### Link do projeto no Wokwi:
> 🔗 [Clique aqui para acessar o circuito no Wokwi](https://wokwi.com/) ← *substitua pelo link real*

---

## 💻 Código ESP32 (C/C++)

O arquivo principal está em [`src/farmtech_esp32.ino`](./src/farmtech_esp32.ino).

### Bibliotecas necessárias:
- `DHT.h` — leitura do sensor DHT22 (instale pelo Library Manager do Arduino IDE: **"DHT sensor library" by Adafruit**)

### Principais funções:

| Função           | Descrição                                              |
|------------------|--------------------------------------------------------|
| `lerPH()`        | Lê o LDR e mapeia para escala de pH 0.0–14.0          |
| `lerNutriente()` | Lê estado do botão (HIGH/LOW) e retorna bool           |
| `ligarBomba()`   | Aciona o relé e exibe log no Serial                    |
| `desligarBomba()`| Desliga o relé e exibe log no Serial                   |
| `lerSerial()`    | Recebe comandos `CHUVA:0` ou `CHUVA:1` via Monitor Serial |

---

## 🌦️ Ir Além — Integração Python + OpenWeather

O arquivo está em [`python/farmtech_clima.py`](./python/farmtech_clima.py).

### Como funciona:

1. O script Python consulta a **API OpenWeather** (`/forecast`) a cada 5 minutos
2. Extrai a probabilidade de chuva nas próximas 3 horas
3. Se probabilidade ≥ **70%**, envia `CHUVA:1` para o ESP32 via Monitor Serial
4. Caso contrário, envia `CHUVA:0` (irrigação liberada)
5. O ESP32 lê o comando pela função `lerSerial()` e ajusta a lógica de irrigação

### Dados exibidos pelo script:

```
==================================================
  FarmTech Solutions - Relatório Climático
==================================================
  Cidade          : Campinas,BR
  Condição        : chuva leve
  Temperatura     : 22.3 °C
  Umidade do ar   : 78 %
  Vol. chuva (3h) : 2.1 mm
  Prob. de chuva  : 80 %
--------------------------------------------------
  🌧  CHUVA PREVISTA - Irrigação SUSPENSA
  → Enviando CHUVA:1 para o ESP32
==================================================
```

### Instalação das dependências:

```bash
pip install requests pyserial
```

### Configuração:

1. Acesse [openweathermap.org](https://openweathermap.org) e crie uma conta gratuita
2. Gere sua **API Key** no painel
3. Abra `python/farmtech_clima.py` e substitua:
   ```python
   API_KEY = "SUA_API_KEY_AQUI"
   CIDADE  = "Campinas,BR"   # Ajuste para sua cidade
   ```
4. Execute:
   ```bash
   python farmtech_clima.py
   ```

### Integração com o Wokwi (manual):

Como o plano gratuito do Wokwi não permite conexão Serial automática, siga estes passos:
1. Rode o script Python no seu computador
2. O script exibirá no terminal: `[MANUAL] Digite no Monitor Serial do Wokwi: CHUVA:1`
3. Acesse o Monitor Serial do Wokwi e digite o comando exibido
4. O ESP32 processará o comando e ajustará a irrigação

---

## ▶️ Como Executar

### 1. Simulação no Wokwi
1. Acesse [wokwi.com](https://wokwi.com) e crie um novo projeto ESP32
2. Importe o arquivo `diagram.json` da pasta [`wokwi/`](./wokwi/)
3. Cole o conteúdo de `src/farmtech_esp32.ino` no editor
4. Clique em **Play** para iniciar a simulação
5. Interaja com os botões e o LDR para simular nutrientes e pH

### 2. Script Python (Ir Além)
```bash
cd python/
pip install requests
python farmtech_clima.py
```

### 3. Envio de dados para o ESP32
No Monitor Serial do Wokwi, digite:
- `CHUVA:1` → simula previsão de chuva (bomba desligada)
- `CHUVA:0` → sem previsão de chuva (irrigação liberada conforme sensores)

---

## 📁 Estrutura de Pastas

```
farmtech-fase2/
│
├── src/
│   └── farmtech_esp32.ino      # Código C/C++ do ESP32
│
├── python/
│   └── farmtech_clima.py       # Script Python + OpenWeather
│
├── wokwi/
│   └── diagram.json            # Diagrama de conexões do Wokwi
│
├── imagens/
│   ├── circuito_completo.png   # Print do circuito no Wokwi
│   └── detalhe_sensores.png    # Detalhe das conexões
│
└── README.md                   # Este arquivo
```

---

## 🎥 Vídeo de Demonstração

> 🔗 [Assista no YouTube] [https://youtu.be/HI2eLzcy9yc?si=-at021Tiq9GXzVad](https://youtu.be/HI2eLzcy9yc?si=zqyLu1pz5Kww3PzU)

O vídeo demonstra:
- Circuito funcionando no Wokwi
- Sensores sendo alterados em tempo real
- Lógica de irrigação sendo acionada e desligada
- Integração com a API OpenWeather via Python

---

## 👥 Integrantes

| Nome | RM |
|------|----|
| Gabriel Fileto Di Capua da Silva | RM569179 |
| Lucas Melo da Silva | RM569580 |

---

*Projeto desenvolvido para a disciplina de Computational Thinking Using Python — FIAP 2025*
