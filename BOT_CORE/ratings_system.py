"""
Sistema de Ratings y Calificaciones
Gestión de reseñas, calificaciones de pasajeros y conductores
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from statistics import mean

class RatingsManager:
    """Gestor de calificaciones y reseñas"""
    
    def __init__(self, db_file: str = "ratings_db.json"):
        self.db_file = db_file
        self.ratings = self._load_database()
    
    def _load_database(self) -> Dict:
        """Carga base de datos de ratings"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_database(self) -> bool:
        """Persiste base de datos"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.ratings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando ratings: {e}")
            return False
    
    # ==================== RATING DE CONDUCTOR ====================
    def calificar_conductor(
        self,
        user_id: str,
        viaje_id: str,
        puntuacion: int,
        comentario: str = "",
        aspecto: str = "general",  # general, seguridad, limpieza, trato, rapidez
    ) -> Tuple[bool, str]:
        """Califica al conductor"""
        
        if not 1 <= puntuacion <= 5:
            return False, "❌ Puntuación debe estar entre 1 y 5"
        
        if user_id not in self.ratings:
            self.ratings[user_id] = {
                "tipo": "conductor",
                "calificacion_promedio": 5.0,
                "total_ratings": 0,
                "historial": [],
            }
        
        rating_entry = {
            "viaje_id": viaje_id,
            "puntuacion": puntuacion,
            "comentario": comentario,
            "aspecto": aspecto,
            "fecha": datetime.now().isoformat(),
        }
        
        self.ratings[user_id]["historial"].append(rating_entry)
        self._actualizar_promedio(user_id)
        self._save_database()
        
        return True, f"✅ Conductor calificado con {puntuacion}⭐"
    
    def calificar_pasajero(
        self,
        user_id: str,
        viaje_id: str,
        puntuacion: int,
        comentario: str = "",
    ) -> Tuple[bool, str]:
        """Califica al pasajero"""
        
        if not 1 <= puntuacion <= 5:
            return False, "❌ Puntuación debe estar entre 1 y 5"
        
        if user_id not in self.ratings:
            self.ratings[user_id] = {
                "tipo": "pasajero",
                "calificacion_promedio": 5.0,
                "total_ratings": 0,
                "historial": [],
            }
        
        rating_entry = {
            "viaje_id": viaje_id,
            "puntuacion": puntuacion,
            "comentario": comentario,
            "fecha": datetime.now().isoformat(),
        }
        
        self.ratings[user_id]["historial"].append(rating_entry)
        self._actualizar_promedio(user_id)
        self._save_database()
        
        return True, f"✅ Pasajero calificado con {puntuacion}⭐"
    
    def _actualizar_promedio(self, user_id: str):
        """Actualiza la calificación promedio del usuario"""
        historial = self.ratings[user_id]["historial"]
        if historial:
            puntuaciones = [r["puntuacion"] for r in historial]
            self.ratings[user_id]["calificacion_promedio"] = round(mean(puntuaciones), 2)
            self.ratings[user_id]["total_ratings"] = len(historial)
    
    # ==================== CONSULTAS ====================
    def obtener_calificacion(self, user_id: str) -> Optional[Dict]:
        """Obtiene la calificación de un usuario"""
        if user_id not in self.ratings:
            return None
        
        data = self.ratings[user_id].copy()
        return {
            "user_id": user_id,
            "calificacion": data["calificacion_promedio"],
            "total_ratings": data["total_ratings"],
            "tipo": data["tipo"],
            "estrellas": "⭐" * int(data["calificacion_promedio"]),
        }
    
    def obtener_historial(self, user_id: str, limite: int = 10) -> List[Dict]:
        """Obtiene historial de calificaciones"""
        if user_id not in self.ratings:
            return []
        
        historial = self.ratings[user_id]["historial"]
        return historial[-limite:]
    
    def obtener_estadisticas(self, user_id: str) -> Optional[Dict]:
        """Obtiene estadísticas detalladas de calificaciones"""
        if user_id not in self.ratings:
            return None
        
        historial = self.ratings[user_id]["historial"]
        if not historial:
            return None
        
        puntuaciones = [r["puntuacion"] for r in historial]
        
        return {
            "user_id": user_id,
            "calificacion_promedio": self.ratings[user_id]["calificacion_promedio"],
            "total_ratings": len(puntuaciones),
            "distribucion": {
                "5_estrellas": puntuaciones.count(5),
                "4_estrellas": puntuaciones.count(4),
                "3_estrellas": puntuaciones.count(3),
                "2_estrellas": puntuaciones.count(2),
                "1_estrella": puntuaciones.count(1),
            },
            "ultimas_valoraciones": historial[-5:],
        }
    
    def es_usuario_confiable(
        self,
        user_id: str,
        calificacion_minima: float = 4.0,
        minimo_ratings: int = 1,
    ) -> Tuple[bool, str]:
        """Verifica si un usuario es confiable según sus ratings"""
        
        if user_id not in self.ratings:
            return True, "✅ Sin historial (asumido confiable)"  # Usuario nuevo es confiable
        
        data = self.ratings[user_id]
        
        if data["total_ratings"] < minimo_ratings:
            return True, f"✅ Muy pocos ratings ({data['total_ratings']})"
        
        if data["calificacion_promedio"] >= calificacion_minima:
            return True, f"✅ Usuario confiable ({data['calificacion_promedio']}⭐)"
        else:
            return False, f"❌ Calificación baja ({data['calificacion_promedio']}⭐)"
    
    # ==================== GESTIÓN ====================
    def reportar_usuario(
        self,
        user_id: str,
        motivo: str,
        detalles: str = "",
        severidad: str = "normal",  # leve, normal, severa
    ) -> Tuple[bool, str]:
        """Reporta un usuario por comportamiento inapropiado"""
        
        if user_id not in self.ratings:
            self.ratings[user_id] = {
                "tipo": "usuario_reportado",
                "reportes": [],
            }
        
        if "reportes" not in self.ratings[user_id]:
            self.ratings[user_id]["reportes"] = []
        
        reporte = {
            "motivo": motivo,
            "detalles": detalles,
            "severidad": severidad,
            "fecha": datetime.now().isoformat(),
        }
        
        self.ratings[user_id]["reportes"].append(reporte)
        self._save_database()
        
        return True, f"✅ Usuario reportado por: {motivo}"
    
    def obtener_reportes(self, user_id: str) -> List[Dict]:
        """Obtiene reportes contra un usuario"""
        if user_id not in self.ratings or "reportes" not in self.ratings[user_id]:
            return []
        
        return self.ratings[user_id]["reportes"].copy()
    
    def suspender_usuario(self, user_id: str, razon: str, duracion_dias: int = 7) -> Tuple[bool, str]:
        """Suspende temporalmente un usuario"""
        
        if user_id not in self.ratings:
            self.ratings[user_id] = {}
        
        from datetime import timedelta
        fecha_reapertura = (datetime.now() + timedelta(days=duracion_dias)).isoformat()
        
        self.ratings[user_id]["suspendido"] = {
            "razon": razon,
            "fecha_inicio": datetime.now().isoformat(),
            "fecha_reapertura": fecha_reapertura,
            "duracion_dias": duracion_dias,
        }
        
        self._save_database()
        return True, f"✅ Usuario suspendido por {duracion_dias} días"
    
    def esta_suspendido(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Verifica si un usuario está suspendido"""
        if user_id not in self.ratings or "suspendido" not in self.ratings[user_id]:
            return False, None
        
        suspension = self.ratings[user_id]["suspendido"]
        fecha_reapertura = datetime.fromisoformat(suspension["fecha_reapertura"])
        
        if datetime.now() > fecha_reapertura:
            # Suspensión expirada
            del self.ratings[user_id]["suspendido"]
            self._save_database()
            return False, None
        
        dias_restantes = (fecha_reapertura - datetime.now()).days
        return True, f"Usuario suspendido. Reabre en {dias_restantes} días"


class ComentariosManager:
    """Gestor de comentarios y reseñas detalladas"""
    
    def __init__(self, db_file: str = "comentarios_db.json"):
        self.db_file = db_file
        self.comentarios = self._load_database()
    
    def _load_database(self) -> Dict:
        """Carga base de datos de comentarios"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_database(self) -> bool:
        """Persiste base de datos"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.comentarios, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    def agregar_comentario(
        self,
        usuario_comentador: str,
        usuario_objetivo: str,
        viaje_id: str,
        comentario: str,
        puntuacion: int,
    ) -> Tuple[bool, str]:
        """Agrega un comentario sobre un usuario"""
        
        if len(comentario) < 5 or len(comentario) > 500:
            return False, "❌ Comentario debe tener entre 5 y 500 caracteres"
        
        if usuario_objetivo not in self.comentarios:
            self.comentarios[usuario_objetivo] = []
        
        entrada = {
            "de_usuario": usuario_comentador,
            "viaje_id": viaje_id,
            "comentario": comentario,
            "puntuacion": puntuacion,
            "fecha": datetime.now().isoformat(),
            "likes": 0,
            "dislikes": 0,
        }
        
        self.comentarios[usuario_objetivo].append(entrada)
        self._save_database()
        
        return True, "✅ Comentario agregado"
    
    def obtener_comentarios(self, user_id: str) -> List[Dict]:
        """Obtiene comentarios sobre un usuario"""
        return self.comentarios.get(user_id, []).copy()
    
    def obtener_comentarios_positivos(self, user_id: str) -> List[Dict]:
        """Obtiene solo comentarios positivos (4-5 estrellas)"""
        comentarios = self.comentarios.get(user_id, [])
        return [c for c in comentarios if c["puntuacion"] >= 4]
    
    def obtener_comentarios_negativos(self, user_id: str) -> List[Dict]:
        """Obtiene solo comentarios negativos (1-2 estrellas)"""
        comentarios = self.comentarios.get(user_id, [])
        return [c for c in comentarios if c["puntuacion"] <= 2]
    
    def dar_like_comentario(self, user_id: str, indice_comentario: int) -> Tuple[bool, str]:
        """Da like a un comentario"""
        
        if user_id not in self.comentarios or indice_comentario >= len(self.comentarios[user_id]):
            return False, "❌ Comentario no encontrado"
        
        self.comentarios[user_id][indice_comentario]["likes"] += 1
        self._save_database()
        return True, "👍 Like agregado"
    
    def dar_dislike_comentario(self, user_id: str, indice_comentario: int) -> Tuple[bool, str]:
        """Da dislike a un comentario"""
        
        if user_id not in self.comentarios or indice_comentario >= len(self.comentarios[user_id]):
            return False, "❌ Comentario no encontrado"
        
        self.comentarios[user_id][indice_comentario]["dislikes"] += 1
        self._save_database()
        return True, "👎 Dislike agregado"


# ==================== INSTANCIAS GLOBALES ====================
ratings_manager = RatingsManager()
comentarios_manager = ComentariosManager()


# ==================== FUNCIONES AUXILIARES ====================
def obtener_insignias(user_id: str) -> List[str]:
    """Retorna insignias ganadas por el usuario"""
    insignias = []
    
    calificacion = ratings_manager.obtener_calificacion(user_id)
    if not calificacion:
        return insignias
    
    rating = calificacion["calificacion"]
    total = calificacion["total_ratings"]
    
    # Insignias por excelencia
    if rating >= 4.9 and total >= 50:
        insignias.append("🏆 Conductor Excelente")
    elif rating >= 4.7 and total >= 20:
        insignias.append("⭐ Muy Recomendado")
    
    # Insignias por experiencia
    if total >= 500:
        insignias.append("🚗 Veterano (500+ viajes)")
    elif total >= 100:
        insignias.append("📈 Experimentado (100+ viajes)")
    
    # Insignias por seguridad
    suspendido, _ = ratings_manager.esta_suspendido(user_id)
    if not suspendido:
        insignias.append("✅ Sin reportes")
    
    return insignias


# ==================== PRUEBAS ====================
if __name__ == "__main__":
    # Probar rating
    ratings_manager.calificar_conductor("driver_001", "trip_123", 5, "Excelente conductor")
    
    rating = ratings_manager.obtener_calificacion("driver_001")
    print(f"Rating de driver_001: {rating}")
