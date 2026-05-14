"""
Overlay Flotante de Viajes (Trip Hijacker)
Notificación flotante que aparece por 10 segundos en pantalla
Diseñado para captar la atención del conductor de manera no intrusiva
"""
import threading
import time
from typing import Optional, Dict, Callable
from datetime import datetime

try:
    from kivy.core.window import Window
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.button import Button
    from kivy.graphics import Color, Ellipse, Line, RoundedRectangle
    from kivy.metrics import dp, sp
    from kivy.animation import Animation
    from kivy.core.audio import SoundLoader
    KIVY_AVAILABLE = True
except ImportError:
    KIVY_AVAILABLE = False


class OverlayViaje:
    """Overlay flotante para mostrar ofertas de viajes"""
    
    def __init__(
        self,
        titulo: str = "NUEVO VIAJE",
        monto: float = 250.0,
        distancia: float = 3.5,
        duracion_estimada: int = 12,
        calificacion_pasajero: float = 4.8,
        ubicacion_salida: str = "Centro Comercial",
        ubicacion_llegada: str = "Aeropuerto",
        posicion: str = "top-right",
        duracion_segundos: int = 10,
        callback_aceptar: Optional[Callable] = None,
        callback_rechazar: Optional[Callable] = None,
        tema: str = "dark",
    ):
        self.titulo = titulo
        self.monto = monto
        self.distancia = distancia
        self.duracion_estimada = duracion_estimada
        self.calificacion_pasajero = calificacion_pasajero
        self.ubicacion_salida = ubicacion_salida
        self.ubicacion_llegada = ubicacion_llegada
        self.posicion = posicion
        self.duracion_segundos = duracion_segundos
        self.callback_aceptar = callback_aceptar
        self.callback_rechazar = callback_rechazar
        self.tema = tema
        self.visible = False
        self.popup = None
        self._auto_close_thread = None
    
    def _obtener_colores(self) -> Dict:
        """Retorna paleta de colores según el tema"""
        if self.tema == "dark":
            return {
                "fondo": (0.15, 0.15, 0.20, 0.95),
                "border": (0.0, 1.0, 0.6, 1.0),  # Verde cyan
                "texto_principal": (1.0, 1.0, 1.0, 1.0),
                "texto_secundario": (0.7, 0.7, 0.7, 1.0),
                "boton_aceptar": (0.0, 0.8, 0.4, 1.0),  # Verde brillante
                "boton_rechazar": (0.8, 0.2, 0.2, 1.0),  # Rojo
            }
        else:  # light
            return {
                "fondo": (0.95, 0.95, 0.95, 0.95),
                "border": (0.0, 0.7, 0.4, 1.0),
                "texto_principal": (0.1, 0.1, 0.1, 1.0),
                "texto_secundario": (0.5, 0.5, 0.5, 1.0),
                "boton_aceptar": (0.0, 0.6, 0.3, 1.0),
                "boton_rechazar": (0.7, 0.1, 0.1, 1.0),
            }
    
    def _reproducir_sonido(self):
        """Reproduce sonido de notificación"""
        try:
            sound = SoundLoader.load('notificacion.wav')
            if sound:
                sound.play()
        except:
            pass  # Sin sonido disponible
    
    def mostrar(self):
        """Muestra el overlay flotante"""
        if not KIVY_AVAILABLE:
            print("⚠️ Kivy no disponible para overlay")
            return
        
        self.visible = True
        colores = self._obtener_colores()
        
        # Crear contenedor principal
        layout_principal = FloatLayout(size_hint=(0.3, 0.25))
        
        # Fondo con borde
        with layout_principal.canvas.before:
            Color(*colores["border"])
            self.border_rect = RoundedRectangle(
                pos=layout_principal.pos,
                size=layout_principal.size,
                radius=[15]
            )
            Color(*colores["fondo"])
            self.bg_rect = RoundedRectangle(
                pos=(layout_principal.x + 2, layout_principal.y + 2),
                size=(layout_principal.width - 4, layout_principal.height - 4),
                radius=[13]
            )
        
        # Contenido
        contenido = BoxLayout(orientation='vertical', padding=dp(12), spacing=dp(8))
        
        # Título
        titulo_label = Label(
            text=f"[b]{self.titulo}[/b]",
            markup=True,
            font_size=sp(18),
            color=colores["texto_principal"],
            size_hint_y=0.15,
        )
        contenido.add_widget(titulo_label)
        
        # Monto y distancia (principal)
        monto_label = Label(
            text=f"[b]RD${self.monto:.0f}[/b]  •  {self.distancia} km  •  {self.duracion_estimada} min",
            markup=True,
            font_size=sp(16),
            color=colores["border"],
            size_hint_y=0.18,
        )
        contenido.add_widget(monto_label)
        
        # Ubicaciones
        ubicaciones_label = Label(
            text=f"[size=12]{self.ubicacion_salida} → {self.ubicacion_llegada}[/size]",
            markup=True,
            font_size=sp(11),
            color=colores["texto_secundario"],
            size_hint_y=0.15,
        )
        contenido.add_widget(ubicaciones_label)
        
        # Calificación del pasajero
        estrellas = "⭐" * int(self.calificacion_pasajero)
        calificacion_label = Label(
            text=f"Pasajero: {estrellas} {self.calificacion_pasajero:.1f}",
            markup=True,
            font_size=sp(10),
            color=colores["texto_secundario"],
            size_hint_y=0.12,
        )
        contenido.add_widget(calificacion_label)
        
        # Botones de acción
        botones_layout = BoxLayout(size_hint_y=0.25, spacing=dp(8))
        
        btn_aceptar = Button(
            text="✓ ACEPTAR",
            background_color=colores["boton_aceptar"],
            font_size=sp(12),
            bold=True,
        )
        btn_aceptar.bind(on_press=self._on_aceptar)
        botones_layout.add_widget(btn_aceptar)
        
        btn_rechazar = Button(
            text="✗ RECHAZAR",
            background_color=colores["boton_rechazar"],
            font_size=sp(12),
            bold=True,
        )
        btn_rechazar.bind(on_press=self._on_rechazar)
        botones_layout.add_widget(btn_rechazar)
        
        contenido.add_widget(botones_layout)
        layout_principal.add_widget(contenido)
        
        # Crear y mostrar popup
        self.popup = Popup(
            title="",
            content=layout_principal,
            size_hint=self._obtener_size_hint(),
            pos_hint=self._obtener_pos_hint(),
        )
        
        # Reproducir sonido
        self._reproducir_sonido()
        
        # Mostrar
        self.popup.open()
        
        # Cerrar automáticamente después de X segundos
        self._iniciar_auto_cierre()
    
    def _obtener_size_hint(self):
        """Retorna el tamaño del overlay según posición"""
        return {"x": 0.3, "y": 0.25}
    
    def _obtener_pos_hint(self):
        """Retorna posición del overlay"""
        posiciones = {
            "top-left": {"x": 0.01, "top": 0.99},
            "top-right": {"right": 0.99, "top": 0.99},
            "bottom-left": {"x": 0.01, "y": 0.01},
            "bottom-right": {"right": 0.99, "y": 0.01},
        }
        return posiciones.get(self.posicion, posiciones["top-right"])
    
    def _iniciar_auto_cierre(self):
        """Inicia thread para cerrar automáticamente"""
        self._auto_close_thread = threading.Thread(target=self._auto_cerrar, daemon=True)
        self._auto_close_thread.start()
    
    def _auto_cerrar(self):
        """Cierra el overlay después de los segundos especificados"""
        time.sleep(self.duracion_segundos)
        if self.visible:
            self.cerrar()
    
    def _on_aceptar(self, instance):
        """Callback cuando se acepta el viaje"""
        self.cerrar()
        if self.callback_aceptar:
            self.callback_aceptar({
                "monto": self.monto,
                "distancia": self.distancia,
                "duracion": self.duracion_estimada,
                "timestamp": datetime.now().isoformat(),
            })
    
    def _on_rechazar(self, instance):
        """Callback cuando se rechaza el viaje"""
        self.cerrar()
        if self.callback_rechazar:
            self.callback_rechazar({
                "timestamp": datetime.now().isoformat(),
            })
    
    def cerrar(self):
        """Cierra el overlay"""
        if self.popup:
            try:
                self.popup.dismiss()
            except:
                pass
        self.visible = False


class OverlayManager:
    """Gestor de overlays flotantes"""
    
    def __init__(self, configuracion: Optional[Dict] = None):
        self.config = configuracion or {
            "duracion_segundos": 10,
            "posicion": "top-right",
            "tema": "dark",
            "sonido_habilitado": True,
        }
        self.overlays_activos = []
    
    def mostrar_viaje(
        self,
        monto: float,
        distancia: float,
        duracion_estimada: int,
        calificacion_pasajero: float = 4.8,
        ubicacion_salida: str = "Centro",
        ubicacion_llegada: str = "Destino",
        callback_aceptar: Optional[Callable] = None,
        callback_rechazar: Optional[Callable] = None,
    ) -> OverlayViaje:
        """Muestra un nuevo overlay de viaje"""
        
        overlay = OverlayViaje(
            titulo="🚗 NUEVO VIAJE",
            monto=monto,
            distancia=distancia,
            duracion_estimada=duracion_estimada,
            calificacion_pasajero=calificacion_pasajero,
            ubicacion_salida=ubicacion_salida,
            ubicacion_llegada=ubicacion_llegada,
            posicion=self.config["posicion"],
            duracion_segundos=self.config["duracion_segundos"],
            callback_aceptar=callback_aceptar,
            callback_rechazar=callback_rechazar,
            tema=self.config["tema"],
        )
        
        overlay.mostrar()
        self.overlays_activos.append(overlay)
        return overlay
    
    def cerrar_todos(self):
        """Cierra todos los overlays activos"""
        for overlay in self.overlays_activos:
            overlay.cerrar()
        self.overlays_activos.clear()
    
    def actualizar_tema(self, tema: str):
        """Actualiza el tema de todos los overlays"""
        self.config["tema"] = tema
    
    def actualizar_posicion(self, posicion: str):
        """Actualiza la posición de nuevos overlays"""
        self.config["posicion"] = posicion


# ==================== INSTANCIA GLOBAL ====================
overlay_manager = OverlayManager()


# ==================== PRUEBA ====================
if __name__ == "__main__" and KIVY_AVAILABLE:
    from kivy.app import App
    
    class TestApp(App):
        def build(self):
            # Mostrar overlay de prueba
            overlay_manager.mostrar_viaje(
                monto=350.0,
                distancia=5.2,
                duracion_estimada=18,
                calificacion_pasajero=4.9,
                ubicacion_salida="Plaza Central",
                ubicacion_llegada="Cibao",
                callback_aceptar=lambda d: print(f"✅ Viaje aceptado: {d}"),
                callback_rechazar=lambda d: print(f"❌ Viaje rechazado"),
            )
            
            from kivy.uix.boxlayout import BoxLayout
            layout = BoxLayout()
            return layout
    
    TestApp().run()
