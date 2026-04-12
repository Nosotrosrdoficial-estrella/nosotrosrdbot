from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import requests
import threading
import android
import time

ADMIN_URL = "https://mi-admin-panel.com/check?id="

class BotApp(App):
    def build(self):
        self.layout = FloatLayout()
        self.status_label = Label(text="Verificando...", size_hint=(.8, .1), pos_hint={"center_x": .5, "center_y": .7})
        self.layout.add_widget(self.status_label)
        self.android_id = self.get_android_id()
        Clock.schedule_once(lambda dt: threading.Thread(target=self.check_status).start(), 1)
        return self.layout

    def get_android_id(self):
        try:
            droid = android.Android()
            return droid.settingsGetSecure("android_id").result
        except Exception:
            return "SIMULATED_ID_123456"

    def check_status(self):
        url = ADMIN_URL + self.android_id
        try:
            r = requests.get(url, timeout=10)
            if r.ok:
                data = r.json()
                status = data.get("status")
                if status == "active":
                    Clock.schedule_once(lambda dt: self.show_bot_button(), 0)
                elif status == "pending":
                    Clock.schedule_once(lambda dt: self.show_pending_screen(), 0)
                else:
                    Clock.schedule_once(lambda dt: self.show_error(), 0)
            else:
                Clock.schedule_once(lambda dt: self.show_error(), 0)
        except Exception:
            Clock.schedule_once(lambda dt: self.show_error(), 0)

    def show_bot_button(self):
        self.layout.clear_widgets()
        btn = Button(text="Bot Flotante", size_hint=(.3, .1), pos_hint={"center_x": .5, "center_y": .5})
        self.layout.add_widget(btn)

    def show_pending_screen(self):
        self.layout.clear_widgets()
        msg = f"ID pendiente: {self.android_id}"
        self.layout.add_widget(Label(text=msg, size_hint=(.8, .2), pos_hint={"center_x": .5, "center_y": .5}))

    def show_error(self):
        self.layout.clear_widgets()
        self.layout.add_widget(Label(text="Error de conexión", size_hint=(.8, .2), pos_hint={"center_x": .5, "center_y": .5}))

if __name__ == "__main__":
    BotApp().run()
