"""
NOSOTROS RD - Sentinel Bot v3.0
Aplicación Principal de última generación
Dashboard completo con todas las funcionalidades
"""
import os
import sys
from datetime import datetime
from threading import Thread
import time

try:
    from kivy.app import App
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.spinner import Spinner
    from kivy.uix.togglebutton import ToggleButton
    from kivy.uix.popup import Popup
    from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
    from kivy.uix.image import Image
    from kivy.uix.screenmanager import Screen, ScreenManager
    from kivy.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
    from kivy.graphics import Color, RoundedRectangle, Line
    from kivy.metrics import dp, sp
    from kivy.core.window import Window
    from kivy.clock import Clock
    from kivy.uix.slider import Slider
    
    from kivymd.app import MDApp
    from kivymd.uix.card import MDCard
    from kivymd.uix.label import MDLabel
    from kivymd.uix.button import MDRaisedButton, MDFlatButton
    from kivymd.uix.boxlayout import MDBoxLayout
    from kivymd.uix.gridlayout import MDGridLayout
    from kivymd.uix.navigationdrawer import MDNavigationDrawer, MDNavigationLayout
    from kivymd.uix.screen import MDScreen
    from kivymd.uix.screenmanager import MDScreenManager
    from kivymd.uix.toolbar import MDTopAppBar
    from kivymd.uix.dialog import MDDialog
    from kivymd.uix.list import MDList, OneLineListItem
    from kivymd.uix.menu import MDDropdownMenu
    from kivymd.icon_definitions import md_icons
    
    KIVY_DISPONIBLE = True
except ImportError:
    KIVY_DISPONIBLE = False
    print("❌ Kivy no disponible")

from BOT_CORE.settings_manager import settings
from BOT_CORE.ui_auth_screens import LoginScreen, RegistroScreen, RecuperacionScreen
from BOT_CORE.overlay_viajes import overlay_manager
from BOT_CORE.gps_rutas import gps, calculadora_tarifa, localizador, MapasOSM
from BOT_CORE.ratings_system import ratings_manager, comentarios_manager, obtener_insignias
from BOT_CORE.support_system import soporte_manager, bandeja_mensajes
from auth_module.auth_manager import auth

Window.size = (1366, 768)
Window.clearcolor = (0.1, 0.1, 0.15, 1)


class PantallaInicio(MDScreen):
    """Pantalla de inicio / Dashboard principal"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nombre = "inicio"
        self.tema = settings.get("ui.tema", "dark")
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Topbar
        toolbar = MDTopAppBar(
            title="NOSOTROS RD - Dashboard",
            size_hint_y=0.1,
        )
        layout.add_widget(toolbar)
        
        # Contenido principal
        scroll = ScrollView()
        contenido = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=None, padding=dp(15))
        contenido.bind(minimum_height=contenido.setter('height'))
        
        # Card: Estado del Bot
        card_estado = self._crear_card(
            "🤖 Estado del Bot",
            "Online\nÚltima actividad: Hace 5 min",
            (0.0, 0.8, 0.4, 1)
        )
        contenido.add_widget(card_estado)
        
        # Card: Ganancias
        stats = settings.obtener_estadisticas_hoy()
        card_ganancias = self._crear_card(
            "💰 Ganancias Hoy",
            f"RD${stats['ganancias']:.2f}\n{stats['viajes']} viajes",
            (0.8, 0.6, 0.0, 1)
        )
        contenido.add_widget(card_ganancias)
        
        # Card: Calificación
        calif = settings.config["ratings"]["calificacion_propia"]
        card_rating = self._crear_card(
            "⭐ Mi Calificación",
            f"{calif:.1f} estrellas\n{settings.config['ratings']['total_viajes']} viajes",
            (0.9, 0.9, 0.0, 1)
        )
        contenido.add_widget(card_rating)
        
        # Card: Modo Automático
        modo_auto = settings.get("trips.aceptar_automaticamente", False)
        estado_auto = "Activado ✓" if modo_auto else "Desactivado ✗"
        card_auto = self._crear_card(
            "🔄 Modo Automático",
            estado_auto,
            (0.0, 0.6, 0.9, 1)
        )
        contenido.add_widget(card_auto)
        
        scroll.add_widget(contenido)
        layout.add_widget(scroll)
        
        # Botones de acción rápida
        botones_layout = MDBoxLayout(size_hint_y=0.12, spacing=dp(10))
        
        btn_inicio = MDRaisedButton(text="Iniciar Bot")
        btn_inicio.bind(on_press=self._iniciar_bot)
        botones_layout.add_widget(btn_inicio)
        
        btn_config = MDRaisedButton(text="Configuración")
        btn_config.bind(on_press=lambda x: self.parent.parent.current = "config")
        botones_layout.add_widget(btn_config)
        
        btn_soporte = MDRaisedButton(text="Soporte")
        btn_soporte.bind(on_press=lambda x: self.parent.parent.current = "soporte")
        botones_layout.add_widget(btn_soporte)
        
        layout.add_widget(botones_layout)
        self.add_widget(layout)
    
    def _crear_card(self, titulo, contenido, color):
        """Crea una tarjeta de información"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(120),
            md_bg_color=color,
        )
        
        card.add_widget(MDLabel(text=f"[b]{titulo}[/b]", markup=True, font_size="18sp"))
        card.add_widget(MDLabel(text=contenido, font_size="14sp"))
        
        return card
    
    def _iniciar_bot(self, instance):
        """Inicia el bot automático"""
        settings.set("trips.aceptar_automaticamente", True)
        self._mostrar_alerta("✅ Bot iniciado en modo automático")
    
    def _mostrar_alerta(self, msg):
        popup = MDDialog(title="NOSOTROS RD", text=msg)
        popup.open()


class PantallaConfiguracion(MDScreen):
    """Pantalla de configuración de parámetros"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nombre = "config"
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        toolbar = MDTopAppBar(
            title="Configuración",
            size_hint_y=0.08,
        )
        layout.add_widget(toolbar)
        
        # Tabs para diferentes secciones
        tabs = TabbedPanel(size_hint_y=0.92)
        
        # Tab: Viajes
        tab_viajes = TabbedPanelItem(text="Viajes")
        layout_viajes = self._crear_tab_viajes()
        tab_viajes.add_widget(layout_viajes)
        tabs.add_widget(tab_viajes)
        
        # Tab: Zonas
        tab_zonas = TabbedPanelItem(text="Zonas")
        layout_zonas = self._crear_tab_zonas()
        tab_zonas.add_widget(layout_zonas)
        tabs.add_widget(tab_zonas)
        
        # Tab: UI
        tab_ui = TabbedPanelItem(text="Interfaz")
        layout_ui = self._crear_tab_ui()
        tab_ui.add_widget(layout_ui)
        tabs.add_widget(tab_ui)
        
        # Tab: GPS
        tab_gps = TabbedPanelItem(text="GPS & Mapas")
        layout_gps = self._crear_tab_gps()
        tab_gps.add_widget(layout_gps)
        tabs.add_widget(tab_gps)
        
        layout.add_widget(tabs)
        self.add_widget(layout)
    
    def _crear_tab_viajes(self):
        """Tab de configuración de viajes"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        # Distancia mínima
        grid.add_widget(Label(text="Distancia Mínima (km):", size_hint_y=None, height=dp(30)))
        dist_min = TextInput(
            text=str(settings.get("trips.distancia_minima_km", 0.5)),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(dist_min)
        
        # Distancia máxima
        grid.add_widget(Label(text="Distancia Máxima (km):", size_hint_y=None, height=dp(30)))
        dist_max = TextInput(
            text=str(settings.get("trips.distancia_maxima_km", 15.0)),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(dist_max)
        
        # Precio mínimo
        grid.add_widget(Label(text="Precio Mínimo (RD$):", size_hint_y=None, height=dp(30)))
        precio_min = TextInput(
            text=str(settings.get("trips.precio_minimo_viaje", 100)),
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(precio_min)
        
        # Rentabilidad mínima
        grid.add_widget(Label(text="Rentabilidad Mínima (RD$/km):", size_hint_y=None, height=dp(30)))
        rent_min = Slider(
            min=20,
            max=100,
            value=settings.get("trips.rentabilidad_minima_ratio", 45),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(rent_min)
        
        rent_label = Label(text=f"Valor: {rent_min.value:.0f}", size_hint_y=None, height=dp(30))
        rent_min.bind(value=lambda instance, value: setattr(rent_label, 'text', f"Valor: {value:.0f}"))
        grid.add_widget(rent_label)
        
        # Botón guardar
        btn_guardar = Button(
            text="💾 Guardar Cambios",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.5, 1),
        )
        
        def guardar_viajes(instance):
            settings.set("trips.distancia_minima_km", float(dist_min.text or 0.5))
            settings.set("trips.distancia_maxima_km", float(dist_max.text or 15))
            settings.set("trips.precio_minimo_viaje", float(precio_min.text or 100))
            settings.set("trips.rentabilidad_minima_ratio", rent_min.value)
            self._mostrar_alerta("✅ Configuración guardada")
        
        btn_guardar.bind(on_press=guardar_viajes)
        grid.add_widget(btn_guardar)
        
        layout.add_widget(grid)
        return layout
    
    def _crear_tab_zonas(self):
        """Tab de gestión de zonas"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        # Zonas Favoritas
        grid.add_widget(Label(text="[b]Zonas Favoritas:[/b]", markup=True, size_hint_y=None, height=dp(30)))
        
        for zona in settings.obtener_zonas_favoritas():
            grid.add_widget(Label(
                text=f"📍 {zona['nombre']} ({zona['radio_km']}km)",
                size_hint_y=None,
                height=dp(30),
            ))
        
        # Agregar zona favorita
        grid.add_widget(Label(text="Nueva Zona Favorita:", size_hint_y=None, height=dp(30)))
        
        nombre_nueva = TextInput(hint_text="Nombre", multiline=False, size_hint_y=None, height=dp(40))
        grid.add_widget(nombre_nueva)
        
        lat_nueva = TextInput(hint_text="Latitud", multiline=False, size_hint_y=None, height=dp(40))
        grid.add_widget(lat_nueva)
        
        lon_nueva = TextInput(hint_text="Longitud", multiline=False, size_hint_y=None, height=dp(40))
        grid.add_widget(lon_nueva)
        
        btn_agregar = Button(
            text="➕ Agregar Zona Favorita",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.7, 1, 1),
        )
        
        def agregar_zona(instance):
            try:
                exito, msg = settings.agregar_zona_favorita(
                    nombre_nueva.text,
                    float(lat_nueva.text),
                    float(lon_nueva.text),
                )
                self._mostrar_alerta(msg)
                nombre_nueva.text = ""
                lat_nueva.text = ""
                lon_nueva.text = ""
            except ValueError:
                self._mostrar_alerta("❌ Coordenadas inválidas")
        
        btn_agregar.bind(on_press=agregar_zona)
        grid.add_widget(btn_agregar)
        
        # Zonas Restringidas
        grid.add_widget(Label(text="\\n[b]Zonas Restringidas:[/b]", markup=True, size_hint_y=None, height=dp(30)))
        
        for zona in settings.obtener_zonas_restringidas():
            grid.add_widget(Label(
                text=f"⛔ {zona['nombre']} ({zona['radio_km']}km)",
                size_hint_y=None,
                height=dp(30),
            ))
        
        layout.add_widget(grid)
        return layout
    
    def _crear_tab_ui(self):
        """Tab de interfaz"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        # Tema
        grid.add_widget(Label(text="Tema:", size_hint_y=None, height=dp(30)))
        
        tema_spinner = Spinner(
            text=settings.get("ui.tema", "dark"),
            values=("dark", "light"),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(tema_spinner)
        
        # Idioma
        grid.add_widget(Label(text="Idioma:", size_hint_y=None, height=dp(30)))
        
        idioma_spinner = Spinner(
            text=settings.get("ui.idioma", "es"),
            values=("es", "en"),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(idioma_spinner)
        
        # Guardar
        btn_guardar = Button(
            text="💾 Guardar",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.5, 1),
        )
        
        def guardar_ui(instance):
            settings.set("ui.tema", tema_spinner.text)
            settings.set("ui.idioma", idioma_spinner.text)
            self._mostrar_alerta("✅ Configuración guardada")
        
        btn_guardar.bind(on_press=guardar_ui)
        grid.add_widget(btn_guardar)
        
        layout.add_widget(grid)
        return layout
    
    def _crear_tab_gps(self):
        """Tab de GPS y mapas"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="Proveedor de Mapas:", size_hint_y=None, height=dp(30)))
        
        proveedor_spinner = Spinner(
            text=settings.get("gps.proveedor_mapas", "osm"),
            values=("google", "osm"),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(proveedor_spinner)
        
        grid.add_widget(Label(text="Distancia de Visualización:", size_hint_y=None, height=dp(30)))
        
        distancia_spinner = Spinner(
            text=settings.get("gps.distancia_mostrar_viajes", "30km"),
            values=("15km", "30km", "50km", "15minutos", "30minutos"),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(distancia_spinner)
        
        # Guardar
        btn_guardar = Button(
            text="💾 Guardar",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.5, 1),
        )
        
        def guardar_gps(instance):
            settings.set("gps.proveedor_mapas", proveedor_spinner.text)
            settings.set("gps.distancia_mostrar_viajes", distancia_spinner.text)
            self._mostrar_alerta("✅ Configuración de GPS guardada")
        
        btn_guardar.bind(on_press=guardar_gps)
        grid.add_widget(btn_guardar)
        
        layout.add_widget(grid)
        return layout
    
    def _mostrar_alerta(self, msg):
        popup = Popup(
            title="Configuración",
            content=Label(text=msg),
            size_hint=(0.8, 0.3),
        )
        popup.open()


class PantallaSoporte(MDScreen):
    """Pantalla de sistema de soporte"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nombre = "soporte"
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        toolbar = MDTopAppBar(
            title="Centro de Soporte",
            size_hint_y=0.08,
        )
        layout.add_widget(toolbar)
        
        # Tabs
        tabs = TabbedPanel(size_hint_y=0.92)
        
        # Tab: Nuevos Tickets
        tab_nuevo = TabbedPanelItem(text="Nuevo Ticket")
        layout_nuevo = self._crear_tab_nuevo_ticket()
        tab_nuevo.add_widget(layout_nuevo)
        tabs.add_widget(tab_nuevo)
        
        # Tab: Mis Tickets
        tab_mis = TabbedPanelItem(text="Mis Tickets")
        layout_mis = self._crear_tab_mis_tickets()
        tab_mis.add_widget(layout_mis)
        tabs.add_widget(tab_mis)
        
        # Tab: FAQ
        tab_faq = TabbedPanelItem(text="FAQ")
        layout_faq = self._crear_tab_faq()
        tab_faq.add_widget(layout_faq)
        tabs.add_widget(tab_faq)
        
        # Tab: Bandeja
        tab_bandeja = TabbedPanelItem(text="Bandeja")
        layout_bandeja = self._crear_tab_bandeja()
        tab_bandeja.add_widget(layout_bandeja)
        tabs.add_widget(tab_bandeja)
        
        layout.add_widget(tabs)
        self.add_widget(layout)
    
    def _crear_tab_nuevo_ticket(self):
        """Tab para crear nuevo ticket"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="Categoría:", size_hint_y=None, height=dp(30)))
        categoria = Spinner(
            text="general",
            values=("general", "tecnico", "billing", "seguridad", "viaje"),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(categoria)
        
        grid.add_widget(Label(text="Asunto:", size_hint_y=None, height=dp(30)))
        asunto = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(asunto)
        
        grid.add_widget(Label(text="Descripción:", size_hint_y=None, height=dp(30)))
        descripcion = TextInput(
            multiline=True,
            size_hint_y=None,
            height=dp(120),
        )
        grid.add_widget(descripcion)
        
        grid.add_widget(Label(text="Prioridad:", size_hint_y=None, height=dp(30)))
        prioridad = Spinner(
            text="normal",
            values=("baja", "normal", "alta", "urgente"),
            size_hint_y=None,
            height=dp(40),
        )
        grid.add_widget(prioridad)
        
        btn_crear = Button(
            text="📬 Enviar Ticket",
            size_hint_y=None,
            height=dp(50),
            background_color=(0, 0.8, 0.5, 1),
        )
        
        def crear_ticket(instance):
            exito, msg, ticket_id = soporte_manager.crear_ticket(
                asunto.text,
                descripcion.text,
                categoria.text,
                prioridad.text,
                "user@example.com",
            )
            self._mostrar_alerta(msg)
            if exito:
                asunto.text = ""
                descripcion.text = ""
        
        btn_crear.bind(on_press=crear_ticket)
        grid.add_widget(btn_crear)
        
        layout.add_widget(grid)
        return layout
    
    def _crear_tab_mis_tickets(self):
        """Tab de tickets del usuario"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        tickets = soporte_manager.obtener_todos_tickets()
        
        if not tickets:
            grid.add_widget(Label(
                text="Sin tickets registrados",
                size_hint_y=None,
                height=dp(40),
            ))
        else:
            for ticket in tickets[-10:]:  # Últimos 10
                titulo = f"#{ticket['id']} - {ticket['asunto']}"
                estado_color = "(🟢 Abierto)" if ticket['estado'] == 'abierto' else f"({ticket['estado']})"
                grid.add_widget(Label(
                    text=f"{titulo} {estado_color}",
                    size_hint_y=None,
                    height=dp(40),
                ))
        
        layout.add_widget(grid)
        return layout
    
    def _crear_tab_faq(self):
        """Tab de FAQ"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        faq_list = soporte_manager.obtener_faq()
        
        for faq in faq_list:
            grid.add_widget(Label(
                text=f"[b]Q: {faq['pregunta']}[/b]",
                markup=True,
                size_hint_y=None,
                height=dp(30),
            ))
            grid.add_widget(Label(
                text=f"A: {faq['respuesta']}",
                size_hint_y=None,
                height=dp(40),
            ))
            grid.add_widget(Label(size_hint_y=None, height=dp(10)))
        
        layout.add_widget(grid)
        return layout
    
    def _crear_tab_bandeja(self):
        """Tab de bandeja de entrada/salida"""
        layout = ScrollView()
        grid = GridLayout(cols=1, spacing=dp(15), size_hint_y=None, padding=dp(15))
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="[b]Bandeja de Entrada[/b]", markup=True, size_hint_y=None, height=dp(30)))
        
        entrada = bandeja_mensajes.obtener_entrada()
        for msg in entrada[-5:]:
            grid.add_widget(Label(
                text=f"De: {msg['de']} - {msg['asunto']}",
                size_hint_y=None,
                height=dp(40),
            ))
        
        grid.add_widget(Label(size_hint_y=None, height=dp(20)))
        grid.add_widget(Label(text="[b]Bandeja de Salida[/b]", markup=True, size_hint_y=None, height=dp(30)))
        
        salida = bandeja_mensajes.obtener_salida()
        for msg in salida[-5:]:
            grid.add_widget(Label(
                text=f"Para: {msg['para']} - {msg['asunto']}",
                size_hint_y=None,
                height=dp(40),
            ))
        
        layout.add_widget(grid)
        return layout
    
    def _mostrar_alerta(self, msg):
        popup = Popup(
            title="Soporte",
            content=Label(text=msg),
            size_hint=(0.8, 0.3),
        )
        popup.open()


class PantallaRatings(MDScreen):
    """Pantalla de calificaciones y estadísticas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nombre = "ratings"
        
        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        toolbar = MDTopAppBar(
            title="Mi Calificación",
            size_hint_y=0.08,
        )
        layout.add_widget(toolbar)
        
        # Mostrar calificación
        user_id = "conductor_001"
        stats = ratings_manager.obtener_estadisticas(user_id)
        
        if stats:
            info_layout = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=0.25)
            
            # Promedio
            calif_card = MDCard(
                orientation='vertical',
                padding=dp(15),
                md_bg_color=(0.9, 0.9, 0.0, 1),
            )
            calif_card.add_widget(MDLabel(
                text=f"⭐ {stats['calificacion_promedio']}",
                font_size="28sp",
            ))
            calif_card.add_widget(MDLabel(
                text=f"De {stats['total_ratings']} viajes",
                font_size="12sp",
            ))
            info_layout.add_widget(calif_card)
            
            # Insignias
            insignias = obtener_insignias(user_id)
            insignias_text = "\\n".join(insignias) if insignias else "Sin insignias"
            
            insignias_card = MDCard(
                orientation='vertical',
                padding=dp(15),
                md_bg_color=(0.8, 0.2, 0.2, 1),
            )
            insignias_card.add_widget(MDLabel(
                text=f"🏆 Insignias\\n{insignias_text}",
                markup=True,
                font_size="12sp",
            ))
            info_layout.add_widget(insignias_card)
            
            layout.add_widget(info_layout)
        
        layout.add_widget(MDLabel(text=""))
        self.add_widget(layout)


class SentinelApp(MDApp):
    """Aplicación Principal"""
    
    def build(self):
        """Construye la aplicación principal"""
        
        if not KIVY_DISPONIBLE:
            return Label(text="❌ Kivy no disponible")
        
        # Screen Manager
        sm = MDScreenManager()
        
        # Pantalla de Login
        login_screen = MDScreen(name="login")
        login_layout = LoginScreen(callback_exito=self._on_login_exito)
        login_screen.add_widget(login_layout)
        sm.add_widget(login_screen)
        
        # Pantalla de Registro
        registro_screen = MDScreen(name="registro")
        registro_layout = RegistroScreen()
        registro_screen.add_widget(registro_layout)
        sm.add_widget(registro_screen)
        
        # Pantalla de Recuperación
        recovery_screen = MDScreen(name="recovery")
        recovery_layout = RecuperacionScreen()
        recovery_screen.add_widget(recovery_layout)
        sm.add_widget(recovery_screen)
        
        # Pantalla de Inicio (Dashboard)
        inicio_screen = PantallaInicio(name="inicio")
        sm.add_widget(inicio_screen)
        
        # Pantalla de Configuración
        config_screen = PantallaConfiguracion(name="config")
        sm.add_widget(config_screen)
        
        # Pantalla de Soporte
        soporte_screen = PantallaSoporte(name="soporte")
        sm.add_widget(soporte_screen)
        
        # Pantalla de Ratings
        ratings_screen = PantallaRatings(name="ratings")
        sm.add_widget(ratings_screen)
        
        # Empezar en login si no autenticado
        if not auth.esta_autenticado():
            sm.current = "login"
        else:
            sm.current = "inicio"
        
        return sm
    
    def _on_login_exito(self, token):
        """Callback cuando login es exitoso"""
        # Navegar a dashboard
        self.root.current = "inicio"


def main():
    """Función principal"""
    try:
        app = SentinelApp()
        app.run()
    except Exception as e:
        print(f"❌ Error en aplicación: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
