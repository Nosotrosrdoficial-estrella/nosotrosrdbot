"""
Endpoint Obfuscation System — Security Layer
Protege las URLs del servidor contra ingeniería inversa del APK
"""
import base64
import json

# Endpoints obfuscados en base64 (decodificados al momento de uso)
OBFUSCATED_ENDPOINTS = {
    # http://127.0.0.1:5000
    "local_dev": "aHR0cDovLzEyNy4wLjAuMTo1MDAwCg==",
    # https://atm-admin-aqk6.onrender.com
    "render_prod": "aHR0cHM6Ly9hdG0tYWRtaW4tYXFrNi5vbmRlcmVuZGVyLmNvbQ==",
    # http://localhost:5000
    "localhost": "aHR0cDovL2xvY2FsaG9zdDo1MDAwCg==",
}

class EndpointObfuscator:
    """Sistema de obfuscación y decodificación segura de endpoints."""
    
    @staticmethod
    def decode_endpoint(obfuscated_key: str) -> str:
        """Decodifica un endpoint obfuscado (solo al momento de uso)."""
        if obfuscated_key not in OBFUSCATED_ENDPOINTS:
            raise ValueError(f"Endpoint '{obfuscated_key}' no exis te.")
        
        try:
            encoded = OBFUSCATED_ENDPOINTS[obfuscated_key]
            decoded = base64.b64decode(encoded).decode('utf-8').strip()
            return decoded
        except Exception as e:
            raise RuntimeError(f"Error decodificando endpoint: {e}")
    
    @staticmethod
    def get_all_endpoints() -> dict:
        """Retorna todos los endpoints decodificados (uso interno únicamente)."""
        return {
            key: base64.b64decode(encoded).decode('utf-8').strip()
            for key, encoded in OBFUSCATED_ENDPOINTS.items()
        }
    
    @staticmethod
    def add_endpoint(name: str, url: str) -> str:
        """Crea un nuevo endpoint obfuscado."""
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        OBFUSCATED_ENDPOINTS[name] = encoded
        return encoded
    
    @staticmethod
    def validate_endpoint(obfuscated_key: str) -> tuple:
        """Valida que un endpoint sea accesible."""
        import requests
        try:
            url = EndpointObfuscator.decode_endpoint(obfuscated_key)
            response = requests.get(url, timeout=3)
            return response.status_code < 500, None
        except Exception as e:
            return False, str(e)


# Función de conveniencia
def get_endpoint(key: str = "local_dev") -> str:
    """Obtiene un endpoint decodificado."""
    return EndpointObfuscator.decode_endpoint(key)
