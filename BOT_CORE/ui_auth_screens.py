"""
Pantalla de Login y Registro
Interfaz completa con Kivy para autenticación
"""
try:
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.textinput import TextInput
    from kivy.uix.button import Button
    from kivy.uix.popup import Popup
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.spinner import Spinner
    from kivy.uix.checkbox import CheckBox
    from kivy.graphics import Color, RoundedRectangle
    from kivy.metrics import dp, sp
    from kivy.core.window import Window
    KIVY_DISPONIBLE = True
except ImportError:
    KIVY_DISPONIBLE = False

from auth_module.auth_manager import auth


class LoginScreen(BoxLayout):
    """Pantalla de login"""
    
    def __init__(self, callback_exito=None, tema="dark", **kwargs):
        super().__init__(orientation='vertical', padding=dp(20), spacing=dp(15), **kwargs)
        self.callback_exito = callback_exito
        self.tema = tema
        self.colores = self._obtener_colores()
        
        # Fondo
        with self.canvas.before:
            Color(*self.colores["fondo"])
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Título
        titulo = Label(
            text="[b]NOSOTROS RD[/b]\nSistema Sentinel",
            markup=True,
            font_size=sp(24),
            color=self.colores["texto_principal"],
            size_hint_y=0.15,
        )
        self.add_widget(titulo)
        
        # Email
        self.email_input = TextInput(
            multiline=False,
            hint_text="Correo Electrónico",
            size_hint_y=0.08,
            background_color=self.colores["input_bg"],
            foreground_color=self.colores["texto_principal"],
        )
        self.add_widget(self.email_input)
        
        # Contraseña
        self.password_input = TextInput(
            multiline=False,
            hint_text="Contraseña",
            password=True,
            size_hint_y=0.08,
            background_color=self.colores["input_bg"],
            foreground_color=self.colores["texto_principal"],
        )
        self.add_widget(self.password_input)
        
        # Botones
        botones_layout = BoxLayout(size_hint_y=0.12, spacing=dp(10))
        
        btn_login = Button(
            text="Iniciar Sesión",
            background_color=self.colores["boton_principal"],
        )
        btn_login.bind(on_press=self._login)
        botones_layout.add_widget(btn_login)
        
        btn_registrar = Button(
            text="Registrarse",
            background_color=self.colores["boton_secundario"],
        )
        btn_registrar.bind(on_press=self._abrir_registro)
        botones_layout.add_widget(btn_registrar)
        
        self.add_widget(botones_layout)
        
        # Enlace recuperar contraseña
        link_recovery = Label(
            text="[color=0099ff][u]¿Olvidaste tu contraseña?[/u][/color]",
            markup=True,
            size_hint_y=0.08,
        )
        link_recovery.bind(on_touch_down=self._abrir_recovery)
        self.add_widget(link_recovery)
        
        # Espacio
        self.add_widget(Label(size_hint_y=0.3))
    
    def _obtener_colores(self):
        """Retorna paleta según tema"""
        if self.tema == "dark":
            return {
                "fondo": (0.1, 0.1, 0.15, 1),
                "texto_principal": (1, 1, 1, 1),
                "boton_principal": (0, 0.8, 0.5, 1),
                "boton_secundario": (0.2, 0.3, 0.5, 1),
                "input_bg": (0.15, 0.15, 0.2, 1),
            }
        else:
            return {
                "fondo": (0.95, 0.95, 0.95, 1),
                "texto_principal": (0.1, 0.1, 0.1, 1),
                "boton_principal": (0, 0.6, 0.4, 1),
                "boton_secundario": (0.3, 0.4, 0.6, 1),
                "input_bg": (0.9, 0.9, 0.9, 1),
            }
    
    def _update_rect(self, instance, value):
        """Actualiza rectángulo de fondo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _login(self, instance):
        """Autentica al usuario"""
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        
        if not email or not password:
            self._mostrar_alerta("❌ Ingresa email y contraseña")
            return
        
        exito, msg, token = auth.login(email, password)
        
        if exito:
            self._mostrar_alerta("✅ " + msg)
            if self.callback_exito:
                self.callback_exito(token)
        else:
            self._mostrar_alerta(msg)
    
    def _abrir_registro(self, instance):
        """Abre pantalla de registro"""
        if self.parent:
            self.parent.current = "registro"
    
    def _abrir_recovery(self, instance, touch):
        """Abre pantalla de recuperación"""
        if self.collide_point(*touch.pos):
            if self.parent:
                self.parent.current = "recovery"
    
    def _mostrar_alerta(self, mensaje):
        """Muestra alerta emergente"""
        popup = Popup(
            title="NOSOTROS RD",
            content=Label(text=mensaje),
            size_hint=(0.8, 0.3),
        )
        popup.open()


class RegistroScreen(BoxLayout):
    """Pantalla de registro"""
    
    def __init__(self, tema="dark", **kwargs):
        super().__init__(orientation='vertical', padding=dp(20), spacing=dp(10), **kwargs)
        self.tema = tema
        self.colores = self._obtener_colores()
        
        with self.canvas.before:
            Color(*self.colores["fondo"])
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # Scroll para formulario largo
        scroll = ScrollView(size_hint=(1, 0.9))
        
        form_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None)
        form_layout.bind(minimum_height=form_layout.setter('height'))
        
        # Título
        titulo = Label(
            text="[b]Crear Cuenta[/b]",
            markup=True,
            font_size=sp(20),
            color=self.colores["texto_principal"],
            size_hint_y=None,
            height=dp(40),
        )
        form_layout.add_widget(titulo)
        
        # Nombre
        self.nombre_input = TextInput(
            hint_text="Nombre Completo",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=self.colores["input_bg"],
        )
        form_layout.add_widget(self.nombre_input)
        
        # Email
        self.email_input = TextInput(
            hint_text="Correo Electrónico",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=self.colores["input_bg"],
        )
        form_layout.add_widget(self.email_input)
        
        # Teléfono
        self.telefono_input = TextInput(
            hint_text="Teléfono (+1-809-XXXXXXXX)",
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=self.colores["input_bg"],
        )
        form_layout.add_widget(self.telefono_input)
        
        # Contraseña
        self.password_input = TextInput(
            hint_text="Contraseña (mín 8 caracteres)",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=self.colores["input_bg"],
        )
        form_layout.add_widget(self.password_input)
        
        # Confirmar Contraseña
        self.confirm_input = TextInput(
            hint_text="Confirmar Contraseña",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(40),
            background_color=self.colores["input_bg"],
        )
        form_layout.add_widget(self.confirm_input)
        
        # Checkbox términos
        terminos_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        checkbox = CheckBox(size_hint_x=0.1)
        self.terminos_check = checkbox
        terminos_layout.add_widget(checkbox)
        terminos_label = Label(
            text="Acepto Términos y Condiciones",
            size_hint_x=0.9,
        )
        terminos_layout.add_widget(terminos_label)
        form_layout.add_widget(terminos_layout)
        
        scroll.add_widget(form_layout)
        self.add_widget(scroll)
        
        # Botones
        botones_layout = BoxLayout(size_hint_y=0.1, spacing=dp(10))
        
        btn_crear = Button(
            text="Crear Cuenta",
            background_color=self.colores["boton_principal"],
        )
        btn_crear.bind(on_press=self._crear_cuenta)
        botones_layout.add_widget(btn_crear)
        
        btn_volver = Button(
            text="Volver",
            background_color=self.colores["boton_secundario"],
        )
        btn_volver.bind(on_press=lambda x: setattr(self.parent, 'current', 'login'))
        botones_layout.add_widget(btn_volver)
        
        self.add_widget(botones_layout)
    
    def _obtener_colores(self):
        """Retorna paleta según tema"""
        if self.tema == "dark":
            return {
                "fondo": (0.1, 0.1, 0.15, 1),
                "texto_principal": (1, 1, 1, 1),
                "boton_principal": (0, 0.8, 0.5, 1),
                "boton_secundario": (0.2, 0.3, 0.5, 1),
                "input_bg": (0.15, 0.15, 0.2, 1),
            }
        else:
            return {
                "fondo": (0.95, 0.95, 0.95, 1),
                "texto_principal": (0.1, 0.1, 0.1, 1),
                "boton_principal": (0, 0.6, 0.4, 1),
                "boton_secundario": (0.3, 0.4, 0.6, 1),
                "input_bg": (0.9, 0.9, 0.9, 1),
            }
    
    def _update_rect(self, instance, value):
        """Actualiza rectángulo de fondo"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def _crear_cuenta(self, instance):
        """Crea nueva cuenta"""
        nombre = self.nombre_input.text.strip()
        email = self.email_input.text.strip()
        telefono = self.telefono_input.text.strip()
        password = self.password_input.text.strip()
        confirm = self.confirm_input.text.strip()
        
        if not all([nombre, email, telefono, password, confirm]):
            self._mostrar_alerta("❌ Completa todos los campos")
            return
        
        if password != confirm:
            self._mostrar_alerta("❌ Contraseñas no coinciden")
            return
        
        if not self.terminos_check.active:
            self._mostrar_alerta("❌ Acepta los términos y condiciones")
            return
        
        exito, msg = auth.registrar(email, password, telefono, nombre)
        
        if exito:
            self._mostrar_alerta("✅ " + msg)
            # Volver a login
            self.parent.current = "login"
        else:
            self._mostrar_alerta(msg)
    
    def _mostrar_alerta(self, mensaje):
        """Muestra alerta emergente"""
        popup = Popup(
            title="Registro",
            content=Label(text=mensaje),
            size_hint=(0.8, 0.3),
        )
        popup.open()


class RecuperacionScreen(BoxLayout):
    """Pantalla de recuperación de contraseña"""
    
    def __init__(self, tema="dark", **kwargs):
        super().__init__(orientation='vertical', padding=dp(20), spacing=dp(15), **kwargs)
        self.tema = tema
        self.colores = self._obtener_colores()
        
        with self.canvas.before:
            Color(*self.colores["fondo"])
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        
        # Título
        titulo = Label(
            text="[b]Recuperar Contraseña[/b]",
            markup=True,
            font_size=sp(20),
            color=self.colores["texto_principal"],
        )
        self.add_widget(titulo)
        
        # Email
        self.email_input = TextInput(
            hint_text="Ingresa tu correo electrónico",
            multiline=False,
            size_hint_y=0.1,
        )
        self.add_widget(self.email_input)
        
        # Botones
        botones_layout = BoxLayout(size_hint_y=0.12, spacing=dp(10))
        
        btn_recuperar = Button(
            text="Enviar Link",
            background_color=self.colores["boton_principal"],
        )
        btn_recuperar.bind(on_press=self._solicitar_recuperacion)
        botones_layout.add_widget(btn_recuperar)
        
        btn_volver = Button(
            text="Volver",
            background_color=self.colores["boton_secundario"],
        )
        btn_volver.bind(on_press=lambda x: setattr(self.parent, 'current', 'login'))
        botones_layout.add_widget(btn_volver)
        
        self.add_widget(botones_layout)
        self.add_widget(Label())  # Espacio
    
    def _obtener_colores(self):
        if self.tema == "dark":
            return {
                "boton_principal": (0, 0.8, 0.5, 1),
                "boton_secundario": (0.2, 0.3, 0.5, 1),
                "texto_principal": (1, 1, 1, 1),
                "fondo": (0.1, 0.1, 0.15, 1),
            }
        else:
            return {
                "boton_principal": (0, 0.6, 0.4, 1),
                "boton_secundario": (0.3, 0.4, 0.6, 1),
                "texto_principal": (0.1, 0.1, 0.1, 1),
                "fondo": (0.95, 0.95, 0.95, 1),
            }
    
    def _solicitar_recuperacion(self, instance):
        """Solicita recuperación de contraseña"""
        email = self.email_input.text.strip()
        
        if not email:
            popup = Popup(
                title="Error",
                content=Label(text="❌ Ingresa tu email"),
                size_hint=(0.8, 0.3),
            )
            popup.open()
            return
        
        exito, msg, token = auth.solicitar_recuperar_contraseña(email)
        
        popup = Popup(
            title="Recuperación",
            content=Label(text="✅ Link enviado a tu email" if exito else msg),
            size_hint=(0.8, 0.3),
        )
        popup.open()
