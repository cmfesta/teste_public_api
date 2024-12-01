# flask_ngrok_example.py
from flask import Flask
from flask import request, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/1", methods=["GET", "POST"])
def hello():
    if request.method == "GET":
        if request.json["hub.challenge"]:
            return request.json["hub.challenge"]


@app.route("/2", methods=["GET", "POST"])
def hello():
    if request.method == "GET":
        if request["hub.challenge"]:
            return request.json["hub.challenge"]


@app.route("/maik", methods=["GET", "POST"])
def maik_response():
    if request.method == "GET":

        return "teste maik"


if __name__ == "__main__":
    app.run()
