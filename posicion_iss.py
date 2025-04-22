import requests
import time

for i in range(3):  # 3 ciclos de ejemplo
    respuesta = requests.get("http://api.open-notify.org/iss-now.json")
    data = respuesta.json()
    lat = data['iss_position']['latitude']
    lon = data['iss_position']['longitude']
    print(f"Posición actual: Latitud {lat}, Longitud {lon}")
    time.sleep(60)
