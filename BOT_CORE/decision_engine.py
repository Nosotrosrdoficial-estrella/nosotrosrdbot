from SECURITY.human_click import human_click
import random

ZONAS_RESTRINGIDAS = {"zona_peligrosa_1", "zona_peligrosa_2"}

class DecisionEngine:
    def __init__(self, min_ratio=40):
        self.min_ratio = min_ratio

    def evaluar(self, precio_viaje, distancia_km, nombre_zona, device, boton_bounds):
        if distancia_km == 0:
            return False
        if (precio_viaje / distancia_km) < self.min_ratio:
            return False
        if nombre_zona.lower() in (z.lower() for z in ZONAS_RESTRINGIDAS):
            return False
        # Extraer centro del botón
        import re
        match = re.findall(r"\d+", boton_bounds)
        if len(match) == 4:
            x1, y1, x2, y2 = map(int, match)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            # Llamar a human_click con jitter aleatorio
            human_click(device, cx, cy, tolerance=random.randint(3, 8))
            return True
        return False
