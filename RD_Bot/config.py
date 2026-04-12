# Configuración general del bot Gemini

MASTER_KEY_HASH = "<PON_AQUI_EL_HASH_DE_TU_CLAVE>"
FUEL_COST = 50  # Gasto de combustible por km
MAX_DISTANCE = 10  # Distancia máxima aceptada (km)
MIN_PRICE = 500  # Precio mínimo aceptado (RD$)
TRAFFIC_MAX_MINUTES = 60  # Tiempo máximo de viaje aceptado (minutos)
TARGET_PACKAGE = "com.nosotrosrd.app"  # Paquete de la app objetivo

# Coordenadas de ejemplo para predicción de tráfico
ORIGIN = (18.5, -69.9)
DESTINATION = (18.6, -69.8)

# Zonas peligrosas (lat, lon, radio_km)
SENTINEL_ZONES = [
    (18.51, -69.91, 1.0),
    (18.55, -69.95, 0.5)
]
