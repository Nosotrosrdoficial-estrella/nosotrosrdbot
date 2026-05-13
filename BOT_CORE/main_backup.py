import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.switch import Switch
from kivy.clock import Clock
import threading
import time
import uiautomator2 as u2
from screen_reader import find_price_buttons
from decision_engine import DecisionEngine
import adbutils
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config_advanced import advanced_config

try:
    from config import ADMIN_URL, VALIDAR_ENDPOINT, REMOTE_ADMIN_URL
except Exception:
    ADMIN_URL = "http://127.0.0.1:5000"
    REMOTE_ADMIN_URL = "https://atm-admin-aqk6.onrender.com"
    VALIDAR_ENDPOINT = "/validar/"

# Subscription Validation Protocol endpoints
SVP_ENDPOINT = "/validar/"
SUSCRIPCIONES_ENDPOINT = "/suscripciones"
REGISTRO_ENDPOINT = "/registro_cliente"
VERIFICAR_REG_ENDPOINT = "/verificar_registro/"
MENSAJE_ENDPOINT = "/mensaje"
SESSION_FILE = "sentinel_session.json"


def _build_base_urls():
    bases = [ADMIN_URL, "http://127.0.0.1:5000", "http://localhost:5000", REMOTE_ADMIN_URL]
    seen = set()
    result = []
    for b in bases:
        if not b:
            continue
        n = b.rstrip("/")
        if n not in seen:
            seen.add(n)
            result.append(n)
    return result


def build_validation_urls(hwid):
    endpoint = (SVP_ENDPOINT or "/validar/").strip("/")
    return [f"{b}/{endpoint}/{hwid}" for b in _build_base_urls()]


def build_subscription_urls():
    return [f"{b}{SUSCRIPCIONES_ENDPOINT}" for b in _build_base_urls()]


def build_registro_urls():
    return [f"{b}{REGISTRO_ENDPOINT}" for b in _build_base_urls()]


def build_verificar_reg_urls(hwid):
    return [f"{b}{VERIFICAR_REG_ENDPOINT}{hwid}" for b in _build_base_urls()]


def build_mensaje_urls():
    return [f"{b}{MENSAJE_ENDPOINT}" for b in _build_base_urls()]


def get_device_id():
    """Obtiene el ID único del dispositivo (HWID) para identificar el Operational Node."""
    try:
        from jnius import autoclass
        Settings = autoclass('android.provider.Settings$Secure')
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        return Settings.getString(context.getContentResolver(), Settings.ANDROID_ID)
    except Exception:
        import uuid
        return str(uuid.getnode())


def cargar_sesion():
    """Carga datos de la última sesión del Client Instance."""
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def guardar_sesion(data: dict):
    """Persiste datos de sesión del Client Instance."""
    try:
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass


def svp_verificar(hwid, nombre_socio=None):
    """Subscription Validation Protocol — Verifica acceso del Operational Node."""
    last_error = "Sin respuesta del servidor de control"
    for url in build_validation_urls(hwid):
        try:
            params = {}
            if nombre_socio:
                params['nombre'] = nombre_socio
            response = requests.get(url, params=params, timeout=10)
            if not response.ok:
                last_error = f"HTTP {response.status_code}"
                continue
            try:
                data = response.json()
            except ValueError:
                last_error = "Respuesta inválida del servidor de control"
                continue

            status = str(data.get("status", "")).strip().lower()
            access = str(data.get("access", "")).strip().lower()
            payment_ok = data.get("payment_status", False)
            vence = data.get("vence")
            nombre_detectado = data.get("nombre_socio") or nombre_socio or hwid

            if not payment_ok:
                return False, "Licencia pendiente de activación.\nContacte al administrador de sistemas.", vence

            if access == "granted" or status == "aprobado":
                return True, f"Operational Node: {nombre_detectado}\nActivo hasta: {vence}", vence

            if status == "expirado":
                return False, "Licencia Expirada.\nContacte al administrador de sistemas.", vence

            if status in ("bloqueado", "blocked"):
                return False, "Acceso Denegado.\nNodo bloqueado por el administrador de sistemas.", vence

            return False, "Licencia pendiente de activación.\nContacte al administrador de sistemas.", None
        except Exception as e:
            last_error = str(e)

    return False, f"Error de Conexión con el servidor de control.\n{last_error}", None


def obtener_suscripciones():
    """Obtiene lista de Client Instances registrados en el servidor de control."""
    for url in build_subscription_urls():
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                data = response.json()
                return data.get('suscripciones', []), None
        except Exception:
            pass
    return [], "Sin respuesta del servidor de control"


def svp_registro(hwid, nombre, email):
    """Registra nuevo Client Instance vía Subscription Validation Protocol."""
    payload = {'hwid': hwid, 'nombre': nombre, 'email': email}
    for url in build_registro_urls():
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.ok:
                return response.json(), None
        except Exception:
            pass
    return None, "Sin conexión con el servidor de control"


def svp_verificar_registro(hwid):
    """Verifica si el Operational Node está registrado en el servidor de control."""
    for url in build_verificar_reg_urls(hwid):
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                return response.json(), None
        except Exception:
            pass
    return None, "Sin conexión con el servidor de control"


def enviar_mensaje(hwid, nombre_socio, contenido):
    """Transmite mensaje desde el Client Instance al servidor de control (bandeja de salida)."""
    payload = {'hwid': hwid, 'nombre_socio': nombre_socio, 'contenido': contenido}
    for url in build_mensaje_urls():
        try:
            response = requests.post(url, json=payload, timeout=10)
            if response.ok:
                return True, "Mensaje transmitido al administrador de sistemas."
        except Exception:
            pass
    return False, "No se pudo transmitir el mensaje. Verifique la conexión."


class SentinelCoreApp(App):

    def build(self):
        self.layout = FloatLayout()
        self.hwid = get_device_id()
        self.selected_client_instance = None
        self._sentinel_activo = False
        sesion = cargar_sesion()
        self.selected_client_instance = sesion.get('client_instance')
        self.status_label = Label(
            text="Inicializando Sentinel Core...",
            size_hint=(.85, .1),
            pos_hint={"center_x": .5, "center_y": .82},
            color=(0, 1, 1, 1),
            halign='center'
        )
        self.layout.add_widget(self.status_label)
        Clock.schedule_once(
            lambda dt: threading.Thread(target=self._svp_inicio, daemon=True).start(), 1
        )
        return self.layout

    # ------------------------------------------------------------------ #
    #  Subscription Validation Protocol — Flujo de inicio
    # ------------------------------------------------------------------ #

    def _svp_inicio(self):
        """SVP Paso 1: verifica si el Operational Node está registrado."""
        reg_data, err = svp_verificar_registro(self.hwid)
        if reg_data is None:
            Clock.schedule_once(lambda dt: self.show_error_screen(
                "Sin conexión con el servidor de control.\nVerifique su red.", retry=True
            ), 0)
            return
        if not reg_data.get('registrado'):
            Clock.schedule_once(lambda dt: self.show_kyc_screen(), 0)
            return
        Clock.schedule_once(
            lambda dt: threading.Thread(target=self._load_suscripciones, daemon=True).start(), 0
        )

    # ------------------------------------------------------------------ #
    #  Pantalla KYC — Registro inicial del Client Instance
    # ------------------------------------------------------------------ #

    def show_kyc_screen(self):
        """Pantalla de Registro KYC — Client Instance no detectado en el servidor."""
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text="Sentinel Core — Registro de Nodo",
            size_hint=(.9, .08), pos_hint={"center_x": .5, "center_y": .93},
            color=(0, 1, 0.5, 1), bold=True
        ))
        self.layout.add_widget(Label(
            text="Este dispositivo no está registrado.\nComplete el formulario para solicitar acceso.",
            size_hint=(.85, .10), pos_hint={"center_x": .5, "center_y": .81},
            color=(0, 1, 1, 1), halign='center'
        ))
        self.layout.add_widget(Label(
            text=f"ID del Nodo (HWID):\n{self.hwid}",
            size_hint=(.85, .09), pos_hint={"center_x": .5, "center_y": .70},
            color=(1, 1, 0, 1), halign='center'
        ))
        self.kyc_nombre = TextInput(
            hint_text="Nombre completo del operador",
            multiline=False,
            size_hint=(.80, .07),
            pos_hint={"center_x": .5, "center_y": .59}
        )
        self.layout.add_widget(self.kyc_nombre)
        self.kyc_email = TextInput(
            hint_text="Correo electrónico",
            multiline=False,
            size_hint=(.80, .07),
            pos_hint={"center_x": .5, "center_y": .49}
        )
        self.layout.add_widget(self.kyc_email)
        self.kyc_status = Label(
            text="", size_hint=(.85, .07),
            pos_hint={"center_x": .5, "center_y": .39},
            color=(1, 0.4, 0.4, 1), halign='center'
        )
        self.layout.add_widget(self.kyc_status)
        reg_btn = Button(
            text="ENVIAR SOLICITUD DE ACCESO",
            size_hint=(.75, .08), pos_hint={"center_x": .5, "center_y": .27},
            background_color=(0, 1, 0.5, 1), color=(0, 0, 0, 1), bold=True
        )
        reg_btn.bind(on_release=lambda _: self._submit_kyc())
        self.layout.add_widget(reg_btn)

    def _submit_kyc(self):
        nombre = self.kyc_nombre.text.strip()
        email = self.kyc_email.text.strip()
        if not nombre:
            self.kyc_status.text = "El nombre del operador es obligatorio."
            return
        self.kyc_status.text = "Enviando solicitud al servidor de control..."
        threading.Thread(target=self._do_registro_kyc, args=(nombre, email), daemon=True).start()

    def _do_registro_kyc(self, nombre, email):
        result, err = svp_registro(self.hwid, nombre, email)
        if result is None:
            Clock.schedule_once(lambda dt: setattr(
                self.kyc_status, 'text',
                f"Error de conexión: {err}\nVerifique su red e intente de nuevo."
            ), 0)
            return
        guardar_sesion({'client_instance': nombre})
        self.selected_client_instance = nombre
        Clock.schedule_once(lambda dt: self.show_activation_pending_screen(), 0)

    # ------------------------------------------------------------------ #
    #  Pantalla de activación pendiente
    # ------------------------------------------------------------------ #

    def _auto_check_activation(self, dt):
        """Auto-polling: verifica cada 20 s si se activó la licencia."""
        threading.Thread(target=self._check_activation_background, daemon=True).start()

    def _check_activation_background(self):
        acceso, mensaje, vence = svp_verificar(self.hwid, self.selected_client_instance)
        if acceso:
            if hasattr(self, '_pending_clock_event') and self._pending_clock_event:
                self._pending_clock_event.cancel()
                self._pending_clock_event = None
            if self.selected_client_instance:
                Clock.schedule_once(lambda dt: self.show_operational_screen(mensaje), 0)
            else:
                Clock.schedule_once(
                    lambda dt: threading.Thread(target=self._load_suscripciones, daemon=True).start(), 0
                )

    def show_activation_pending_screen(self):
        """Pantalla: payment_status=False o estado pendiente."""
        # Cancelar cualquier polling previo antes de limpiar
        if hasattr(self, '_pending_clock_event') and self._pending_clock_event:
            self._pending_clock_event.cancel()
            self._pending_clock_event = None
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text="Sentinel Core",
            size_hint=(.9, .07), pos_hint={"center_x": .5, "center_y": .91},
            color=(0, 1, 0.5, 1), bold=True
        ))
        self.layout.add_widget(Label(
            text="Licencia pendiente de activación.\nContacte al administrador de sistemas.",
            size_hint=(.85, .13), pos_hint={"center_x": .5, "center_y": .78},
            color=(1, 1, 0, 1), halign='center'
        ))
        self.layout.add_widget(Label(
            text=f"HWID: {self.hwid}",
            size_hint=(.85, .06), pos_hint={"center_x": .5, "center_y": .65},
            color=(0.5, 0.5, 0.5, 1), halign='center'
        ))
        # Bandeja de salida: campo de mensaje
        self._msg_input = TextInput(
            hint_text="Escriba su mensaje al administrador de sistemas...",
            multiline=True,
            size_hint=(.82, .13),
            pos_hint={"center_x": .5, "center_y": .50}
        )
        self.layout.add_widget(self._msg_input)
        self._msg_status = Label(
            text="", size_hint=(.85, .05),
            pos_hint={"center_x": .5, "center_y": .37},
            color=(0, 1, 1, 1), halign='center'
        )
        self.layout.add_widget(self._msg_status)
        send_btn = Button(
            text="&#9993; TRANSMITIR MENSAJE AL ADMINISTRADOR",
            size_hint=(.78, .07), pos_hint={"center_x": .5, "center_y": .28},
            background_color=(0, 0.7, 1, 1), color=(0, 0, 0, 1)
        )
        send_btn.bind(on_release=lambda _: self._send_outbox_message())
        self.layout.add_widget(send_btn)
        retry_btn = Button(
            text="Verificar Activación",
            size_hint=(.55, .07), pos_hint={"center_x": .5, "center_y": .17},
            background_color=(0.15, 0.15, 0.15, 1), color=(0, 1, 1, 1)
        )
        retry_btn.bind(on_release=lambda _: threading.Thread(
            target=self._svp_inicio, daemon=True
        ).start())
        self.layout.add_widget(retry_btn)
        # Auto-polling cada 20 segundos
        self._pending_clock_event = Clock.schedule_interval(self._auto_check_activation, 20)

    def _send_outbox_message(self):
        contenido = self._msg_input.text.strip() if hasattr(self, '_msg_input') else ''
        if not contenido:
            self._msg_status.text = "Escriba un mensaje antes de transmitir."
            return
        nombre = self.selected_client_instance or self.hwid
        self._msg_status.text = "Transmitiendo..."
        threading.Thread(target=self._do_send_message, args=(contenido, nombre), daemon=True).start()

    def _do_send_message(self, contenido, nombre):
        ok, resp = enviar_mensaje(self.hwid, nombre, contenido)
        def _update(dt):
            self._msg_status.text = resp
            if ok and hasattr(self, '_msg_input'):
                self._msg_input.text = ''
        Clock.schedule_once(_update, 0)

    # ------------------------------------------------------------------ #
    #  Selector de Client Instance (Operational Node)
    # ------------------------------------------------------------------ #

    def _load_suscripciones(self):
        suscripciones, error = obtener_suscripciones()
        Clock.schedule_once(lambda dt: self.show_node_selector(suscripciones, error), 0)

    def show_node_selector(self, suscripciones, error=None):
        """Selector de Operational Node / Client Instance."""
        # Cancelar auto-polling si venimos de la pantalla pendiente
        if hasattr(self, '_pending_clock_event') and self._pending_clock_event:
            self._pending_clock_event.cancel()
            self._pending_clock_event = None
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text="Sentinel Core — Selección de Client Instance",
            size_hint=(.9, .08), pos_hint={"center_x": .5, "center_y": .93},
            color=(0, 1, 0.5, 1), bold=True
        ))
        self.layout.add_widget(Label(
            text="Seleccione el Operational Node para esta sesión:",
            size_hint=(.9, .07), pos_hint={"center_x": .5, "center_y": .85},
            color=(0, 1, 1, 1)
        ))
        if error:
            self.layout.add_widget(Label(
                text=f"Sin datos del servidor de control.\n{error}",
                size_hint=(.9, .07), pos_hint={"center_x": .5, "center_y": .77},
                color=(1, 0.3, 0.3, 1)
            ))

        unique_names = []
        seen = set()
        for item in suscripciones:
            nombre = (item.get('nombre_socio') or '').strip()
            if not nombre or nombre.lower() in seen:
                continue
            seen.add(nombre.lower())
            unique_names.append(item)

        start_y = 0.67
        for index, item in enumerate(unique_names[:4]):
            nombre = item.get('nombre_socio') or ''
            plan = item.get('plan') or 'Sin plan'
            estado = item.get('status') or 'Pendiente'
            payment = "Pago OK" if item.get('payment_status') else "Sin pago"
            node_btn = Button(
                text=f"{nombre}  |  {plan}  |  {estado}  |  {payment}",
                size_hint=(.82, .08),
                pos_hint={"center_x": .5, "center_y": start_y - index * 0.09},
                background_color=(0, 0.8, 1, 1), color=(0, 0, 0, 1)
            )
            node_btn.bind(on_release=lambda _, n=nombre: self._activate_node(n))
            self.layout.add_widget(node_btn)

        self.manual_node_input = TextInput(
            hint_text="ID del Client Instance (nombre)",
            multiline=False,
            size_hint=(.82, .07),
            pos_hint={"center_x": .5, "center_y": .21}
        )
        if self.selected_client_instance:
            self.manual_node_input.text = self.selected_client_instance
        self.layout.add_widget(self.manual_node_input)

        confirm_btn = Button(
            text="ACTIVAR NODO OPERACIONAL",
            size_hint=(.65, .08), pos_hint={"center_x": .5, "center_y": .10},
            background_color=(0, 1, 0.5, 1), color=(0, 0, 0, 1), bold=True
        )
        confirm_btn.bind(on_release=lambda _: self._activate_node(self.manual_node_input.text.strip()))
        self.layout.add_widget(confirm_btn)

    def _activate_node(self, nombre_socio):
        nombre_socio = (nombre_socio or '').strip()
        if not nombre_socio:
            self.show_error_screen("Debe seleccionar o ingresar un Client Instance.", retry=False)
            Clock.schedule_once(
                lambda dt: threading.Thread(target=self._load_suscripciones, daemon=True).start(), 2
            )
            return
        self.selected_client_instance = nombre_socio
        guardar_sesion({'client_instance': nombre_socio})
        self._show_validating_screen(nombre_socio)
        threading.Thread(target=self._svp_check_and_launch, daemon=True).start()

    def _show_validating_screen(self, nombre):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text=f"Ejecutando Subscription Validation Protocol...\nClient Instance: {nombre}",
            size_hint=(.85, .15), pos_hint={"center_x": .5, "center_y": .55},
            color=(0, 1, 1, 1), halign='center'
        ))

    def _svp_check_and_launch(self):
        """Subscription Validation Protocol — Verificación completa del Operational Node."""
        acceso, mensaje, vence = svp_verificar(self.hwid, self.selected_client_instance)
        if acceso:
            Clock.schedule_once(lambda dt: self.show_operational_screen(mensaje), 0)
        else:
            Clock.schedule_once(lambda dt: self.show_activation_pending_screen(), 0)

    # ------------------------------------------------------------------ #
    #  Pantalla operacional — Sentinel Core activo
    # ------------------------------------------------------------------ #

    def show_operational_screen(self, mensaje):
        """Pantalla principal del Operational Node activo."""
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text=mensaje,
            size_hint=(.85, .12), pos_hint={"center_x": .5, "center_y": .75},
            color=(0, 1, 1, 1), halign='center'
        ))
        self._op_status_label = Label(
            text="",
            size_hint=(.85, .07), pos_hint={"center_x": .5, "center_y": .65},
            color=(1, 1, 0, 1), halign='center'
        )
        self.layout.add_widget(self._op_status_label)
        launch_btn = Button(
            text="INICIAR SENTINEL CORE",
            size_hint=(.65, .09), pos_hint={"center_x": .5, "center_y": .55},
            background_color=(0, 1, 0.5, 1), color=(0, 0, 0, 1), bold=True
        )
        def _on_launch(btn_instance):
            if getattr(self, '_sentinel_activo', False):
                return
            launch_btn.disabled = True
            launch_btn.text = "Iniciando..."
            self._op_status_label.text = "Cargando módulos del Operational Node..."
            threading.Thread(target=self.start_sentinel_logic, daemon=True).start()
        launch_btn.bind(on_release=_on_launch)
        self.layout.add_widget(launch_btn)
        msg_btn = Button(
            text="&#9993; Bandeja de Salida — Enviar Mensaje",
            size_hint=(.65, .08), pos_hint={"center_x": .5, "center_y": .43},
            background_color=(0.1, 0.15, 0.35, 1), color=(0, 1, 1, 1)
        )
        msg_btn.bind(on_release=lambda _: self.show_outbox_screen())
        self.layout.add_widget(msg_btn)
        config_btn = Button(
            text="⚙ Configuración Avanzada",
            size_hint=(.65, .08), pos_hint={"center_x": .5, "center_y": .32},
            background_color=(0.08, 0.1, 0.2, 1), color=(0, 1, 1, 1)
        )
        config_btn.bind(on_release=lambda _: self.show_advanced_config_screen())
        self.layout.add_widget(config_btn)

    # ------------------------------------------------------------------ #
    #  Bandeja de Salida — mensajería hacia el panel
    # ------------------------------------------------------------------ #

    def show_outbox_screen(self):
        """Bandeja de Salida — Transmisión de mensajes al servidor de control."""
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text="Bandeja de Salida — Mensaje al Administrador",
            size_hint=(.9, .08), pos_hint={"center_x": .5, "center_y": .91},
            color=(0, 1, 0.5, 1), bold=True
        ))
        self._outbox_input = TextInput(
            hint_text="Escriba su mensaje aquí...",
            multiline=True,
            size_hint=(.85, .32),
            pos_hint={"center_x": .5, "center_y": .66}
        )
        self.layout.add_widget(self._outbox_input)
        self._outbox_status = Label(
            text="", size_hint=(.85, .06),
            pos_hint={"center_x": .5, "center_y": .47},
            color=(0, 1, 1, 1), halign='center'
        )
        self.layout.add_widget(self._outbox_status)
        send_btn = Button(
            text="TRANSMITIR MENSAJE",
            size_hint=(.65, .08), pos_hint={"center_x": .5, "center_y": .37},
            background_color=(0, 0.8, 1, 1), color=(0, 0, 0, 1)
        )
        send_btn.bind(on_release=lambda _: self._send_from_outbox())
        self.layout.add_widget(send_btn)
        back_btn = Button(
            text="Volver",
            size_hint=(.45, .07), pos_hint={"center_x": .5, "center_y": .25},
            background_color=(0.15, 0.15, 0.15, 1), color=(0, 1, 1, 1)
        )
        back_btn.bind(on_release=lambda _: threading.Thread(
            target=self._svp_check_and_launch, daemon=True
        ).start())
        self.layout.add_widget(back_btn)

    def _send_from_outbox(self):
        contenido = self._outbox_input.text.strip() if hasattr(self, '_outbox_input') else ''
        if not contenido:
            self._outbox_status.text = "El mensaje no puede estar vacío."
            return
        nombre = self.selected_client_instance or self.hwid
        self._outbox_status.text = "Transmitiendo al servidor de control..."
        threading.Thread(target=self._do_send_message, args=(contenido, nombre), daemon=True).start()

    # ------------------------------------------------------------------ #
    #  Advanced Configuration Interface — Dark Industrial Theme
    # ------------------------------------------------------------------ #

    def show_advanced_config_screen(self):
        """Interfaz de Configuración Avanzada — Dark Industrial."""
        self.layout.clear_widgets()
        
        # Header
        self.layout.add_widget(Label(
            text="⚙ Sentinel Core — Advanced Configuration",
            size_hint=(.9, .07), pos_hint={"center_x": .5, "center_y": .92},
            color=(0, 1, 0.5, 1), bold=True
        ))
        
        # Status Monitor
        status = advanced_config.get_status()
        status_text = (
            f"Connection: {status.get('connection_status', 'N/A')} | "
            f"Latency: {status.get('last_latency', 'N/A')}ms | "
            f"Uptime: {status.get('uptime_seconds', 0)}s"
        )
        self.layout.add_widget(Label(
            text=status_text,
            size_hint=(.85, .06), pos_hint={"center_x": .5, "center_y": .84},
            color=(0, 1, 1, 1), halign='center', font_size='11sp'
        ))
        
        # Configuration options in a scrollable area
        scroll = ScrollView(size_hint=(.85, .60), pos_hint={"center_x": .5, "center_y": .52})
        config_grid = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        config_grid.bind(minimum_height=config_grid.setter('height'))
        
        # Refresh Rate
        config_grid.add_widget(Label(
            text="Refresh Rate (segundos):", size_hint_y=None, height=30,
            color=(0, 1, 0.5, 1), bold=True
        ))
        refresh_input = TextInput(
            text=str(advanced_config.get("refresh_rate", 30)),
            multiline=False, size_hint_y=None, height=40,
            background_color=(0.05, 0.05, 0.05, 1), foreground_color=(0, 1, 1, 1)
        )
        config_grid.add_widget(refresh_input)
        
        # Server Endpoint
        config_grid.add_widget(Label(
            text="Server Endpoint:", size_hint_y=None, height=30,
            color=(0, 1, 0.5, 1), bold=True
        ))
        endpoint_input = TextInput(
            text=advanced_config.get("server_endpoint", "http://127.0.0.1:5000"),
            multiline=False, size_hint_y=None, height=40,
            background_color=(0.05, 0.05, 0.05, 1), foreground_color=(0, 1, 1, 1)
        )
        config_grid.add_widget(endpoint_input)
        
        # High Encryption Toggle
        config_grid.add_widget(Label(
            text="High Encryption:", size_hint_y=None, height=30,
            color=(0, 1, 0.5, 1), bold=True
        ))
        encryption_toggle = Switch(
            active=advanced_config.get("high_encryption", True),
            size_hint_y=None, height=40
        )
        config_grid.add_widget(encryption_toggle)
        
        # Auto-Reconnect Toggle
        config_grid.add_widget(Label(
            text="Auto-Reconnect:", size_hint_y=None, height=30,
            color=(0, 1, 0.5, 1), bold=True
        ))
        reconnect_toggle = Switch(
            active=advanced_config.get("auto_reconnect", True),
            size_hint_y=None, height=40
        )
        config_grid.add_widget(reconnect_toggle)
        
        # Background Sync Toggle
        config_grid.add_widget(Label(
            text="Background Sync:", size_hint_y=None, height=30,
            color=(0, 1, 0.5, 1), bold=True
        ))
        bg_sync_toggle = Switch(
            active=advanced_config.get("background_sync", True),
            size_hint_y=None, height=40
        )
        config_grid.add_widget(bg_sync_toggle)
        
        scroll.add_widget(config_grid)
        self.layout.add_widget(scroll)
        
        # Save Button
        save_btn = Button(
            text="💾 GUARDAR CONFIGURACIÓN",
            size_hint=(.65, .07), pos_hint={"center_x": .5, "center_y": .13},
            background_color=(0, 1, 0.5, 1), color=(0, 0, 0, 1), bold=True
        )
        def _save_config():
            try:
                advanced_config.update_setting("refresh_rate", int(refresh_input.text))
                advanced_config.update_setting("server_endpoint", endpoint_input.text)
                advanced_config.update_setting("high_encryption", encryption_toggle.active)
                advanced_config.update_setting("auto_reconnect", reconnect_toggle.active)
                advanced_config.update_setting("background_sync", bg_sync_toggle.active)
                advanced_config.save()
                self._op_status_label.text = "✓ Configuración guardada."
                Clock.schedule_once(lambda dt: self.show_operational_screen("Sentinel Core — Nodo Operacional Activo"), 2)
            except Exception as e:
                self._op_status_label.text = f"✗ Error: {e}"
        save_btn.bind(on_release=lambda _: _save_config())
        self.layout.add_widget(save_btn)
        
        # Emergency Reset Button
        reset_btn = Button(
            text="🚨 RESETEO DE EMERGENCIA",
            size_hint=(.65, .07), pos_hint={"center_x": .5, "center_y": .04},
            background_color=(0.7, 0.1, 0.1, 1), color=(1, 1, 1, 1), bold=True
        )
        def _emergency_reset():
            ok, msg = advanced_config.emergency_reset()
            self._op_status_label.text = msg
            Clock.schedule_once(lambda dt: self.show_operational_screen("Reinicia la aplicación para aplicar cambios."), 3)
        reset_btn.bind(on_release=lambda _: _emergency_reset())
        self.layout.add_widget(reset_btn)

    # ------------------------------------------------------------------ #
    #  Pantalla de error genérico
    # ------------------------------------------------------------------ #

    def show_error_screen(self, mensaje, retry=False):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text=mensaje,
            size_hint=(.85, .20), pos_hint={"center_x": .5, "center_y": .58},
            color=(1, 0.2, 0.2, 1), halign='center'
        ))
        if retry:
            btn = Button(
                text="REINTENTAR CONEXIÓN",
                size_hint=(.55, .08), pos_hint={"center_x": .5, "center_y": .38},
                background_color=(0, 1, 1, 1), color=(0, 0, 0, 1)
            )
            btn.bind(on_release=lambda _: threading.Thread(
                target=self._svp_inicio, daemon=True
            ).start())
            self.layout.add_widget(btn)

    # ------------------------------------------------------------------ #
    #  SVP re-verificación periódica y lógica del Sentinel Core
    # ------------------------------------------------------------------ #

    def _svp_periodico(self, dt):
        """Subscription Validation Protocol — Re-verificación periódica del Operational Node."""
        acceso, _, _ = svp_verificar(self.hwid, self.selected_client_instance)
        if not acceso:
            self._sentinel_activo = False
            Clock.schedule_once(lambda dt2: self.show_activation_pending_screen(), 0)

    def _reset_launch_btn(self, msg=""):
        """Restaura el botón de inicio y muestra un mensaje de error."""
        if hasattr(self, '_op_status_label') and self._op_status_label:
            self._op_status_label.text = msg
        for w in list(getattr(self, 'layout', FloatLayout()).children):
            if isinstance(w, Button) and ('INICIAR' in (w.text or '') or 'Iniciando' in (w.text or '')):
                w.disabled = False
                w.text = "INICIAR SENTINEL CORE"
        self._sentinel_activo = False

    def start_sentinel_logic(self):
        """Lógica principal del Sentinel Core — Operational Node activo."""
        import logging
        import re
        import sys
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from BOT_CORE.ocr_extractor import extract_distance_and_zone
            from BOT_CORE.logic import es_viaje_rentable
            from SECURITY.stealth import human_click
            from BOT_CORE.screen_reader import find_price_buttons
            logging.basicConfig(filename='sentinel.log', level=logging.INFO)
            self._sentinel_activo = True
            from kivy.clock import Clock as KivyClock
            from config import CHECK_LICENSE_INTERVAL
            KivyClock.schedule_interval(self._svp_periodico, CHECK_LICENSE_INTERVAL)
            Clock.schedule_once(lambda dt: setattr(self._op_status_label, 'text', 'Sentinel Core activo — Operational Node en línea.') if hasattr(self, '_op_status_label') and self._op_status_label else None, 0)
            try:
                d = u2.connect()
            except Exception as adb_err:
                Clock.schedule_once(lambda dt: self._reset_launch_btn(
                    f"Sin dispositivo Android.\n{adb_err}"
                ), 0)
                return
            # Confirmar en UI que el Sentinel Core está activo
            def _mark_active(dt):
                if hasattr(self, '_op_status_label') and self._op_status_label:
                    self._op_status_label.text = 'Sentinel Core activo \u2014 Operational Node en l\u00ednea.'
                for w in list(getattr(self, 'layout', FloatLayout()).children):
                    if isinstance(w, Button) and 'Iniciando' in (w.text or ''):
                        w.text = 'SENTINEL CORE ACTIVO \u25cf'
                        w.background_color = (0, 0.4, 0.2, 1)
            Clock.schedule_once(_mark_active, 0)
            while self._sentinel_activo:
                try:
                    # Monitorear latencia y conexión
                    latency_start = time.time()
                    acceso, _, _ = svp_verificar(self.hwid, self.selected_client_instance)
                    latency_ms = int((time.time() - latency_start) * 1000)
                    
                    advanced_config.update_status(
                        connection_status="connected" if acceso else "reconnecting",
                        last_latency=latency_ms,
                        last_sync=time.strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    if not acceso and advanced_config.get("auto_reconnect"):
                        # Reconexión automática
                        advanced_config.update_status(reconnect_attempts=advanced_config.status.get('reconnect_attempts', 0) + 1)
                        if advanced_config.status['reconnect_attempts'] >= advanced_config.get("max_reconnect_attempts", 5):
                            Clock.schedule_once(lambda dt: self._reset_launch_btn(
                                "Licencia revocada o expirada. Reintentando..."
                            ), 0)
                            self._sentinel_activo = False
                            # Volver a la pantalla de activación
                            threading.Thread(target=self._svp_inicio, daemon=True).start()
                            break
                        time.sleep(advanced_config.get("reconnect_delay", 5))
                        continue
                    
                    # Reset counter si está conectado
                    if acceso:
                        advanced_config.update_status(reconnect_attempts=0)
                    
                    # Lógica principal de automatización
                    botones = find_price_buttons(d)
                    for btn in botones:
                        precio_match = re.search(r"(\d+[\.,]?\d*)", btn['text'])
                        if not precio_match:
                            continue
                        precio_viaje = float(precio_match.group(1).replace(",", "."))
                        distancia_km, _ = extract_distance_and_zone()
                        if not distancia_km:
                            distancia_km = 1
                        if es_viaje_rentable(precio_viaje, distancia_km):
                            match = re.findall(r"\d+", btn['bounds'])
                            if len(match) == 4:
                                x1, y1, x2, y2 = map(int, match)
                                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                                human_click(cx, cy)
                                logging.info(f"Node accepted: price={precio_viaje}, distance={distancia_km}")
                        else:
                            logging.info(f"Node skipped: price={precio_viaje}, distance={distancia_km}")
                except Exception as loop_err:
                    advanced_config.update_status(
                        connection_status="error",
                        last_error=str(loop_err)
                    )
                    logging.error(f"Loop error: {loop_err}")
                
                time.sleep(advanced_config.get("refresh_rate", 30))
        except Exception as fatal_err:
            Clock.schedule_once(lambda dt: self._reset_launch_btn(
                f"Error al iniciar:\n{fatal_err}"
            ), 0)


if __name__ == "__main__":
    SentinelCoreApp().run()
