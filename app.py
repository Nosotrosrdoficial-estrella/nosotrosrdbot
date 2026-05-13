import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Llave de seguridad Sentinel
ACCESS_KEY = "Diosamor"

@app.route('/')
def home():
    return "Servidor Nosotros RD Operativo y Protegido", 200

@app.route('/conectar', methods=['POST'])
def conectar():
    data = request.get_json()
    
    # Validación de seguridad
    if not data or data.get("key") != ACCESS_KEY:
        return jsonify({"status": "error", "message": "Acceso Denegado"}), 403
    
    # Si la clave es correcta
    return jsonify({
        "status": "success", 
        "message": "Conexión establecida con Nosotros RD",
        "encriptacion": "Sentinel Active"
    }), 200

if __name__ == "__main__":
    # Render usa la variable de entorno PORT
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)