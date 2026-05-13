"""Servicio Android de escaneo Sentinel.
Se ejecuta en segundo plano y mantiene heartbeat para diagnóstico.
"""

import json
import os
import time
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEARTBEAT_FILE = os.path.join(BASE_DIR, "service_heartbeat.json")


def write_heartbeat(state: str):
    payload = {
        "state": state,
        "timestamp": datetime.now().isoformat(),
    }
    with open(HEARTBEAT_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    write_heartbeat("started")
    try:
        while True:
            write_heartbeat("running")
            time.sleep(4)
    except KeyboardInterrupt:
        write_heartbeat("stopped")
