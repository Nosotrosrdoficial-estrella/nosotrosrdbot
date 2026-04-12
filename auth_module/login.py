from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
import sys

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cyber-UI Login")
        self.setFixedSize(320, 220)
        self.setStyleSheet("background-color: #0B0E14; color: #00FFFF;")
        layout = QVBoxLayout()
        for label in ["Usuario:", "Contraseña:", "Token:"]:
            layout.addWidget(QLabel(label))
            entry = QLineEdit()
            if "Contraseña" in label or "Token" in label:
                entry.setEchoMode(QLineEdit.EchoMode.Password)
            setattr(self, f"input_{label.lower().replace(':','').replace(' ','_')}", entry)
            layout.addWidget(entry)
        self.status = QLabel("")
        layout.addWidget(self.status)
        btn = QPushButton("Entrar")
        btn.setStyleSheet("background-color: #00FFFF; color: #0B0E14;")
        btn.clicked.connect(self.check_login)
        layout.addWidget(btn)
        self.setLayout(layout)
        self.accepted = False

    def check_login(self):
        if self.input_usuario.text() and self.input_contraseña.text() and self.input_token.text():
            self.accepted = True
            self.close()
        else:
            self.status.setText("Completa todos los campos.")

def show_login():
    app = QApplication(sys.argv)
    win = LoginWindow()
    win.show()
    app.exec()
    return win.accepted
