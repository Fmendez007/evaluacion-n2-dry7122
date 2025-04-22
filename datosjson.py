import json
import yaml  

# Abrimos el archivo JSON
with open("myfile.json", "r") as archivo:
    json_file = archivo

    # Cargamos el contenido del JSON en una variable
    ourjson = json.load(json_file)

    # Imprimimos el valor del token
    print("Token:", ourjson["token"])

    # Imprimimos el tiempo restante para que el token caduque
    print("Tiempo restante para que caduque:", ourjson["expires_in"], "segundos")
