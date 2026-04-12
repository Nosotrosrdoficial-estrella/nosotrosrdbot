UMBRAL_RENTABILIDAD = 45  # pesos por KM
DISTANCIA_MAXIMA = 4      # KM

def es_viaje_rentable(precio, distancia):
    if distancia == 0:
        return False
    rentabilidad = precio / distancia
    return rentabilidad > UMBRAL_RENTABILIDAD and distancia < DISTANCIA_MAXIMA
