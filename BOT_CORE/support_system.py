"""
Sistema de Soporte al Cliente
Gestión de tickets, chat, FAQ y resolución de problemas
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import uuid

class SoporteTicket:
    """Representa un ticket de soporte individual"""
    
    def __init__(
        self,
        asunto: str,
        descripcion: str,
        categoria: str = "general",
        prioridad: str = "normal",
        email_usuario: str = None,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.asunto = asunto
        self.descripcion = descripcion
        self.categoria = categoria
        self.prioridad = prioridad
        self.email_usuario = email_usuario
        self.estado = "abierto"  # abierto, en_progreso, resuelto, cerrado
        self.fecha_creacion = datetime.now().isoformat()
        self.fecha_ultima_actualizacion = datetime.now().isoformat()
        self.respuestas = []
        self.asignado_a = None
    
    def to_dict(self) -> Dict:
        """Convierte ticket a diccionario"""
        return {
            "id": self.id,
            "asunto": self.asunto,
            "descripcion": self.descripcion,
            "categoria": self.categoria,
            "prioridad": self.prioridad,
            "email_usuario": self.email_usuario,
            "estado": self.estado,
            "fecha_creacion": self.fecha_creacion,
            "fecha_ultima_actualizacion": self.fecha_ultima_actualizacion,
            "respuestas": self.respuestas,
            "asignado_a": self.asignado_a,
        }


class SoporteManager:
    """Gestor centralizado de soporte"""
    
    def __init__(self, db_file: str = "soporte_db.json"):
        self.db_file = db_file
        self.tickets = self._load_database()
        self.categorias = [
            "general",
            "tecnico",
            "billing",
            "seguridad",
            "viaje",
            "conductor",
            "pasajero",
            "otro",
        ]
        self.prioridades = ["baja", "normal", "alta", "urgente"]
    
    def _load_database(self) -> Dict:
        """Carga base de datos de soporte"""
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
                json.dump(self.tickets, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error guardando soporte: {e}")
            return False
    
    # ==================== CREAR TICKET ====================
    def crear_ticket(
        self,
        asunto: str,
        descripcion: str,
        categoria: str = "general",
        prioridad: str = "normal",
        email_usuario: str = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """Crea un nuevo ticket de soporte"""
        
        if len(asunto) < 5:
            return False, "❌ Asunto muy corto", None
        
        if len(descripcion) < 10:
            return False, "❌ Descripción muy corta", None
        
        if categoria not in self.categorias:
            return False, f"❌ Categoría inválida. Válidas: {self.categorias}", None
        
        if prioridad not in self.prioridades:
            return False, f"❌ Prioridad inválida. Válidas: {self.prioridades}", None
        
        ticket = SoporteTicket(
            asunto=asunto,
            descripcion=descripcion,
            categoria=categoria,
            prioridad=prioridad,
            email_usuario=email_usuario,
        )
        
        self.tickets[ticket.id] = ticket.to_dict()
        self._save_database()
        
        return True, f"✅ Ticket #{ticket.id} creado", ticket.id
    
    # ==================== CONSULTAR TICKETS ====================
    def obtener_ticket(self, ticket_id: str) -> Optional[Dict]:
        """Obtiene un ticket por ID"""
        return self.tickets.get(ticket_id)
    
    def obtener_tickets_usuario(self, email_usuario: str) -> List[Dict]:
        """Obtiene todos los tickets de un usuario"""
        return [
            t for t in self.tickets.values()
            if t["email_usuario"] == email_usuario
        ]
    
    def obtener_tickets_por_estado(self, estado: str) -> List[Dict]:
        """Obtiene tickets por estado"""
        return [t for t in self.tickets.values() if t["estado"] == estado]
    
    def obtener_tickets_por_categoria(self, categoria: str) -> List[Dict]:
        """Obtiene tickets por categoría"""
        return [t for t in self.tickets.values() if t["categoria"] == categoria]
    
    def obtener_tickets_por_prioridad(self, prioridad: str) -> List[Dict]:
        """Obtiene tickets ordenados por prioridad"""
        orden_prioridad = {"urgente": 0, "alta": 1, "normal": 2, "baja": 3}
        tickets = [t for t in self.tickets.values() if t["prioridad"] == prioridad]
        return sorted(tickets, key=lambda x: x["fecha_creacion"])
    
    def obtener_todos_tickets(self) -> List[Dict]:
        """Obtiene todos los tickets"""
        return list(self.tickets.values())
    
    # ==================== ACTUALIZAR TICKET ====================
    def actualizar_estado(self, ticket_id: str, nuevo_estado: str) -> Tuple[bool, str]:
        """Actualiza el estado de un ticket"""
        
        if ticket_id not in self.tickets:
            return False, "❌ Ticket no encontrado"
        
        estados_validos = ["abierto", "en_progreso", "resuelto", "cerrado"]
        if nuevo_estado not in estados_validos:
            return False, f"❌ Estado inválido. Válidos: {estados_validos}"
        
        self.tickets[ticket_id]["estado"] = nuevo_estado
        self.tickets[ticket_id]["fecha_ultima_actualizacion"] = datetime.now().isoformat()
        self._save_database()
        
        return True, f"✅ Ticket #{ticket_id} actualizado a {nuevo_estado}"
    
    def asignar_agente(self, ticket_id: str, agente: str) -> Tuple[bool, str]:
        """Asigna un agente al ticket"""
        
        if ticket_id not in self.tickets:
            return False, "❌ Ticket no encontrado"
        
        self.tickets[ticket_id]["asignado_a"] = agente
        self._save_database()
        
        return True, f"✅ Ticket asignado a {agente}"
    
    # ==================== RESPUESTAS ====================
    def agregar_respuesta(self, ticket_id: str, respuesta: str, por: str) -> Tuple[bool, str]:
        """Agrega una respuesta a un ticket"""
        
        if ticket_id not in self.tickets:
            return False, "❌ Ticket no encontrado"
        
        if len(respuesta) < 5:
            return False, "❌ Respuesta muy corta"
        
        entrada = {
            "fecha": datetime.now().isoformat(),
            "de": por,
            "contenido": respuesta,
        }
        
        self.tickets[ticket_id]["respuestas"].append(entrada)
        self.tickets[ticket_id]["fecha_ultima_actualizacion"] = datetime.now().isoformat()
        self._save_database()
        
        return True, "✅ Respuesta agregada"
    
    def obtener_respuestas(self, ticket_id: str) -> List[Dict]:
        """Obtiene respuestas de un ticket"""
        
        if ticket_id not in self.tickets:
            return []
        
        return self.tickets[ticket_id].get("respuestas", []).copy()
    
    # ==================== ESTADÍSTICAS ====================
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de soporte"""
        
        total = len(self.tickets)
        abiertos = len([t for t in self.tickets.values() if t["estado"] == "abierto"])
        en_progreso = len([t for t in self.tickets.values() if t["estado"] == "en_progreso"])
        resueltos = len([t for t in self.tickets.values() if t["estado"] == "resuelto"])
        cerrados = len([t for t in self.tickets.values() if t["estado"] == "cerrado"])
        
        tickets_urgentes = len([t for t in self.tickets.values() if t["prioridad"] == "urgente"])
        
        return {
            "total_tickets": total,
            "abiertos": abiertos,
            "en_progreso": en_progreso,
            "resueltos": resueltos,
            "cerrados": cerrados,
            "urgentes": tickets_urgentes,
            "tasa_resolucion": f"{(resueltos / max(total, 1) * 100):.1f}%",
        }
    
    # ==================== FAQ ====================
    def obtener_faq(self) -> List[Dict]:
        """Retorna preguntas frecuentes"""
        return [
            {
                "id": 1,
                "pregunta": "¿Cómo cambio mi contraseña?",
                "respuesta": "Ve a Configuración > Seguridad > Cambiar Contraseña",
            },
            {
                "id": 2,
                "pregunta": "¿Cómo reporto un problema?",
                "respuesta": "Abre un ticket de soporte desde la sección Ayuda > Nuevo Ticket",
            },
            {
                "id": 3,
                "pregunta": "¿Cuál es el horario de atención?",
                "respuesta": "Atendemos 24/7. Respuesta en 4 horas para urgentes.",
            },
            {
                "id": 4,
                "pregunta": "¿Cómo reclamo una comisión?",
                "respuesta": "Accede a tu Dashboard > Finanzas > Reclamaciones",
            },
            {
                "id": 5,
                "pregunta": "¿Qué hago si pierdo acceso a mi cuenta?",
                "respuesta": "Usa 'Recuperar Contraseña' en la pantalla de login",
            },
        ]
    
    # ==================== RESOLVER TICKET ====================
    def resolver_ticket(self, ticket_id: str, solucion: str, puntuacion_satisfaccion: int = 5) -> Tuple[bool, str]:
        """Marca un ticket como resuelto"""
        
        if ticket_id not in self.tickets:
            return False, "❌ Ticket no encontrado"
        
        if not 1 <= puntuacion_satisfaccion <= 5:
            return False, "❌ Puntuación debe estar entre 1 y 5"
        
        self.tickets[ticket_id]["estado"] = "resuelto"
        self.tickets[ticket_id]["fecha_ultima_actualizacion"] = datetime.now().isoformat()
        self.tickets[ticket_id]["puntuacion_satisfaccion"] = puntuacion_satisfaccion
        
        # Agregar respuesta final
        self.agregar_respuesta(ticket_id, solucion, "soporte_admin")
        
        return True, f"✅ Ticket #{ticket_id} resuelto"
    
    # ==================== CERRAR TICKET ====================
    def cerrar_ticket(self, ticket_id: str) -> Tuple[bool, str]:
        """Cierra permanentemente un ticket"""
        
        if ticket_id not in self.tickets:
            return False, "❌ Ticket no encontrado"
        
        self.tickets[ticket_id]["estado"] = "cerrado"
        self.tickets[ticket_id]["fecha_ultima_actualizacion"] = datetime.now().isoformat()
        self._save_database()
        
        return True, f"✅ Ticket #{ticket_id} cerrado"


class BandejaMensajes:
    """Bandeja de entrada y salida para mensajes de soporte"""
    
    def __init__(self):
        self.bandeja_entrada = []
        self.bandeja_salida = []
        self.leidos = set()
    
    def agregar_entrada(self, de: str, asunto: str, contenido: str) -> Tuple[bool, str]:
        """Agrega mensaje a bandeja de entrada"""
        
        mensaje = {
            "id": str(uuid.uuid4())[:8],
            "de": de,
            "asunto": asunto,
            "contenido": contenido,
            "fecha": datetime.now().isoformat(),
            "leido": False,
        }
        
        self.bandeja_entrada.append(mensaje)
        return True, f"✅ Mensaje recibido de {de}"
    
    def agregar_salida(self, para: str, asunto: str, contenido: str) -> Tuple[bool, str]:
        """Agrega mensaje a bandeja de salida"""
        
        mensaje = {
            "id": str(uuid.uuid4())[:8],
            "para": para,
            "asunto": asunto,
            "contenido": contenido,
            "fecha": datetime.now().isoformat(),
            "estado": "enviado",
        }
        
        self.bandeja_salida.append(mensaje)
        return True, f"✅ Mensaje enviado a {para}"
    
    def obtener_entrada(self) -> List[Dict]:
        """Obtiene bandeja de entrada"""
        return self.bandeja_entrada.copy()
    
    def obtener_salida(self) -> List[Dict]:
        """Obtiene bandeja de salida"""
        return self.bandeja_salida.copy()
    
    def marcar_leido(self, mensaje_id: str) -> Tuple[bool, str]:
        """Marca un mensaje como leído"""
        
        for msg in self.bandeja_entrada:
            if msg["id"] == mensaje_id:
                msg["leido"] = True
                self.leidos.add(mensaje_id)
                return True, "✅ Mensaje marcado como leído"
        
        return False, "❌ Mensaje no encontrado"
    
    def obtener_no_leidos(self) -> int:
        """Retorna cantidad de mensajes no leídos"""
        return sum(1 for msg in self.bandeja_entrada if not msg["leido"])


# ==================== INSTANCIAS GLOBALES ====================
soporte_manager = SoporteManager()
bandeja_mensajes = BandejaMensajes()


# ==================== PRUEBAS ====================
if __name__ == "__main__":
    # Crear ticket
    exito, msg, ticket_id = soporte_manager.crear_ticket(
        "No puedo actualizar mi perfil",
        "Cuando intento guardar mis datos el sistema falla",
        "tecnico",
        "alta",
        "juan@example.com"
    )
    print(msg)
