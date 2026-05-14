"""
Módulo de GPS, Mapas y Trazador de Rutas
Integración con Google Maps API y OpenStreetMap
"""
import requests
import math
from typing import Tuple, Optional, Dict, List
from datetime import datetime
import json

class GPSHandler:
    """Manejo de GPS y ubicación"""
    
    def __init__(self):
        self.ubicacion_actual = None
        self.historial_ubicaciones = []
        self.velocidad_promedio = 0
    
    def obtener_ubicacion_simulada(self, lat_offset: float = 0, lon_offset: float = 0) -> Tuple[float, float]:
        """Obtiene ubicación actual (simulada o real)"""
        # Para desarrollo, usar coordenadas de Santo Domingo, RD
        lat_base = 18.486
        lon_base = -69.931
        
        self.ubicacion_actual = (lat_base + lat_offset, lon_base + lon_offset)
        self.historial_ubicaciones.append({
            "timestamp": datetime.now().isoformat(),
            "ubicacion": self.ubicacion_actual,
        })
        
        return self.ubicacion_actual
    
    def calcular_distancia_haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula distancia entre dos puntos en km usando fórmula haversine"""
        R = 6371  # Radio de la Tierra en km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    def calcular_rumbo(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calcula el rumbo (bearing) entre dos puntos (0-360 grados)"""
        dlon = math.radians(lon2 - lon1)
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon)
        
        rumbo = math.degrees(math.atan2(y, x))
        return (rumbo + 360) % 360


class MapasGoogle:
    """Integración con Google Maps API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "AIzaSyDemoKeyNotReal"  # Usar API key real
        self.base_url = "https://maps.googleapis.com/maps/api"
    
    def obtener_ruta(self, lat_origen: float, lon_origen: float, lat_destino: float, lon_destino: float, modo: str = "driving") -> Optional[Dict]:
        """Obtiene ruta optimizada desde origen a destino"""
        
        url = f"{self.base_url}/directions/json"
        
        params = {
            "origin": f"{lat_origen},{lon_origen}",
            "destination": f"{lat_destino},{lon_destino}",
            "mode": modo,  # driving, walking, bicycling, transit
            "key": self.api_key,
            "language": "es",
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data["status"] == "OK":
                    ruta = data["routes"][0]
                    pierna = ruta["legs"][0]
                    
                    return {
                        "distancia_km": pierna["distance"]["value"] / 1000,
                        "duracion_minutos": pierna["duration"]["value"] / 60,
                        "duracion_trafico_minutos": pierna.get("duration_in_traffic", {}).get("value", 0) / 60,
                        "pasos": pierna["steps"],
                        "puntos_ruta": ruta["overview_polyline"]["points"],
                        "resumen": pierna["summary"],
                    }
        except Exception as e:
            print(f"Error obteniendo ruta de Google: {e}")
        
        return None
    
    def obtener_matriz_distancias(self, origenes: List[Tuple], destinos: List[Tuple]) -> Optional[Dict]:
        """Calcula distancia entre múltiples puntos"""
        
        url = f"{self.base_url}/distancematrix/json"
        
        origins_str = "|".join([f"{lat},{lon}" for lat, lon in origenes])
        destinations_str = "|".join([f"{lat},{lon}" for lat, lon in destinos])
        
        params = {
            "origins": origins_str,
            "destinations": destinations_str,
            "mode": "driving",
            "key": self.api_key,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"Error en matriz de distancias: {e}")
        
        return None
    
    def obtener_trafico_en_vivo(self, lat: float, lon: float, radio_km: float = 2) -> Optional[Dict]:
        """Obtiene información de tráfico en vivo para un área"""
        
        # Usar Static Maps API para info de tráfico
        url = f"{self.base_url}/staticmap"
        
        params = {
            "center": f"{lat},{lon}",
            "zoom": 13,
            "size": "400x400",
            "style": "feature:road|element:geometry.stroke|color:0xc0c0c0|visibility:simplified",
            "style": "feature:transit.line|color:0xffffff",
            "key": self.api_key,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return {"trafico_disponible": True}
        except:
            pass
        
        return {"trafico_disponible": False}


class MapasOSM:
    """Integración con OpenStreetMap (alternativa gratuita)"""
    
    def __init__(self):
        self.base_url = "https://router.project-osrm.org"
    
    def obtener_ruta(self, lat_origen: float, lon_origen: float, lat_destino: float, lon_destino: float) -> Optional[Dict]:
        """Obtiene ruta usando OSRM"""
        
        url = f"{self.base_url}/route/v1/driving/{lon_origen},{lat_origen};{lon_destino},{lat_destino}"
        
        params = {
            "overview": "full",
            "steps": "true",
            "geometries": "geojson",
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data["code"] == "Ok":
                    ruta = data["routes"][0]
                    
                    return {
                        "distancia_km": ruta["distance"] / 1000,
                        "duracion_minutos": ruta["duration"] / 60,
                        "geometria": ruta["geometry"],
                        "pasos": ruta["legs"][0]["steps"],
                    }
        except Exception as e:
            print(f"Error obteniendo ruta OSM: {e}")
        
        return None


class CalculadoraTarifa:
    """Calcula tarifa según distancia, duración y tipo de servicio"""
    
    def __init__(
        self,
        precio_por_km: float = 2.5,
        precio_espera_por_min: float = 1.8,
        cargo_base: float = 50.0,
        precio_noche: float = 1.0,  # Multiplicador 2x entre 22:00 y 06:00
        precio_lluvia: float = 1.3,  # Multiplicador por lluvia
    ):
        self.precio_por_km = precio_por_km
        self.precio_espera_por_min = precio_espera_por_min
        self.cargo_base = cargo_base
        self.precio_noche = precio_noche
        self.precio_lluvia = precio_lluvia
    
    def calcular(
        self,
        distancia_km: float,
        duracion_minutos: float,
        tiempo_espera_minutos: float = 0,
        es_noche: bool = False,
        hay_lluvia: bool = False,
    ) -> Dict:
        """Calcula tarifa completa"""
        
        # Tarifa base
        tarifa = self.cargo_base
        
        # Tarifa por distancia
        tarifa += distancia_km * self.precio_por_km
        
        # Tarifa por duración (tiempo en movimiento)
        tarifa += duracion_minutos * self.precio_por_km / 60
        
        # Tarifa por espera
        tarifa += tiempo_espera_minutos * self.precio_espera_por_min
        
        # Multiplicadores
        multiplicador = 1.0
        if es_noche:
            multiplicador *= self.precio_noche
        if hay_lluvia:
            multiplicador *= self.precio_lluvia
        
        tarifa = tarifa * multiplicador
        
        return {
            "tarifa_total": round(tarifa, 2),
            "cargo_base": self.cargo_base,
            "por_distancia": round(distancia_km * self.precio_por_km, 2),
            "por_tiempo": round(duracion_minutos * self.precio_por_km / 60, 2),
            "por_espera": round(tiempo_espera_minutos * self.precio_espera_por_min, 2),
            "multiplicador": multiplicador,
            "detalles": {
                "distancia_km": distancia_km,
                "duracion_minutos": duracion_minutos,
                "tiempo_espera": tiempo_espera_minutos,
                "es_noche": es_noche,
                "hay_lluvia": hay_lluvia,
            }
        }
    
    def es_viaje_rentable(self, tarifa: float, distancia_km: float, umbral_ratio: float = 45.0) -> bool:
        """Verifica si el viaje es rentable"""
        if distancia_km == 0:
            return False
        ratio = tarifa / distancia_km
        return ratio >= umbral_ratio


class LocalizadorViajes:
    """Encuentra viajes cercanos dentro de un rango de distancia o tiempo"""
    
    def __init__(self, gps_handler: GPSHandler, mapas=None):
        self.gps = gps_handler
        self.mapas = mapas or MapasOSM()
    
    def obtener_viajes_en_radio(
        self,
        lat_actual: float,
        lon_actual: float,
        lista_viajes: List[Dict],
        distancia_maxima_km: float = 30,
        tiempo_maximo_minutos: int = 15,
    ) -> List[Dict]:
        """Filtra viajes que están dentro del radio especificado"""
        
        viajes_cercanos = []
        
        for viaje in lista_viajes:
            try:
                # Calcular distancia
                dist = self.gps.calcular_distancia_haversine(
                    lat_actual, lon_actual,
                    viaje["lat_origen"], viaje["lon_origen"]
                )
                
                # Obtener ruta y duración
                ruta = self.mapas.obtener_ruta(
                    lat_actual, lon_actual,
                    viaje["lat_origen"], viaje["lon_origen"]
                )
                
                duracion = ruta["duracion_minutos"] if ruta else dist / 50 * 60  # Asumir 50km/h
                
                # Filtrar por distancia o tiempo
                if dist <= distancia_maxima_km or duracion <= tiempo_maximo_minutos:
                    viaje_con_distancia = viaje.copy()
                    viaje_con_distancia["distancia_al_viaje_km"] = round(dist, 2)
                    viaje_con_distancia["tiempo_al_viaje_minutos"] = round(duracion, 1)
                    viajes_cercanos.append(viaje_con_distancia)
            
            except Exception as e:
                print(f"Error procesando viaje: {e}")
                continue
        
        # Ordenar por distancia
        viajes_cercanos.sort(key=lambda v: v["distancia_al_viaje_km"])
        
        return viajes_cercanos


# ==================== INSTANCIAS GLOBALES ====================
gps = GPSHandler()
mapas_google = MapasGoogle()
mapas_osm = MapasOSM()
calculadora_tarifa = CalculadoraTarifa()
localizador = LocalizadorViajes(gps, mapas_osm)


# ==================== PRUEBAS ====================
if __name__ == "__main__":
    # Prueba de distancia
    dist = gps.calcular_distancia_haversine(18.486, -69.931, 18.591, -72.295)
    print(f"Distancia Santo Domingo - Santiago: {dist:.2f} km")
    
    # Prueba de tarifa
    tarifa_datos = calculadora_tarifa.calcular(
        distancia_km=5.2,
        duracion_minutos=18,
        tiempo_espera_minutos=2,
        es_noche=False,
        hay_lluvia=False,
    )
    print(f"Tarifa calculada: RD${tarifa_datos['tarifa_total']}")
