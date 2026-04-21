"""
============================================================
FarmTech Solutions - Integração Python + OpenWeather
Cultura: Milho
Fase 2 - Ir Além (Opcional 1)
============================================================

Como usar:
1. Instale as dependências: pip install requests pyserial
2. Cadastre-se em https://openweathermap.org e obtenha sua API Key gratuita
3. Preencha API_KEY e CIDADE abaixo
4. Com o Wokwi aberto e o Monitor Serial ativo, rode este script
5. O script enviará automaticamente "CHUVA:1" ou "CHUVA:0" para o ESP32

NOTA: Se não conseguir conexão Serial com o Wokwi no plano gratuito,
o script exibe os dados na tela e você pode digitar manualmente
no Monitor Serial do Wokwi.
============================================================
"""

import requests
import time

# ===================== CONFIGURAÇÕES =====================
API_KEY = "SUA_API_KEY_AQUI"        # Substitua pela sua chave da OpenWeather
CIDADE  = "Campinas,BR"             # Cidade da fazenda
INTERVALO_SEGUNDOS = 300            # Consulta a cada 5 minutos

# Limiar: se probabilidade de chuva >= 70%, suspende irrigação
LIMIAR_CHUVA = 0.70

# Porta serial do ESP32 (descomente e ajuste se quiser envio automático)
# PORTA_SERIAL = "COM3"       # Windows
# PORTA_SERIAL = "/dev/ttyUSB0"  # Linux/Mac
# BAUD_RATE = 115200
# =========================================================


def consultar_clima(cidade: str, api_key: str) -> dict:
    """
    Consulta a API OpenWeather (previsão para as próximas 3 horas).
    Endpoint: /forecast (5 days / 3-hour forecast)
    """
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q":     cidade,
        "appid": api_key,
        "units": "metric",
        "lang":  "pt_br",
        "cnt":   1   # Apenas o próximo período (3h)
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("[ERRO] Sem conexão com a internet.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"[ERRO] HTTP {e.response.status_code} - Verifique sua API Key e cidade.")
        return None
    except Exception as e:
        print(f"[ERRO] {e}")
        return None


def analisar_chuva(dados: dict) -> tuple:
    """
    Extrai probabilidade de chuva e volume do JSON da OpenWeather.
    Retorna: (chuva_prevista: bool, prob: float, descricao: str, temp: float)
    """
    if not dados or "list" not in dados:
        return False, 0.0, "Dados indisponíveis", 0.0

    periodo = dados["list"][0]

    prob        = periodo.get("pop", 0.0)          # Probabilidade de precipitação (0 a 1)
    descricao   = periodo["weather"][0]["description"]
    temp        = periodo["main"]["temp"]
    umidade_ar  = periodo["main"]["humidity"]
    chuva_vol   = periodo.get("rain", {}).get("3h", 0.0)  # Volume de chuva em mm (3h)

    chuva_prevista = prob >= LIMIAR_CHUVA

    return chuva_prevista, prob, descricao, temp, umidade_ar, chuva_vol


def exibir_relatorio(cidade, chuva_prevista, prob, descricao, temp, umidade_ar, chuva_vol):
    print("\n" + "=" * 50)
    print("  FarmTech Solutions - Relatório Climático")
    print("=" * 50)
    print(f"  Cidade          : {cidade}")
    print(f"  Condição        : {descricao.capitalize()}")
    print(f"  Temperatura     : {temp:.1f} °C")
    print(f"  Umidade do ar   : {umidade_ar} %")
    print(f"  Vol. chuva (3h) : {chuva_vol:.1f} mm")
    print(f"  Prob. de chuva  : {prob * 100:.0f} %")
    print("-" * 50)

    if chuva_prevista:
        print("  🌧  CHUVA PREVISTA - Irrigação SUSPENSA")
        print("  → Enviando CHUVA:1 para o ESP32")
    else:
        print("  ☀️  SEM CHUVA PREVISTA - Irrigação LIBERADA")
        print("  → Enviando CHUVA:0 para o ESP32")

    print("=" * 50)


def enviar_serial(porta: str, baud: int, mensagem: str):
    """
    Envia dado via porta Serial para o ESP32.
    Descomente o bloco abaixo e instale pyserial para usar.
    """
    try:
        import serial
        with serial.Serial(porta, baud, timeout=2) as ser:
            time.sleep(2)  # Aguarda ESP32 inicializar
            ser.write((mensagem + "\n").encode("utf-8"))
            print(f"[SERIAL] Enviado: {mensagem}")
    except ImportError:
        print("[AVISO] pyserial não instalado. Execute: pip install pyserial")
    except Exception as e:
        print(f"[SERIAL] Erro ao enviar: {e}")


def main():
    print("\n  FarmTech Solutions - Monitoramento Climático")
    print("  Cultura: Milho | Cidade:", CIDADE)
    print("  Pressione Ctrl+C para encerrar.\n")

    if API_KEY == "SUA_API_KEY_AQUI":
        print("[AVISO] Você não configurou sua API Key!")
        print("  Acesse https://openweathermap.org/api e crie uma conta gratuita.")
        print("  Depois substitua 'SUA_API_KEY_AQUI' no topo deste arquivo.\n")

        # Modo demonstração sem API Key
        print("  Rodando em MODO DEMO (sem API Key)...")
        print("  Simulando: 80% de chance de chuva → Irrigação SUSPENSA")
        print("\n  Digite manualmente no Monitor Serial do Wokwi:")
        print("  CHUVA:1   (para suspender irrigação)")
        print("  CHUVA:0   (para liberar irrigação)")
        return

    while True:
        dados = consultar_clima(CIDADE, API_KEY)

        if dados:
            chuva_prevista, prob, descricao, temp, umidade_ar, chuva_vol = analisar_chuva(dados)

            exibir_relatorio(
                CIDADE, chuva_prevista, prob,
                descricao, temp, umidade_ar, chuva_vol
            )

            # Monta mensagem para o ESP32
            mensagem = "CHUVA:1" if chuva_prevista else "CHUVA:0"

            # --- Envio automático via Serial (descomente para usar) ---
            # enviar_serial(PORTA_SERIAL, BAUD_RATE, mensagem)

            # --- Envio manual: exibe instrução na tela ---
            print(f"\n  [MANUAL] Digite no Monitor Serial do Wokwi:")
            print(f"  {mensagem}\n")

        else:
            print("[ERRO] Não foi possível obter dados do clima. Tentando novamente...")

        print(f"  Próxima consulta em {INTERVALO_SEGUNDOS // 60} minuto(s)...")
        time.sleep(INTERVALO_SEGUNDOS)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  Sistema encerrado pelo usuário.")
