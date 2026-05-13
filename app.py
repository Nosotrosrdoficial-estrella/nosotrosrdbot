import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ACCESS_KEY = "Diosamor"

# HTML para la interfaz del servidor
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Nosotros RD - Sentinel Core</title>
    <style>
        body { background-color: #1a1a1a; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { text-align: center; border: 2px solid #007bff; padding: 40px; border-radius: 15px; background-color: #262626; box-shadow: 0 0 20px rgba(0,123,255,0.5); }
        h1 { color: #007bff; margin-bottom: 10px; }
        .status { font-size: 1.2em; color: #00ff00; }
        .brand { font-weight: bold; letter-spacing: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="brand">NOSOTROS RD</h1>
        <p class="status">● SENTINEL CORE ONLINE</p>
        <p>Esperando conexión del bot...</p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # Esto es lo que verás al entrar a la URL en el navegador
    return BASE_HTML

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if data and data.get("key") == ACCESS_KEY:
        return jsonify({
            "acceso": "CONFIRMADO",
            "mensaje": "Conexión Segura Establecida"
        }), 200
    else:
        return jsonify({
            "acceso": "DENEGADO",
            "mensaje": "Error de Autenticación"
        }), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)