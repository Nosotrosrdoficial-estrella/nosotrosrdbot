import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import threading
import time
import uiautomator2 as u2
from screen_reader import find_price_buttons
from decision_engine import DecisionEngine
import adbutils

SERVER_URL = "https://atm-admin-aqk6.onrender.com"

def get_android_id():
    try:
        from jnius import autoclass
        Settings = autoclass('android.provider.Settings$Secure')
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        return Settings.getString(context.getContentResolver(), Settings.ANDROID_ID)
    except Exception:
        import uuid
        return str(uuid.getnode())

def verificar_suscripcion(hwid):
    """Verifica suscripción contra el servidor. Retorna (bool_acceso, mensaje, fecha_vencimiento)"""
    try:
        response = requests.get(f"{SERVER_URL}/validar/{hwid}", timeout=10)
        data = response.json()
        status = data.get("status")
        vence = data.get("vence")
        if status == "Aprobado":
            print(f"Socio Activo. Suscripción vence el: {vence}")
            return True, f"Activo hasta: {vence}", vence
        elif status == "Expirado":
            print(">>> ERROR: Tu suscripción ha vencido. Contacta a Edwin.")
            return False, "Suscripción Expirada\nContacta a Edwin.", vence
        else:
            print(f">>> ESPERA: Estado pendiente de aprobación ({status}).")
            return False, f"Pendiente de Aprobación\nID: {hwid}", None
    except Exception as e:
        print(f"Error de conexión con el satélite de control: {e}")
        return False, "Error de Conexión\nVerifica tu internet.", None

class BotApp(App):

    def build(self):
        self.layout = FloatLayout()
        self.status_label = Label(
            text="Verificando suscripcion...",
            size_hint=(.8, .1),
            pos_hint={"center_x": .5, "center_y": .7},
            color=(0, 1, 1, 1)
        )
        self.layout.add_widget(self.status_label)
        self.hwid = get_android_id()
        Clock.schedule_once(lambda dt: threading.Thread(target=self.check_access_and_start, daemon=True).start(), 1)
        return self.layout

    def check_access_and_start(self):
        acceso, mensaje, vence = verificar_suscripcion(self.hwid)
        if acceso:
            Clock.schedule_once(lambda dt: self.show_bot_button(mensaje), 0)
        else:
            Clock.schedule_once(lambda dt: self.show_pending_screen(mensaje), 0)

    def show_bot_button(self, mensaje):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text=mensaje, size_hint=(.8, .1),
            pos_hint={"center_x": .5, "center_y": .65}, color=(0, 1, 1, 1)
        ))
        btn = Button(
            text="[INICIAR CAZA DE VIAJES]",
            size_hint=(.6, .1),
            pos_hint={"center_x": .5, "center_y": .5},
            background_color=(0, 1, 1, 1), color=(0, 0, 0, 1)
        )
        btn.bind(on_release=lambda x: threading.Thread(target=self.start_bot_logic, daemon=True).start())
        self.layout.add_widget(btn)

    def show_pending_screen(self, mensaje):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(
            text=mensaje, size_hint=(.8, .2),
            pos_hint={"center_x": .5, "center_y": .5}, color=(1, 0.2, 0.2, 1)
        ))

    def _verificar_periodico(self, dt):
        """Re-verifica suscripción cada CHECK_LICENSE_INTERVAL segundos"""
        acceso, mensaje, _ = verificar_suscripcion(self.hwid)
        if not acceso:
            Clock.schedule_once(lambda dt: self.show_pending_screen("Suscripcion Expirada.\nDeteniendo bot."), 0)
            self._bot_activo = False

    def start_bot_logic(self):
        import logging
        import re
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from BOT_CORE.ocr_extractor import extract_distance_and_zone
        from BOT_CORE.logic import es_viaje_rentable
        from SECURITY.stealth import human_click
        from BOT_CORE.screen_reader import find_price_buttons
        logging.basicConfig(filename='bot.log', level=logging.INFO)
        self._bot_activo = True
        # Verifica suscripción periódicamente (cada 5 min)
        from kivy.clock import Clock as KivyClock
        from config import CHECK_LICENSE_INTERVAL
        KivyClock.schedule_interval(self._verificar_periodico, CHECK_LICENSE_INTERVAL)
        d = u2.connect()
        while self._bot_activo:
            botones = find_price_buttons()
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
                        logging.info(f"Clic aceptado: precio={precio_viaje}, distancia={distancia_km}")
                else:
                    logging.info(f"Viaje ignorado: precio={precio_viaje}, distancia={distancia_km}")
            time.sleep(2)

if __name__ == "__main__":
    BotApp().run()
