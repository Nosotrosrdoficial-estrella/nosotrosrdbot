import requests
import uuid
from config import ADMIN_URL, VALIDAR_ENDPOINT

def get_device_id():
    try:
        from jnius import autoclass
        Settings = autoclass('android.provider.Settings$Secure')
        context = autoclass('org.kivy.android.PythonActivity').mActivity
        return Settings.getString(context.getContentResolver(), Settings.ANDROID_ID)
    except Exception:
        return str(uuid.getnode())

def register_device():
    device_id = get_device_id()
    # Registrar en el servidor (POST /registrar)
    try:
        r = requests.post(f"{ADMIN_URL}/registrar", json={"hwid": device_id, "nombre_socio": "bot", "plan": "1 Mes"}, timeout=10)
        if r.ok:
            return r.json().get("status", "pendiente")
    except Exception as e:
        print(f"Error de registro: {e}")
    # Si falla el registro, verificar si ya existe
    try:
        r2 = requests.get(f"{ADMIN_URL}{VALIDAR_ENDPOINT}{device_id}", timeout=10)
        if r2.ok:
            return r2.json().get("status", "pendiente")
    except Exception:
        pass
    return "pendiente"
