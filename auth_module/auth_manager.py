"""
Sistema de Autenticación y Registro
Login robusto con validación, recuperación de contraseña, etc.
"""
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Tuple, Dict, Optional
import os
import re

class AuthManager:
    """Gestor de autenticación con encriptación y validación"""
    
    def __init__(self, db_file: str = "users_db.json"):
        self.db_file = db_file
        self.users = self._load_database()
        self.sessions = {}  # Sesiones activas
        self.password_reset_tokens = {}  # Tokens para recuperar contraseña
        
    def _load_database(self) -> Dict:
        """Carga la base de datos de usuarios"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_database(self) -> bool:
        """Persiste la base de datos de usuarios"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar BD: {e}")
            return False
    
    # ==================== VALIDACIONES ====================
    def _validar_email(self, email: str) -> Tuple[bool, str]:
        """Valida formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "❌ Email inválido"
        return True, "✅"
    
    def _validar_contraseña(self, password: str) -> Tuple[bool, str]:
        """Valida fortaleza de contraseña"""
        if len(password) < 8:
            return False, "❌ Contraseña debe tener al menos 8 caracteres"
        if not re.search(r'[A-Z]', password):
            return False, "❌ Debe contener al menos una mayúscula"
        if not re.search(r'[0-9]', password):
            return False, "❌ Debe contener al menos un número"
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "❌ Debe contener al menos un carácter especial"
        return True, "✅"
    
    def _validar_telefono(self, telefono: str) -> Tuple[bool, str]:
        """Valida formato de teléfono"""
        telefono = telefono.replace("+", "").replace("-", "").replace(" ", "")
        if len(telefono) < 10 or not telefono.isdigit():
            return False, "❌ Teléfono inválido"
        return True, "✅"
    
    def _hash_password(self, password: str) -> str:
        """Encripta contraseña con salt"""
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verifica contraseña contra hash almacenado"""
        try:
            salt, hash_hex = stored_hash.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hash_obj.hex() == hash_hex
        except:
            return False
    
    # ==================== REGISTRO ====================
    def registrar(self, email: str, contraseña: str, telefono: str, nombre: str) -> Tuple[bool, str]:
        """Registra un nuevo usuario"""
        
        # Validaciones
        valido, msg = self._validar_email(email)
        if not valido:
            return False, msg
        
        if email in self.users:
            return False, "❌ Email ya registrado"
        
        valido, msg = self._validar_contraseña(contraseña)
        if not valido:
            return False, msg
        
        valido, msg = self._validar_telefono(telefono)
        if not valido:
            return False, msg
        
        if len(nombre) < 2:
            return False, "❌ Nombre debe tener al menos 2 caracteres"
        
        # Crear usuario
        user_id = secrets.token_hex(16)
        self.users[email] = {
            "user_id": user_id,
            "nombre": nombre,
            "email": email,
            "telefono": telefono,
            "password_hash": self._hash_password(contraseña),
            "fecha_registro": datetime.now().isoformat(),
            "activo": True,
            "verificado": False,
            "prefil_completado": False,
        }
        
        self._save_database()
        return True, f"✅ Usuario {nombre} registrado exitosamente"
    
    # ==================== LOGIN ====================
    def login(self, email: str, contraseña: str) -> Tuple[bool, str, Optional[str]]:
        """Autentica un usuario y crea sesión"""
        
        if email not in self.users:
            return False, "❌ Usuario no encontrado", None
        
        usuario = self.users[email]
        
        if not usuario.get("activo"):
            return False, "❌ Usuario inactivo", None
        
        if not self._verify_password(contraseña, usuario["password_hash"]):
            return False, "❌ Contraseña incorrecta", None
        
        # Crear token de sesión
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            "email": email,
            "user_id": usuario["user_id"],
            "fecha_inicio": datetime.now().isoformat(),
            "fecha_expiracion": (datetime.now() + timedelta(days=7)).isoformat(),
        }
        
        return True, f"✅ Bienvenido {usuario['nombre']}", token
    
    def logout(self, token: str) -> Tuple[bool, str]:
        """Cierra la sesión del usuario"""
        if token in self.sessions:
            del self.sessions[token]
            return True, "✅ Sesión cerrada"
        return False, "❌ Token inválido"
    
    # ==================== VALIDACIÓN DE SESIÓN ====================
    def validar_token(self, token: str) -> Tuple[bool, Optional[Dict]]:
        """Valida si un token es válido y no expiró"""
        if token not in self.sessions:
            return False, None
        
        sesion = self.sessions[token]
        fecha_exp = datetime.fromisoformat(sesion["fecha_expiracion"])
        
        if datetime.now() > fecha_exp:
            del self.sessions[token]
            return False, None
        
        return True, sesion
    
    def obtener_usuario(self, email: str) -> Optional[Dict]:
        """Obtiene datos del usuario (sin contraseña)"""
        if email not in self.users:
            return None
        
        usuario = self.users[email].copy()
        del usuario["password_hash"]
        return usuario
    
    # ==================== RECUPERACIÓN DE CONTRASEÑA ====================
    def solicitar_recuperar_contraseña(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """Genera token para recuperar contraseña"""
        
        if email not in self.users:
            return False, "❌ Email no registrado", None
        
        token = secrets.token_urlsafe(32)
        self.password_reset_tokens[token] = {
            "email": email,
            "fecha_creacion": datetime.now().isoformat(),
            "expiracion": (datetime.now() + timedelta(hours=1)).isoformat(),
        }
        
        return True, f"✅ Token de recuperación enviado a {email}", token
    
    def cambiar_contraseña_con_token(self, token: str, nueva_contraseña: str) -> Tuple[bool, str]:
        """Cambia contraseña usando token de recuperación"""
        
        if token not in self.password_reset_tokens:
            return False, "❌ Token inválido"
        
        reset_data = self.password_reset_tokens[token]
        exp = datetime.fromisoformat(reset_data["expiracion"])
        
        if datetime.now() > exp:
            del self.password_reset_tokens[token]
            return False, "❌ Token expirado"
        
        valido, msg = self._validar_contraseña(nueva_contraseña)
        if not valido:
            return False, msg
        
        email = reset_data["email"]
        self.users[email]["password_hash"] = self._hash_password(nueva_contraseña)
        self._save_database()
        
        del self.password_reset_tokens[token]
        return True, "✅ Contraseña cambiada exitosamente"
    
    def cambiar_contraseña_directo(self, email: str, contraseña_actual: str, nueva_contraseña: str) -> Tuple[bool, str]:
        """Cambia contraseña verificando la actual"""
        
        if email not in self.users:
            return False, "❌ Usuario no encontrado"
        
        usuario = self.users[email]
        
        if not self._verify_password(contraseña_actual, usuario["password_hash"]):
            return False, "❌ Contraseña actual incorrecta"
        
        valido, msg = self._validar_contraseña(nueva_contraseña)
        if not valido:
            return False, msg
        
        usuario["password_hash"] = self._hash_password(nueva_contraseña)
        self._save_database()
        return True, "✅ Contraseña cambiada"
    
    # ==================== ACTUALIZACIÓN DE PERFIL ====================
    def actualizar_perfil(self, email: str, **kwargs) -> Tuple[bool, str]:
        """Actualiza datos del perfil del usuario"""
        
        if email not in self.users:
            return False, "❌ Usuario no encontrado"
        
        usuario = self.users[email]
        
        permitidos = ["nombre", "telefono", "foto_url", "prefil_completado"]
        
        for key, value in kwargs.items():
            if key not in permitidos:
                continue
            
            if key == "telefono":
                valido, msg = self._validar_telefono(value)
                if not valido:
                    return False, msg
            
            usuario[key] = value
        
        self._save_database()
        return True, "✅ Perfil actualizado"
    
    # ==================== INFORMACIÓN ====================
    def obtener_todas_sesiones(self) -> Dict:
        """Retorna todas las sesiones activas (para debug)"""
        return self.sessions.copy()
    
    def obtener_total_usuarios(self) -> int:
        """Retorna cantidad total de usuarios"""
        return len(self.users)
    
    def obtener_estadisticas(self) -> Dict:
        """Retorna estadísticas de usuarios"""
        usuarios_activos = sum(1 for u in self.users.values() if u.get("activo"))
        perfiles_completos = sum(1 for u in self.users.values() if u.get("prefil_completado"))
        
        return {
            "total_usuarios": len(self.users),
            "usuarios_activos": usuarios_activos,
            "perfiles_completos": perfiles_completos,
            "sesiones_activas": len(self.sessions),
        }


# ==================== EXPORTAR INSTANCIA GLOBAL ====================
auth = AuthManager()


# ==================== FUNCIONES DE PRUEBA ====================
if __name__ == "__main__":
    # Pruebas
    exito, msg = auth.registrar(
        "juan@example.com",
        "MiPassword123!",
        "+1-809-2345678",
        "Juan Pérez"
    )
    print(msg)
    
    exito, msg, token = auth.login("juan@example.com", "MiPassword123!")
    print(msg, token if exito else "")
