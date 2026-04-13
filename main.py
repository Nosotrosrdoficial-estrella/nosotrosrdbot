import threading
from auth_module.register import register_device, get_device_id
from auth_module.login import show_login
from kivy.app import App
from kivy.uix.label import Label
import requests

class SentinelApp(App):
    def build(self):
        # Aquí es donde ocurre la magia del enlace
        url_render = "https://atm-admin-aqk6.onrender.com/validar/TEST_ID"
        
        try:
            response = requests.get(url_render, timeout=5)
            if response.status_code == 200:
                mensaje = "Conectado al Panel RD\nEsperando Aprobación..."
            else:
                mensaje = "Error de Servidor\nRevisa tu conexión"
        except:
            mensaje = "Sentinel Core Activo\nBuscando señal de Render..."

        return Label(text=mensaje, font_size='20sp', color=(0, 1, 1, 1))

if __name__ == '__main__':
    SentinelApp().run()
