import customtkinter as ctk
import socket
import threading
import uiautomator2 as u2
import time

SECRET_KEY = "tu_clave_secreta"
SOCKET_HOST = "127.0.0.1"
SOCKET_PORT = 8080
SEARCH_TEXT = "RD$"

class LoginApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Login RD_Bot")
        self.geometry("300x180")
        self.label = ctk.CTkLabel(self, text="Clave de acceso:")
        self.label.pack(pady=10)
        self.entry = ctk.CTkEntry(self, show="*")
        self.entry.pack(pady=5)
        self.button = ctk.CTkButton(self, text="Entrar", command=self.try_login)
        self.button.pack(pady=10)
        self.status = ctk.CTkLabel(self, text="")
        self.status.pack(pady=5)

    def try_login(self):
        if self.entry.get() == SECRET_KEY:
            self.status.configure(text="Acceso concedido", text_color="green")
            self.after(1000, self.start_bot)
        else:
            self.status.configure(text="Clave incorrecta", text_color="red")

    def start_bot(self):
        self.destroy()
        start_socket_and_detection()

def start_socket_and_detection():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SOCKET_HOST, SOCKET_PORT))
        print("Conexión con overlay exitosa.")
    except Exception as e:
        print(f"Error de conexión: {e}")
        return

    d = u2.connect()

    def detection_loop():
        while True:
            d.dump_hierarchy()
            nodes = d.xpath(f"//*[contains(@text, '{SEARCH_TEXT}')]" ).all()
            if nodes:
                print(f"Texto '{SEARCH_TEXT}' encontrado.")
                try:
                    s.sendall(b"FOUND\n")
                except Exception as e:
                    print(f"Error enviando señal: {e}")
                    break
            time.sleep(1)

    threading.Thread(target=detection_loop, daemon=True).start()
    print("Bot iniciado. Buscando texto en pantalla...")

if __name__ == "__main__":
    app = LoginApp()
    app.mainloop()
