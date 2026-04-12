from flask import Flask, request, jsonify

app = Flask(__name__)

# Lista blanca de IDs aprobados
WHITELIST = {"SIMULATED_ID_123456", "ID_DE_PRUEBA_2"}
PENDING = {"ID_PENDIENTE_1"}

@app.route('/check')
def check():
    device_id = request.args.get('id')
    if not device_id:
        return jsonify({"status": "error", "msg": "No ID"}), 400
    if device_id in WHITELIST:
        return jsonify({"status": "active"})
    elif device_id in PENDING:
        return jsonify({"status": "pending"})
    else:
        return jsonify({"status": "pending"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
