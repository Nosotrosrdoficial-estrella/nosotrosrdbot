"""
Sentinel Core — Advanced Configuration System
Dark Industrial Theme with Real-time Monitoring
"""
import json
import os
import time
from datetime import datetime

CONFIG_FILE = "sentinel_config.json"

# Default configuration
DEFAULT_CONFIG = {
    "refresh_rate": 30,  # segundos
    "server_endpoint": "http://127.0.0.1:5000",
    "backup_endpoints": [
        "https://atm-admin-aqk6.onrender.com",
        "http://localhost:5000"
    ],
    "high_encryption": True,
    "auto_reconnect": True,
    "reconnect_delay": 5,  # segundos
    "max_reconnect_attempts": 5,
    "connection_timeout": 10,
    "background_sync": True,
}

class AdvancedConfig:
    """Sistema de configuración avanzado con persistencia y monitoreo."""
    
    def __init__(self):
        self.config = self._load_or_create()
        self.status = {
            "last_sync": None,
            "last_latency": None,
            "data_consumed_mb": 0.0,
            "connection_status": "disconnected",
            "reconnect_attempts": 0,
            "last_error": None,
            "uptime_seconds": 0,
        }
        self.start_time = time.time()
        
    def _load_or_create(self):
        """Carga configuración desde archivo o crea una nueva."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Merge con defaults para nuevas claves
                    merged = {**DEFAULT_CONFIG, **loaded}
                    return merged
        except Exception as e:
            print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()
    
    def save(self):
        """Persiste configuración a disco."""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True, "Configuración guardada exitosamente."
        except Exception as e:
            return False, f"Error al guardar: {e}"
    
    def update_setting(self, key, value):
        """Actualiza una configuración individual."""
        if key not in self.config:
            return False, f"Configuración '{key}' no existe."
        
        # Validaciones
        if key == "refresh_rate" and (not isinstance(value, (int, float)) or value < 1):
            return False, "Refresh Rate debe ser >= 1 segundo."
        if key == "server_endpoint" and not isinstance(value, str):
            return False, "Server Endpoint debe ser una URL válida."
        if key == "high_encryption" and not isinstance(value, bool):
            return False, "High Encryption debe ser True/False."
        
        self.config[key] = value
        return self.save()
    
    def get_all(self):
        """Retorna toda la configuración."""
        return self.config
    
    def get(self, key, default=None):
        """Obtiene un valor de configuración."""
        return self.config.get(key, default)
    
    def update_status(self, **kwargs):
        """Actualiza el estado del monitoreo."""
        for key, value in kwargs.items():
            if key in self.status:
                self.status[key] = value
        self.status["uptime_seconds"] = int(time.time() - self.start_time)
    
    def get_status(self):
        """Retorna estado actual del sistema."""
        return self.status
    
    def emergency_reset(self):
        """Reset de emergencia: limpia caché de licencia y reconecta."""
        try:
            # Limpiar sesión
            if os.path.exists("sentinel_session.json"):
                os.remove("sentinel_session.json")
            
            # Resetear estado
            self.status = {
                "last_sync": None,
                "last_latency": None,
                "data_consumed_mb": 0.0,
                "connection_status": "disconnected",
                "reconnect_attempts": 0,
                "last_error": None,
                "uptime_seconds": 0,
            }
            self.start_time = time.time()
            
            return True, "Sistema restaurado. Por favor, reinicia la aplicación."
        except Exception as e:
            return False, f"Error en reset: {e}"
    
    def validate_endpoint(self, url):
        """Valida que una URL sea accesible."""
        import requests
        try:
            response = requests.get(url + "/ping", timeout=3)
            return response.status_code == 200, None
        except Exception as e:
            return False, str(e)


# Instancia global
advanced_config = AdvancedConfig()
