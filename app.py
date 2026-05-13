import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# La llave única de Nosotros RD
ACCESS_KEY = "Diosamor"

@app.route('/')
def home():
    return "SENTINEL CORE: ESPERANDO LLAVE", 200

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Verificación simple: ¿Es la llave correcta?
    if data and data.get("key") == ACCESS_KEY:
        return jsonify({
            "acceso": "CONFIRMADO",
            "mensaje": "Bienvenido al Sistema Nosotros RD"
        }), 200
    else:
        return jsonify({
            "acceso": "DENEGADO",
            "mensaje": "Llave de seguridad incorrecta"
        }), 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)