# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "GET":
        if request.json["hub.challenge"]:
            return request.json["hub.challenge"]

        if request["hub.challenge"]:
            return request.json["hub.challenge"]


if __name__ == "__main__":
    app.run()
