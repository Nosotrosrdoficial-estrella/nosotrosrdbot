from engine import DecisionEngine
from SECURITY.stealth import human_click
import requests
import time

# Configura tu HWID y la URL de Render
HWID = "TU_ID_UNICO_AQUI"
URL_RENDER = "https://nosotrosrdbot-1.onrender.com/validar/"

def loop_principal():
    # 1. Verificar acceso en el Centro de Admisión
    permiso = requests.get(f"{URL_RENDER}{HWID}").json()
    if permiso.get("status") != "Aprobado":
        print("Acceso denegado. Contacta al administrador.")
        return
    # 2. Si está aprobado, inicia el bot
    cerebro = DecisionEngine()
    while True:
        # Simulación de lectura de pantalla (reemplaza por tu lógica real)
        datos_pantalla = {
            "precio": "RD$500",
            "distancia": 4.2,
            "zona": "Villa Mella"
        }
        if cerebro.evaluar_viaje(datos_pantalla['precio'], datos_pantalla['distancia'], datos_pantalla['zona']):
            # Simular tiempo de reacción humano
            time.sleep(cerebro.generar_jitter_humano())
            # Ejecutar el clic sigiloso en las coordenadas del botón 'Aceptar'
            human_click(540, 1600)  # Coordenadas de ejemplo
        else:
            print("Viaje ignorado por lógica de rentabilidad o zona.")
        time.sleep(2)

if __name__ == "__main__":
    loop_principal()
