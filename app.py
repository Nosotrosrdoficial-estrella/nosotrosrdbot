from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({"status": "online", "message": "SENTINEL ACTIVE"})


@app.route('/validate', methods=['POST'])
def validate():
    return jsonify({"authorized": True})
