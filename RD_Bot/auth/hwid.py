import hashlib
import platform
import uuid

def get_hwid():
    # Combina información única del hardware y sistema
    info = f"{platform.node()}_{platform.machine()}_{uuid.getnode()}"
    return hashlib.sha256(info.encode()).hexdigest()

if __name__ == "__main__":
    print(get_hwid())
