import random

class DecisionEngine:
    def __init__(self):
        # Parámetros lógicos ajustables desde tu estrategia
        self.tarifa_minima_por_km = 45.0  # RD$ por cada KM recorrido
        self.distancia_max_recogida = 3.5  # No ir más lejos de 3.5km por un cliente
        self.zonas_peligrosas = ["Zona Roja 1", "Calle Callejón X", "Sector Peligro"]

    def evaluar_viaje(self, precio, distancia_total, nombre_zona):
        """
        Determina si el viaje cumple con los estándares de rentabilidad.
        """
        # 1. Limpieza de datos (quitar símbolos de moneda)
        precio_limpio = float(str(precio).replace('RD$', '').replace(',', '').strip())
        # 2. Cálculo de rentabilidad neta
        rentabilidad = precio_limpio / distancia_total if distancia_total > 0 else 0
        print(f"Analizando: RD${precio_limpio} | {distancia_total}km | Zona: {nombre_zona}")
        print(f"Rentabilidad calculada: RD${rentabilidad:.2f}/km")
        # --- CAMPOS LÓGICOS DE DECISIÓN ---
        if rentabilidad < self.tarifa_minima_por_km:
            print(">>> RECHAZADO: Baja rentabilidad.")
            return False
        if distancia_total > self.distancia_max_recogida:
            print(">>> RECHAZADO: Cliente muy lejos.")
            return False
        if nombre_zona in self.zonas_peligrosas:
            print(">>> RECHAZADO: Zona de alto riesgo.")
            return False
        print(">>> VIAJE APROBADO: Iniciando secuencia de captura...")
        return True

    def generar_jitter_humano(self):
        """Genera un retraso aleatorio para no ser detectado."""
        return random.uniform(0.4, 0.9)
