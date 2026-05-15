"""
Sistema de Configuración Avanzado - NOSOTROS RD Sentinel v2.0
Gestión completa de preferencias, zonas, pricing y UI
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
import hashlib

class SettingsManager:
    """Gestor de configuración persistente con validación y sincronización"""
    
    def __init__(self, config_file: str = "sentinel_settings.json"):
        self.config_file = config_file
        self.config = self._load_or_create()
        self.observers = []  # Para notificar cambios en tiempo real
        
    def _load_or_create(self) -> Dict:
        """Carga configuración existente o crea una nueva"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return self._merge_with_defaults(loaded)
            except Exception as e:
                print(f"Error al cargar config: {e}")
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """Retorna la configuración por defecto completa"""
        return {
            # === AUTENTICACIÓN ===
            "auth": {
                "user_id": None,
                "device_id": None,
                "token": None,
                "email": None,
                "phone": None,
                "whatsapp": None,
                "last_login": None,
                "is_authenticated": False,
                "hwid": self._generate_hwid(),
            },
            
            # === CONFIGURACIÓN DE VIAJES ===
            "trips": {
                "distancia_minima_km": 0.5,
                "distancia_maxima_km": 15.0,
                "precio_minimo_viaje": 100.0,
                "precio_por_km": 2.5,
                "precio_espera_por_minuto": 1.8,
                "rentabilidad_minima_ratio": 45.0,  # pesos/km
                "aceptar_automaticamente": False,
                "modo_seguro": True,  # Validar zona antes de aceptar
            },
            
            # === ZONAS GEOGRÁFICAS ===
            "zonas": {
                "favoritas": [
                    {"nombre": "Centro Comercial", "lat": 18.486, "lon": -69.931, "radio_km": 2.0},
                    {"nombre": "Aeropuerto", "lat": 18.591, "lon": -72.295, "radio_km": 3.0},
                ],
                "restringidas": [
                    {"nombre": "Zona Roja", "lat": 18.500, "lon": -69.900, "radio_km": 1.5},
                    {"nombre": "Area Peligrosa", "lat": 18.470, "lon": -69.950, "radio_km": 1.0},
                ],
                "horarios_restriccion": {
                    "22:00-06:00": ["Zona Roja"],  # No entrar de noche
                    "06:00-22:00": []
                }
            },
            
            # === CALIFICACIÓN Y RATINGS ===
            "ratings": {
                "calificacion_minima_aceptar": 4.0,  # No aceptar viajes de pasajeros < 4 estrellas
                "calificacion_propia": 5.0,
                "total_viajes": 0,
                "total_ganancias": 0.0,
                "promedio_viaje": 0.0,
            },
            
            # === GPS Y MAPAS ===
            "gps": {
                "usar_gps": True,
                "actualizar_ubicacion_cada": 5,  # segundos
                "proveedor_mapas": "google",  # google, osm
                "mostrar_ruta_estimada": True,
                "mostrar_trafico": True,
                "distancia_mostrar_viajes": "30km",  # O "15minutos"
            },
            
            # === NOTIFICACIONES Y OVERLAY ===
            "notificaciones": {
                "overlay_viajes_activo": True,
                "overlay_duracion_segundos": 10,
                "overlay_posicion": "top-right",  # top-left, top-right, bottom-left, bottom-right
                "sonido_notificacion": True,
                "volumen": 80,
                "vibrar": True,
                "mostrar_pasajero": True,
                "mostrar_calificacion": True,
            },
            
            # === INTERFAZ ===
            "ui": {
                "tema": "dark",  # dark, light
                "idioma": "es",  # es, en
                "tamaño_fuente": 14,
                "animaciones": True,
                "mostrar_tips": True,
            },
            
            # === SOPORTE ===
            "soporte": {
                "modo_soporte": False,
                "bandejas": {
                    "entrada": [],  # Tickets recibidos
                    "salida": [],   # Tickets enviados
                },
                "email_soporte": "soporte@nosotrosrd.com",
                "whatsapp_soporte": "+1-809-2345678",
                "linksoporte": "https://nosotrosrd.com/soporte",
            },
            
            # === SEGURIDAD ===
            "seguridad": {
                "encriptacion_habilitada": True,
                "validar_contra_render": True,
                "endpoint_render": "https://nosotrosrdbot-1.onrender.com",
                "access_key": "Diosamor",
                "auto_reconectar": True,
                "timeout_conexion": 10,
            },
            
            # === ESTADÍSTICAS ===
            "estadisticas": {
                "fecha_creacion": datetime.now().isoformat(),
                "ultima_actualizacion": datetime.now().isoformat(),
                "viajes_hoy": 0,
                "ganancias_hoy": 0.0,
                "tiempo_online_hoy": 0,
                "historial_viajes": [],
            },
        }
    
    def _merge_with_defaults(self, loaded: Dict) -> Dict:
        """Mezcla configuración cargada con valores por defecto"""
        defaults = self._get_default_config()
        
        def merge_dict(default, loaded):
            for key, value in default.items():
                if key not in loaded:
                    loaded[key] = value
                elif isinstance(value, dict) and isinstance(loaded[key], dict):
                    merge_dict(value, loaded[key])
            return loaded
        
        return merge_dict(defaults, loaded)
    
    def _generate_hwid(self) -> str:
        """Genera ID único del hardware"""
        import socket
        hostname = socket.gethostname()
        mac = os.popen('ipconfig getmac 2>/dev/null || ip link 2>/dev/null').read()
        hwid_string = f"{hostname}-{mac}".encode()
        return hashlib.sha256(hwid_string).hexdigest()[:16]
    
    def save(self) -> Tuple[bool, str]:
        """Persiste configuración a disco"""
        try:
            self.config["estadisticas"]["ultima_actualizacion"] = datetime.now().isoformat()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self._notify_observers("config_saved")
            return True, f"✅ Configuración guardada en {self.config_file}"
        except Exception as e:
            return False, f"❌ Error al guardar: {e}"
    
    # ==================== GETTERS ====================
    def get(self, key: str, default=None) -> Any:
        """Obtiene valor anidado usando punto (ej: 'trips.distancia_minima_km')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def get_all(self) -> Dict:
        """Retorna toda la configuración"""
        return self.config.copy()
    
    # ==================== SETTERS ====================
    def set(self, key: str, value: Any) -> Tuple[bool, str]:
        """Establece valor anidado con validación"""
        keys = key.split('.')
        config = self.config
        
        # Navegar hasta la clave anterior
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Validar según el tipo
        if not self._validate_setting(key, value):
            return False, f"❌ Valor inválido para {key}: {value}"
        
        config[keys[-1]] = value
        self.save()
        self._notify_observers(f"setting_changed_{key}")
        return True, f"✅ {key} = {value}"
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """Valida valores según reglas de negocio"""
        rules = {
            "trips.distancia_minima_km": lambda v: isinstance(v, (int, float)) and 0 <= v <= 100,
            "trips.distancia_maxima_km": lambda v: isinstance(v, (int, float)) and 0 <= v <= 100,
            "trips.precio_minimo_viaje": lambda v: isinstance(v, (int, float)) and v >= 0,
            "trips.rentabilidad_minima_ratio": lambda v: isinstance(v, (int, float)) and v >= 0,
            "ratings.calificacion_minima_aceptar": lambda v: isinstance(v, (int, float)) and 0 <= v <= 5,
            "ui.tema": lambda v: v in ["dark", "light"],
            "ui.idioma": lambda v: v in ["es", "en"],
            "notificaciones.overlay_posicion": lambda v: v in ["top-left", "top-right", "bottom-left", "bottom-right"],
        }
        
        validator = rules.get(key, lambda v: True)
        return validator(value)
    
    # ==================== ZONAS ====================
    def agregar_zona_favorita(self, nombre: str, lat: float, lon: float, radio_km: float = 2.0) -> Tuple[bool, str]:
        """Agrega una zona favorita"""
        zona = {"nombre": nombre, "lat": lat, "lon": lon, "radio_km": radio_km}
        self.config["zonas"]["favoritas"].append(zona)
        self.save()
        return True, f"✅ Zona favorita '{nombre}' agregada"
    
    def agregar_zona_restringida(self, nombre: str, lat: float, lon: float, radio_km: float = 1.5) -> Tuple[bool, str]:
        """Agrega una zona restringida"""
        zona = {"nombre": nombre, "lat": lat, "lon": lon, "radio_km": radio_km}
        self.config["zonas"]["restringidas"].append(zona)
        self.save()
        return True, f"✅ Zona restringida '{nombre}' agregada"
    
    def eliminar_zona_favorita(self, nombre: str) -> Tuple[bool, str]:
        """Elimina una zona favorita"""
        self.config["zonas"]["favoritas"] = [
            z for z in self.config["zonas"]["favoritas"] if z["nombre"] != nombre
        ]
        self.save()
        return True, f"✅ Zona favorita '{nombre}' eliminada"
    
    def eliminar_zona_restringida(self, nombre: str) -> Tuple[bool, str]:
        """Elimina una zona restringida"""
        self.config["zonas"]["restringidas"] = [
            z for z in self.config["zonas"]["restringidas"] if z["nombre"] != nombre
        ]
        self.save()
        return True, f"✅ Zona restringida '{nombre}' eliminada"
    
    def obtener_zonas_favoritas(self) -> List[Dict]:
        """Retorna lista de zonas favoritas"""
        return self.config["zonas"]["favoritas"].copy()
    
    def obtener_zonas_restringidas(self) -> List[Dict]:
        """Retorna lista de zonas restringidas"""
        return self.config["zonas"]["restringidas"].copy()
    
    def verificar_zona_segura(self, lat: float, lon: float, hora: str = None) -> Tuple[bool, str]:
        """Verifica si una ubicación es segura para realizar viajes"""
        import math
        
        def distancia_haversine(lat1, lon1, lat2, lon2):
            R = 6371  # km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            return R * 2 * math.asin(math.sqrt(a))
        
        # Verificar zonas restringidas
        for zona_rest in self.config["zonas"]["restringidas"]:
            dist = distancia_haversine(lat, lon, zona_rest["lat"], zona_rest["lon"])
            if dist <= zona_rest["radio_km"]:
                # Verificar horarios de restricción
                if hora:
                    restricciones = self.config["zonas"]["horarios_restriccion"]
                    for horario_rango, zonas_restringidas in restricciones.items():
                        if zona_rest["nombre"] in zonas_restringidas:
                            return False, f"⚠️ Zona {zona_rest['nombre']} restringida a esta hora"
                return False, f"⚠️ Ubicación en zona restringida: {zona_rest['nombre']}"
        
        return True, "✅ Zona segura"
    
    # ==================== AUTENTICACIÓN ====================
    def autenticar(self, email: str, token: str) -> Tuple[bool, str]:
        """Autentica el usuario"""
        self.config["auth"]["email"] = email
        self.config["auth"]["token"] = token
        self.config["auth"]["is_authenticated"] = True
        self.config["auth"]["last_login"] = datetime.now().isoformat()
        self.save()
        return True, f"✅ Autenticado como {email}"
    
    def desautenticar(self) -> Tuple[bool, str]:
        """Cierra sesión del usuario"""
        self.config["auth"]["is_authenticated"] = False
        self.config["auth"]["token"] = None
        self.save()
        return True, "✅ Sesión cerrada"
    
    def esta_autenticado(self) -> bool:
        """Verifica si el usuario está autenticado"""
        return self.config["auth"].get("is_authenticated", False)
    
    # ==================== SOPORTE ====================
    def agregar_ticket_entrada(self, asunto: str, descripcion: str, categoria: str = "general") -> Tuple[bool, str]:
        """Agrega un ticket de soporte recibido"""
        ticket = {
            "id": len(self.config["soporte"]["bandejas"]["entrada"]) + 1,
            "asunto": asunto,
            "descripcion": descripcion,
            "categoria": categoria,
            "fecha": datetime.now().isoformat(),
            "estado": "abierto",
        }
        self.config["soporte"]["bandejas"]["entrada"].append(ticket)
        self.save()
        return True, f"✅ Ticket #{ticket['id']} registrado"
    
    def agregar_ticket_salida(self, asunto: str, descripcion: str) -> Tuple[bool, str]:
        """Agrega un ticket de soporte enviado"""
        ticket = {
            "id": len(self.config["soporte"]["bandejas"]["salida"]) + 1,
            "asunto": asunto,
            "descripcion": descripcion,
            "fecha": datetime.now().isoformat(),
            "estado": "enviado",
        }
        self.config["soporte"]["bandejas"]["salida"].append(ticket)
        self.save()
        return True, f"✅ Soporte enviado #{ticket['id']}"
    
    def obtener_tickets_entrada(self) -> List[Dict]:
        """Retorna tickets de entrada"""
        return self.config["soporte"]["bandejas"]["entrada"].copy()
    
    def obtener_tickets_salida(self) -> List[Dict]:
        """Retorna tickets de salida"""
        return self.config["soporte"]["bandejas"]["salida"].copy()
    
    # ==================== ESTADÍSTICAS ====================
    def registrar_viaje(self, monto: float, duracion_min: int, distancia_km: float, calificacion: float = 5.0):
        """Registra un viaje completado"""
        viaje = {
            "fecha": datetime.now().isoformat(),
            "monto": monto,
            "duracion": duracion_min,
            "distancia": distancia_km,
            "calificacion": calificacion,
        }
        
        stats = self.config["estadisticas"]
        stats["historial_viajes"].append(viaje)
        stats["viajes_hoy"] += 1
        stats["ganancias_hoy"] += monto
        
        self.config["ratings"]["total_viajes"] += 1
        self.config["ratings"]["total_ganancias"] += monto
        
        self.save()
        return True, f"✅ Viaje registrado: ${monto}"
    
    def obtener_estadisticas_hoy(self) -> Dict:
        """Retorna estadísticas del día"""
        stats = self.config["estadisticas"]
        return {
            "viajes": stats["viajes_hoy"],
            "ganancias": stats["ganancias_hoy"],
            "promedio_viaje": stats["ganancias_hoy"] / max(stats["viajes_hoy"], 1),
        }
    
    # ==================== OBSERVERS (Patrón Observer) ====================
    def subscribe(self, callback):
        """Se suscribe a cambios de configuración"""
        self.observers.append(callback)
    
    def unsubscribe(self, callback):
        """Se desuscribe de cambios"""
        if callback in self.observers:
            self.observers.remove(callback)
    
    def _notify_observers(self, event: str):
        """Notifica a todos los observadores"""
        for callback in self.observers:
            try:
                callback(event)
            except Exception as e:
                print(f"Error notificando observador: {e}")


# ==================== EXPORTAR INSTANCIA GLOBAL ====================
settings = SettingsManager()


# ==================== FUNCIONES AUXILIARES ====================
def resetear_configuracion():
    """Borra la configuración y crea una nueva"""
    if os.path.exists("sentinel_settings.json"):
        os.remove("sentinel_settings.json")
    global settings
    settings = SettingsManager()
    return True, "✅ Configuración reseteada"
