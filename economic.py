import requests
import pandas as pd
from datetime import datetime, timedelta
import time

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
API_KEY = "ea0431dfffmsheba0bbf09b34ddbp1d1e52jsn4e38e06d0c63"  # tu RapidAPI Key
API_HOST = "ultimate-economic-calendar.p.rapidapi.com"

START_DATE = datetime(2000, 1, 1)  # inicio histórico
END_DATE = datetime.now()           # hasta hoy

BLOCK_DAYS = 30                     # días por bloque
OUTPUT_CSV = "usd_economic_calendar_full.csv"
MAX_RETRIES = 3                     # reintentos si falla la API
SLEEP_BETWEEN_BLOCKS = 1            # segundos de espera entre bloques

# -----------------------------
# FUNCIONES
# -----------------------------
def fetch_usd_events(start_date, end_date):
    """Descarga eventos USD desde la API para un rango de fechas dado, con reintentos."""
    url = f"https://{API_HOST}/economic-events/tradingview"
    query = {
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "countries": "US"
    }
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, params=query, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get("events", [])
            else:
                print(f"⚠️ Error {response.status_code} en rango {query['from']} - {query['to']}")
        except Exception as e:
            print(f"⚠️ Excepción en intento {attempt} para {query['from']} - {query['to']}: {e}")
        time.sleep(2)  # espera antes de reintento
    return []

# -----------------------------
# DESCARGA HISTÓRICA COMPLETA
# -----------------------------
all_events = []
current_start = START_DATE

while current_start < END_DATE:
    current_end = min(current_start + timedelta(days=BLOCK_DAYS), END_DATE)
    
    print(f"Descargando eventos USD desde {current_start.strftime('%Y-%m-%d')} hasta {current_end.strftime('%Y-%m-%d')}...")
    
    events = fetch_usd_events(current_start, current_end)
    
    if events:
        all_events.extend(events)
        print(f"  → {len(events)} eventos encontrados y agregados")
    else:
        print(f"  → No se encontraron eventos para este bloque")
    
    current_start = current_end + timedelta(days=1)
    time.sleep(SLEEP_BETWEEN_BLOCKS)

# -----------------------------
# GUARDAR EN CSV
# -----------------------------
if all_events:
    df = pd.DataFrame(all_events)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Descarga completa. Total eventos USD: {len(df)}")
    print(f"Archivo guardado como: {OUTPUT_CSV}")
else:
    print("\n⚠️ No se encontraron eventos USD.")
