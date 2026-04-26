from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return jsonify({"status": "online", "message": "SENTINEL STARK ACTIVE"})


if __name__ == '__main__':
    app.run()
