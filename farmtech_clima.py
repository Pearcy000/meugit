"""
============================================================
FarmTech Solutions - Integração Python + OpenWeather
Cultura: Milho
Fase 2 - Ir Além (Opcional 1)
============================================================
"""

import requests
import time

# ===================== CONFIGURAÇÕES =====================
API_KEY = "16ec5243ffe2d2057f29eefcd7b4ae04"
CIDADE  = "Campinas,BR"
INTERVALO_SEGUNDOS = 300
LIMIAR_CHUVA = 0.70
# =========================================================


def consultar_clima():
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q":     CIDADE,
        "appid": API_KEY,
        "units": "metric",
        "lang":  "pt_br",
        "cnt":   1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"[ERRO] HTTP {e.response.status_code} - Verifique sua API Key.")
        return None
    except Exception as e:
        print(f"[ERRO] {e}")
        return None


def main():
    print("\n  FarmTech Solutions - Monitoramento Climatico")
    print(f"  Cultura: Milho | Cidade: {CIDADE}\n")

    dados = consultar_clima()

    if not dados:
        print("[ERRO] Nao foi possivel obter dados do clima.")
        return

    periodo    = dados["list"][0]
    prob       = periodo.get("pop", 0.0)
    descricao  = periodo["weather"][0]["description"]
    temp       = periodo["main"]["temp"]
    umidade    = periodo["main"]["humidity"]
    chuva_vol  = periodo.get("rain", {}).get("3h", 0.0)
    chuva      = prob >= LIMIAR_CHUVA

    print("=" * 50)
    print("  FarmTech Solutions - Relatorio Climatico")
    print("=" * 50)
    print(f"  Cidade          : {CIDADE}")
    print(f"  Condicao        : {descricao.capitalize()}")
    print(f"  Temperatura     : {temp:.1f} C")
    print(f"  Umidade do ar   : {umidade} %")
    print(f"  Vol. chuva (3h) : {chuva_vol:.1f} mm")
    print(f"  Prob. de chuva  : {prob * 100:.0f} %")
    print("-" * 50)

    if chuva:
        print("  CHUVA PREVISTA - Irrigacao SUSPENSA")
        print("  Digite no Monitor Serial do Wokwi: CHUVA:1")
    else:
        print("  SEM CHUVA PREVISTA - Irrigacao LIBERADA")
        print("  Digite no Monitor Serial do Wokwi: CHUVA:0")

    print("=" * 50)


if __name__ == "__main__":
    main()
