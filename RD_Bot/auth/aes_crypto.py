from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import hashlib

BLOCK_SIZE = 16

def pad(s):
    pad_len = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + (chr(pad_len) * pad_len)

def unpad(s):
    pad_len = ord(s[-1])
    return s[:-pad_len]

def get_key(password):
    return hashlib.sha256(password.encode()).digest()

def encrypt(raw, password):
    raw = pad(raw)
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = AES.new(get_key(password), AES.MODE_CBC, iv)
    enc = cipher.encrypt(raw.encode())
    return base64.b64encode(iv + enc).decode()

def decrypt(enc, password):
    enc = base64.b64decode(enc)
    iv = enc[:BLOCK_SIZE]
    cipher = AES.new(get_key(password), AES.MODE_CBC, iv)
    dec = cipher.decrypt(enc[BLOCK_SIZE:]).decode()
    return unpad(dec)

if __name__ == "__main__":
    secret = encrypt("clave_maestra", "password_seguro")
    print(secret)
    print(decrypt(secret, "password_seguro"))
