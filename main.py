import threading
from auth_module.register import register_device, get_device_id
from auth_module.login import show_login
from perception_engine.ui_reader import find_buttons
from stealth_controller.human_click import human_click
from admin_bridge.license_check import periodic_license_check

import adbutils
import time
import re

def main():
    status = register_device()
    if status != 'aprobado':
        print(f"Estado de registro: {status}. Espera aprobación.")
        return
    if not show_login():
        print("Login fallido.")
        return
    device_id = get_device_id()
    threading.Thread(target=periodic_license_check, args=(device_id,), daemon=True).start()
    device = adbutils.adb.device()
    while True:
        botones = find_buttons()
        for btn in botones:
            match = re.findall(r"\d+", btn['bounds'])
            if len(match) == 4:
                x1, y1, x2, y2 = map(int, match)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                human_click(device, cx, cy)
        time.sleep(1)

if __name__ == "__main__":
    main()
