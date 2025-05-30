
#!/usr/bin/env python3
"""viaje_ors.py (versión Español)

Evaluación Parcial Nº2 – Item B
--------------------------------
Script que consume la API de OpenRouteService (ORS) y muestra la ruta
entre dos ciudades con la narrativa en español.

Requisitos:
- requests
- python-dotenv
- Archivo .env con ORS_KEY

Autor: Felipe Méndez
Fecha: 2025-05-29
"""

import os
import sys
import requests
from dotenv import load_dotenv

# ---------------- Configuración ---------------- #
load_dotenv()
API_KEY = os.getenv("ORS_KEY")
if not API_KEY:
    sys.exit("⚠️  Falta la API KEY en el archivo .env (ORS_KEY=...)")

GEOCODE_URL    = "https://api.openrouteservice.org/geocode/search"
DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
LANGUAGE       = "es"   # <<--- narrativa en español
FUEL_L_POR_KM  = 0.08   # 8 L / 100 km

# --------------- Funciones auxiliares ---------- #
def geocode(ciudad: str):
    """Devuelve (lat, lon) de la ciudad usando la API de geocodificación"""
    params = {
        "api_key": API_KEY,
        "text": ciudad,
        "size": 1,
        "language": LANGUAGE
    }
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    r.raise_for_status()
    features = r.json().get("features")
    if not features:
        raise ValueError(f"No se encontró la ciudad: {ciudad}")
    lon, lat = features[0]["geometry"]["coordinates"]
    return lat, lon

def obtener_ruta(origen: tuple, destino: tuple):
    """Obtiene la ruta y narrativa en español"""
    coords = [[origen[1], origen[0]], [destino[1], destino[0]]]
    body = {"coordinates": coords}
    params = {
        "api_key": API_KEY,
        "language": LANGUAGE,
        "instructions": "true"
    }
    r = requests.post(f"{DIRECTIONS_URL}/geojson", json=body, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def seg_a_hms(seg):
    h = int(seg//3600)
    m = int((seg%3600)//60)
    s = int(seg%60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def estimar_combustible(km, consumo=FUEL_L_POR_KM):
    return km * consumo

# --------------- Programa principal ------------ #
print("\n=== Evaluación Parcial Nº2 – Consumo de API Pública (ORS) ===")
print("Escribe 'q' para salir.\n")

while True:
    origen = input("Ciudad de Origen: ").strip()
    if origen.lower() == "q":
        break
    destino = input("Ciudad de Destino: ").strip()
    if destino.lower() == "q":
        break

    try:
        print("\n🔍 Geocodificando…")
        org = geocode(origen)
        dst = geocode(destino)

        print("🚗 Calculando ruta…")
        data = obtener_ruta(org, dst)
        summary = data["features"][0]["properties"]["summary"]
        dist_km = summary["distance"] / 1000
        dur_sec = summary["duration"]
        lit = estimar_combustible(dist_km)

        print(f"\n📏 Distancia : {dist_km:.2f} km")
        print(f"⏱  Duración  : {seg_a_hms(dur_sec)} (h:m:s)")
        print(f"⛽ Combustible: {lit:.2f} litros")

        print("\n🗺  Narrativa (ES):")
        pasos = data["features"][0]["properties"]["segments"][0]["steps"]
        for i, paso in enumerate(pasos, 1):
            print(f" {i:02d}. {paso['instruction']}")

        print("\n---\n")

    except Exception as e:
        print("❌ Error:", e, "\n")
