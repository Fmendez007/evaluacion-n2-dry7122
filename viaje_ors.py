#!/usr/bin/env python3
"""viaje_ors.py

Evaluación Parcial Nº2 – Item B
--------------------------------
Script de consumo de API pública (OpenRouteService) que:

1. Solicita ciudad de origen y destino al usuario (permite salir con 'q').
2. Consulta la API de geocodificación y direcciones de ORS para obtener:
   • Distancia (km, 2 decimales)
   • Duración (horas:minutos:segundos)
   • Combustible estimado (litros, 2 decimales)
   • Narrativa paso a paso del viaje
3. Imprime los resultados formateados.
4. Pensado para ejecutarse en macOS / DEVASC con Python 3.

Requisitos:
- requests
- python-dotenv
- Archivo .env con la variable ORS_KEY=<tu_api_key>

Autor: Felipe Méndez
Fecha: 2025-05-29
"""

import os
import sys
import requests
from dotenv import load_dotenv

# ----------------------------- Configuración ----------------------------- #

load_dotenv()  # Carga variables desde .env
API_KEY = os.getenv("ORS_KEY")

if not API_KEY:
    sys.exit("⚠️  Falta la API KEY en el archivo .env (ORS_KEY=...)")

GEOCODE_URL = "https://api.openrouteservice.org/geocode/search"
DIRECTIONS_URL = "https://api.openrouteservice.org/v2/directions/driving-car"
FUEL_CONSUMPTION_L_PER_KM = 0.08  # 8 L / 100 km

# ----------------------------- Funciones --------------------------------- #

def geocode(city: str):
    """Devuelve (lat, lon) de la ciudad usando ORS Geocode API"""
    params = {
        "api_key": API_KEY,
        "text": city,
        "size": 1
    }
    r = requests.get(GEOCODE_URL, params=params, timeout=10)
    r.raise_for_status()
    features = r.json().get("features")
    if not features:
        raise ValueError(f"No se encontró la ciudad: {city}")
    lon, lat = features[0]["geometry"]["coordinates"]
    return lat, lon


def obtener_ruta(origen: tuple, destino: tuple):
    """Devuelve la ruta entre dos pares (lat, lon)"""
    coords = [[origen[1], origen[0]], [destino[1], destino[0]]]
    body = {"coordinates": coords}
    params = {"api_key": API_KEY}
    r = requests.post(f"{DIRECTIONS_URL}/geojson", json=body, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def segundos_a_hms(seg: float):
    h = int(seg // 3600)
    m = int((seg % 3600) // 60)
    s = int(seg % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ----------------------------- Programa ---------------------------------- #

INTRO = """\n=== Evaluación Parcial Nº2 – API Pública (OpenRouteService) ===
Ingresa las ciudades usando el formato "Ciudad, País" (ej. "Santiago, Chile").
Escribe 'q' en cualquier momento para salir.\n"""

print(INTRO)

while True:
    origen = input("Ciudad de Origen: ").strip()
    if origen.lower() == "q":
        break

    destino = input("Ciudad de Destino: ").strip()
    if destino.lower() == "q":
        break

    try:
        print("\n🔎 Geocodificando…")
        org_coords = geocode(origen)
        dst_coords = geocode(destino)

        print("🚗 Consultando ruta…")
        ruta_geojson = obtener_ruta(org_coords, dst_coords)
        props = ruta_geojson["features"][0]["properties"]["summary"]

        distancia_km = props["distance"] / 1000
        duracion_sec = props["duration"]
        combustible_l = distancia_km * FUEL_CONSUMPTION_L_PER_KM

        print(f"\n📍 Distancia : {distancia_km:.2f} km")
        print(f"⏱  Duración  : {segundos_a_hms(duracion_sec)} (h:m:s)")
        print(f"⛽ Combustible: {combustible_l:.2f} litros")

        print("\n🗺️  Narrativa del viaje:")
        pasos = ruta_geojson["features"][0]["properties"]["segments"][0]["steps"]
        for idx, paso in enumerate(pasos, start=1):
            print(f" {idx:02d}. {paso['instruction']}")
        print("\n---\n")

    except Exception as e:
        print("❌  Error:", e, "\n")

print("\nPrograma finalizado. ¡Éxito en tu evaluación!\n")
