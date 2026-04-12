import requests
import time
from config import ADMIN_URL, CHECK_LICENSE_INTERVAL, VALIDAR_ENDPOINT

def check_license(device_id):
    try:
        r = requests.get(f"{ADMIN_URL}{VALIDAR_ENDPOINT}{device_id}", timeout=10)
        if r.ok:
            data = r.json()
            return data.get("status") == "Aprobado"
    except Exception as e:
        print(f"Error de licencia: {e}")
    return False

def periodic_license_check(device_id, interval=CHECK_LICENSE_INTERVAL):
    while True:
        if not check_license(device_id):
            print("Licencia revocada o expirada. Apagando bot.")
            exit(0)
        time.sleep(interval)
