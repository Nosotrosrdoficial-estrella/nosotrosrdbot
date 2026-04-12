import random
import time
import os

def human_click(x, y):
    """
    Ejecuta un clic simulando el comportamiento de un dedo humano:
    1. Variación de coordenadas (+/- 5px).
    2. Delay de presión aleatorio (jitter).
    3. Movimiento antes del toque.
    """
    target_x = x + random.randint(-5, 5)
    target_y = y + random.randint(-3, 3)
    duration = random.randint(100, 180)
    os.system(f"adb shell input swipe {target_x} {target_y} {target_x} {target_y} {duration}")
    print(f"Sentinel: Clic ejecutado en ({target_x}, {target_y}) con duración {duration}ms")
