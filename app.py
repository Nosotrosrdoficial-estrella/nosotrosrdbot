from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "SENTINEL CORE v1.0 ACTIVE"
    })


@app.route('/validate', methods=['POST'])
def validate():
    return jsonify({"authorized": True})

# No pongas nada mas debajo de esta linea
