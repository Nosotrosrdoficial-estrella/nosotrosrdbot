from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def home():
    return jsonify({"status": "online", "message": "SENTINEL STARK ACTIVE"})


if __name__ == '__main__':
    app.run()
