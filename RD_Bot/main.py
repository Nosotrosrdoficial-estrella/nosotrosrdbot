import sys
import threading
from auth.login import show_login
from perception.ui_tree import scan_for_price
from perception.ocr import screenshot_and_ocr
from logic.decision import should_accept
from controller.stealth import human_click
from overlay.overlay import show_overlay
from traffic.traffic_api import get_traffic_time
import uiautomator2 as u2
import adbutils

RUNNING = True

# Kill-switch callback
def kill_all():
    global RUNNING
    RUNNING = False
    print("Kill-Switch activado. Todos los procesos detenidos.")
    sys.exit(0)

def main_loop():
    device = adbutils.adb.device()
    d = u2.connect()
    while RUNNING:
        # 1. Percepción multimodal
        text, bounds = scan_for_price()
        if not text:
            text, bbox = screenshot_and_ocr()
        if not text:
            continue
        # 2. Extraer valor y distancia
        try:
            valor = float(''.join(filter(str.isdigit, text)))
            distancia = 5  # Aquí deberías extraer la distancia real
        except:
            continue
        # 3. Lógica de decisión
        aceptar, ganancia = should_accept(valor, distancia, fuel_cost=50, max_distance=10, min_price=500)
        if aceptar:
            # 4. Predicción de tráfico
            tiempo_trafico = get_traffic_time(18.5, -69.9, 18.6, -69.8)  # Ejemplo de coordenadas
            if tiempo_trafico and tiempo_trafico > 60:
                print("Viaje rechazado por tráfico excesivo.")
                continue
            # 5. Actuación sigilosa
            # Calcular centro del botón
            if bounds:
                import re
                match = re.findall(r"\d+", bounds)
                if len(match) == 4:
                    x1, y1, x2, y2 = map(int, match)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    human_click(device, cx, cy)
        # Espera antes de siguiente ciclo
        import time
        time.sleep(1)

if __name__ == "__main__":
    if not show_login():
        sys.exit(0)
    threading.Thread(target=show_overlay, args=(kill_all,), daemon=True).start()
    main_loop()
