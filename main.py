# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "POST":
        response = request.json
        return jsonify(response)

    if request.method == "GET":
        response = request.json
        return request


if __name__ == "__main__":
    app.run()
