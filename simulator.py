import time
import random
from supabase import create_client

# --- GANTI DENGAN MILIK ANDA ---
URL = "https://qdlwjdbfeeaamufjxhfg.supabase.co"
KEY = "sb_publishable_uf9ZbRwkXfF4WT22BpNfLg_aFnTH4zY"

supabase = create_client(URL, KEY)

def kirim_data():
    print("--- Simulator Buoy Aktif (GPS + Sensor) ---")
    while True:
        try:
            data = {
                "suhu": round(random.uniform(25.0, 30.0), 2),
                "ph": round(random.uniform(6.5, 8.5), 2),
                "turbidity": round(random.uniform(5.0, 50.0), 2),
                "conductivity": round(random.uniform(200, 500), 2),
                "dissolved_oxygen": round(random.uniform(5.0, 9.0), 2),
                "battery": random.randint(80, 100),
                "rssi": random.randint(-80, -40),
                # Koordinat area Danau Toba
                "latitude": round(random.uniform(2.6500, 2.6510), 6),
                "longitude": round(random.uniform(98.8500, 98.8510), 6)
            }
            supabase.table("water_quality").insert(data).execute()
            print(f"📡 Terkirim: {data}")
        except Exception as e:
            print(f"❌ Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    kirim_data()